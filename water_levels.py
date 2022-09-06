import streamlit  as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import date, timedelta
# from scipy import stats

from water_levels_texts import texts
import helper
import plots
import pymannkendall as mk

import const as cn
import gw_data


MIN_OBSERVATIONS_FOR_MK = 10
FIGURE = 'fig'
TABLE = 'tab'
CURRENT_YEAR = int(date.today().strftime("%Y"))
time_intervals = ['day','month','year']

class Analysis():
    def __init__(self):
        self.wl_data = self.get_water_level_data()
        self.monitoring_stations = list(self.wl_data['stationid'].unique())
        self.well_records = gw_data.get_well_records(self.monitoring_stations)
        self.precip = self.get_precip_data()
        self.rhein_pegel = self.get_rheinpegel_data()
        self.settings = {}


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
        df['month'] = df['date'].dt.month
        df['day'] = 15
        df['month_date'] = pd.to_datetime(df[['year','month','day']])
        cols=["year","month", "day"]
        df['year_date'] = pd.to_datetime(df[cols].apply(lambda x: f"{x.year}-07-15", axis="columns"))
        return df
    
    @st.cache
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
            aggregate_by = st.selectbox('Aggregate data by', options=time_intervals)
        
        if len(selected)>0:
            selected = selected.iloc[0]
            station_sel = selected['laufnummer']
            df = self.wl_data[(self.wl_data['stationid']==station_sel)]
            df = df[(df['year'].isin(range(start_year, end_year+1)))]
            # define how many days of missing data defines missing data and will interrupt the connection of data points
            max_x_distance = 50
            if time_intervals.index(aggregate_by)==1:
                df = df.groupby(['stationid','month_date']).agg('value').mean().reset_index()
                df.columns=['stationid','date','value']
                max_x_distance = 100
            elif time_intervals.index(aggregate_by)==2:
                df = df.groupby(['stationid','year_date']).agg('value').mean().reset_index()
                df.columns=['stationid','date','value']
                max_x_distance = 400

            if len(df)>0:
                settings={'title': f"{selected['street']} {selected['house_number']} ({station_sel})", 'x':'date', 'y':'value', 'tooltip':['date', 'value'], 
                    'width':1000, 'height': 300, 'x_title':'', 'y_title': 'WL elevation (masl)'}
                min_y = int(df['value'].min())-1
                max_y = int(df['value'].max())+1
                settings['y_domain'] = [min_y, max_y]
                settings['x_domain'] = list(pd.to_datetime([date(start_year,1,1), date(end_year,12,31)]).astype(int) / 10 ** 6)
                settings['max_x_distance'] = max_x_distance 
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


    def show_stats(self):
        def get_settings():
            with st.sidebar.expander("⚙️Settings",expanded=True):
                self.settings['show_table']=st.checkbox('Show stat. results table', value=True)
                self.settings['show_linechart']=st.checkbox('Show linechart', value=True)
                self.settings['temporal_aggregation'] = 'year'
                self.settings['aggregation_func'] = 'mean'

        def get_line_chart_settings(df, station):
            plot_cfg = {'x':'year', 'y':'mean_wl','title': f'Mean waterlevel for station {station}', 'width':800,'height':400, 'y_title':'mean waterlevel (masl)'}
            plot_cfg['max_x_distance'] = 1
            plot_cfg['x_dt']='O'
            df['ci_95']= df['mean_wl'] + 1.65 * df['std_wl']
            df['ci_05']= df['mean_wl'] - 1.65 * df['std_wl']
            plot_cfg['x_domain'] = (df[self.settings['temporal_aggregation']].min(), df[self.settings['temporal_aggregation']].max())
            plot_cfg['y_domain'] = (df['ci_05'].min()-0.4, df['ci_95'].max()+0.4)
            plot_cfg['tooltip']= [self.settings['temporal_aggregation'],'mean_wl' ]
            return plot_cfg

        options = ['<select stations>'] + self.monitoring_stations
        sel_stations = st.sidebar.multiselect('Station', options=options,help='If no station is selected, all stations will be analysed')
        if not sel_stations:
            sel_stations = list(self.monitoring_stations)
        options_groupplots = ['No plot groups','station']
        options_agg_functions = ['min','max','mean','std','count']
        title_dict={
            'min': "minimum values",
            'max': "maximum values",
            'mean': "average values",
            'std': "standard deviation"}
        
        df = self.wl_data[self.wl_data['stationid'].isin(sel_stations)]
        get_settings()
        df = df[[self.settings['temporal_aggregation'],'stationid','value']].groupby(['stationid',self.settings['temporal_aggregation']]).agg(options_agg_functions).reset_index()
        df.columns=['stationid', 'year', 'min_wl', 'max_wl', 'mean_wl', 'std_wl', 'count']
        df[['min_wl', 'max_wl', 'mean_wl', 'std_wl']] = df[['min_wl', 'max_wl', 'mean_wl', 'std_wl']].round(2)
        table_cfg = {'height':250, 'selection_mode':'single', 'fit_columns_on_grid_load':False}
        for station in df['stationid'].unique():
            df_table = df[df['stationid'] == station]
            if self.settings['show_table']:
                st.markdown(f"#### Station {station}")
                helper.show_table(df_table, [], table_cfg)
            if self.settings['show_linechart']:
                plot_cfg = get_line_chart_settings(df_table, station)
                plots.confidence_band(df_table, plot_cfg)
                st.write(f"Yearly average for waterlevels of station {station}, shaded area showes the 90% confidence interval")
        

    def show_trend_analysis(self):
        def get_settings():
            with st.sidebar.expander("⚙️Settings",expanded=True):
                self.settings['show_table']=st.checkbox('Show stat. results table', value=True)
                self.settings['show_linechart']=st.checkbox('Show linechart', value=False)

        def get_filter():
            with st.sidebar.expander("🔎 Filter", expanded=True):
                options = ['<select stations>'] + self.monitoring_stations
                self.settings['sel_stations'] = st.multiselect('Station', options=options,help='If no station is selected, all stations will be analysed')
                if not self.settings['sel_stations']:
                    self.settings['sel_stations'] = list(self.monitoring_stations)
                options = ['Show all', 'Increasing', 'Decreasing', 'Trend present', 'No trend']
                show_trend = st.selectbox('Trend direction', options)
                self.settings['show_trend'] = int(options.index(show_trend))

        def get_linechart_settings(df, result,station):
            cfg = {'title':f"Station {station}, trend: {result.trend}, p={result.p:.4f}",'x':'month_date', 'y': 'value', 'x_title':'','y_title':'wl (masl)', 'tooltip':['stationid','month_date', 
                'value'], 'width':1000, 'height':400}
            cfg['y_domain']= [df['value'].min()-0.5, df['value'].max()+0.5] 
            cfg['x_domain']= [df['month_date'].min(), df['month_date'].max()] 
            cfg['max_x_distance']=90
            return cfg
            
        with st.expander('Info'):
            st.markdown(texts['trend_intro'])
        get_filter()
        get_settings()
        df = self.wl_data.copy()
        df['month'] = df['date'].dt.month
        df['day'] = 15
        df['month_date'] = pd.to_datetime(df[['year','month','day']])
        df = df = df[['year','month','month_date','stationid','value']].groupby(['year','month','month_date','stationid']).agg('mean').reset_index()
        result_df = pd.DataFrame()
        for station in self.settings['sel_stations']:
            df_filtered = df[df['stationid'] == station]
            values = list(df_filtered['value'])
            result = mk.original_test(values)
            row = pd.DataFrame({'station':[station], 'trend':[result.trend], 'p':[result.p], 'z':[result.z], 'Tau':[result.Tau], 's':[result.s], 'var_s':[result.var_s], 'slope':[result.slope], 'intercept':[result.intercept]})
            criteria_met = (self.settings['show_trend'] == 0) or (self.settings['show_trend'] == 1 and result.trend=='increasing') or (self.settings['show_trend'] == 2 and result.trend=='decreasing') or (self.settings['show_trend'] == 3 and result.h == True)  or (self.settings['show_trend'] == 4 and result.h == False)
            if criteria_met:
                result_df = result_df.append(row, ignore_index = True)
                if self.settings['show_linechart']:
                    cfg = get_linechart_settings(df_filtered, result, station)
                    plots.time_series_chart(df_filtered, cfg)

        if self.settings['show_table']:
            st.markdown('### Summary Table')
            st.markdown(f"{len(result_df)} records found." + texts['trend_table_addition'] if not self.settings['show_linechart'] else '')

            settings = {'height':400, 'selection_mode':'single', 'fit_columns_on_grid_load':False}
            sel_row = helper.show_table(result_df, [], settings)
            
            if (len(sel_row)>0) and (self.settings['show_linechart']==False):
                station = sel_row.iloc[0]['station']
                df_filtered = df[df['stationid'] == station]
                values = list(df_filtered['value'])
                result = mk.original_test(values)
                cfg = get_linechart_settings(df_filtered, result, station)
                plots.time_series_chart(df_filtered, cfg)
           

    def show_menu(self):
        menu_options = ['Info', 'Water level plots', 'Statistics', 'Trend analysis']
        menu_sel = st.sidebar.selectbox('Show', options=menu_options)
        if menu_options.index(menu_sel)==0:
            self.show_info()
        if menu_options.index(menu_sel)==1:
            self.show_waterlevel_plot()
        if menu_options.index(menu_sel)==2:
            self.show_stats()
        if menu_options.index(menu_sel)==3:
            self.show_trend_analysis()