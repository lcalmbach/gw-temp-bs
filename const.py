config = 'local'
cfg = {
    'local': {
        'data_source': {'wl-level':'./data/100164.gzip', 
        'rheinpegel': './data/100089.gzip', 
        'well-records': './data/100182.gzip',
        'meteo':'./data/meteo_blue_temp_prec.gzip',
        'gw-temperature': './data/1000179.gzip',
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
station_grid_fields = ['laufnummer','art','street','house_number','geology','gwl_elevation','depth_m', 'lat', 'long']
wq_sample_parameter = ["station_id", 'date', 'sampleno']
wq_value_grid_fields = ['parameter','value','unit','detection_limit']
wq_parameters_value_grid_fields = ['parameter','cas_bezeichnung','gruppe','allgemeine_parametergruppe']
wq_parameter_value_grid_fields = ["station_id", 'date', 'value', 'unit','value_num', 'nd_flag']
GRID_ROW_HEIGHT = 30
DMY_FORMAT = "%d.%m.%Y"