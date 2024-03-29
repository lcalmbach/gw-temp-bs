# from webbrowser import BackgroundBrowser

import pandas as pd
import streamlit as st
import requests
from streamlit_lottie import st_lottie
from st_aggrid import GridOptionsBuilder, AgGrid, DataReturnMode,GridUpdateMode
import const as cn
import base64
import numpy as np

FONT_SIZE_SMALL = 0.9

@st.experimental_memo()
def get_lottie(url):
    ok=True
    r=''
    try:
        r = requests.get(url).json()
    except:
        ok = False
    return r,ok

def show_lottie(url):
    lottie_search_names, ok = get_lottie(url)
    if ok:
        with st.sidebar:
            st_lottie(lottie_search_names
            , height=80
            , loop=True
        )

def font_size_small(text:str, size:float=0.9)->str:
    """wraps a font size tag around a given text to change the font size of a standard markdown text

    Args:
        text (str): tesxt to be sent to markdown
        size (float, optional): font size. Defaults to 0.9.

    Returns:
        str: text with tags
    """
    return f'<span style="font-size:{FONT_SIZE_SMALL}em">{text}</span>'

def show_table(df: pd.DataFrame, cols, settings):
    gb = GridOptionsBuilder.from_dataframe(df)
    #customize gridOptions
    if 'update_mode' not in settings:
        settings['update_mode']=GridUpdateMode.SELECTION_CHANGED
    gb.configure_default_column(groupable=False, value=True, enableRowGroup=False, aggFunc='sum', editable=False)
    for col in cols:
        gb.configure_column(col['name'], type=col['type'], precision=col['precision'], hide=col['hide'])
    gb.configure_selection(settings['selection_mode'], use_checkbox=False)#, rowMultiSelectWithClick=rowMultiSelectWithClick, suppressRowDeselection=suppressRowDeselection)
    gb.configure_grid_options(domLayout='normal')
    gridOptions = gb.build()

    grid_response = AgGrid(
        df, 
        gridOptions=gridOptions,
        height=settings['height'], 
        data_return_mode=DataReturnMode.AS_INPUT, 
        update_mode=settings['update_mode'],
        fit_columns_on_grid_load=settings['fit_columns_on_grid_load'],
        allow_unsafe_jscode=True, 
        enable_enterprise_modules=False,
        )
    selected = grid_response['selected_rows']
    selected_df = pd.DataFrame(selected)
    return selected_df

def show_legend(texts:list, legend_type:str, id:int, args:list=[])->int:
    """
    writes a legend statement for a specified figure or table index and 
    returns the index for the next figure or table.

    Args:
        texts (list): all legends for this type (figure or table)
        legend_type (str): _description_
        id (int): figure or table index in text, the listindex is therefore id-1
        args (list, optional): list of arguments to be added to the format statement.

    Returns:
        int: _description_
    """
    text = texts[legend_type][id-1].format(id, *args)
    st.markdown(font_size_small(text), unsafe_allow_html=True)
    return id + 1

def get_auto_grid_height(df:pd.DataFrame, max_height: int)->int:
    if (len(df)+1) * cn.GRID_ROW_HEIGHT < max_height:
        return 30 + (len(df)+1) * cn.GRID_ROW_HEIGHT
    else:
        return max_height

def get_table_download_link(df: pd.DataFrame, filename:str) -> str:
    """
    Generates a link allowing the data in a given panda dataframe to be downloaded

    :param df:  table with data
    :return:    link string including the data
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">⬇️Download csv file</a>'
    return href

def get_digits(values:list):
    values.sort()
    min,max= values[0], values[-1]
    m = int(np.log10(min))
    if m<0:m-=1
    if m < 0:
        return abs(m)
    elif m < 100:
        return 1
    else:
        return 0 
    