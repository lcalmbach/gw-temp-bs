texts = {
'intro': """## Groundwater temperature trend since 1993 in Basel (Switzerland)

Groundwater temperature remains generally stable over the seasons as opposed to surface water. Todate, an overall increase in groundwater temperature 
can be observed across Switzerland ([bafu.admin.ch](https://www.bafu.admin.ch/bafu/en/home/topics/water/info-specialists/state-of-waterbodiestate-of-groundwater/groundwater-temperature.html)). This study attempts to characterize the temperature trend in the groundwater of the canton of Basel (northern Switzerland) where 30 years of groundwater monitoring data has been published on the Opendata portal [data.bs](https://data.bs.ch/explore/dataset/100067). The article attempts to answer the following questions:
- Is the groundwater temperature generally rising?
- Is there a link between groundwater depth and the extent of temperature increase? 
- What groundwater temperatures can be expected in ten years?

### Location of wells
Figure 1 shows the location for all monitoring wells with available temperature measurements. Accourding to the [Hydrologisches Jahrbuch](https://www.aue.bs.ch/dam/jcr:872ee028-68e7-4d85-8fb9-2477be116423/Hydrologisches-Jahrbuch-2020-Grundwasserstand.pdf)
waterlevels and temperatures are measured in many more stations over the canton's area. However, this data is not yet available publically.
""",

'eval': """## Methodology
This study uses a combination of stastistical methods and visual inspection for classifying the temperature trends in each station. In a first step, all stations with less than 10 observations were discarded. Then the Mann Kendall trend test estimator was calculated for each station. Time series diagrams were generated for each station and a linear regression conducted on all time series. 

### Mann-Kendall test
The Mann Kendall test is a statistical hypthesis test, where the H0-hypothesis is: There is no trend in the data. The calculated estimator is based on the slopes that can be constructed between the data points: if the number of positive slopes exeed by far the number of negative slopes, a positive trend is likely. The higher the reatio psoitive to negative, the more likely the trend. The Mann-Kendall quantifies  the probability of a certain number of positive slopes to occur in a time series with no trend. A threshold can them be defined for an acceptable probablity outccome. If the chance to reach a given ratio of positive and negative slopes in a dataset is less than for example 5%, we may reject the H0-hypothesis and assume that the trend for this dataset is increasing. Many variations exist for the Mann-Kendall test, introducing various corrections for seasonality, co-correlation and others. We applied the original Mann-Kendall test and used the python package *pyMannKendall* ([Hussain et al., (2019)](https://joss.theoj.org/papers/10.21105/joss.01556)) to calculate the Mann-Kendall trend estimators.
""",

"fig1": "Figure 1: Location of stations with available groundwater temperature observations. Use the cursor to see the depth and mean temperature for these locations.",

'result': """## Results
### Statistical tests (Mann-Kendall)
Mann-Kendall tests have been performed on all stations having  a minimum of 10 temperature observations. As Shown in Table 1, {0} stations comprised the requested number of observations, {1} were identified as having an increasing trend and {2} had no significant trend. Among the stations having no trend, visual inspection reveals, that the overall trend is generally increasing, however the trend is not sufficiently string to pass the Mann Kendall test. This si also confirmed by the positive slope of the linear regression line. Only {3} stations were found to have a decreasing trend. Table 1 generates the correpsonding time series diagrams when a station is marked using the mouse cursor.""",

'tab1':"""Table 1: Mann Kendall results for all stations having a minimum of 10 temperature observations. The p-value reflects the probability for the given distribution of positive and negative slopes in the time series to represent a no trend. The lower p, the lower the probability of the given time series representing an increasing trend and, therefore, the higher the chance that the time series follows a positive trend.""",

'result_map': """### Spatial distribution
Figure 2 shows the spatial distribution of the different trend test results: *increasing* (orange), *decreasing* (blue), and *no trend* (gray). This map does not allow to distinguish areas of clear common trend. Further knowledge of the local groundwater flow system should be included, in order to interpret the spatial distribution of temperature trends.
""",

'fig2': """Figure 2: Spatial distribution of positive, negative, and neutral groundwater temperature trends.""",

'result_heatmap': """### Heatmap
Heatmaps are an efficient visual tool to detect patterns in data. For this study, the y axis represents all stations and the x-axis with a resolution of one year per rectagle. For each rectangle, the average temperature for the speciic year nd station is calculated. Since the average values are based on a varying number of observations, the average temperature may not alwaystruly represent the true average temperature for this station. Stations with yearly averages calculated only on few or even a single value may not represent the true yearly average correctly. In addition, stations are ordered by their sampling depth with shallow sampling depths on the top, and deeper sampling depths at the bottom of the plot. The increasing trend is represented on a color change from yellow to blue, as can be observed in station F_1097, or F_1068. The color transition from blue to yellow from top to bottom reflects the average temperature decrease towards deeper sampling locations. Overall, the heatmap allows to apreciate the data density, the five year monitoring interval as well as the data gap for most wells from 2010 to 2015. Station F_2614 shows an anomaly in two aspects: stations with a comparable sampling depth have generally a lower average temparature. In addition, this station is one of the few stations where a statistically significant negative trends is observed.
""",

'fig3': """Figure 3: Heatmap for average temperature values for all stations in the groundwater monitoring network with availabe temperature data. Stations are ordered by groundwater sampling depth, with shallow stations on the top of the chart. The mouse cursor may by used to show additional information when moving over a colored rectangle on the plot.""",

'prediction': """### 10 Year Temperature Prediction
A linear regression was conducted on all stations having a minimum number of {} temperature observations. Increasing trend rates are estimated using the intercept and slope of the linear regression. slopes range from {:.2f} to {:.2f} °C/yr with an average value of {:.2f} °C/yr. Extrapolating the linear trend over the next 10 years therefore may lead to a groundwater temperature rise of between {:.1f} and {:.1f} °C with an average of {:.1f} °C.
""",

'conclusion': """### Conclusion
This study has found, that nearly half of all stations in the in groundwater monitoring network of Basel show a increasing trend for temperature. Visual inspection of the most of wells where the statistical tests does not reject the hyposthesis of no trend, still show a positive regression. Temperature increase per year is between 1 and 3 degrees, based on the linear regression.   
""",

'analysis_heatmap': """Heatmap of average yearly groundwater temperature. Stations are ordered by increasing sampling depth from shallow on the top- to
 deeper sampling depth towards the bottom part of the chart. Overall the wells are fairly shallow and range from {:,.1f} to {:,.1f} meters below ground surface. Note that some wells are sampled only once a year and average values reflect the temperature of the day the sampling occurred rather than the average for the year. Point your mouse cursor to a rectabgle in the plot to see the the temperature value, depth and number of values used to generate the average."""
}