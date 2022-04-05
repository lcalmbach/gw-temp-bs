import streamlit as st
from info import Info
from analysis import Analysis

MENU_OPTIONS = ['Info', 'Trend analysis', 'report']

def main():
    menu_item = st.sidebar.selectbox('Menu', options=MENU_OPTIONS)
    if menu_item==MENU_OPTIONS[0]:
        app = Info()
    elif menu_item==MENU_OPTIONS[1]:
        app = Analysis()
    app.show_menu()

if __name__ == "__main__":
    main()
    