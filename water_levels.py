import streamlit  as st
import streamlit.components.v1 as components
import pandas as pd
import altair as alt
import numpy as np
from datetime import datetime, date, timedelta
from scipy import stats
from water_levels_texts import texts
import json
import helper
import plots

import const as cn
from well_records_texts import texts
import gw_data


MIN_OBSERVATIONS_FOR_MK = 10
FIGURE = 'fig'
TABLE = 'tab'
CURRENT_YEAR = int(date.today().strftime("%Y"))

class Analysis():
    def __init__(self):
        self.wl_data = self.get_water_level_data()
        self.monitoring_stations = list(self.wl_data['stationid'].unique())
        self.well_records = gw_data.get_well_records(self.monitoring_stations)
        self.precip = self.get_precip_data()
        self.rhein_pegel = self.get_rheinpegel_data()


    @st.cache
    def get_rheinpegel_data(self):
        df = gw_data.get_standard_dataset('rheinpegel')
        df = df[['date', 'pegel_masl']]
        df = df[df['pegel_masl'] > 230]
        df.columns = ['date','pegel']
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['week'] = df['date'].dt.week
        df['day_of_week'] = df['date'].dt.dayofweek
        df['first_day_of_week'] = df.date - df.day_of_week * timedelta(days=1)
        return df

    @st.cache
    def get_water_level_data(self):
        df = gw_data.get_standard_dataset('wl-level')
        df.columns = ['date','stationid','value']
        df = df[df['value'] < 500]
        df['year'] = df['date'].dt.year
        return df
    
    #@st.cache
    def get_precip_data(self):
        df = gw_data.get_standard_dataset('meteo')
        df = df[['timestamp','precip_sum']]
        df['year'] = df['timestamp'].dt.year
        df['month'] = df['timestamp'].dt.month
        df['week'] = df['timestamp'].dt.week
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['first_day_of_week'] = df.timestamp - df.day_of_week * timedelta(days=1)
        return df
    

    def show_record(self, id):
        df =  self.well_records[ self.well_records['laufnummer'] == id]
        if df.iloc[0]['has_chemical_analysis'] == 1:
            df['chemische_analysen'] =  f"https://data.bs.ch/explore/embed/dataset/100164/table/?sort=timestamp&refine.stationid={id}"
        if df.iloc[0]['grundwasserdaten'] == 1:
            df['grundwasser_messungen'] =  f"https://data.bs.ch/explore/embed/dataset/100164/table/?sort=timestamp&refine.stationid={id}"
        df[df.columns] = df[df.columns].astype(str)
        table = df.transpose().to_html(render_links=True, escape=False)
        style = """<style>
            table,
            th,
            td {
                padding: 10px;
                border: 1px solid black;
                border-collapse: collapse;
            }
            </style>"""
        components.html(style + table,height=1000, scrolling=True)
        

    def show_info(self):
        text = texts['info'].format(len(self.well_records), len(self.monitoring_stations))
        st.markdown(text, unsafe_allow_html=True)
    
    
    def get_filtered_stations(self):
        df = self.well_records
        with st.sidebar.expander('🔎 Filter'):
            chem_only = st.checkbox('Boreholes with chem analysis')
            water_level_only = st.checkbox('Boreholes with waterlevels')
            options_geology = ['<Select type>'] + list(df['rock_desc'].unique())
            sel_geology = st.selectbox('Bedrock geology', options = options_geology)
            options_art = ['<Select type>'] + list(df['art'].unique())
            sel_type = st.selectbox('Borehole type', options = options_art)
            if chem_only:
                df =  df[df['has_chemical_analysis']==1]
            if water_level_only:
                df =  df[df['laufnummer'].isin(self.monitoring_stations)]
            if options_art.index(sel_type)>0:
                df =  df[df['art']==sel_type]
            if options_geology.index(sel_geology)>0:
                df = df[df['rock_desc']==sel_geology]
            depth = st.number_input('Borehole depth (m)', min_value=0,max_value=5000)
            if depth > 0:
                depth_comp = st.radio('Depth comparison',['<', '>'])
                if depth >0:
                    if depth_comp=='<':
                        df =  df[df['bohrtiefe_m'] < depth]
                    else:
                        df =  df[df['bohrtiefe_m'] > depth]
            df = df[cn.station_grid_fields]
        return df


    def show_waterlevel_plot(self):
        def bar_width(start_year, end_year):
            if  end_year - start_year < 2:
                result = 5
            elif end_year - start_year <5:
                result = 2
            else:
                result = 1
            return result

        df = self.well_records
        df =  df[df['laufnummer'].isin(self.monitoring_stations)]
        df = df[cn.station_grid_fields]
        settings = {'height':250, 'selection_mode':'single', 'fit_columns_on_grid_load':False}
        st.markdown(f"#### {len(df)} records found")
        selected = helper.show_table(df, [], settings)

        options_years = range(1976, CURRENT_YEAR+1)
        with st.sidebar.expander("🔎 Filter",expanded=True):
            start_year, end_year = st.select_slider('Year', options=options_years, value=(options_years[0],options_years[-1]))
        with st.sidebar.expander("⚙️ Settings", expanded=True):
            show_precipitation = st.checkbox('Show precipitation plot', value=True)
            show_rheinpegel = st.checkbox('Show Rhine water level plot', value=False)
            show_map = st.checkbox('Show station location on map', value=True)
            show_record = st.checkbox('Show well record', value=False)
        
        if len(selected)>0:
            selected = selected.iloc[0]
            station_sel = selected['laufnummer']
            df = self.wl_data[(self.wl_data['stationid']==station_sel)]
            df = df[(df['year'].isin(range(start_year, end_year+1)))]
            
            if len(df)>0:
                settings={'title': f"{selected['street']} {selected['house_number']} ({station_sel})", 'x':'date', 'y':'value', 'tooltip':['date', 'value'], 
                    'width':1000, 'height': 300, 'x_title':'', 'y_title': 'WL elevation (masl)'}
                min_y = int(df['value'].min())-1
                max_y = int(df['value'].max())+1
                settings['y_domain'] = [min_y, max_y]
                settings['x_domain'] = list(pd.to_datetime([date(start_year,1,1), date(end_year,12,31)]).astype(int) / 10 ** 6)
                plots.wl_time_series_chart(df, settings)
                filename = f"{station_sel}_wl.csv"
                st.markdown(helper.get_table_download_link(df, filename), unsafe_allow_html=True)
                
                if show_precipitation: 
                    df = self.precip[['first_day_of_week','precip_sum']]
                    df = df.groupby(['first_day_of_week']).sum().reset_index()
                    df.columns=['date','precip_mm']
                    settings={'title': f"Precipitation, Meteo Station Binningen, aggregated by week", 'x':'date', 'y':'precip_mm', 'tooltip':['date', 'precip_mm'], 
                        'width':1000, 'height': 200, 'x_title': '', 'y_title': 'Precipitation (mm)'}
                    settings['x_domain'] = list(pd.to_datetime([date(start_year,1,1), date(end_year,12,31)]).astype(int) / 10 ** 6)
                    settings['size'] = bar_width(start_year, end_year)
                    plots.time_series_bar(df, settings)
                    filename = f"precipitation.csv"
                    st.markdown(helper.get_table_download_link(df, filename), unsafe_allow_html=True)

                if show_rheinpegel:
                    df = self.rhein_pegel[['first_day_of_week','pegel']]
                    df = df.groupby(['first_day_of_week']).mean().reset_index()
                    df.columns=['date','pegel']
                    settings={'title': f"Rheinpegel, Kleinbasler Seite auf Höhe des Birs-Zuflusses", 'x':'date', 'y':'pegel', 'tooltip':['date', 'pegel'], 
                        'width':1000, 'height': 200, 'x_title': '', 'y_title': 'Water level (masl)'}
                    settings['x_domain'] = list(pd.to_datetime([date(start_year,1,1), date(end_year,12,31)]).astype(int) / 10 ** 6)
                    min_y = int(df['pegel'].min()) - 1
                    max_y = int(df['pegel'].max()) + 1
                    settings['y_domain'] = [min_y, max_y]
                    plots.time_series_line(df, settings)
                    filename = f"rhine_level.csv"
                    st.markdown(helper.get_table_download_link(df, filename), unsafe_allow_html=True)

                # Map
                if show_map:
                    settings={'title': f"Station location:", 'x':'long', 'y':'lat', 
                        'width':200, 'height': 200, 'lat':'lat', 'long':'long'}
                    df = self.well_records[self.well_records['laufnummer']==station_sel]
                    settings['midpoint'] = (df['lat'], df['long'] )
                    st.markdown(settings['title'])
                    plots.location_map(df, settings)
                if show_record:
                    st.markdown('Well record')
                    self.show_record(station_sel)
            else:
                st.markdown(f"😞 Sorry, no records found for station {station_sel}")

    def show_menu(self):
        menu_options = ['Info', 'Show water level plots']
        menu_sel = st.sidebar.selectbox('Show', options=menu_options)
        if menu_options.index(menu_sel)==0:
            self.show_info()
        if menu_options.index(menu_sel)==1:
            self.show_waterlevel_plot()