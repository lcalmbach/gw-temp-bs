import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import numpy as np
import altair as alt
import helper
import const as cn
import datetime

ZOOM_START_DETAIL = 13

def plot_colormap (df: pd.DataFrame, settings: dict):
    def get_auto_legend(digits:int):
        st.write(min,max)
        if min == max:
            text = f"""Legend | &nbsp; 
------ | ------
🟢   | {min.round(digits)}"""
        else:
            text = f"""Legend | &nbsp; 
------ | ------
🟢   | {min.round(digits)} - {(min + (max-min) * 0.25).round(digits)} 
🟡   | >{(min + (max-min) * 0.25).round(digits)} - {(min + (max-min) * 0.5).round(digits)}
🟠   | >{(min + (max-min) * 0.5).round(digits)} - {(min + (max-min) * 0.75).round(digits)}
🔴   | >{(min + (max-min) * 0.75).round(digits)}"""
        return text
    
    def get_color_legend(digits:int):
        text =f"""Legend | &nbsp; 
------ | ------
🟢   | compliant 
🔴   | non compliant
"""
        return text

    def get_defaults(settings):
        if 'size' not in settings: settings['size'] = 20
        if 'tooltip_html' not in settings:
            settings['tooltip_html'] = """
            <b>Station:</b> {}<br/>           
            <b>Value:</b> {}<br/>"""
        return settings
    
    df.dropna( subset=[settings['lat'], settings['long'], settings['value_col']], inplace=True)
    df[[settings['lat'], settings['long']]] =df[[settings['lat'], settings['long']]] .astype(float)
    
    settings = get_defaults(settings)
    midpoint = list(df[['lat','long']].mean())
    m = folium.Map(location=midpoint, width="%100", height="%100", zoom_start=ZOOM_START_DETAIL)
    digits = helper.get_digits(list(df[settings['value_col']]))
    df[settings['value_col']]=df[settings['value_col']].round(digits)
    if 'colors' not in settings:
        stats = df[settings['value_col']].agg(['mean','std', 'min', 'max'])
        min=stats[0]-stats[1]*2 if stats[0]-stats[1]*2 > stats[2] else stats[2]
        max=stats[0]+stats[1]*2 if stats[0]+stats[1]*2 < stats[3]  else stats[3]
        colormap = folium.StepColormap(colors=['green','yellow','orange','red'], 
            index=[min, (max-min) * 0.25, (max-min) * 0.5, (max-min) * 0.75, max], vmin=min, vmax=max)
    else:
        colormap = folium.StepColormap(colors=settings['colors'], index=settings['limits'], vmin=settings['limits'][0], vmax=settings['limits'][-1])
    for index, row in df.iterrows():
        tooltip = settings['tooltip_html'].format(row[settings['station_col']], row[settings['value_col']])
        folium.Circle(
            location=(row[settings['lat']], row[settings['long']]),
            radius=settings['size'],
            fill=True, 
            color=colormap(row[settings['value_col']]),
            tooltip=tooltip
    ).add_to(m)
    folium_static(m)
    if 'colors' not in settings:
        text = get_auto_legend(digits)
    else:
        text = get_color_legend(digits)
    st.markdown(text, unsafe_allow_html=True)

def plot_map(df: pd.DataFrame, settings: dict, categories: dict={}):
    #complete default settings where missing
    df[settings['lat']] = df[settings['lat']].astype(float)
    df[settings['long']] = df[settings['long']].astype(float)
    if 'midpoint' not in settings:
        settings['midpoint'] = (np.average(df[settings['lat']]), np.average(df[settings['long']]))
    if 'station_col' not in settings:
         settings['station_col'] = 'stationid'

    m = folium.Map(location=settings['midpoint'], zoom_start=ZOOM_START_DETAIL)
    for index, row in df.iterrows():
        tooltip_vals = [row[x] for x in settings['tooltip_cols']]
        tooltip = settings['tooltip_html'].format(*tooltip_vals)
        popup = row[settings['station_col']]
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
    """_summary_

    Args:
        df (pd.DataFrame): _description_
        settings (dict): _description_
    """
    m = folium.Map(location=settings['midpoint'], zoom_start=ZOOM_START_DETAIL, width=400, height=400)
    for index, row in df.iterrows():
        folium.Marker(
            [row[settings['lat']], row[settings['long']]]
        ).add_to(m)
    folium_static(m)

