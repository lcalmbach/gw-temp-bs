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

MIN_OBSERVATIONS_FOR_MK = 10
FIGURE = 'fig'
TABLE = 'tab'

class Analysis():
    def __init__(self, data):
        self.data = data
        self.data['year'] = self.data['sampling_date'].dt.year
        self.stations = data['station'].unique()
    
    def get_line_df(self, slope, intercept, min_x, max_x):
        df = pd.DataFrame({"x":min_x, "y": slope * min_x + intercept})
        pd.concat(df, {"x":min_x, "y": slope * min_x + intercept}, ignore_index=True)
        return df

    def time_series_chart(self, df, settings):
        #line = alt.Chart(df_line).mark_line(color= 'red').encode(
        #    x= 'x',
        #    y= 'y'
        #    )
        
        chart = alt.Chart(df).mark_line(width = 20, point=alt.OverlayMarkDef(color='blue')).encode(
            x= alt.X('sampling_date:T', scale=alt.Scale(domain=settings['x_domain'])),
            y= alt.Y('temperature:Q', scale=alt.Scale(domain=settings['y_domain'])),
            tooltip=['sampling_date', 'temperature']    
        )
        line = chart.transform_regression('sampling_date', 'temperature').mark_line()
        return (chart + line).properties(width=800, height = 400, title = settings['title'])
    
    def select_stations(self):
        stations = st.sidebar.multiselect('Select stations', options = self.stations, help='For no selection, all stations are included')
        return stations

    def show_mann_kendall(self):
        """
        https://github.com/mmhs013/pymannkendall
        Hussain et al., (2019). pyMannKendall: a python package for non parametric Mann Kendall family of trend tests.. Journal of Open Source Software, 4(39), 1556, https://doi.org/10.21105/joss.01556
        """

        def get_summary_df():
            keys = ['date range',
                'Sampling depth (m)',
                'Min temperature (°C)', 
                'Max temperature (°C)', 
                'Avg temperature (°C)',
                'Std temperature (°C)',
                'MK Trend',
                'MK p',
                'Sen slope'
            ]
            values = [f"{df['sampling_date'].min().year} to {df['sampling_date'].max().year}",
                f"{df['sampling_depth'].min():.2f}",
                f"{df['temperature'].min():.2f}",
                f"{df['temperature'].max():.2f}",
                f"{df['temperature'].mean():.2f}",
                f"{df['temperature'].std():.2f}",
                result.trend,
                f"{result.p:.2E}",
                f"{result.slope:.4f}"
            ]
            return pd.DataFrame({'Parameter': keys, 'Value':values})

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
        minimum_number_of_obs = st.sidebar.number_input('Min number of observations', min_value=0, max_value = 20, value = 5)
        display = st.sidebar.selectbox("Display", options = DISPLAY_OPTIONS)
        settings = {}
        
        if st.sidebar.button("Run MK-test"):
            if len(stations)== 0:
                stations = self.stations
            #df_result = pd.DataFrame(columns=['trend','h','p','z','Tau','s','var_s','slope','intercept'])
            num_stations=st.empty()
            st.markdown(f'Minimum number of temperature observations: {minimum_number_of_obs}')
            settings['x_domain'] = [ f"{self.data['sampling_date'].min().year}-01-01", f"{self.data['sampling_date'].max().year}-12-31"]
            min_y = int(self.data['temperature'].min())-1
            max_y = int(self.data['temperature'].max())+1
            settings['y_domain'] = [min_y, max_y]
            cnt_stations = 0
            cnt_all_stations = 0
            for station in stations:
                df = self.data[self.data['station'] == station].sort_values(by='sampling_date')
                if len(df) >= minimum_number_of_obs:
                    cnt_all_stations += 1
                    temperatures = list(df['temperature'])
                    result = mk.original_test(temperatures)
                    settings['title'] = f"{station}: {result.trend}"
                    if show_result(result):
                        cnt_stations+=1
                        plot = self.time_series_chart(df, settings)
                        st.altair_chart(plot)
                        summary_df = get_summary_df()
                        cols = st.columns([4,5])
                        with cols[0]:
                            AgGrid(summary_df, key = station, height=len(summary_df)*30 + 35)
            num_stations.markdown(f"{cnt_stations} of {cnt_all_stations} stations shown")
            #st.write(df_result)

    def get_heat_map_data(self, stations):
        df = self.data
        if stations != []:
            df = df[df['station'].isin(stations)]
        df = df[['station','year', 'temperature', 'sampling_depth']].groupby(['station','year']).agg(['mean', 'count']).reset_index()
        df.columns = ['station','year','temperature','observations', 'sampling_depth', 'cnt']
        df = df.sort_values(by='sampling_depth', ascending=False)
        return df


    def show_location_map(self, station_data):
        def get_tooltip_html():
            text = """
            <b>Station:</b> {}<br/>           
            <b>Depth(m):</b> {}<br/>
            <b>Mean temperature:</b> {}<br/>"""
            return text

        midpoint = (np.average(station_data['latitude']), np.average(station_data['longitude']))
        settings = {'midpoint': midpoint, 'layer_type': 'IconLayer', 'tooltip_html': get_tooltip_html()}
        plots.plot_map(station_data, settings)
    
    def show_trend_distribution_map(self, df):
        def get_tooltip_html():
            text = """
            <b>Station:</b> {}<br/>           
            <b>Depth(m):</b> {}<br/>
            <b>Mean temperature:</b> {}<br/>"""
            return text

        midpoint = (np.average(df['latitude']), np.average(df['longitude']))
        settings = {'midpoint': midpoint, 'layer_type': 'IconLayer', 'tooltip_html': get_tooltip_html(), 'cat_field':'trend_result'}
        categories = {
            'increasing': {'color': 'orange', 'icon': 'arrow-up'}, 
            'decreasing': {'color': 'blue', 'icon': 'arrow-down'}, 
            'no trend': {'color': 'lightgray', 'icon': 'arrow-right'}
        }
        plots.plot_map(df, settings, categories)
        

    def get_regression_table(self, stations):
        result = {}
        future_date = date(date.today().year + 10, date.today().month, date.today().day)
        for station in stations:
            df = self.data[self.data['station']==station].sort_values(by='sampling_date')
            min_date = df['sampling_date'].min()
            min_date = date(min_date.year, min_date.month, min_date.day)
            x = list( (df['sampling_date'] - df['sampling_date'].min())  / np.timedelta64(1,'D'))
            y = list(df['temperature'])
            linreg = stats.linregress(x, y)
            days_to_future_date = (future_date - min_date).days
            extrapol_temperature = linreg.intercept + days_to_future_date * linreg.slope
            row = pd.DataFrame({'station': station, 'start_date': min_date, 'r-value': linreg.rvalue, 'intercept':linreg.intercept, 'slope (°C/yr)':linreg.slope*365, '10yr prediction': extrapol_temperature }, index=[0])
            if len(result)==0:
                result = row
            else:
                result = pd.concat([result, row], ignore_index=True)
        return result

    def get_station_data(self):
        df = self.data
        df = df[['station', 'temperature', 'sampling_depth', 'latitude', 'longitude']].groupby(['station', 'latitude', 'longitude']).agg(['min', 'max', 'mean', 'count']).reset_index()
        df.columns=['station', 'latitude','longitude', 'temp_min', 'temp_max', 'temp_mean', 'temp_count', 'depth_min', 'depth_max', 'depth', 'depth_count']
        df = df[['station', 'latitude','longitude', 'depth', 'temp_min', 'temp_max', 'temp_mean', 'temp_count']]
        df["latitude"] = df["latitude"].astype("float")
        df["longitude"] = df["longitude"].astype("float")
        return df

    def get_surface_temp_data(self):
        df = pd.read_csv(cn.datasource['surface_temp_year'], sep = '\t')
        df = df[df['year']>1992]
        df.sort_values(by='year')
        return df

    def report(self):
        """
        This function generates the temperature report with all texts, tables and figures
        """

        def get_result_table(station_data):
            result = pd.DataFrame()
            valid_stations = list(station_data[station_data['temp_count'] >= MIN_OBSERVATIONS_FOR_MK]['station'])
            df = station_data[station_data['station'].isin(valid_stations)]
            for index, row in df.iterrows():
                df_station = self.data[self.data['station'] == row['station']].sort_values(by='sampling_date')
                temperatures = list(df_station['temperature'])
                mk_result = mk.original_test(temperatures)
                result_row = pd.DataFrame({'station':row['station'], 'trend_result': mk_result.trend, "p-value": mk_result.p, 'no_of_points': row['temp_count']}, index=[0])
                if len(result)==0:
                    result = result_row
                else:
                    result = pd.concat([result, result_row], ignore_index=True)
            return result

        def show_table1(df, all_data):
            cols = st.columns(2)
            tab_cols = [{'name':'p-value', 'hide':False, 'type':["numericColumn","numberColumnFilter","customNumericFormat"], 'precision':4}]
            with cols[0]:
                settings = {'height':500, 'selection_mode':'single', 'fit_columns_on_grid_load': False}
                selected = helper.show_table(df, tab_cols, settings)
            with cols[1]:
                if len(selected)>0:
                    station = selected.iloc[0]['station']
                    df = all_data[all_data['station'] == station].sort_values(by='sampling_date')
                    settings={'width':500, 'height':200}
                    settings['title'] = f"{station}: {selected.iloc[0]['trend_result']}"
                    settings['x_domain'] = [ f"{self.data['sampling_date'].min().year}-01-01", f"{self.data['sampling_date'].max().year}-12-31"]
                    min_y = int(self.data['temperature'].min())-1
                    max_y = int(self.data['temperature'].max())+1
                    settings['y_domain'] = [min_y, max_y]
                    plots.time_series_chart(df, settings, regression=True)
                    df = df[['sampling_date', 'temperature']]
                    settings = {'height':250, 'selection_mode':'single', 'fit_columns_on_grid_load': False}
                    selected = helper.show_table(df, [], settings)
        
        def get_trends(df):
            trends = {}
            trends['num'] = len(df)
            trends['increasing'] = len(df[df['trend_result']=='increasing'])
            trends['decreasing'] = len(df[df['trend_result']=='decreasing'])
            trends['no_trend'] = trends['num'] - trends['increasing'] - trends['decreasing']
            return trends

        def show_surface_temp_chart(df):
            settings = {"x": 'year:Q', "y": "temperature (°C):Q","width":800,"height":200}
            settings['x_domain'] = [1993, int(df['year'].max())] 
            settings['y_domain'] = [7,14] 
            settings['tooltip'] = ["year", "temperature (°C)"]
            plots.line_chart(df, settings, True)
        
        def get_compare_temperatures_data(df_gw, df_sw):
            df_gw = df_gw[['year', 'temperature']].groupby(['year']).agg(['mean']).reset_index()
            df_merge = pd.merge(df_gw, df_sw, left_on='year', right_on='year') 
            df_merge.columns = ['year','dummy','groundwater (°C)', 'surface (°C)']
            df_merge = df_merge [['year','groundwater (°C)', 'surface (°C)']]
            return df_merge

        fig_num = 1
        tab_num = 1

        # intro
        station_data = self.get_station_data()
        st.markdown(texts['intro'], unsafe_allow_html=True)
        self.show_location_map(station_data)
        fig_num = helper.show_legend(texts, FIGURE, fig_num) 
        
        # methodology
        st.markdown(texts['eval'], unsafe_allow_html=True)
        
        # results
        result_table = get_result_table(station_data)
        trends = get_trends(result_table)
        st.markdown(texts['result'].format(
            trends['num'], 
            trends['increasing'], 
            trends['no_trend'], 
            trends['decreasing']), unsafe_allow_html=True)
        show_table1(result_table, self.data)
        args = [MIN_OBSERVATIONS_FOR_MK]
        tab_num = helper.show_legend(texts,TABLE,tab_num, args)
        
        # show a map showing the spatial distribution
        st.markdown(texts['result_map'], unsafe_allow_html=True)
        df = pd.merge(station_data, result_table, left_on='station', right_on='station') 
        self.show_trend_distribution_map(df)
        fig_num = helper.show_legend(texts, FIGURE, fig_num)

        #surface temperature
        df = self.get_surface_temp_data()
        surface_linreg = stats.linregress(list(df['year']), list(df['temperature (°C)']))
        st.markdown(texts['surface_temperature'].format(surface_linreg.slope), unsafe_allow_html=True)
        show_surface_temp_chart(df)
        fig_num = helper.show_legend(texts, FIGURE, fig_num)
        compare_data = get_compare_temperatures_data(self.data, df)
        settings = {'x': 'groundwater (°C):Q','y':'surface (°C):Q', 
            'domain': [9,18],
            'color': 'year:Q',
            'tooltip':['year','groundwater (°C)','surface (°C)'], 'width': 400, 'height':400}
        
        st.markdown(texts['surface_temperature_compare_to_groundwater'].format(surface_linreg.slope), unsafe_allow_html=True)
        plots.scatter_plot(compare_data, settings)
        fig_num = helper.show_legend(texts, FIGURE, fig_num)
        
        #heatmap
        st.markdown(texts['result_heatmap'], unsafe_allow_html=True)
        df = self.get_heat_map_data([])
        settings = {'x': 'year:O','y':alt.Y('station:O',sort=alt.EncodingSortField(field='sampling_temperature', order='ascending')),
            'color':'temperature:Q', 'tooltip':['station','year','sampling_depth','temperature','observations']}
        settings['title']=f'Heatmap (all stations with at least one temperature observation)'
        plots.heatmap(df, settings)
        fig_num = helper.show_legend(texts,FIGURE,fig_num)
        
        # prediction
        valid_stations = list(station_data[station_data['temp_count'] >= MIN_OBSERVATIONS_FOR_MK]['station'])
        regr_table = self.get_regression_table(valid_stations)
        regr_table_pos = regr_table[regr_table['slope (°C/yr)']>0]
        min_slope = regr_table_pos['slope (°C/yr)'].min()
        max_slope = regr_table_pos['slope (°C/yr)'].max()
        mean_slope = regr_table_pos['slope (°C/yr)'].mean()
        min_predict = regr_table_pos['10yr prediction'].min()
        max_predict = regr_table_pos['10yr prediction'].max()
        mean_predict = regr_table_pos['10yr prediction'].mean()
        st.markdown(texts['prediction'].format(MIN_OBSERVATIONS_FOR_MK,
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
        tab_num = helper.show_legend(texts, TABLE, tab_num, [MIN_OBSERVATIONS_FOR_MK])
        st.markdown(texts['conclusion'].format(min_slope, max_slope,surface_linreg.slope), unsafe_allow_html=True)
        
    def show_menu(self):
        MENU_OPTIONS = ['Report','Mann Kendall Test']
        menu_item = st.sidebar.selectbox('Analysis', options=MENU_OPTIONS)

        if menu_item == MENU_OPTIONS[0]:
            self.report()
        elif menu_item == MENU_OPTIONS[1]:
            self.show_mann_kendall()
