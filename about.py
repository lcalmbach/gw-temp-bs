import streamlit as st
from datetime import datetime
import texts
import helper
import gw_data as data


class About():
    def __init__(self):
        self.wq_data = data.get_water_quality_data()
        self.stations_list = list(self.wq_data['station_id'].unique())
        self.well_records = data.get_well_records([])
    
    def show_menu(self):
        st.image('./img/rhein.jpg', caption=None, width=None, use_column_width='auto', clamp=False, channels='RGB', output_format='auto')
        figure = '[Quelle Abbildung](https://www.bs.ch/bilddatenbank)'
        st.markdown(helper.font_size_small(figure), unsafe_allow_html=True)
        st.markdown(texts.intro.format(len(self.stations_list)))
