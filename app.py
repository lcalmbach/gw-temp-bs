from http.client import OK
import streamlit as st
import pandas as pd
import pickle
from os.path import exists

from about import About
import helper
import temperature 

__version__ = '0.0.1'
__author__ = 'Lukas Calmbach'
__author_email__ = 'lcalmbach@gmail.com'
VERSION_DATE = '2022-04-09'
GIT_REPO = 'https://github.com/lcalmbach/gw-temp-bs'
APP_NAME = 'groundwater.bs'
APP_ICON="💧"


MENU_OPTIONS = ['About', 'Temperature Trends']
DATA_FILE = './temperature_data.pkl'
LOTTIE_URL = "https://assets5.lottiefiles.com/packages/lf20_ZQqYEY.json"
LOTTIE_URL = "https://assets1.lottiefiles.com/packages/lf20_fwlx9xtz.json"

APP_INFO = f"""<div style="background-color:powderblue; padding: 10px;border-radius: 15px;">
    <small>App created by <a href="mailto:{__author_email__}">{__author__}</a><br>
    version: {__version__} ({VERSION_DATE})<br>
    <a href="{GIT_REPO}">git-repo</a>
    """

def get_data():
    def extract_geopoint(df):
        df[['latitude', 'longitude']] = df['Geo Point'].str.split(',', expand=True)
        df.pop('Geo Point')
        return df

    def create_pickle():
        ok = False
        try:
            df_temp = pd.read_csv('./data/100067_temp.csv', sep=';')
            fields = ['Probenahmestelle', 'Probenahmedatum_date', 'Geo Point', 'Wert']
            df_temp = df_temp[fields]
            df_temp = extract_geopoint(df_temp)
            df_temp.columns=['station','sampling_date','temperature','latitude','longitude']

            df_depth = pd.read_csv('./data/100067_tiefe.csv', sep=';')
            fields = ['Probenahmestelle', 'Wert']
            df_depth = df_depth[fields]
            df_depth = df_depth.groupby('Probenahmestelle').aggregate(['mean']).reset_index()
            df_depth.columns = ['station', 'sampling_depth']

            df_joined = pd.merge(df_temp, df_depth, left_on='station', right_on='station') 
            df_joined=df_joined[['station', 'latitude', 'longitude','sampling_date','sampling_depth', 'temperature']]
            df_joined['sampling_date']= pd.to_datetime(df_joined['sampling_date'])
            pd.to_pickle(df_joined, DATA_FILE)
            ok=True
        except:
            ok = False
        return ok

    if not exists(DATA_FILE):
        create_pickle()
    
    return pd.read_pickle(DATA_FILE)

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
    app.show_menu()
    st.sidebar.markdown(APP_INFO, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    