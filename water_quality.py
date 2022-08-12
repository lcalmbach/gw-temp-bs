import streamlit  as st
import streamlit.components.v1 as components
import pandas as pd
import altair as alt
import numpy as np
from datetime import datetime, date, timedelta
from scipy import stats
from water_quality_texts import texts
import helper
import plots
import const as cn
import gw_data as data


MIN_OBSERVATIONS_FOR_MK = 10
FIGURE = 'fig'
TABLE = 'tab'
CURRENT_YEAR = int(date.today().strftime("%Y"))
select_grid_fields = ['catnr45', 'art', 'street', 'h_number', 'rock_desc','bohrtiefe_m', 'long', 'lat']

class Analysis():
    def __init__(self):
        self.wq_data = data.get_water_quality_data()
        self.samples = self.wq_data[cn.wq_sample_parameter].drop_duplicates()
        self.wq_parameters = data.get_standard_dataset('water-quality-parameters')
        self.stations_list = list(self.wq_data['station_id'].unique())
        self.well_records = data.get_well_records(self.stations_list)
        current_year = datetime.now().year
        last_5years = range(current_year-5,current_year+1)
        self.stations_with_recent_data = list(self.wq_data[self.wq_data['year'].isin(last_5years)]['station_id'].unique())

    def show_record(self, id):
        df =  self.data[ self.data['catnr45'] == id]
        if df.iloc[0]['chemische_untersuchung_janein'] == 1:
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
        text = texts['info'].format(len(self.stations_list), len(self.stations_with_recent_data),3000)
        st.markdown(text, unsafe_allow_html=True)
    
    def get_filtered_stations(self):
        df = self.data
        with st.sidebar.expander('🔎 Filter'):
            chem_only = st.checkbox('Boreholes with chem analysis')
            water_level_only = st.checkbox('Boreholes with waterlevels')
            options_geology = ['<Select type>'] + list(df['rock_desc'].unique())
            sel_geology = st.selectbox('Bedrock geology', options = options_geology)
            options_art = ['<Select type>'] + list(df['art'].unique())
            sel_type = st.selectbox('Borehole type', options = options_art)
            if chem_only:
                df =  df[df['chemische_untersuchung_janein']==1]
            if water_level_only:
                df =  df[df['catnr45'].isin(self.monitoring_stations)]
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
            df = df[select_grid_fields]
        return df
    
    def show_water_quality_plot():
        pass


    def show_waterlevel_plot(self):
        def bar_width(start_year, end_year):
            if  end_year - start_year < 2:
                result = 5
            elif end_year - start_year <5:
                result = 2
            else:
                result = 1
            return result

        df = self.data
        df =  df[df['catnr45'].isin(self.monitoring_stations)]
        df = df[select_grid_fields]
        settings = {'height':250, 'selection_mode':'single', 'fit_columns_on_grid_load':False}
        st.markdown(f"#### {len(df)} records found")
        selected = helper.show_table(df, [], settings)

        options_years = range(1976, CURRENT_YEAR+1)
        with st.sidebar.expander("🔎 Filter"):
            start_year, end_year = st.select_slider('Year', options=options_years, value=(options_years[0],options_years[-1]))
        with st.sidebar.expander("⚙️ Settings"):
            show_precipitation = st.checkbox('Show precipitation plot', value=True)
            show_rheinpegel = st.checkbox('Show Rhine water level plot', value=False)
            show_map = st.checkbox('Show station location on map', value=True)
            show_record = st.checkbox('Show well record', value=False)
        
        if len(selected)>0:
            selected = selected.iloc[0]
            station_sel = selected['catnr45']
            df = self.wl_data[(self.wl_data['stationid']==station_sel)]
            df = df[(df['year'].isin(range(start_year, end_year+1)))]
            
            if len(df)>0:
                settings={'title': f"{selected['street']} {selected['h_number']} ({station_sel})", 'x':'date', 'y':'value', 'tooltip':['date', 'value'], 
                    'width':1000, 'height': 300, 'x_title':'', 'y_title': 'WL elevation (masl)'}
                min_y = int(df['value'].min())-1
                max_y = int(df['value'].max())+1
                settings['y_domain'] = [min_y, max_y]
                settings['x_domain'] = list(pd.to_datetime([date(start_year,1,1), date(end_year,12,31)]).astype(int) / 10 ** 6)
                plots.wl_time_series_chart(df, settings)
                
                if show_precipitation: 
                    df = self.precip[['first_day_of_week','precip_sum']]
                    df = df.groupby(['first_day_of_week']).sum().reset_index()
                    df.columns=['date','precip_mm']
                    settings={'title': f"Precipitation, Meteo Station Binningen, aggregated by week", 'x':'date', 'y':'precip_mm', 'tooltip':['date', 'precip_mm'], 
                        'width':1000, 'height': 200, 'x_title': '', 'y_title': 'Precipitation (mm)'}
                    settings['x_domain'] = list(pd.to_datetime([date(start_year,1,1), date(end_year,12,31)]).astype(int) / 10 ** 6)
                    settings['size'] = bar_width(start_year, end_year)
                    plots.time_series_bar(df, settings)

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

                # Map
                if show_map:
                    settings={'title': f"Station location:", 'x':'long', 'y':'lat', 
                        'width':200, 'height': 200, 'lat':'lat', 'long':'long'}
                    df = pd.DataFrame({'long':[selected['long']], 'lat':[selected['lat']]})
                    settings['midpoint'] = (selected['lat'], selected['long'] )
                    st.markdown(settings['title'])
                    plots.location_map(df, settings)
                if show_record:
                    st.markdown('Well record')
                    self.show_record(station_sel)
            else:
                st.markdown(f"😞 Sorry, no records found for station {station_sel}")

    def show_single_record(self):
        df = self.get_filtered_stations()
        settings = {'height':250, 'selection_mode':'single', 'fit_columns_on_grid_load': False}
        st.markdown(f"#### {len(df)} records found")
        selected = helper.show_table(df, [], settings)
        if len(selected)>0:
            selected = selected.iloc[0]
            station_sel = selected['catnr45']
            self.show_record(station_sel)

            # show map
            settings={'title': f"Station location:", 'long':'long', 'lat':'lat', 
                'width':200, 'height': 200}
            df = pd.DataFrame({'long':[selected['long']], 'lat':[selected['lat']]})
            settings['midpoint'] = (selected['lat'], selected['long'] )
            st.write(settings['title'])
            plots.location_map(df, settings)


    def show_stations(self):
        def get_filter():
            f={}
            with st.sidebar.expander("🔎Filter",expanded=True):
                f['geology'] = st.selectbox('Geology', options=[])
            filter = ''
            return filter


        def show_sample_detail(sampleno):
            st.write('here comes a grid with all measurements')
        

        def show_samples(station_id):
            df = self.samples[self.samples['station_id']==int(station_id)]
            settings['height'] = helper.get_auto_grid_height(df,400)
            st.markdown(f"**{len(df)} samples**")
            sel_sample = helper.show_table(df, cols,settings)
            if len(sel_station)>0:
                #todo include sample no in 
                sampleno = sel_station.iloc[0]['sampleno']
                show_sample_detail(sampleno)

        filter = get_filter()
        df = self.well_records[cn.station_grid_fields]
        cols={}
        
        settings = {'height':helper.get_auto_grid_height(df,400), 'selection_mode':'single', 'fit_columns_on_grid_load': False}
        st.markdown(f"**{len(df)} stations found**")
        sel_station = helper.show_table(df,cols,settings)
        if len(sel_station)>0:
            station_id = sel_station.iloc[0]['laufnummer']
            show_samples(station_id)
        

    def show_parameters(self):
        pass
    

    def show_stats(self):
        pass


    def show_menu(self):
        menu_options = ['Info', 'Station/Samples', 'Parameters', 'Statistics']
        menu_sel = st.sidebar.selectbox('Show',options=menu_options)
        if menu_options.index(menu_sel)==0:
            self.show_info()
        if menu_options.index(menu_sel)==1:
            self.show_stations()
        if menu_options.index(menu_sel)==2:
            self.show_parameters()
        if menu_options.index(menu_sel)==3:
            self.show_stats()