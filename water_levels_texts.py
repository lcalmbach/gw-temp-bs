texts = {
    "info": """## Water level monitoring
The water level shows a list of wells with associated water level monitoring information. By clicking on a well, the corespsonding water level plots will be generated. Optionally additional groundwater related dataset can be shown as discussed below using the `⚙️Settings`. The original dataset has been cleaned for unreasonably high values > 500 masl. 

### Menu options
**water level plot**: This menu option allows to display water levels plots for {1} monitoring wells. Each water level plot may be compared to 
- the timeseries for precipitation ([datasource](https://data.bs.ch/explore/dataset/100051)) 
- the Rhine-water level ([datasource](https://data.bs.ch/explore/dataset/100089))

for comparison. In addition the well record information can be displayed and the position of the selected map on a map.
""",

"trend_intro": "[Mann Kendall](https://up-rs-esp.github.io/mkt/) trend analysis for water levels. The calculation is based on monthly averaged values. The straight line represent the Sen's line (median slope and intercept).",
"trend_table_addition": " Click on a row to see to display the corresponding time series."

}