texts = {
'intro': """## Groundwater temperature trend since 1993 in Basel (Switzerland)

Temperature is considered to be an important quality indicator. Higher water temperature limit the amount of dissolved oxygen and impact the solubility of minerals. Higher temperatures in groundwater also stimualtes microbial activity. The observation in ground water temperature may contribute important information to better understand climate change process. To date, an overall increase in groundwater temperature can be observed across Switzerland ([bafu.admin.ch](https://www.bafu.admin.ch/bafu/en/home/topics/water/info-specialists/state-of-waterbodies/state-of-groundwater/groundwater-temperature.html)). This study attempts to characterize the temperature trend in the groundwater of the canton of Basel (northern Switzerland) where 30 years of groundwater monitoring data have been published on the Opendata portal [data.bs](https://data.bs.ch/explore/dataset/100067). The article attempts to answer the following questions:
- Is the groundwater temperature generally increasing?
- Is there a link between groundwater depth and the extent of temperature increase? 
- What groundwater temperatures can be expected in ten years?

### Location of Stations
Figure 1 shows the location of all monitoring wells with available temperature measurements in the study area. These wells are sampled for water quality parameters primarily. According to the [Hydrologisches Jahrbuch](https://www.aue.bs.ch/dam/jcr:872ee028-68e7-4d85-8fb9-2477be116423/Hydrologisches-Jahrbuch-2020-Grundwasserstand.pdf). Water levels and temperatures are recorded in many more stations and more frequently within the canton's limits. However, this data is not yet available publically.
""",

'eval': """## Methodology
This study uses a combination of statistical methods and visual inspection for classifying the temperature trends in each station. In the first step, all stations with less than 10 observations were discarded. Then the Mann-Kendall trend test estimator was calculated for each station. 
This test allows to determine whether a time series has a monotonic upward or downward trend. Time series diagrams were generated for each station, and a linear regression was conducted on the all-time series. 

### Mann-Kendall test
The Mann-Kendall test is a statistical hypothesis test, where the h0-hypothesis assumes that there is no trend in the data. The calculated estimator to accept or reject the hypothesis is based on the slopes that can be constructed between data points: if the number of positive slopes exceeds the number of negative slopes, a positive trend is likely. The test assumes that in a time series without trend, the nubmer of positive and negative slopes should be similar, if either positive or negative slopes clearly dominate, the hypothesis is rejected and therefore the alternative hypothesis of increasing or decreasing trend is accepted. Many variations exist for the Mann-Kendall test, introducing various corrections for seasonality, co-correlation, and others. We applied the original Mann-Kendall test and used the python package *pyMannKendall* ([Hussain et al., (2019)](https://joss.theoj.org/papers/10.21105/joss.01556)) to calculate the Mann-Kendall trend estimators.
""",

'tab':[
        """Table {}: Mann-Kendall results for all stations having a minimum of 10 temperature observations. The p-value reflects the probability for the given distribution of positive and negative slopes in the time series to represent a no trend. The lower p, the lower the probability of the given time series representing an increasing trend and, therefore, the higher the chance that the time series follows a positive trend.""",
        """Table {}: Linear regression results for all stations having a minimum of {} temperature observations. r-value= pearson-correlation coefficient: a values close to one indicate a high correlation, values close to zero a low correlation, intercept: y-axis intercept of the correlation line, slope: slope of line in °Cyear, 10yr prediction: extrapolation of correlation line to the date 10 years from today."""
    ],

"fig": [
        "Figure {}: Location of stations with available groundwater temperature observations. Use the cursor to discover the depth and mean temperature for these locations.",
        "Figure {}: Spatial distribution of positive, negative, and neutral groundwater temperature trends.",
        "Figure {}: Surface temperature in the study area.",
        "Figure {}: Comparison of yearly average temperatures at the surface with groundwater.",
        "Figure {}: Heatmap for average temperature values for all stations in the groundwater monitoring network with available temperature data. Stations are ordered by groundwater sampling depth, with shallow stations on the top of the chart. Hover the mouse cursor over a colored rectangle on the plot to show additional information for the respective year and station.",

    ],
'result': """## Results
### Statistical tests (Mann-Kendall)
Mann-Kendall tests have been performed on all stations having a minimum of 10 temperature observations. As shown in table 1, {0} stations comprised the requested number of observations, {1} were identified as having an increasing trend, and {2} had no significant trend. Among the stations having no trend, visual inspection reveals that the overall trend is generally increasing; however, the trend is not sufficiently strong to pass the Mann-Kendall test. This is also confirmed by the positive slope of the linear regression line. Only {3} stations were found to have a decreasing trend. Table 1 generates the corresponding time series diagrams when a station is marked using the mouse cursor.""",

'result_map': """### Spatial distribution
Figure 2 shows the spatial distribution of the different trend test results: *increasing* (orange), *decreasing* (blue), and *no trend* (gray). This map does not allow to delineate ares of a common trend pattern. The difference of trend and average temperature, that can be observed in neighbouring stations suggests that manmade processes may impact the natural groundwater. Further knowledge of the local groundwater flow system should be included in order to interpret the spatial distribution of temperature time series.
""",

'surface_temperature': """### Comparison to Surface Temperature
Groundwater infiltrates from the surface. In the absence of cooling or heating effects in the subsurface, groundwater temperature should closely reflect the temperature on the surface during infiltration, particularly in shallow systems. Figure 3 shows the yearly average of surface temperature at the Meteorologische Station Basel-Binningen ([Statistisches Amt des Kantons Basel-Stadt, Auswertungen zur Meteostatistik](https://www.statistik.bs.ch/zahlen/tabellen/2-raum-landschaft-umwelt.html)). The temperature curve seems to follow an increasing trend, which is confirmed by the Mann-Kendall test result (p=0.05) and the regression line. The temperature regression results in a yearly temperature increase of {:.2f}°C/year.
""",
'surface_temperature_compare_to_groundwater':"""Figure 4 compares annual mean temperatures of ground and surface water in a scatter plot. This representation shows, that groundwater temperatures are approximately 4 degrees warmer than the surface temperature. There is also a poor correlation between the two parameters. Note that the during the years 2010 to 2014 very few groundwater temperaturess were recorded and therefore these average values may not be very representative. This may explain the high groundwater value of 16°C for the year 2011. In addition, such a correlation may only be expected on a broad timescale and with a considerable time lag, since warmer oder cooler surface water requires a considerable time span to reach the water table.""",

'result_heatmap': """### Heatmap
Heatmaps are an efficient visual tool to detect patterns in data. For this study, the y-axis represents all stations and the x-axis with a resolution of one year per rectagle. For each rectangle, the average temperature for the year and station is calculated and a color is assigned to the rectagle representing the temperature value. It must be noted that stations with yearly averages, calculated based on few or even a single value may not represent the true yearly average correctly. This may explain some significant average temperature differences among nearby stations. Stations are ordered by their sampling depth with shallow sampling depths on the top, and deeper sampling depths at the bottom of the plot. The increasing trend is represented by a color change from yellow to blue, as can be observed in station F_1097, or F_1068. The color transition from blue to yellow from top to bottom suggests that the average temperature decreases from shallow towards deeper sampling locations. 

Overall, the heatmap allows to apreciate the data density, the five year monitoring interval as well as the data gap for most wells from 2010 to 2015. Station F_2614 shows an anomaly in two aspects: stations with a comparable sampling depth have generally a lower average temparature. In addition, this station is one of the few stations where a statistically significant negative trends is observed.
""",

'prediction': """### 10 Year Groundwater Temperature Prediction
A linear regression was conducted on all stations having a minimum number of {} temperature observations. Increasing trend rates are estimated using the intercept and slope of the linear regression. slopes range from {:.2f} to {:.2f} °C/yr with an average value of {:.2f} °C/yr. Extrapolating the linear trend over the next ten years therefore, may lead to a groundwater temperature rise of between {:.1f} and {:.1f} °C with an average of {:.1f} °C.
""",

'conclusion': """### Conclusion
This study has found that nearly half of all stations in the groundwater monitoring network of Basel show an significant increasing trend in temperature. Temperature increase per year varies between {:.2f} and {:.2f} °C/year, based on the linear regression. This is considerably higher than the observed surface temperature increase during the same period of {:.2f}°C/year. While the increasing trend may at least partly be explained by the equally increasing surface temperature, this does not explain why groundwater temperature should increase faster than the surface temperature. A natural explanation for the discrepancy in ground and surface water temperature may be explained by a gradual change in recharge dynamics. This change would require an increased reqcharge of warm summer rains or a decrease of recharge of colder winter precipitation. in an area of pronounced residential and industrial land use, artificial processes impacting subsurface temperatures such as underground constructions and heat pumps represent additional suspects for impacting the groundwater temperature. Both processes are, as of now, mere candidates to explain the observed temperature trend phenomenon. Additional data and research is required to confirm these hypotheses.
""",

'analysis_heatmap': """Heatmap of average yearly groundwater temperature. Stations are ordered by increasing sampling depth from shallow on the top- to
 deeper sampling depth towards the bottom part of the chart. Overall the wells are fairly shallow and range from {:,.1f} to {:,.1f} meters below ground surface. Note that some wells are sampled only once a year and average values reflect the temperature of the day the sampling occurred rather than the average for the year. Point your mouse cursor to a rectangle in the plot to see the the temperature value, depth and number of values used to generate the average value."""
}