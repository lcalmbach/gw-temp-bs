import streamlit as st
import texts
import helper

class About():
    def __init__(self, data):
        self.data = data

    def show_menu(self):
        st.image('./img/rhein.jpg', caption=None, width=None, use_column_width='auto', clamp=False, channels='RGB', output_format='auto')
        figure = '[Quelle Abbildung](https://www.bs.ch/bilddatenbank)'
        st.markdown(helper.font_size_small(figure), unsafe_allow_html=True)

        stations = len(self.data['station'].unique())
        st.markdown(texts.intro.format(stations))
        
