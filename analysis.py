import streamlit  as st

import streamlit as st


class Analysis():
    def __init__(self):
        pass

    def show_menu(self):
        MENU_OPTIONS = ['Mann Kendall Test', 'Heatmap']
        menu_item = st.sidebar.selectbox('Analysis', options=MENU_OPTIONS)
