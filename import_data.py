import streamlit as st
import pandas as pd
from datetime import datetime, date
from temperature_texts import texts
import requests
import json


CURRENT_YEAR = int(date.today().strftime("%Y"))
MONTHS = [f'"{str(x).zfill(2)}"' for x in range(1,2)]


def get_data(url:str, years:list, dataset, stations):
    all_df = pd.DataFrame()
    info = st.empty()
    for station in stations:
        #for month in MONTHS:
        for year in years:
            print(year, station)
            #url_data = requests.get(url.format(dataset, 1, 0, station, month, year)).content # create HTTP response object 
            url_formatted=url.format(dataset, 1, 0, station, year)
            url_data = requests.get(url_formatted).content # create HTTP response object 
            data = json.loads(url_data)
            total_count = data['total_count']
            
            if total_count > 0:
                has_more_records = total_count > 0
                offset=0
                df_list = []
                with st.spinner('Loading data'):
                    while has_more_records:
                        info.text(f"Importing Station: {station}, Year: {year}, records read:{offset}")
                        url_data = requests.get(url_formatted).content # create HTTP response object 
                        data = json.loads(url_data)
                        total_count = data['total_count']
                        if offset >= 9800 or offset >= total_count:
                            has_more_records=False
                            if offset >= 9800:
                                st.warning('offset exceeded')
                        elif data['total_count'] > 0:
                            data = data['records']
                            df = pd.DataFrame(data)['record']
                            df = pd.DataFrame(x['fields'] for x in df)
                            df_list.append(df)
                            offset += 100
                        else:
                            has_more_records=False
                all_df = pd.concat(df_list)
    return all_df 


if st.button("Load Waterlevels incremental"):
    def get_stations():
        df = pd.read_csv("./data/100164.csv", sep=';')
        stations = df['StationId'].unique()
        return list(stations)

    dataset = '100164'
    first_year = 1976
    years=range(first_year, CURRENT_YEAR + 1)

    st.info("starting")
    stations = get_stations()
    url = 'https://data.bs.ch/api/v2/catalog/datasets/{}/records?limit={}&offset={}&select=stationid,timestamp,value&where=stationid="{}"%20and%20year(timestamp)={}'
    df = get_data(url, years, dataset, stations)
    st.write(df.head(500))
    st.info('Saving file')
    filename = f'./{dataset}.gzip'
    df.to_parquet(filename, compression='gzip')
    df_check = pd.read_parquet(filename)
    st.success('Done')
    
    st.write("😁And here is what I got:")
    st.write(df_check.head(500))

if st.button("Load Waterlevels bulk"):
    filename = './data/100164.csv'
    
    st.info("starting")
    df = pd.read_csv(filename,sep=';')
    st.write(df.head())
    df = df[df['Status'] == 'cleansed']
    df = df[['StationId','Date','Value']]
    df.columns = ['stationid','date','value']
    
    df = df.astype({'stationid':'string'})
    df['date'] = pd.to_datetime(df['date'])
    df = df.groupby(['date', 'stationid']).mean().reset_index()
    st.info('Saving file')
    filename = f'./100164.gzip'
    df.to_parquet(filename, compression='gzip')
    df.to_csv('./100164.csv', sep=';',index=False)
    df_check = pd.read_parquet(filename)
    st.success('Done')
    
    st.write("😁And here is what I got:")
    st.write(df_check.head(500))
    
if st.button('Meteo blue Station Binningen'):
    filename = './data/meteo_blue_temp_prec.csv'
    
    st.info("starting")
    df = pd.read_csv(filename,sep=',')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    filename = './meteo_blue_temp_prec.gzip'
    df.to_parquet(filename, compression='gzip')
    st.success('Done')
    st.write("😁And here is what I got:")
    df_check = pd.read_parquet(filename)
    st.write(df_check.head(500))
   
   
if st.button('Rhein Wasserstand'):
    datensatz = '100089'
    filename = f'./data/{datensatz}.csv'
    
    st.info("starting")
    df = pd.read_csv(filename,sep=';')
    df.columns = ['timestamp','abfluss','pegelhoehe','pegel']
    
    df = df[['timestamp','abfluss','pegel']]
    st.write(df.head())
    # converting timestamp directly results in a strange error, and column is not recognized as datetime. I assume there is an errror with a daylaight saving timestamp
    # I first extract the date which is what I need anyways
    df['date']=df['timestamp'].str[:10]
    df['date'] = pd.to_datetime(df['date'] )
    df = df[['date','abfluss','pegel']]
    df = df.groupby(['date'])['abfluss','pegel'].agg(['sum','mean']).reset_index()
    print(df.head())
    df.columns= ['date', 'sum_abfluss', 'mean_abfluss', 'sum_pegel', 'mean_pegel']
    # only use sum abfluss and mean pegel, 
    df = df[['date', 'sum_abfluss', 'mean_pegel']]
    filename = f'./{datensatz}.gzip'
    df.to_parquet(filename, compression='gzip')
    # if output needs to be checed
    #df.to_csv( f'./{datensatz}_formatted.csv')
    st.success('Done')
    st.write("😁And here is what I got:")
    df_check = pd.read_parquet(filename)
    st.write(df_check.head(500))
   