# not working, needs to be fixed
def insert_blank_time_records(df:pd.DataFrame, settings:dict)->pd.DataFrame:
    """checks the distance between the x values of a dataframe and inserts new x values with a null y value
    if the distance between rows is larger than settings['max_x_distance']. this will force lines to break in a plot
    instead of being connected. note that the date column is first converted to int (unix msec) then the difference is 
    calculated on the int64 column.

    Args:
        df (pd.DataFrame): data with a x and y column specified in the settings
        settings (dict):plot settings

    Returns:
        pd.DataFrame: _description_
    """    

    dist = -settings['max_x_distance'] * 24 * 3600 #convert to seconds
    df['date2'] = (df[settings['x']].astype(np.int64)) / 10**9  #convert to seconds
    df['diff'] = df['date2'].diff(-1)
    for index,row in df[df['diff'] < dist].iterrows():
        df_new_row = pd.DataFrame({settings['x']:row[settings['x']] + datetime.timedelta(1),settings['y']: np.nan}, index=[0])
        df = pd.concat([df, df_new_row], ignore_index=True)
    return df

def insert_blank_records(df:pd.DataFrame, settings:dict)->pd.DataFrame:
    """checks the distance between the x values of a dataframe and inserts new x values with a null y value
    if the distinacne between rows is larger than settings['max_x_distance']. this will force lines to break in a plot
    instead of being connected.

    Args:
        df (pd.DataFrame): data with a x and y column specified in the settings
        settings (dict):plot settings

    Returns:
        pd.DataFrame: _description_
    """    

    dist = -settings['max_x_distance']
    df['diff'] = df[[settings['x']]].diff(periods=-1)
    for index,row in df[df['diff'] < dist].iterrows():
        df_new_row = pd.DataFrame({settings['x']:row[settings['x']] + abs(dist), settings['y']: np.nan}, index=[0])
        df = pd.concat([df, df_new_row], ignore_index=True)
    return df


def confidence_band(df, settings):
    title = settings['title'] if 'title' in settings else ''
    st.write(settings['x'],settings['y'])
    if 'max_x_distance' in settings:
        df = insert_blank_records(df,settings)
    line = alt.Chart(df).mark_line().encode(
        x=alt.X(f"{settings['x']}"),
        y=alt.Y('mean_wl', title = settings['y_title'], scale=alt.Scale(domain=settings['y_domain'])),
        )
    band = alt.Chart(df).mark_area(opacity=0.5).encode(
        x=f"{settings['x']}",
        y='ci_95',
        y2='ci_05',
        tooltip=[settings['x'],settings['y'],'ci_95','ci_05']
        )
    plot = (line + band).properties(width=settings['width'], height=settings['height'], title = title)
    st.altair_chart(plot)


def line_chart(df, settings):
    title = settings['title'] if 'title' in settings else ''
    if 'x_dt' not in settings: settings['x_dt'] = 'Q'
    if 'y_dt' not in settings: settings['y_dt'] = 'Q'
    if 'max_x_distance' in settings:
        df = insert_blank_records(df,settings)
    chart = alt.Chart(df).mark_line(width = 2, clip=True).encode(
            x= alt.X(f"{settings['x']}:{settings['x_dt']}", scale=alt.Scale(domain=settings['x_domain'])),
            y= alt.Y(f"{settings['y']}:{settings['y_dt']}", scale=alt.Scale(domain=settings['y_domain'])),
            tooltip=settings['tooltip']    
        )
    if 'regression' in settings:
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

    if 'max_x_distance' in settings:
        df = insert_blank_time_records(df, settings)

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
            color = f"{settings['color']}:N",
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
                color = f"{settings['color']}:N",
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

    if 'max_x_distance' in settings:
        df = insert_blank_time_records(df, settings)

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

def bar_chart(df:pd.DataFrame, settings:dict):
    if 'title' not in settings:
        settings['title'] = ''
    # if 'tooltip' not in settings:
    settings['tooltip'] = [settings['x'], settings['y']]
    bar_width = settings['width'] / len(df) * .75
    plot = alt.Chart(df).mark_bar(size=bar_width).encode(
        x=f"{settings['x']}:N",
        y=settings['y'],
        tooltip=settings['tooltip'] 
    )
    if 'h_line' in settings:
        plot += alt.Chart(df).mark_line(color='red').encode(
            x=f"{settings['x']}:N",
            y = settings['h_line'],
        )

    plot = plot.properties(title = settings['title'],width=settings['width'], height=settings['height'])

    return st.altair_chart(plot)