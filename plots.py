import folium
from streamlit_folium import folium_static
import pandas as pd
import altair as alt
import streamlit as st

ZOOM_START_DETAIL = 13

def plot_map(df: pd.DataFrame, settings: dict, categories: dict={}):
    m = folium.Map(location=settings['midpoint'], zoom_start=ZOOM_START_DETAIL)
    for index, row in df.iterrows():
        tooltip = settings['tooltip_html'].format(
                row['station']
                ,row['depth']
                ,row['temp_mean']
            )
        popup = row['station']
        if len(categories)==0:
            folium.Marker(
                [row['latitude'], row['longitude']], popup=popup, tooltip=tooltip,
            ).add_to(m)
        else:
            category_field = row[settings['cat_field']]
            _icon=categories[category_field]['icon']
            _color=categories[category_field]['color']
            folium.Marker(
                [row['latitude'], row['longitude']], popup=popup, tooltip=tooltip,
                icon=folium.Icon(color=_color, prefix='fa', icon=_icon),
            ).add_to(m)
    folium_static(m)

def line_chart(df, settings, regression:bool=True):
    title = settings['title'] if 'title' in settings else ''
    chart = alt.Chart(df).mark_line(width = 2, clip=True).encode(
            #x= alt.X(settings['x']),
            x= alt.X(settings['x'], scale=alt.Scale(domain=settings['x_domain'])),
            y= alt.Y(settings['y'], scale=alt.Scale(domain=settings['y_domain'])),
            #y= alt.Y(settings['y']),
            tooltip=settings['tooltip']    
        )
    if regression:
        line = chart.transform_regression('year', 'temperature (°C)').mark_line()
        plot = (chart + line).properties(width=settings['width'], height=settings['height'], title = title)
    else:
        plot = chart.properties(width=settings['width'], height=settings['height'], title = title)
    st.altair_chart(plot)

def scatter_plot(df, settings):
    title = settings['title'] if 'title' in settings else ''
    chart = alt.Chart(df).mark_circle(size=60).encode(
        x= alt.X(settings['x'], scale=alt.Scale(domain=settings['domain'])),
        y= alt.Y(settings['y'], scale=alt.Scale(domain=settings['domain'])),
        tooltip=settings['tooltip'],
        color=settings['color']
    ).interactive()
    plot = chart.properties(width=settings['width'], height=settings['height'], title = title)
    st.altair_chart(plot)

def time_series_chart(df, settings, regression:bool=True):
    #line = alt.Chart(df_line).mark_line(color= 'red').encode(
    #    x= 'x',
    #    y= 'y'
    #    )
    title = settings['title'] if 'title' in settings else ''
    chart = alt.Chart(df).mark_line(width = 20, point=alt.OverlayMarkDef(color='blue')).encode(
        x= alt.X('sampling_date:T', scale=alt.Scale(domain=settings['x_domain'])),
        y= alt.Y('temperature:Q', scale=alt.Scale(domain=settings['y_domain'])),
        tooltip=['sampling_date', 'temperature']    
    )
    if regression:
        line = chart.transform_regression('sampling_date', 'temperature').mark_line()
        plot = (chart + line).properties(width=settings['width'], height=settings['height'], title = title)
    else:
        plot = chart.properties(width=settings['width'], height=settings['height'], title = title)
    st.altair_chart(plot)

def heatmap(df, settings):
    chart = alt.Chart(df).mark_rect().encode(
        x=settings['x'],
        y=settings['y'],
        color=settings['color'],
        tooltip=settings['tooltip']
    ).properties(title = settings['title'])
    st.altair_chart(chart)
