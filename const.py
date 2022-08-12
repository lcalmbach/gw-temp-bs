S3_BUCKET = "lc-opendata01"

config = 'local'
cfg = {
    'local': {
        'data_source': {'wl-level':'./data/100164.gzip', 
        'rheinpegel': './data/100089.gzip', 
        'well-records': './data/100182.gzip',
        'meteo':'./data/meteo_blue_temp_prec.gzip',
        'temperature': './data/100067_temp.pkl',
        'surface_temp_year':'./data/surface_temp_year.csv',
        'water-quality-values': './data/100067_values.gzip',
        'water-quality-parameters': './data/100067_parameters.gzip'
        }
    },
    's3': {
        'data_source': {'wl-level':'s3://lc-opendata01/100164.gzip', 
        'rheinpegel': 's3://lc-opendata01/100089.gzip', 
        'well-records': 's3://lc-opendata01/100182.gzip',
        'meteo':'s3://lc-opendata01/meteo_blue_temp_prec.gzip',
        'temperature': 'todo'
        }
    }
}

datasource = cfg[config]['data_source']
station_grid_fields = ['laufnummer','art','street','house_number','geology','gwl_elevation','depth_m']
wq_sample_parameter = ["station_id", 'date']
GRID_ROW_HEIGHT = 30