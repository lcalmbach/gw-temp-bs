config = 's3'
base= {'local':'./data/',
        's3': 'https://lc-opendata01.s3.amazonaws.com/'}
datasource = {
        'wl-level':f'{base[config]}100164.gzip', 
        'rheinpegel': f'{base[config]}100089.gzip', 
        'well-records': f'{base[config]}100182.gzip',
        'meteo':f'{base[config]}meteo_blue_temp_prec.gzip',
        'gw-temperature': f'{base[config]}1000179.gzip',
        'water-quality-values': f'{base[config]}100067_values.gzip',
        'water-quality-parameters': f'{base[config]}100067_parameter.gzip',
        'wq_guidelines': f'{base[config]}guideline_ch_single_obs.csv'
    }

station_grid_fields = ['laufnummer','art','street','house_number','geology','gwl_elevation','depth_m', 'lat', 'long']
wq_sample_parameter = ["station_id", 'date', 'sampleno']
wq_value_grid_fields = ['parameter','value','unit','detection_limit']
wq_parameters_value_grid_fields = ['parameter','gl_value','cas_bezeichnung','gruppe','allgemeine_parametergruppe']
wq_parameter_value_grid_fields = ["station_id", 'date', 'value', 'unit','value_num', 'nd_flag','gl_value','gl_unit']
GRID_ROW_HEIGHT = 30
DMY_FORMAT = "%d.%m.%Y"