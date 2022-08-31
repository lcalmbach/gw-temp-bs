import streamlit as st

from about import About
import helper

import well_records
import water_levels
import water_quality
#articles
import temperature 
import nitrate
__version__ = '0.0.12'
__author__ = 'Lukas Calmbach'
__author_email__ = 'lcalmbach@gmail.com'
VERSION_DATE = '2022-08-30'
GIT_REPO = 'https://github.com/lcalmbach/gw-temp-bs'
APP_NAME = 'groundwater.bs'
APP_ICON = "💧"


MENU_OPTIONS = ['About', 'Borehole records', 'Water level monitoring', 'Water quality monitoring', 'Analysis/Reports']
MENU_ANALYSIS = ['Temperature Trend', 'Nitrate in Groundwater']
LOTTIE_URL = "https://assets5.lottiefiles.com/packages/lf20_ZQqYEY.json"
LOTTIE_URL = "https://assets1.lottiefiles.com/packages/lf20_fwlx9xtz.json"

APP_INFO = f"""<div style="background-color:powderblue; padding: 10px;border-radius: 15px;">
    <small>App created by <a href="mailto:{__author_email__}">{__author__}</a><br>
    version: {__version__} ({VERSION_DATE})<br>
    <a href="{GIT_REPO}">git-repo</a>
    """

def get_article():
    article = st.sidebar.selectbox('Select a report', options=MENU_ANALYSIS)
    if article==MENU_ANALYSIS[0]:
        app = temperature.Analysis()
    elif article==MENU_ANALYSIS[1]:
        app = nitrate.Analysis()
    return app

def main():
    st.set_page_config(
        page_title=APP_NAME,
        page_icon=APP_ICON,
        layout="wide")
    st.sidebar.markdown(f"## <center>{APP_NAME}</center>", unsafe_allow_html=True) 
    helper.show_lottie(LOTTIE_URL)
    menu_item = st.sidebar.selectbox('Menu', options=MENU_OPTIONS)
    if menu_item==MENU_OPTIONS[0]:
        app = About()
    elif menu_item==MENU_OPTIONS[1]:
        app = well_records.Analysis()
    elif menu_item==MENU_OPTIONS[2]:
        app = water_levels.Analysis()
    elif menu_item==MENU_OPTIONS[3]:
        app = water_quality.Analysis()
    elif menu_item==MENU_OPTIONS[4]:
        app = get_article()
    
    app.show_menu()
    st.sidebar.markdown(APP_INFO, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    