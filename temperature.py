import streamlit  as st
import pymannkendall as mk
import pandas as pd
import altair as alt
import numpy as np
from st_aggrid import AgGrid
from datetime import datetime, date
from scipy import stats
from temperature_texts import texts
import helper
import plots
import const as cn
import gw_data

FIGURE = 'fig'
TABLE = 'tab'

class Analysis():
    def __init__(self):
        self.data = gw_data.get_standard_dataset('gw-temperature')
        self.data = self.data[['stationid','year','month','avg_temp']]
        self.data.columns=['stationid','year','month','temperature']
        self.data['day'] = 15
        self.data['month_date'] = pd.to_datetime(self.data[['year','month','day']])
        self.stations = list(self.data['stationid'].unique())
        self.well_records=gw_data.get_well_records(self.stations)
        self.well_records['laufnummer']=self.well_records['laufnummer'].astype(int)
        self.surface_temperature = gw_data.get_standard_dataset('meteo')
        self.surface_temperature['year'] = self.surface_temperature['timestamp'].dt.year
    
    def get_line_df(self, slope, intercept, min_x, max_x):
        df = pd.DataFrame({"x":min_x, "y": slope * min_x + intercept})
        pd.concat(df, {"x":min_x, "y": slope * min_x + intercept}, ignore_index=True)
        return df


    def select_stations(self):
        stations = st.sidebar.multiselect('Select stations', options = self.stations, help='For no selection, all stations are included')
        return stations

    def show_mann_kendall(self):
        """
        https://github.com/mmhs013/pymannkendall
        Hussain et al., (2019). pyMannKendall: a python package for non parametric Mann Kendall family of trend tests.. Journal of Open Source Software, 4(39), 1556, https://doi.org/10.21105/joss.01556
        """

        def get_summary_df(df, result):
            keys = ['date range',
                'Min temperature (°C)', 
                'Max temperature (°C)', 
                'Avg temperature (°C)',
                'Std temperature (°C)',
                'MK Trend',
                'MK p',
                'Sen slope'
            ]
            values = [f"{df['month_date'].min().year} to {df['month_date'].max().year}",
                f"{df['temperature'].min():.2f}",
                f"{df['temperature'].max():.2f}",
                f"{df['temperature'].mean():.2f}",
                f"{df['temperature'].std():.2f}",
                result.trend,
                f"{result.p:.2E}",
                f"{result.slope:.4f}"
            ]
            df=pd.DataFrame({'Parameter': keys, 'Value':values})
            return df

        def show_result(result):
            ok = (display == DISPLAY_OPTIONS[0]) 
            ok = ok or (display == DISPLAY_OPTIONS[1] and result.trend=='increasing')
            ok = ok or (display == DISPLAY_OPTIONS[2] and result.trend=='decreasing')
            ok = ok or (display == DISPLAY_OPTIONS[3] and result.trend=='no trend')
            return ok

        with st.expander("Info", expanded=True):
            st.markdown(texts['mk-menu'])
        DISPLAY_OPTIONS = ['all results', 'increasing', 'decreasing', 'no trend']
        stations = self.select_stations()
        display = st.sidebar.selectbox("Display", options = DISPLAY_OPTIONS)
        settings = {'x':'month_date', 'y': 'temperature', 'x_title':'','y_title':'mean temperature °C', 'tooltip':['stationid','month_date', 
            'temperature'], 'width':1000, 'height':400}
        
        if st.button("Run MK-test"):
            if len(stations)== 0:
                stations = self.stations
            #df_result = pd.DataFrame(columns=['trend','h','p','z','Tau','s','var_s','slope','intercept'])
            num_stations=st.empty()
            settings['x_domain'] = [ f"{self.data['month_date'].min().year}-01-01", f"{self.data['month_date'].max().year}-12-31"]
            min_y = int(self.data['temperature'].min())-1
            max_y = int(self.data['temperature'].max())+1
            settings['y_domain'] = [min_y, max_y]
            cnt_stations = 0
            cnt_all_stations = 0
            averaged_data = self.get_averaged_data(self.data,['month','year','month_date'])
            for station in stations:
                df = averaged_data[averaged_data['stationid'] == station].sort_values(by='month_date')
                #settings['x_domain'] = [ f"{df['month_date'].min().year}-01-01", f"{df['month_date'].max().year}-12-31"]
                cnt_all_stations += 1
                temperatures = list(df['temperature'])
                result = mk.original_test(temperatures)
                settings['title'] = f"{station}: {result.trend}"
                if show_result(result):
                    cnt_stations+=1
                    plots.time_series_chart(df, settings)

                    summary_df = get_summary_df(df, result)
                    cols = st.columns([4,5])
                    with cols[0]:
                        tab_settings = {'height':280, 'selection_mode':'single', 'fit_columns_on_grid_load': False}
                        cols=[]
                        helper.show_table(summary_df, cols,  tab_settings)
            num_stations.markdown(f"{cnt_stations} of {cnt_all_stations} stations shown")


    def get_heat_map_data(self, stations):
        df = self.data
        if stations != []:
            df = df[df['stationid'].isin(stations)]
        df = df[['stationid','year', 'temperature']].groupby(['stationid','year']).agg(['mean', 'count']).reset_index()
        df.columns = ['stationid','year','temperature','observations']
        return df


    def show_location_map(self, station_data):
        def get_tooltip_html():
            text = """
            <b>Station:</b> {}<br/>           
            <b>Mean temperature:</b> {}<br/>
            <b>Min temperature:</b> {}<br/>
            <b>Max temperature:</b> {}<br/>
            <b>First sample year:</b> {}<br/>
            <b>Last sample year:</b> {}<br/>"""
            return text

        midpoint = (np.average(station_data['lat']), np.average(station_data['long']))
        settings = {'lat':'lat', 'long':'long', 'midpoint': midpoint, 'layer_type': 'IconLayer', 'tooltip_html': get_tooltip_html()}
        settings['tooltip_cols'] = ['stationid','temp_mean','temp_min','temp_max','year_min','year_max']
        plots.plot_map(station_data, settings)
    
    def show_trend_distribution_map(self, df):
        def get_tooltip_html():
            text = """
            <b>Station:</b> {}<br/>           
            <b>Mean temperature:</b> {}<br/>"""
            return text

        midpoint = (np.average(df['lat']), np.average(df['long']))
        settings = {'lat':'lat', 'long':'long','midpoint': midpoint, 'layer_type': 'IconLayer', 'tooltip_html': get_tooltip_html(), 'cat_field':'trend_result'}
        settings['tooltip_cols'] = ['stationid','temp_mean']
        categories = {
            'increasing': {'color': 'orange', 'icon': 'arrow-up'}, 
            'decreasing': {'color': 'blue', 'icon': 'arrow-down'}, 
            'no trend': {'color': 'lightgray', 'icon': 'arrow-right'}
        }
        plots.plot_map(df, settings, categories)
        

    def get_regression_table(self, stations):
        MIN_VALS_4_REGRESSION = 0
        result = {}
        future_date = date(date.today().year + 10, date.today().month, date.today().day)
        for station in stations:
            df = self.data[self.data['stationid']==station].sort_values(by='month_date')
            if len(df) > MIN_VALS_4_REGRESSION:
                min_date = df['month_date'].min()
                min_date = date(min_date.year, min_date.month, min_date.day)
                x = list( (df['month_date'] - df['month_date'].min())  / np.timedelta64(1,'D'))
                y = list(df['temperature'])
                linreg = stats.linregress(x, y)
                days_to_future_date = (future_date - min_date).days
                extrapol_temperature = linreg.intercept + days_to_future_date * linreg.slope
                row = pd.DataFrame({'stationid': station, 'start_date': min_date, 'r-value': linreg.rvalue, 'intercept':linreg.intercept, 'slope (°C/yr)':linreg.slope*365, '10yr prediction': extrapol_temperature }, index=[0])
                if len(result)==0:
                    result = row
                else:
                    result = pd.concat([result, row], ignore_index=True)
        return result

    def get_station_data(self):
        df = self.data
        df = df[['stationid','temperature','year']].groupby(['stationid']).agg({'temperature':['min', 'max', 'mean', 'count'], 'year':['min','max']}).reset_index()
        df.columns=['stationid', 'temp_min', 'temp_max', 'temp_mean', 'temp_count', 'year_min','year_max']
        df2=self.well_records[['laufnummer','lat','long']]
        df = pd.merge(df, df2, how='left', left_on=['stationid'], right_on=['laufnummer'])
        df = df[['stationid', 'lat','long', 'temp_min', 'temp_max', 'temp_mean', 'temp_count', 'year_min', 'year_max']]
        df["lat"] = df["lat"].astype("float")
        df["long"] = df["long"].astype("float")
        df['temp_min']=df['temp_min'].round(2)
        df['temp_max']=df['temp_max'].round(2)
        df['temp_mean']=df['temp_mean'].round(2)
        return df
    

    def get_averaged_data(self, data:pd.DataFrame, groupby)->pd.DataFrame:
        if type(groupby)!=list:
            groupby = [groupby]
        if not 'stationid' in groupby:
            groupby.append('stationid')
        df = data[['temperature'] + groupby].groupby(groupby).mean().reset_index()
        df['temperature'] = df['temperature'].round(2)
        return df


    def report(self):
        """
        This function generates the temperature report with all texts, tables and figures
        """

        def get_surface_temp_data():
            df_st = self.surface_temperature
            df_st = df_st[['year','temp_mean']].groupby('year').agg(['mean','count']).reset_index()
            df_st.columns=['year','mean_surface_temperature','cnt']
            df_st = df_st[df_st['cnt'] > 350]
            return df_st

        def get_result_table(data, stations):
            result = pd.DataFrame()
            for index, row in stations.iterrows():
                df_filtered = data[data['stationid'] == row['stationid']].sort_values(by='month_date')
                if len(df_filtered) > 1:
                    temperatures = list(df_filtered['temperature'])
                    mk_result = mk.original_test(temperatures)
                    result_row = pd.DataFrame({'stationid':row['stationid'], 'trend_result': mk_result.trend, "p-value": mk_result.p, 'no_of_points': row['temp_count']}, index=[0])
                    if len(result)==0:
                        result = result_row
                    else:
                        result = pd.concat([result, result_row], ignore_index=True)
            return result

        def show_table1(result, all_data):
            cols = st.columns(2)
            tab_cols = [{'name':'p-value', 'hide':False, 'type':["numericColumn","numberColumnFilter","customNumericFormat"], 'precision':4}]
            with cols[0]:
                settings = {'height':500, 'selection_mode':'single', 'fit_columns_on_grid_load': False}
                selected = helper.show_table(result, tab_cols, settings)
            with cols[1]:
                if len(selected)>0:
                    station = selected.iloc[0]['stationid']
                    df_filtered = all_data[all_data['stationid'] == station].sort_values(by='month_date')
                    settings={'x': 'month_date', 'y':'temperature','width':500, 'height':200,'x_title':'', 'y_title': 'mean temperature °C'}
                    settings['title'] = f"{station}: {selected.iloc[0]['trend_result']}"
                    settings['x_domain'] = [ f"{df_filtered['month_date'].min().year}-01-01", f"{all_data['month_date'].max().year}-12-31"]
                    min_y = int(all_data['temperature'].min())-1
                    max_y = int(all_data['temperature'].max())+1
                    settings['y_domain'] = [min_y, max_y]
                    settings['tooltip'] = ['month_date:T','temperature:Q']
                    plots.time_series_chart(df_filtered, settings, regression=True)
                    
                    df_filtered = df_filtered[['year', 'month', 'temperature']]
                    settings = {'height':250, 'selection_mode':'single', 'fit_columns_on_grid_load': False}
                    selected = helper.show_table(df_filtered, [], settings)
        
        def get_trends(df):
            trends = {}
            trends['num'] = len(df)
            trends['increasing'] = len(df[df['trend_result']=='increasing'])
            trends['decreasing'] = len(df[df['trend_result']=='decreasing'])
            trends['no_trend'] = trends['num'] - trends['increasing'] - trends['decreasing']
            return trends

        def show_surface_temp_chart(df):
            settings = {"x": 'year', "y": "mean_surface_temperature","width":800,"height":200, 'x_title':'','y_title':'average yearly temperature(°C)'}
            settings['x_domain'] = [int(df['year'].min()), int(df['year'].max())] 
            settings['y_domain'] = [7,14] 
            settings['tooltip'] = ["year", "mean_surface_temperature"]
            settings['regression'] = True
            plots.line_chart(df, settings)
        
        def get_compare_temperatures_data(df_gw:pd.DataFrame, df_st:pd.DataFrame):
            df_gw = df_gw[['year', 'temperature']].groupby(['year']).agg(['mean']).reset_index()
            df_gw.columns = ['year', 'mean_groundwater_temperature']
            df_merge = pd.merge(df_gw, df_st, left_on='year', right_on='year')
            df_merge.columns = ['year','groundwater', 'surface','cnt']
            df_merge = df_merge [['year','groundwater', 'surface']]
            return df_merge

        fig_num = 1
        tab_num = 1

        # prepare the data
        station_data = self.get_station_data()
        #station_data = station_data[station_data['temp_count']> MIN_OBSERVATIONS]
        averaged_data = self.get_averaged_data(self.data,['month','year','month_date'])
        
        # intro
        st.markdown(texts['intro'].format(self.data.year.min(), len(self.stations)), unsafe_allow_html=True)
        self.show_location_map(station_data)
        fig_num = helper.show_legend(texts, FIGURE, fig_num) 
        
        # methodology
        st.markdown(texts['eval'], unsafe_allow_html=True)
        
        # results
        result_table = get_result_table(averaged_data, station_data)
        trends = get_trends(result_table)
        st.markdown(texts['result'].format(
            trends['num'], 
            trends['increasing'], 
            trends['no_trend'], 
            trends['decreasing']), unsafe_allow_html=True)
        show_table1(result_table, averaged_data)
        tab_num = helper.show_legend(texts, TABLE, tab_num)
        
        # show a map showing the spatial distribution
        st.markdown(texts['result_map'], unsafe_allow_html=True)
        df = pd.merge(station_data, result_table, left_on='stationid', right_on='stationid') 
        self.show_trend_distribution_map(df)
        fig_num = helper.show_legend(texts, FIGURE, fig_num)

        #surface temperature
        df = get_surface_temp_data()
        surface_linreg = stats.linregress(list(df['year']), list(df['mean_surface_temperature']))
        st.markdown(texts['surface_temperature'].format(surface_linreg.slope), unsafe_allow_html=True)
        show_surface_temp_chart(df)
        fig_num = helper.show_legend(texts, FIGURE, fig_num)
        compare_data = get_compare_temperatures_data(self.data, df)
       
        settings = {'x': 'groundwater','y':'surface', 
            'domain': [9,18],
            'color': 'year',
            'tooltip':['year','groundwater','surface'], 
            'width': 400, 
            'height':400}
        st.markdown(texts['surface_temperature_compare_to_groundwater'].format(surface_linreg.slope), unsafe_allow_html=True)
        plots.scatter_plot(compare_data, settings)
        fig_num = helper.show_legend(texts, FIGURE, fig_num)
        
        #heatmap
        st.markdown(texts['result_heatmap'], unsafe_allow_html=True)
        df = self.get_heat_map_data([])
        
        settings = {'x': 'year:O','y':alt.Y('stationid:O'),
            'color':'temperature:Q', 'tooltip':['stationid','year','temperature','observations']}
        settings['title']=f'Heatmap (all stations with at least one temperature observation)'
        plots.heatmap(df, settings)
        fig_num = helper.show_legend(texts,FIGURE,fig_num)
        
        # prediction
        regr_table = self.get_regression_table(list(station_data['stationid']))
        regr_table_pos = regr_table[regr_table['slope (°C/yr)'] > 0]
        min_slope = regr_table_pos['slope (°C/yr)'].min()
        max_slope = regr_table_pos['slope (°C/yr)'].max()
        mean_slope = regr_table_pos['slope (°C/yr)'].mean()
        min_predict = regr_table_pos['10yr prediction'].min()
        max_predict = regr_table_pos['10yr prediction'].max()
        mean_predict = regr_table_pos['10yr prediction'].mean()
        st.markdown(texts['prediction'].format(
            min_slope,
            max_slope,
            mean_slope,
            min_predict,
            max_predict,
            mean_predict), unsafe_allow_html=True)
        
        settings = {'height':500, 'selection_mode':'single', 'fit_columns_on_grid_load': False}
        tab_cols = [{'name':'r-value', 'hide':False, 'type':["numericColumn","numberColumnFilter","customNumericFormat"], 'precision':2}]
        tab_cols.append({'name':'intercept', 'hide':False, 'type':["numericColumn","numberColumnFilter","customNumericFormat"], 'precision':2})
        tab_cols.append({'name':'slope (°C/yr)', 'hide':False, 'type':["numericColumn","numberColumnFilter","customNumericFormat"], 'precision':3})
        tab_cols.append({'name':'10yr prediction', 'hide':False, 'type':["numericColumn","numberColumnFilter","customNumericFormat"], 'precision':2})
        selected = helper.show_table(regr_table, tab_cols, settings)
        tab_num = helper.show_legend(texts, TABLE, tab_num)
        st.markdown(texts['conclusion'].format(min_slope, max_slope,surface_linreg.slope), unsafe_allow_html=True)
        
    def show_menu(self):
        MENU_OPTIONS = ['Report','Mann Kendall Test']
        menu_item = st.sidebar.selectbox('Analysis', options=MENU_OPTIONS)

        if menu_item == MENU_OPTIONS[0]:
            self.report()
        elif menu_item == MENU_OPTIONS[1]:
            self.show_mann_kendall()
