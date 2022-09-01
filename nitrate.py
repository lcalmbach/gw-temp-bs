import streamlit  as st
import pymannkendall as mk
import pandas as pd
import altair as alt
import numpy as np
from datetime import datetime, date
from scipy import stats
from nitrate_texts import texts
import helper
import plots
import const as cn
import gw_data

FIGURE = 'fig'
TABLE = 'tab'
GUIDELINE_NO3_N = 5.6

class Analysis():
    def __init__(self):
        self.data = gw_data.get_standard_dataset('water-quality-values')
        self.data.loc[self.data['parameter']=='Nitrat', 'wert_num'] = self.data['wert_num'] / 4.427
        self.data.loc[self.data['parameter']=='Nitrat', 'parameter'] = 'Nitrat(N)'
        self.data = self.data[self.data['parameter']=='Nitrat(N)']
        self.data['year'] = self.data['probenahmedatum_date'].dt.year
        self.stations = list(self.data['station_id'].unique())
        self.well_records = gw_data.get_well_records(self.stations)
        self.well_records['laufnummer'] = self.well_records['laufnummer'].astype(int)
        self.well_records = self.well_records[self.well_records['laufnummer'].isin(self.data.station_id.unique())]
        self.first_year = self.data['year'].min()
        self.years_of_data = datetime.now().year - self.first_year


    def get_line_df(self, slope, intercept, min_x, max_x):
        df = pd.DataFrame({"x":min_x, "y": slope * min_x + intercept})
        pd.concat(df, {"x":min_x, "y": slope * min_x + intercept}, ignore_index=True)
        return df


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
            <b>Maximum Nitrate :</b> {} mg/L<br/>    
            <b>Average Nitrate :</b> {} mg/L<br/>    
            <b>Number of samples :</b> {}<br/>    
            <b>First year:</b> {}<br/>    
            <b>Last year:</b> {}<br/>    
           """
            return text
        agg_dict = {'wert_num':['mean','max', 'count'], 'year':['min','max']}
        df = self.data[['station_id', 'lat','long', 'wert_num', 'year']].groupby(['station_id', 'lat', 'long']).agg(agg_dict).reset_index()

        df.columns=['station_id','lat','long','mean_nitrate','max_nitrate','nbr_observations','first_year','last_year']
        df[['mean_nitrate','max_nitrate']] = df[['mean_nitrate','max_nitrate']].round(1)
        df[['first_year','last_year']] = df[['first_year','last_year']].astype(str)
        settings = {'lat':'lat', 'long':'long', 'layer_type': 'IconLayer', 'station_col':'station_id','tooltip_html': get_tooltip_html()}
        settings['tooltip_cols'] = ['station_id','max_nitrate','mean_nitrate','nbr_observations','first_year','last_year']
        plots.plot_map(df, settings)
    

    def show_spatial_distribution(self, df):
        def get_tooltip_html():
            text = """
                <b>Station:</b> {}<br/>           
                <b>Max concentration in year:</b> {} mg/L<br/>           
            """
            return text

        df.columns = ['station_id','lat','long','max_nitrate']
        settings = {'lat':'lat', 'long': 'long', 'value_col': 'max_nitrate', 'width':400,'height':400, 'tooltip_html': get_tooltip_html(),
            'tooltip_cols':['station_id', 'max_nitrate'], 'station_col':'station_id'}
        settings['colors'] = ['green','red']
        settings['limits'] = [0, 5.59, 50]
        plots.plot_colormap(df, settings)
    

    def show_temporal_distribution(self):
        stations = st.multiselect('Add or remove stations:', options=self.stations, default=[1026, 1061, 1068, 1305, 1316])
        df = self.data[self.data['station_id'].isin(stations)]
        df['guideline'] = GUIDELINE_NO3_N
        settings = {'x':'probenahmedatum_date', 'y': 'wert_num', 'width':800,'height':400, 'color':'station_id', 'x_title':'', 
            'symbol_size': 40, 'y_title':'Concentration (mg/L)', 'y_domain': [0, 20], 'h_line': 'guideline',
            'tooltip': ['station_id','probenahmedatum_date','wert_num'], 'title':''}
        plots.time_series_line(df, settings)

    def show_yearly_stat_table(self):
        _df = self.data
        _df['is_exceedance'] = 0
        _df.loc[ (_df['wert_num'] >= GUIDELINE_NO3_N), 'is_exceedance'] = 1

        agg_dict = {'wert_num':['mean','max', 'count'], 'is_exceedance':['sum']}
        _df = _df[['year', 'wert_num', 'is_exceedance']].groupby(['year']).agg(agg_dict).reset_index()
        _df.columns=['year','mean_nitrate','max_nitrate','observations','nbr > guideline']
        _df['pct > guideline'] = (_df['nbr > guideline'] / _df['observations'] * 100).round(1)        
        _df[['mean_nitrate','max_nitrate']] = _df[['mean_nitrate','max_nitrate']].round(1)
        return _df
    
    def show_well_stat_table(self):
        _df = self.data
        _df['is_exceedance'] = 0
        _df.loc[ (_df['wert_num'] >= GUIDELINE_NO3_N), 'is_exceedance'] = 1

        agg_dict = {'wert_num':['mean','max', 'count'], 'is_exceedance':['sum'], 'year':['min','max']}
        _df = _df[['station_id', 'wert_num', 'is_exceedance','year']].groupby(['station_id']).agg(agg_dict).reset_index()
        
        _df.columns=['station_id','mean_nitrate','max_nitrate','observations','nbr > guideline', 'first_year','last_year']

        _df['pct > guideline'] = (_df['nbr > guideline'] / _df['observations'] * 100).round(1)        
        _df['years'] = _df['last_year'] - _df['first_year'] + 1     
        _df=_df[['station_id','mean_nitrate','max_nitrate','observations','nbr > guideline', 'pct > guideline', 'first_year','last_year', 'years']]
        _df[['mean_nitrate','max_nitrate']] = _df[['mean_nitrate','max_nitrate']].round(1)
        return _df

    def report(self):
        """
        This function generates the temperature report with all texts, tables and figures
        """

        
        def get_trends(df):
            trends = {}
            trends['num'] = len(df)
            trends['increasing'] = len(df[df['trend_result']=='increasing'])
            trends['decreasing'] = len(df[df['trend_result']=='decreasing'])
            trends['no_trend'] = trends['num'] - trends['increasing'] - trends['decreasing']
            return trends

        # start
        fig_num = 1
        tab_num = 1

        # intro
        samples_in_last5_years = self.data[self.data['year'] >= datetime.now().year]
        samples_in_last5_years = len(samples_in_last5_years['station_id'].unique())
        st.markdown(texts['intro'].format(self.data.year.min(), len(self.stations), samples_in_last5_years), unsafe_allow_html=True)
        self.show_location_map(self.well_records)
        fig_num = helper.show_legend(texts, FIGURE, fig_num) 

        # stats
        # yearly stats
        df = self.show_yearly_stat_table()
        max_conc = df['pct > guideline'].max()
        year_max_conc = int(df[df['pct > guideline'] == max_conc].iloc[0]['year'])
        min_conc = df['pct > guideline'].min()
        year_min_conc = int(df[df['pct > guideline'] == min_conc].iloc[0]['year'])
        st.markdown(texts['yearly_stats'].format(tab_num, fig_num, max_conc,year_max_conc, min_conc, year_min_conc), unsafe_allow_html=True)
        
        cols = st.columns(2)
        df_plot = df[['year','pct > guideline','mean_nitrate']]
        df_plot['guideline'] = GUIDELINE_NO3_N
        with cols[0]:
            settings = {'x':'year', 'y': 'pct > guideline', 'width':400,'height':200, 'tooltip':df_plot.columns}
            plots.bar_chart(df_plot, settings)
        with cols[1]:
            settings['y'] = 'mean_nitrate'
            settings['h_line'] = 'guideline'
            plots.bar_chart(df_plot, settings)
        fig_num = helper.show_legend(texts, FIGURE, fig_num) 
        settings = {'height':250, 'selection_mode':'none', 'fit_columns_on_grid_load': False}
        helper.show_table(df, [], settings)
        tab_num = helper.show_legend(texts, TABLE, tab_num,{self.years_of_data}) 
        
        ## well stats
        df = self.show_well_stat_table()
        max_conc = df['max_nitrate'].max()
        station_max_conc = int(df[df['max_nitrate'] == max_conc].iloc[0]['station_id'])
        _df = df[df['years']>=20]
        max_mean_conc = _df['max_nitrate'].max()
        station_max_mean_conc = int(_df[_df['max_nitrate'] == max_mean_conc].iloc[0]['station_id'])
        st.markdown(texts['well_stats'].format(tab_num, max_conc, station_max_conc, station_max_mean_conc, max_mean_conc), unsafe_allow_html=True)
        
        settings = {'height':250, 'selection_mode':'none', 'fit_columns_on_grid_load': False}
        helper.show_table(df, [], settings)
        tab_num = helper.show_legend(texts, TABLE, tab_num,{self.years_of_data}) 

        # spatial distribution
        #time series
        st.markdown(texts['spatial_distribution'].format(fig_num), unsafe_allow_html=True)
        year = st.slider('Select a year:', min_value=int(self.first_year), max_value=int(datetime.now().year), value=int(datetime.now().year))
        df = self.data[self.data['year']==year]
        df = df[['station_id', 'lat','long','wert_num']].groupby(['station_id', 'lat','long']).agg('max').reset_index()
        self.show_spatial_distribution(df)

        fig_num = helper.show_legend(texts, FIGURE, fig_num) 

        # time series
        
        st.markdown(texts['time_series'].format(fig_num), unsafe_allow_html=True)
        self.show_temporal_distribution()
        fig_num = helper.show_legend(texts, FIGURE, fig_num) 

        text = texts['conclusion'].format(self.years_of_data, len(self.stations), GUIDELINE_NO3_N)
        st.markdown(text, unsafe_allow_html=True)

    
    def show_menu(self):
        self.report()