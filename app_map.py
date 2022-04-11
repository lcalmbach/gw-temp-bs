# from sqlite3.dbapi2 import Timestamp
# from numpy.random.mtrand import random_integers
import streamlit as st
import altair as alt
import pandas as pd
import pydeck as pdk
import numpy as np
import streamlit as st
from streamlit_folium import folium_static
import folium
# import random
from datetime import datetime, time
from queries import qry

import helper

def plot_map(df: pd.DataFrame, settings: dict):
    m = folium.Map(location=settings['midpoint'], zoom_start=cn.ZOOM_START_DETAIL)

    for index, row in df.iterrows():
        tooltip = settings['tooltip_html'].format(
                row['site_id']
                ,row['location']
                ,row['direction_street']
                ,row['start_date']
                ,row['end_date']
                ,row['exceedance_rate']
                ,row['zone']
                ,row['v50']
                ,row['v85']
                ,row['diff_v50']
                ,row['diff_v85']
                ,row['diff_v50_perc']
                ,row['diff_v85_perc']
            )
        popup = row['site_id']
        folium.Marker(
            [row['latitude'], row['longitude']], popup=popup, tooltip=tooltip,
        ).add_to(m)
    return m

    settings = init_settings()
    df, ok = prepare_map_data(conn, settings)
    map_placeholder = st.empty()
    slider_placeholder = st.empty()
    text_placeholder = st.empty()

    settings['midpoint'] = (np.average(df['latitude']), np.average(df['longitude']))
    
    df_year_week = df[['woche','jahr']].drop_duplicates()
    df_year_week['label'] = df["jahr"].apply(str) + "-" + df["woche"].apply(str)
    df_year_week = df_year_week.set_index('label').sort_index()
    time = slider_placeholder.select_slider('Wähle Woche und Jahr', options=list(df_year_week.index))
    week = df_year_week.loc[time]['woche']
    year = df_year_week.loc[time]['jahr']
    df_filtered = df.query(f"(woche == @week) & (jahr == @year) & (direction == {settings['direction']})")
    df_filtered = get_radius(df_filtered, settings)
    df_filtered = get_colors(df_filtered, settings)

    # st.write(df_filtered)
    if len(df_filtered) > 0:
        chart = plot_map(df_filtered, settings)
        folium_static(chart)
        text_placeholder.markdown(get_figure_text(df_filtered,settings,year,week),unsafe_allow_html=True)

