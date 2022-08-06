from http.client import OK
import streamlit as st
import pandas as pd

from about import About
import helper
import temperature 
import well_records
import const as cn

__version__ = '0.0.4'
__author__ = 'Lukas Calmbach'
__author_email__ = 'lcalmbach@gmail.com'
VERSION_DATE = '2022-07-25'
GIT_REPO = 'https://github.com/lcalmbach/gw-temp-bs'
APP_NAME = 'groundwater.bs'
APP_ICON = "💧"


MENU_OPTIONS = ['About', 'Temperature Trends', 'Well records']
LOTTIE_URL = "https://assets5.lottiefiles.com/packages/lf20_ZQqYEY.json"
LOTTIE_URL = "https://assets1.lottiefiles.com/packages/lf20_fwlx9xtz.json"

APP_INFO = f"""<div style="background-color:powderblue; padding: 10px;border-radius: 15px;">
    <small>App created by <a href="mailto:{__author_email__}">{__author__}</a><br>
    version: {__version__} ({VERSION_DATE})<br>
    <a href="{GIT_REPO}">git-repo</a>
    """

def get_data():
    return pd.read_pickle(cn.datasource['temperature'])

def main():
    st.set_page_config(
        page_title=APP_NAME,
        page_icon=APP_ICON,
        layout="wide")
    st.sidebar.markdown(f"## <center>{APP_NAME}</center>", unsafe_allow_html=True) 
    helper.show_lottie(LOTTIE_URL)
    data = get_data()
    menu_item = st.sidebar.selectbox('Menu', options=MENU_OPTIONS)
    if menu_item==MENU_OPTIONS[0]:
        app = About(data)
    elif menu_item==MENU_OPTIONS[1]:
        app = temperature.Analysis(data)
    elif menu_item==MENU_OPTIONS[2]:
        app = well_records.Analysis()
    app.show_menu()
    st.sidebar.markdown(APP_INFO, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    