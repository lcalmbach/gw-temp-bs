# gw-temp-bs
[groundwater-bs](https://groundwater-bs.herokuapp.com/) allows to explore datasets related to groundwater quality and water levels in Basel (Switzerland). Most datasets used are published on the open governemnt data portal [data.bs](https://data.bs.ch). 

This app is written in Python and uses the framework [Streamlit](https://streamlit.io/). For plotting the packages [Altair](https://altair-viz.github.io/) and [Folium](https://python-visualization.github.io/folium/) are used for most visualisations.

If you wish to install this application locally and make changes to it, proceed as follows (on Windows system):

```
> git clone https://github.com/lcalmbach/gw-temp-bs.git
> cd gw-temp-bs
> python -m venv env
> env\scripts\activate
> pip install -r requirements.txt
> streamlit run app.py
```
