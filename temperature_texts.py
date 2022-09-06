texts = {
'intro': """## Groundwater temperature trend since {0} in Basel (Switzerland)

Temperature is considered an important quality indicator for ground and surface water. A higher water temperature limits the solubility of oxygen and various minerals. Higher temperatures in groundwater also stimulate microbial activity. The observation of groundwater temperature may contribute important information to better understanding the climate change process. To date, an overall increase in groundwater temperature can be observed across Switzerland ([bafu.admin.ch](https://www.bafu.admin.ch/bafu/en/home/topics/water/info-specialists/state-of-waterbodies/state-of-groundwater/groundwater-temperature.html)). This study attempts to characterize the temperature state and past trend in the groundwater of the canton of Basel-Stadt (northern Switzerland) and to answer the following questions:
- Is the groundwater temperature generally increasing?
- How does groundwater temperature compare to ambient surface temperature
- What groundwater temperatures can be expected in ten years?

### Location of Stations
The Office for environmental protection of Basel-Stadt (AUE) has published its groundwater temperature monitoring data since {0} on the Open Government Data portal [data.bs](https://data.bs.ch/explore/dataset/100067). Figure 1 shows the location of all monitoring sites with available temperature measurements in the study area. At most of these sites, the temperature is registered hourly. To optimize processing time, these values have been aggregated to daily averages.
""",

'eval': """## Methodology
This study uses a combination of statistical methods and visual inspection to classify the temperature trends in each station. The initial hourly observation frequency was averaged to monthly average values. Then, the Mann-Kendall trend test estimator was calculated for each station. 
This test allows determining whether a time series has a monotonic upward or downward trend. Some details on the test are given in the paragraph below. Time series diagrams were generated for each station, and a linear regression was conducted on all time series. Yearly surface temperature values were also compiled to study the correlation of temperature above and below ground surface.

### Mann-Kendall Test
hypothesis assumes no trend in the data. The calculated estimator to accept or reject the hypothesis is based on the slopes that can be constructed between data points: if the number of positive slopes exceeds the number of negative slopes, a positive trend is more likely. The test assumes that in a time series without trend, the number of positive and negative slopes should be similar. If either positive or negative slopes clearly dominate, the hypothesis is rejected, and therefore the alternative hypothesis of an increasing or decreasing trend is accepted. Many variations exist for the Mann-Kendall test, introducing various corrections for seasonality, co-correlation, and others. We applied the original Mann-Kendall test and used the python package *pyMannKendall* ([Hussain et al., (2019)](https://joss.theoj.org/papers/10.21105/joss.01556)) to calculate the Mann-Kendall trend estimators.
""",

'tab':[
        """Table {}: Mann-Kendall results for all stations having a minimum of 10 temperature observations. The p-value reflects the probability for the given distribution of positive and negative slopes in the time series to represent the outcome that the data is not increasing or decreasing. The lower the p-value, the higher the chance that the time series follows an increasing or decreasing trend.""",

        """Table {}: Linear regression results for groundwater temperature time series. r-value= pearson-correlation coefficient: values close to one indicate a high correlation, values close to zero a low correlation, intercept: y-axis intercept of the correlation line, slope: slope of regression line in °C/year, 10yr prediction: extrapolation of correlation line to the date 10 years from today."""
    ],

"fig": [
        "Figure {}: Location of stations with available groundwater temperature observations. Min, max und average values are calculated based on monthly averaged values. Use the cursor to discover the depth and mean temperature for these locations.",
        "Figure {}: Spatial distribution of positive, negative, and neutral groundwater temperature trends.",
        "Figure {}: Surface temperature in the study area with linear regression line.",
        "Figure {}: Comparison of yearly average for surface temperature and groundwater temperature.",
        "Figure {}: Heatmap for average temperature values for all stations in the groundwater monitoring network with available temperature data. Stations are ordered by groundwater sampling depth, with shallow stations on the top of the chart. Hover the mouse cursor over a colored rectangle on the plot to show additional information for the respective year and station.",

    ],

'result': """## Results
### Statistical tests
Mann-Kendall tests have been performed on all stations having a minimum of 10 temperature observations. The data provided from stations equipped with sensors were averaged by month. As shown in table {}, out of {} stations, {} were identified as having an increasing trend, and {} had no significant trend. Among the stations having no trend, visual inspection reveals that the overall trend is generally increasing; however, the trend is not sufficiently strong to pass the Mann-Kendall test. This is also confirmed by the positive slope of the linear regression line. Only {} stations were found to have a decreasing trend. Table 1 generates the corresponding time series diagrams when a station is marked using the mouse cursor. The result table below is interactive: clicking on a station in this table will display the unlying data as a time series with a regression line as well as the table of the data used for the calculation.""",

'result_map': """### Spatial Distribution
Figure 2 shows the spatial distribution of the different trend test results: *increasing* (orange), *decreasing* (blue), and *no trend* (gray). This map does not allow to delineate ares of a common trend pattern. The difference of trend and average temperature, that can be observed in neighbouring stations suggests that manmade processes may impact the natural groundwater. Further knowledge of the local groundwater flow system should be included in order to interpret the spatial distribution of temperature time series.
""",

'surface_temperature': """### Comparison to Surface Temperature
Groundwater infiltrates from the surface. In the absence of cooling or heating effects in the subsurface, groundwater temperature should closely reflect the temperature on the surface during infiltration, particularly in shallow systems. Figure 3 shows the yearly average of surface temperature at the Meteorologische Station Basel-Binningen (data source: [Meteoblue](https://www.meteoblue.com/de/historyplus)). The temperature curve seems to follow an increasing trend, which is confirmed by the Mann-Kendall test result (p=0.05) and the regression line. The temperature regression results in a yearly temperature increase of {:.2f}°C/year.
""",
'surface_temperature_compare_to_groundwater':"""Figure 4 compares the annual average temperatures of ground and surface water in a scatter plot. This representation shows that groundwater temperatures are approximately 4 degrees warmer than the surface temperature. Each marker represents a year, and the marker fill color ranging from blue = early years to red = later years allows to appreciate a trend from the lower left to the upper right. The correlation between the two parameters is relatively low. Such a correlation may only be expected on a broad timescale and with a considerable time lag since warmer or cooler surface water requires a substantial time span to reach the water table. In addition, the groundwater temperature may be influenced by anthropogenic activities such as heat extraction by heat pumps or heated underground constructions.""",

'result_heatmap': """### Heatmap
Heatmaps are an efficient visual tool to detect patterns in data. For this study, the y-axis represents all stations, and the x-axis with a resolution of one year. For each rectangle, the average temperature for the year and station is calculated, and a color is assigned to the rectangle representing the temperature value. It must be noted that in earlier years, a yearly average may consist only of a single observation, whereas more recently, most stations provide daily observations. This figure allows us to spot stations where groundwater seems warmer or colder than that of most other stations. For example, the temperature measured at station 1854 appears to be overall higher, and the temperature at 1655 overall lower.

The heatmap allows us to appreciate time series data density and completeness. Most time series start in 2008; there is a general data gap from 2014 to 2017. Only stations 580 and 1090 provide data over a longer time interval.
""",

'prediction': """### 10 Year Groundwater Temperature Prediction
Linear regression was conducted on stations of the groundwater temperature monitoring stations. Increasing trend rates are estimated using the intercept and slope of the linear regression. slopes range from {:.2f} to {:.2f} °C/yr with an average value of {:.2f} °C/yr. Extrapolating the linear trend over the next ten years may lead to a groundwater temperature between {:.1f} and {:.1f} °C and an average of {:.1f} °C.
""",

'conclusion': """### Conclusion
This study has found that nearly half of all stations in the groundwater monitoring network of Basel show an increasing temperature trend. Temperature increase per year varies between {:.2f} and {:.2f} °C/year, based on the linear regression calculation. This increase is considerably higher than the observed surface temperature increase during the same period of {:.2f}°C/year. While the increasing surface temperature may partly explain the increasing temperature trend in groundwater, this fact does not explain why the process should be stronger in the subsurface than on the surface. In an area of intensive urban residential and industrial land use, artificial processes represent additional suspects for impacting the groundwater temperature. Underground constructions and heat exchange pumps used for heating or cooling are potential candidates for such processes. However, all mentioned processes are mere candidates to explain the observed temperature trend phenomenon. Additional data and research is required to confirm these hypotheses.

#### More information 
- [Umweltbericht beider Basel](https://www.umweltberichtbeiderbasel.bs.ch/indikatoren/indikatoren-uebersicht/16-wasser/wassertemperatur-grundwasser.html)
- [Groundwater temperature (Federal Office for the Environment FOEN)](https://www.bafu.admin.ch/bafu/en/home/topics/water/info-specialists/state-of-waterbodies/state-of-groundwater/groundwater-temperature.html)

""",


'mk-menu':"""This menu item allows to conduct and inspect the [Mann-Kendall test](https://wikitia.com/wiki/Mann-Kendall_trend_test) on all or a selection of wells. The table below provides more detail on the temperature stastistics as well as on the test results. The line on the plots represents the [Theil–Sen estimator](https://en.wikipedia.org/wiki/Theil%E2%80%93Sen_estimator).

Select your stations and define the minimum number of points required to conduct the test, then press the `Run MK-test` button.
"""
}