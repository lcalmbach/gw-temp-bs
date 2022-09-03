import streamlit  as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime, date
# from scipy import stats
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
        self.wq_parameter_general_groups = list(self.wq_parameters['allgemeine_parametergruppe'].unique())
        self.wq_parameter_groups = list(self.wq_parameters['gruppe'].unique())
        self.stations_list = list(self.wq_data['station_id'].unique())
        self.well_records = data.get_well_records(self.stations_list)
        self.well_records['laufnummer']=self.well_records['laufnummer'].astype(int)
        self.geology = list(self.well_records['geology'].unique())
        self.guideline = pd.read_csv(cn.datasource['wq_guidelines'],sep=';')
        gl = self.guideline[['parameter','value','unit']]
        gl.columns = ['parameter','gl_value','gl_unit']
        self.wq_parameters = self.wq_parameters.merge(gl, on='parameter', how='left')
        current_year = datetime.now().year
        last_5years = range(current_year-5,current_year+1)
        self.stations_with_recent_data = list(self.wq_data[self.wq_data['year'].isin(last_5years)]['station_id'].unique())
        self.settings = {}

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
        text = texts['info'].format(len(self.stations_list), len(self.stations_with_recent_data),len(self.wq_parameters))
        st.markdown(text, unsafe_allow_html=True)
    
    def filter_parameters(self,df):
        filter = {}
        with st.sidebar.expander("🔎Filter",expanded=True):
            options_general_groups = ['<select general group>'] + self.wq_parameter_general_groups
            sel_general_group = st.selectbox('General parameter group', options=options_general_groups)
            if options_general_groups.index(sel_general_group)>0:
                df = df[df['allgemeine_parametergruppe']==sel_general_group]
            
            options_groups = ['<select group>'] + self.wq_parameter_groups
            sel_group = st.selectbox('Parameter group', options=options_groups)
            if options_groups.index(sel_group)>0:
                df = df[df['gruppe']==sel_group]
            
            if options_groups.index(sel_group)>0:
                options = list(self.wq_parameters[self.wq_parameters['gruppe']==sel_group ]['parameter'])
            elif options_general_groups.index(sel_general_group)>0:
                options = list(self.wq_parameters[self.wq_parameters['allgemeine_parametergruppe']==sel_general_group ]['parameter'])
            else:
                options = list(self.wq_parameters['parameter'])
            sel_parameters = st.multiselect('Parameter', options=options)
            if sel_parameters:
                df = df[df['parameter'].isin(sel_parameters)]
            filter['sel_parameters']=sel_parameters
            filter['exceedances_only'] = st.checkbox('Show exceeding values only')
            options = ['<select stations>'] + self.stations_list
            filter['sel_stations'] = st.multiselect('Station', options=options)
            filter['years'] = st.slider('Years', 1993, 2022, (1993,2022))
        return df, filter

    def show_parameters(self):
        def get_settings():
            ymin, ymax = 0,0
            with st.sidebar.expander("⚙️Settings",expanded=True):
                self.settings['show_time_series']=st.checkbox("Show time series plot", help='Plots show only, if at least one station is selected in the filter section')
                if self.settings['show_time_series']:
                    yax_auto = st.checkbox("Y-Axis  auto scale",value=True)
                    if not yax_auto:
                        ymin = st.number_input("y-axis min", min_value = -999999.000, max_value= 9999999.000, value = 0.000)
                        ymax = st.number_input("y-axis max", min_value = -999999.000, max_value= 9999999.000, value = 0.000)
                        
                    self.settings['show_guideline'] = st.checkbox('Show guideline value as h-line')
                self.settings['show_map']=st.checkbox("Show map", help='Maps required data to be aggregated if multiple sample over time are available from the same station')
                if self.settings['show_map']:
                    options = ['mean','min','max','std']
                    self.settings['map_aggregation'] = st.selectbox("Aggregation for station values on map", options=options)
                self.settings['y_domain'] = [ymin, ymax]


        def show_values_grid(sel_parameter: dict, filter):
            parameter = sel_parameter.iloc[0]['parameter']
            df = self.wq_data[self.wq_data['parameter']==parameter]
            if filter['sel_stations']: 
                df = df[df['station_id'].isin(filter['sel_stations'])]

            df = df.merge(self.wq_parameters,how='left')
            df = df[cn.wq_parameter_value_grid_fields]
            df = df.sort_values(by = ['station_id', 'date'])
            df[['value_num', 'gl_value']] = df[['value_num', 'gl_value']].astype(float)
            if filter['exceedances_only']:
                df = df[df['value_num'] > df['gl_value']]
            if filter['years'] != (1993,2022):
                df = df[df['date'].dt.year.isin(filter['years'])]
            settings = get_settings()
            st.markdown(f'**{len(df)} observations for selected parameter {parameter}**')
            if len(df)>0 and df.iloc[0]['gl_value']>0:
                st.markdown(f"Guideline value: {df.iloc[0]['gl_value']}")
            settings = {'height':helper.get_auto_grid_height(df,400), 'selection_mode':'single', 'fit_columns_on_grid_load': False}
            helper.show_table(df,cols,settings)
            filename = f"{parameter}.csv"
            st.markdown(helper.get_table_download_link(df, filename), unsafe_allow_html=True)
            if self.settings['show_time_series'] and filter['sel_stations']:
                cfg = {'x': 'date', 'y': 'value_num', 'color': 'station_id', 'tooltip':['station_id', 'date','value'], 
                    'x_title': '', 'y_title':parameter, 'width':1000, 'height':400, 'title': parameter, 'symbol_size':40}
                if 'y_domain' in self.settings:
                    cfg['y_domain'] = self.settings['y_domain']
                if self.settings['show_guideline']:
                    cfg['h_line'] = 'gl_value'
                plots.time_series_line(df, cfg) 
            if self.settings['show_map']:
                df = df[['station_id','value_num']].groupby(['station_id']).agg(self.settings['map_aggregation']).reset_index()
                df = pd.merge(df, self.well_records, how='left', left_on=['station_id'], right_on=['laufnummer'])
                settings = {'lat':'lat','long':'long','value_col':'value_num', 'station_col':'station_id', 'min_val':0,'max_val':10,'station_id':'station_id',
                    'size':50, 'tooltip_html' : f"""<b>Station:</b> {{}}<br/><b>{parameter}:</b> {{}}<br/>"""}
                plots.plot_colormap(df, settings)


        df = self.wq_parameters
        df, filter = self.filter_parameters(df)
        cols={}
        settings = {'height':helper.get_auto_grid_height(df,400), 'selection_mode':'single', 'fit_columns_on_grid_load': False}
        st.markdown(f"**{len(df)} parameters found**")
        sel_parameter = helper.show_table(df,cols,settings)
        if len(sel_parameter)>0:
            show_values_grid(sel_parameter, filter)
        
    def show_stations(self):
        def filter_stations(df):
            with st.sidebar.expander("🔎Filter",expanded=True):
                options = ['<select geology>'] + self.geology
                sel_geology = st.selectbox('Geology', options=options)
                sel_stations = st.multiselect('Stations',options=self.stations_list)
                
                if options.index(sel_geology)>0:
                    df = df[df['geology']==sel_geology]
                if sel_stations:
                    sel_stations=[str(x) for x in sel_stations]
                    df = df[df['laufnummer'].isin(sel_stations)]
            return df


        def show_sample_detail(sel_sample:dict):
            sampleno = sel_sample.iloc[0]['sampleno']
            sample_date = datetime.strptime(sel_sample.iloc[0]['date'], '%Y-%m-%dT%H:%M:%S')
            df = self.wq_data[self.wq_data['sampleno']==int(sampleno)]
            df = df[cn.wq_value_grid_fields]
            df = df.merge(self.wq_parameters[cn.wq_parameters_value_grid_fields], on='parameter', how='left')
            st.markdown(f'**Observations for selected sample {sampleno} (station={station_id}, sampling date={sample_date.strftime(cn.DMY_FORMAT)})**')
            settings = {'height':helper.get_auto_grid_height(df,400), 'selection_mode':'single', 'fit_columns_on_grid_load': False}
            helper.show_table(df,cols,settings)

        def show_samples_grid(station_id):
            df = self.samples[self.samples['station_id']==int(station_id)]
            settings['height'] = helper.get_auto_grid_height(df,400)
            st.markdown(f"**{len(df)} samples**")
            sel_sample = helper.show_table(df, cols, settings)
            if len(sel_sample)>0:
                #todo include sample no in 
                show_sample_detail(sel_sample)

        df = self.well_records[cn.station_grid_fields]
        df = filter_stations(df)
        cols={}
        
        settings = {'height':helper.get_auto_grid_height(df,400), 'selection_mode':'single', 'fit_columns_on_grid_load': False}
        st.markdown(f"**{len(df)} stations found**")
        sel_station = helper.show_table(df,cols,settings)
        if len(sel_station)>0:
            station_id = sel_station.iloc[0]['laufnummer']
            show_samples_grid(station_id)
    

    def show_stats(self):
        options_groupplots = ['No plot groups','station','parameter']
        options_agg_functions = ['min','max','mean','std']
        title_dict={
            'min': "minimum values",
            'max': "maximum values",
            'mean': "average values",
            'std': "standard deviation"}
        options_temporal_agg=['year','month','month_date']
        def get_settings():
            with st.sidebar.expander("⚙️Settings",expanded=True):
                self.settings['temporal_aggregation']=st.selectbox('Temporal aggregation', options=options_temporal_agg)
                self.settings['aggregation_func']=st.selectbox('Aggregation function', options=options_agg_functions)                
                self.settings['group_plot'] = st.selectbox('Group plots by', options=options_groupplots)
        
        
        df = self.wq_data.merge(self.wq_parameters[cn.wq_parameters_value_grid_fields], on='parameter', how='left')
        df, filter = self.filter_parameters(df)
        get_settings()
        if options_groupplots.index(self.settings['group_plot'])==0:
            parameter=filter['sel_parameters'][0]
            df = df[df['parameter']==parameter]
            df_plot = df[[self.settings['temporal_aggregation'],'value_num']].groupby([self.settings['temporal_aggregation']]).agg([self.settings['aggregation_func']]).reset_index()
            df_plot.columns = [self.settings['temporal_aggregation'], parameter]
            settings = {'x':self.settings['temporal_aggregation'], 'y':parameter,'title':parameter, 'width':800,'height':400}
            plots.bar_chart(df_plot, settings)
        elif options_groupplots.index(self.settings['group_plot'])==1:
            if (len(filter['sel_stations']) == 0) or (len(filter['sel_stations']) > 50):
                st.warning('Pleas select less than 50 stations')
            else:
                parameter=filter['sel_parameters'][0]
                df = df[df['parameter']==parameter]
                for station in filter['sel_stations']:
                    df_plot = df[df['station_id']==station]
                    df_plot = df_plot[[self.settings['temporal_aggregation'],'value_num']].groupby([self.settings['temporal_aggregation']]).agg([self.settings['aggregation_func']]).reset_index()
                    df_plot.columns = [self.settings['temporal_aggregation'], parameter]
                    settings = {'x':self.settings['temporal_aggregation'], 'y':parameter,'title':f"Station:{station}, {title_dict[self.settings['aggregation_func']]}", 'width':800,'height':400}
                    plots.bar_chart(df_plot, settings)
        elif options_groupplots.index(self.settings['group_plot'])==2:
            if (len(filter['sel_parameters']) == 0) or (len(filter['sel_parameters']) > 50):
                st.warning('Pleas select less than 50 parameters')
            else:
                for parameter in filter['sel_parameters']:
                    df_plot = df[df['parameter']==parameter]
                    df_plot = df_plot[[self.settings['temporal_aggregation'],'value_num']].groupby([self.settings['temporal_aggregation']]).agg([self.settings['aggregation_func']]).reset_index()
                    df_plot.columns = [self.settings['temporal_aggregation'], parameter]
                    settings = {'x':self.settings['temporal_aggregation'], 'y':parameter,'title':parameter, 'width':800,'height':400}
                    plots.bar_chart(df_plot, settings)


    def show_menu(self):
        menu_options = ['Info', 'Station/Samples', 'Parameters'] #, 'Statistics'
        menu_sel = st.sidebar.selectbox('Show',options=menu_options)
        if menu_options.index(menu_sel)==0:
            self.show_info()
        if menu_options.index(menu_sel)==1:
            self.show_stations()
        if menu_options.index(menu_sel)==2:
            self.show_parameters()
        if menu_options.index(menu_sel)==3:
            self.show_stats()