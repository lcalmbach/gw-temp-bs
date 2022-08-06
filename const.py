S3_BUCKET = "lc-opendata01"

config = 'local'
cfg = {
    'local': {'data_source': {'wl-level':'./data/100164.gzip', 
        'rheinpegel': './data/100089.gzip', 
        'well-records': './data/100182.gzip',
        'meteo':'./data/meteo_blue_temp_prec.gzip',
        'temperature': './data/100067_temp.pkl',
        'surface_temp_year':'./data/surface_temp_year.csv'
        }
    },
    's3': {'data_source': {'wl-level':'s3://lc-opendata01/100164.gzip', 
        'rheinpegel': 's3://lc-opendata01/100089.gzip', 
        'well-records': 's3://lc-opendata01/100182.gzip',
        'meteo':'s3://lc-opendata01/meteo_blue_temp_prec.gzip',
        'temperature': 'todo'
        }
    }
}

datasource = cfg[config]['data_source']
