import streamlit  as st
import streamlit.components.v1 as components
import pandas as pd
import altair as alt
import numpy as np
from st_aggrid import AgGrid
from datetime import datetime, date, timedelta
from scipy import stats
from temperature_texts import texts
import requests
import json
import io
import helper
import plots
from well_records_texts import texts

MIN_OBSERVATIONS_FOR_MK = 10
FIGURE = 'fig'
TABLE = 'tab'
CURRENT_YEAR = int(date.today().strftime("%Y"))

class Analysis():
    def __init__(self):
        self.data = self.get_records()        
        self.stations_list = list(self.data['Vollständige Laufnummer'])
        self.wl_data = self.get_water_level_data()
        self.precip = self.get_precip_data()
        self.rhein_pegel = self.get_rheinpegel_data()
        self.monitoring_stations = list(self.wl_data['stationid'].unique())
     
    def get_records(self):
        df = pd.read_csv("./data/100182.csv", sep=';')
        df[['Lat', 'Long']] = df['Geo Point'].str.split(',', expand=True)
        df['Bohrtiefe (m)'] = df['Z-Koordinate vom Top'] - df['Z-Koordinate von der Basis']
        df['Vollständige Laufnummer'] = df['Vollständige Laufnummer'].astype('str')
        # df[df['Bohrtiefe (m)'].isna()]['Bohrtiefe (m)'] = df['Terrain-Kote'] - df['Sohle-Kote']
       
        df = df.drop(['Geo Point', 'Geo Shape', 'Kanton', 'Klassifikation', 'Gemeinde bzw. Sektion'], axis=1)
        return df
    
    def get_rheinpegel_data(self):
        filename = './100089.gzip'
        df = pd.read_parquet(filename)
        df = df[['date', 'mean_pegel']]
        df.columns = ['date','pegel']
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['week'] = df['date'].dt.week
        df['day_of_week'] = df['date'].dt.dayofweek
        df['first_day_of_week'] = df.date - df.day_of_week * timedelta(days=1)
        return df

    def get_water_level_data(self):
        filename = './100164.gzip'
        df = pd.read_parquet(filename)
        df.columns = ['date','stationid','value']
        df = df[df['value'] < 500]
        df['year'] = df['date'].dt.year
        return df
    
    def get_precip_data(self):
        filename = './meteo_blue_temp_prec.gzip'
        df = pd.read_parquet(filename)
        df = df[['timestamp','precip_sum']]
        df['year'] = df['timestamp'].dt.year
        df['month'] = df['timestamp'].dt.month
        df['week'] = df['timestamp'].dt.week
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['first_day_of_week'] = df.timestamp - df.day_of_week * timedelta(days=1)
        return df
    

    def show_record(self, id):
        df =  self.data[ self.data['Vollständige Laufnummer'] == id]
        if df.iloc[0]['chemische Untersuchung (ja/nein)'] == 1:
            df['Chemische Analysen'] =  f"https://data.bs.ch/explore/embed/dataset/100164/table/?sort=timestamp&refine.stationid={id}"
        if df.iloc[0]['Grundwasserdaten'] == 1:
            df['Grundwassermessungen'] =  f"https://data.bs.ch/explore/embed/dataset/100164/table/?sort=timestamp&refine.stationid={id}"
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
        text = texts['info'].format(len(self.data), len(self.monitoring_stations))
        st.markdown(text, unsafe_allow_html=True)
    
    
    def get_filtered_stations(self):
        df = self.data
        with st.sidebar.expander('🔎Filter'):
            chem_only = st.checkbox('boreholes with chem analysis')
            water_level_only = st.checkbox('boreholes with waterlevels')
            options_geology = ['<Select type>'] + list(df['Oberkante Fels-Stratigraphie'].unique())
            sel_geology = st.selectbox('Bedrock geology', options = options_geology)
            options_art = ['<Select type>'] + list(df['Art'].unique())
            sel_type = st.selectbox('Borehole type', options = options_art)
            if chem_only:
                df =  df[df['chemische Untersuchung (ja/nein)']==1]
            if water_level_only:
                df =  df[df['Vollständige Laufnummer'].isin(self.monitoring_stations)]
            if options_art.index(sel_type)>0:
                df =  df[df['Art']==sel_type]
            if options_geology.index(sel_geology)>0:
                df = df[df['Oberkante Fels-Stratigraphie']==sel_geology]
            depth = st.number_input('borehole depth (m)', min_value=0,max_value=5000)
            if depth > 0:
                depth_comp = st.radio('depth comparison',['<', '>'])
                if depth >0:
                    if depth_comp=='<':
                        df =  df[df['Bohrtiefe (m)'] < depth]
                    else:
                        df =  df[df['Bohrtiefe (m)'] > depth]
            fields = ['Vollständige Laufnummer', 'Art', 'Strasse', 'Hausummer', 'Oberkante Fels-Stratigraphie','Bohrtiefe (m)']
            df = df[fields]
        return df
    

    def get_water_level_data_obsolet(self, stationid, year):
        url = "https://data.bs.ch/api/v2/catalog/datasets/100164/records?limit={}&offset={}&select=stationid,timestamp,value&where=stationid={}%20and%20year(timestamp)={}"
        url_data = requests.get(url.format(1, 0, stationid, year)).content # create HTTP response object 
        data = json.loads(url_data)
        total_count = data['total_count']
        all_df = pd.DataFrame()
        if total_count > 0:
            has_more_records = total_count > 0
            offset=0
            df_list = []
            with st.spinner('Loading data'):
                while has_more_records:
                    url_data = requests.get(url.format(-1, offset,stationid, year)).content # create HTTP response object 
                    data = json.loads(url_data)
                    total_count = data['total_count']
                    if offset >= 9800 or offset >= total_count:
                        has_more_records=False
                    elif data['total_count'] > 0:
                        data = data['records']
                        df = pd.DataFrame(data)['record']
                        df = pd.DataFrame(x['fields'] for x in df)
                        df_list.append(df)
                        offset += 100
                    else:
                        has_more_records=False
            all_df = pd.concat(df_list)
        return all_df 


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
        df =  df[df['Vollständige Laufnummer'].isin(self.monitoring_stations)]
        settings = {'height':250, 'selection_mode':'single', 'fit_columns_on_grid_load':False}
        st.markdown(f"#### {len(df)} records found")
        selected = helper.show_table(df, [], settings)

        options_years = range(1976, CURRENT_YEAR+1)
        with st.sidebar.expander("🔎 Filter"):
            start_year, end_year = st.select_slider('Year', options=options_years, value=(options_years[0],options_years[-1]))
        with st.sidebar.expander("⚙️ Settings"):
            show_precipitation = st.checkbox('Show Precipitation plot', value=True)
            show_rheinpegel = st.checkbox('Show Rhein water level plot', value=True)
            show_map = st.checkbox('Show station location on map', value=True)
        
        if len(selected)>0:
            selected = selected.iloc[0]
            station_sel = selected['Vollständige Laufnummer']
            df = self.wl_data[(self.wl_data['stationid']==station_sel)]
            df = df[(df['year'].isin(range(start_year, end_year+1)))]
            
            if len(df)>0:
                settings={'title': f"{selected['Strasse']} {selected['Hausummer']} ({station_sel})", 'x':'date', 'y':'value', 'tooltip':['date', 'value'], 
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
                    settings={'title': f"Precipitation, Meteo Station Binningen", 'x':'date', 'y':'precip_mm', 'tooltip':['date', 'precip_mm'], 
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
                    min_y = int(df['pegel'].min())-1
                    max_y = int(df['pegel'].max())+1
                    settings['y_domain'] = [min_y, max_y]
                    plots.time_series_line(df, settings)

                # Map
                if show_map:
                    settings={'title': f"Station location:", 'x':'Long', 'y':'Lat', 
                        'width':200, 'height': 200}
                    df = pd.DataFrame({'Long':[selected['Long']], 'Lat':[selected['Lat']]})
                    settings['midpoint'] = (selected['Lat'], selected['Long'] )
                    st.write(settings['title'])
                    plots.location_map(df, settings)
            else:
                st.markdown(f"😞 Sorry, no records found for station {station_sel}")

    def show_single_record(self):
        df = self.get_filtered_stations()
        settings = {'height':250, 'selection_mode':'single', 'fit_columns_on_grid_load': False}
        st.markdown(f"#### {len(df)} records found")
        selected = helper.show_table(df, [], settings)
        if len(selected)>0:
            station_sel = selected.iloc[0]['Vollständige Laufnummer']
            self.show_record(station_sel)

    def show_menu(self):
        menu_options = ['Info', 'Well record', 'Water level plot']
        menu_sel = st.sidebar.selectbox('Show',options=menu_options)
        if menu_options.index(menu_sel)==0:
            self.show_info()
        if menu_options.index(menu_sel)==1:
            self.show_single_record()
        if menu_options.index(menu_sel)==2:
            self.show_waterlevel_plot()