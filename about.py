import streamlit as st
from datetime import datetime
import about_texts
import helper
import gw_data as data


class About():
    def __init__(self):
        #self.wq_data = data.get_water_quality_data()
        #self.stations_list = list(self.wq_data['station_id'].unique())
        #self.well_records = data.get_well_records([])
        pass
    
    def show_menu(self):
        """
        numbers from 
        https://www.aue.bs.ch/wasser/grundwasser/grundwasserpegel-grundwasserqualitaet.html > 84

        """
        st.image('./img/rhein.jpg', caption=None, width=None, use_column_width='auto', clamp=False, channels='RGB', output_format='auto')
        figure = '[Quelle Abbildung](https://www.bs.ch/bilddatenbank)'
        st.markdown(helper.font_size_small(figure), unsafe_allow_html=True)

        st.markdown(about_texts.intro.format(28, 84))
