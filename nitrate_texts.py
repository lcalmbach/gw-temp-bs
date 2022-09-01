texts = {
'intro': """## Nitrate concentrations in groundwater of Basel since {0} 


Groundwater usually contains less than 1 milligram of nitrate-nitrogen per liter. Significantly higher nitrate concentrations indicate that the drinking water has been contaminated and may pose a severe health concern. The Swiss [Waters Protection Ordinance](https://www.fedlex.admin.ch/eli/cc/1998/2863_2863_2863/de)(WPO) sets the limit for surface water to 5.6 mg/L for nitrate as N (corresponds to 25 mg/L nitrates as NO3). Common sources of nitrate pollution include nitrogen fertilizers, manure, septic systems, and sewage treatment practices. 

This study analyzes temporal and spatial trends in nitrate concentrations in the groundwater of Basel.

###  Station Locations and data
The Office for environmental protection of Basel-Stadt (AUE) has published groundwater quality monitoring data since {0} on the Open Government Data portal [data.bs](https://data.bs.ch/explore/dataset/100179). Figure 1 shows {1} locations of monitoring stations where historical and recent nitrate values are available. Of these, {2} have observations in the last five years and participate in the current monitoring program.
""",

'yearly_stats': """### Statistics of Nitrate
#### Yearly Statistics for all Wells
Table {} and figure {} show the yearly statistics of nitrate concentrations and the number and percentage of samples exceeding the guideline level of 5.6 mg/L. Mean and maximum values and the number of exceedances are significantly higher at the beginning of the observation period than in more recent years. The highest percentage of exceedances ({} mg/L) occurred in {}. The lowest percentage ({} mg/L) was observed in {}. Until 2001, the average concentration of nitrate often exceeded the guideline value. After 2001, the yearly average nitrate concentration was always lower than the guideline value. 
""",

'well_stats': """#### Statistics per Well
Table {} shows the statistics of nitrate concentrations per well. The percentage of exceedances varies strongly depending on the number of samples analyzed at the respective locations. Even among stations with a long time series, the exceedance percentage may be as low as 0%, e.g., in stations 1064 and 432 or as high as 75% in station 1026. The highest nitrate value of {} mg/L was measured in station {}. Station {} has the highest mean concentration ({} mg/L) among stations with at least 20 years of data. Some stations have higher average values, but the high value is mostly related to few and high measurements, and the high average tendency needs to be confirmed by future analysis.
""",

'spatial_distribution': """#### Spatial Distribution
Figure {} shows the spatial distribution of stations with exceedances (red dots). The slider above the figure allows stepping through different years of data. At the beginning of the monitoring, exceedances are common in the canton's western, southern, and northeastern parts. Starting from 2005, exceedances are less common and limited to the western and southern areas. The wells scattered around the axis from Badischer Bahnhof to Riehen have consistently shifted from exceedance to compliance in recent years. 
""",

"time_series": """#### Temporal development
Figure {}, showing the trend of nitrate in the wells where most exceedances were encountered, confirms the gradual decrease of nitrate concentration in these wells. Of the five wells, the most recent monitoring event shows that three are below the guideline limit, one is slightly exceeding, and only well 1305 clearly exceeds the guideline limit. In 1999 there was a sharp drop in nitrate concentrations in three of the five wells, which may indicate a laboratory or sampling error rather than an actual drop in concentration. A common mistake causing sudden concentration changes in nitrate time-series is concentration conversion: nitrate analyses can be reported as N or NO3. If a nitrate as NO3 concentration is later added to a time series with nitrate as N, its value is 4.4 times higher than its Nitrate as N value. If such values are combined in a time series, the nitrate as NO3 value will cause a peak. Samples from 31.5.2021 seem to be originally reported as N. However, a NO3 to N conversion factor was likely incorrectly applied to them again, causing the observed drop. This phenomenon deserves further analysis as this effect happens in many wells simultaneously on the same date.
""",

'conclusion': """### Conclusion
Data from the {} years of water quality monitoring in {} wells show that the frequency of nitrate guideline level exceedance ({} mg/L) has decreased. The few wells still showing occasional exceedances are limited to the western and southern parts of the canton. The aquifer below the densely populated area of Basel is shallow and unconfined and, therefore, vulnerable to pollution. In this setting, the low nitrate values should be considered a sign of excellent and effective water protection measures. Continued monitoring will show if the high groundwater quality can be maintained. Also, we will examine other pollutants included in the groundwater quality dataset in further interactive articles.

### Further information
- [Umweltbericht beider Basel- Nitrat im Grundwasser](https://www.umweltberichtbeiderbasel.bs.ch/indikatoren/indikatoren-uebersicht/16-wasser/nitrat-im-grundwasser.html)
- [Nitrate in groundwater (admin.ch)](https://www.bafu.admin.ch/bafu/de/home/themen/wasser/fachinformationen/zustand-der-gewaesser/zustand-des-grundwassers/grundwasser-qualitaet/nitrat-im-grundwasser.html/)
""",
'tab':[
        """Table {}: Guideline exceedances and mean trend over the past {} years""",

        """Table {}: Statistics of nitrate concentrations and exceedances  (guideline=5.6 mg/L) of all water quality monitoring wells with nitrate values. """,

        """Table {}: Spatial distribution of nitrate exceedances"""
    ],

"fig": [
        "Figure {}: Location of water quality monitoring wells where nitrate concentration values are available",
        "Figure {}: Percentage of measured Nitrate concentrations exceeding the guideline level for surface water of 5.6 mg/L (left) and mean average concentrations for nitrate over time (right",
        "Figure {}: Spatial distribution of maximum nitrate concentrations for the year selected by the slider above the graph. Red markers indicate exceedances, and green markers analysis results below the guideline level.",
        "Figure {}: Time series of stations having a initial high concentration. You may add additional wells to the chart or remove existing wells using the multiselectbox above the plot.",
    ]
}