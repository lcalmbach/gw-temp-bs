import streamlit  as st
import streamlit.components.v1 as components
import pandas as pd
import altair as alt
import numpy as np
from datetime import datetime, date, timedelta
from scipy import stats
from temperature_texts import texts
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
        self.well_records = gw_data.get_well_records([])
        self.stations_list = list(self.well_records['laufnummer'])
        self.wl_data = self.get_water_level_data()
        self.monitoring_stations = list(self.wl_data['stationid'].unique())


    @st.cache
    def get_water_level_data(self):
        df = gw_data.get_standard_dataset('wl-level')
        df.columns = ['date','stationid','value']
        df = df[df['value'] < 500]
        df['year'] = df['date'].dt.year
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
            options_geology = ['<Select geology>'] + list(df['geology'].unique())
            sel_geology = st.selectbox('Bedrock geology', options = options_geology)
            options_art = ['<Select type>'] + list(df['art'].unique())
            sel_type = st.selectbox('Borehole type', options = options_art)
            sel_stations = st.multiselect("Stations",options=list(self.well_records['laufnummer']))
            if sel_stations:
                df =  df[df['laufnummer'].isin(sel_stations)]
            if chem_only:
                df =  df[df['has_chemical_analysis']==1]
            if water_level_only:
                df =  df[df['laufnummer'].isin(self.monitoring_stations)]
            if options_art.index(sel_type)>0:
                df =  df[df['art']==sel_type]
            if options_geology.index(sel_geology)>0:
                df = df[df['geology']==sel_geology]
            depth = st.number_input('Borehole depth (m)', min_value=0,max_value=5000)
            if depth > 0:
                depth_comp = st.radio('Depth comparison',['<', '>'])
                if depth >0:
                    if depth_comp=='<':
                        df =  df[df['depth_m'] < depth]
                    else:
                        df =  df[df['depth_m'] > depth]
            df = df[cn.station_grid_fields]
        return df
    
    
    def show_single_record(self):
        df = self.get_filtered_stations()
        settings = {'height':250, 'selection_mode':'single', 'fit_columns_on_grid_load': False}
        st.markdown(f"#### {len(df)} records found")
        st.markdown('click on record to show details')
        selected = helper.show_table(df, [], settings)
        if len(selected)>0:
            selected = selected.iloc[0]
            station_sel = selected['laufnummer']
            self.show_record(station_sel)

            # show map
            settings={'title': f"Station location:", 'long':'long', 'lat':'lat', 
                'width':200, 'height': 200}
            df = pd.DataFrame({'long':[selected['long']], 'lat':[selected['lat']]})
            settings['midpoint'] = (selected['lat'], selected['long'] )
            st.write(settings['title'])
            plots.location_map(df, settings)
            

    def show_menu(self):
        menu_options = ['Info', 'Show record']
        menu_sel = st.sidebar.selectbox('Show', options=menu_options)
        if menu_options.index(menu_sel)==0:
            self.show_info()
        if menu_options.index(menu_sel)==1:
            self.show_single_record()