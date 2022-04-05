import streamlit as st
import texts

class Info():
    def __init__(self):
        pass

    def show_menu(self):
        st.markdown(texts.intro)
