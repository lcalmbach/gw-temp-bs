import pandas as pd
import const as cn
import streamlit as st

#@st.cache
def get_well_records(stations_list: list)->pd.DataFrame:
    df = pd.read_parquet(cn.datasource['well-records'])

    df['depth_m'] = df['borehole_top'] - df['borehole_bottom']
    #df['catnr45'] = df['catnr45'].astype('str')
    #df['year']=df['year'].astype(float)
    #df.fillna('', inplace=True)
    if stations_list != []:
        stations_list = [str(x) for x in stations_list]
        df = df[df['laufnummer'].astype(str).isin(stations_list)]

    return df

def get_standard_dataset(datasource):
    df = pd.read_parquet(cn.datasource[datasource])
    #st.write(df)
    return df

#@st.cache
def get_water_quality_data():
    df = pd.read_parquet(cn.datasource['water-quality-values'])
    columns = ['station_id', 'probenahmedatum_date','parameter', 'wert', 'bg', 'einheit']
    df = df[columns]
    df.columns = ['station_id', 'date','parameter', 'value', 'detection_limit', 'unit']
    df['year'] = df['date'].dt.year
    return df