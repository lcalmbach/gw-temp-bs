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
                int(row['stationid'])
                ,row['temp_mean']
                ,row['temp_min']
                ,row['temp_max']
                ,int(row['year_min'])
                ,int(row['year_max'])
            )
        popup = row['stationid']
        if len(categories)==0:
            folium.Marker(
                [row['lat'], row['long']], popup=popup, tooltip=tooltip,
            ).add_to(m)
        else:
            category_field = row[settings['cat_field']]
            _icon=categories[category_field]['icon']
            _color=categories[category_field]['color']
            folium.Marker(
                [row['lat'], row['long']], popup=popup, tooltip=tooltip,
                icon=folium.Icon(color=_color, prefix='fa', icon=_icon),
            ).add_to(m)
    folium_static(m)

def location_map(df: pd.DataFrame, settings: dict):
    m = folium.Map(location=settings['midpoint'], zoom_start=ZOOM_START_DETAIL, width=400, height=400)
    for index, row in df.iterrows():
        folium.Marker(
            [row[settings['lat']], row[settings['long']]]
        ).add_to(m)
    folium_static(m)

def line_chart(df, settings, regression:bool=True):
    title = settings['title'] if 'title' in settings else ''
    chart = alt.Chart(df).mark_line(width = 2, clip=True).encode(
            x= alt.X(settings['x'], scale=alt.Scale(domain=settings['x_domain'])),
            y= alt.Y(settings['y'], scale=alt.Scale(domain=settings['y_domain'])),
            tooltip=settings['tooltip']    
        )
    if regression:
        line = chart.transform_regression(settings['x'], settings['y']).mark_line()
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
        color=alt.Color(settings['color'], sort="descending", scale=alt.Scale(scheme='redblue'))
    ).interactive()
    plot = chart.properties(width=settings['width'], height=settings['height'], title = title)
    st.altair_chart(plot)


def wl_time_series_chart(df, settings):
    #line = alt.Chart(df_line).mark_line(color= 'red').encode(
    #    x= 'x',
    #    y= 'y'
    #    )
    chart = alt.Chart(df).mark_line().encode(
        x = alt.X(f"{settings['x']}:T", scale=alt.Scale(domain=settings['x_domain']), title=settings['x_title']),
        y = alt.Y(f"{settings['y']}:Q", scale=alt.Scale(domain=settings['y_domain']), title=settings['y_title']),
        tooltip = settings['tooltip']
    ).interactive()
    plot = chart.properties(width=settings['width'], height=settings['height'], title=settings['title'])
    st.altair_chart(plot)

def time_series_bar(df, settings):
    chart = alt.Chart(df).mark_bar(size=settings['size'], clip=True).encode(
        x = alt.X(f"{settings['x']}:T", title=settings['x_title'], scale=alt.Scale(domain=settings['x_domain'])),
        y = alt.Y(f"{settings['y']}:Q", title=settings['y_title']),
        tooltip=settings['tooltip']
    )
    plot = chart.properties(width=settings['width'], height=settings['height'], title = settings['title'])
    st.altair_chart(plot)


def time_series_line(df, settings):
    if 'x_domain' in settings:
        xax = alt.X(f"{settings['x']}:T", title=settings['x_title'], scale=alt.Scale(domain=settings['x_domain']))
    else:
        xax = alt.X(f"{settings['x']}:T", title=settings['x_title'])
    
    if settings['y_domain'][0] != settings['y_domain'][1]:
        yax = alt.Y(f"{settings['y']}:Q", title=settings['y_title'], scale=alt.Scale(domain=settings['y_domain']))
    else:  
        yax = alt.Y(f"{settings['y']}:Q", title=settings['y_title'])

    if 'color' in settings:
        chart = alt.Chart(df).mark_line(clip=True).encode(
            x = xax,
            y = yax,
            color = settings['color'],
            tooltip=settings['tooltip']
        )
    else:
        chart = alt.Chart(df).mark_line(clip=True).encode(
            x = xax,
            y = yax,
            tooltip=settings['tooltip']
        )
    
    if 'h_line' in settings:
        chart += alt.Chart(df).mark_line(clip=True, color='red').encode(
        x = xax,
        y = settings['h_line'],
        tooltip = settings['h_line'])
    
    if 'symbol_size' in settings:
        if not('symbol_opacity' in settings):
            settings['symbol_opacity'] = 0.6
        if 'color' in settings:
            chart += alt.Chart(df).mark_circle(size=settings['symbol_size'], clip=True, opacity=settings['symbol_opacity']).encode(
                x = xax,
                y = yax,
                color = settings['color'],
                tooltip = settings['tooltip']
            )
        else:
            chart += alt.Chart(df).mark_circle(size=settings['symbol_size'], opacity=settings['symbol_opacity']).encode(
                x = xax,
                y = yax,
                tooltip = settings['tooltip']
            )
    plot = chart.properties(width=settings['width'], height=settings['height'], title=settings['title'])
    st.altair_chart(plot)

def time_series_chart(df, settings, regression:bool=True):
    #line = alt.Chart(df_line).mark_line(color= 'red').encode(
    #    x= 'x',
    #    y= 'y'
    #    )
    title = settings['title'] if 'title' in settings else ''
    chart = alt.Chart(df).mark_line(point=alt.OverlayMarkDef(color='blue')).encode(
        x= alt.X(f"{settings['x']}:T"),#, scale=alt.Scale(domain=settings['x_domain']), title=settings['x_title']),
        y= alt.Y(f"{settings['y']}:Q", scale=alt.Scale(domain=settings['y_domain']), title=settings['y_title']),
        tooltip=settings['tooltip']
    )
    if regression:
        line = chart.transform_regression(settings['x'], settings['y']).mark_line(color='orange')
        plot = (chart + line).properties(width=settings['width'], height=settings['height'], title = title)
    else:
        plot = chart.properties(width=settings['width'], height=settings['height'], title = title)
    st.altair_chart(plot)

def heatmap(df, settings):
    plot = alt.Chart(df).mark_rect().encode(
        x=settings['x'],
        y=settings['y'],
        color=settings['color'],
        tooltip=settings['tooltip']
    ).properties(title = settings['title'])
    st.altair_chart(plot)
