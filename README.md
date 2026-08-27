## Data for Reserve Bank of Australia (RBA) economic modelling

The RBA requires climate data out to 2100 relating to heatwaves, droughts, bushfires, storms and floods.

### Metrics

The following metrics were selected:
- *Warm Spell Duration Index (WSDI)*:
  This heatwave indicator represents the number of days in a sequence of at least six consecutive days
  during which the value of the daily maximum temperature (tasmax)
  is greater than the 90th percentile of tasmax calculated for a five-day window centered on each calendar day,
  using all data for the given calendar daypentad from the data period for a reference climate (1950-2014). 
- *Standardised Precipitation Evapotranspiration Index (SPEI)*:
  This drought indicator is a measure of the integrated water deficit in a location,
  taking into account the contributions of both precipitation (pr) and temperature dependent evapotranspiration.
  The water deficit values are "standardised" (i.e. transformed to a normal distribution) when calculating the SPEI,
  such that SPEI values represent standard deviations. 
  The integration period for this production is 12 months (i.e. the SPEI-12).
- *Forest Fire Danger Index (FFDI)*:
  This indicator of the potential danger of a forest fire
  is based on the weather conditions only
  (temperature, rainfall deficit, humidity and wind speed).
  We calculate the maximum daily FFDI value for the year (FFDIx)
  and the number of days per year above the 99th percentile (FFDIgt99p)
  of the reference period (1950-2014).
- *Wettest day of the year (Rx1day)*:
  The wettest day of the year (in mm of rain) was used as a very simple proxy for storms.

The WSDI and SPEI were partly selected because they are also available from the
[Climate Data Knowledge Portal](https://climateknowledgeportal.worldbank.org/country/australia/climate-data-projections),
which allows for comparisons against other countries.

### CMIP6 models

In order to calculate empirical likelihoods and how they are changing over time,
large model ensembles were required.
In other words, it was preferable to use data from CMIP6 climate models that performed
multiple simulations (i.e. multiple ensemble members) for each future emission scenario.

For the WSDI (which requires tasmax data),
SPEI (tasmax, tasmin and pr) and Rx1day (pr) indices
we selected all CMIP6 models that archived daily data for at least five common runs
across the ssp126, ssp245, ssp370 and ssp585 future emissions scenarios:
- *EC-Earth3 (57 runs)*
- CanESM (50)
- ACCESS-ESM1-5 (40)
- MPI-ESM1-2-LR (10)
- ACCESS-CM2 (10)
- IPSL-CM6A-LR (6)
- UK-ESM1-0-LL (5)
- *EC-Earth3-Veg (5)*

*Note: The EC-Earth and EC-Earth-Veg replica datasets on [NCI](https://dx.doi.org/10.25914/Q1CT-RM13) are not complete for the required variables.
We are going to submit a data download request to rectify this, but in the meantime those models have not been processed.*

For the FFDI (which requires pr, tasmax, hursmin, sfcWindmax),
there is only one model that archived the required daily variables for at least five runs:
- ACCESS-ESM1-5 (40)

### Spatial aggregation

Each metric is calculated on the native grid of the climate model.
For state and national values, a weighted mean is then calculated
where the weight for each grid cell is the area of the cell multiplied
by the fraction of the cell that overlaps
with the geopgraphic shape (e.g. state) of interest. 
See [development/wsdi_cmip6.ipynb](https://github.com/AusClimateService/rba/blob/master/development/wsdi_cmip6.ipynb)
for an illustrated example.

For spatial aggregation of FFDI values,
grid points in arid climate zones were excluded since the FFDI isn't as appropriate / relevant in those zones.
See [development/koppen_climate_zones.ipynb](https://github.com/AusClimateService/rba/blob/master/development/koppen_climate_zones.ipynb)
and [development/ffdi-cmip6.ipynb](https://github.com/AusClimateService/rba/blob/master/development/ffdi-cmip6.ipynb) for details.

For the WSDI and Rx1day, we also include values for each captial city,
which simply represent the model grid point closest to the GPO of that city.

It's important to note that spatial aggregation can distort the meaning of the absolute values of some metrics.
For instance, while an FFDI value of >100 at a point location is indicative of severe fire weather,
this is not true of a state or national average (these aggregated values tend to be lower).
Similarly, while an SPEI value of -2 at a point location is two standard deviations from the mean,
that's not true when averaged over many grid points (again, the aggregated values tend to be lower).

See [example_data/wsdi_yr_ACCESS-CM2_ssp245_ensemble_aus-states-cities_1850-2100.csv](https://github.com/AusClimateService/rba/blob/master/example_data/wsdi_yr_ACCESS-CM2_ssp245_ensemble_aus-states-cities_1850-2100.csv)
for an example of a data file at the end of the spatial aggregation step.
A visualisation of those data can also be seen in the scatterplots in
[wsdi-analysis.ipynb](https://github.com/AusClimateService/rba/blob/master/wsdi-analysis.ipynb),
[spei-analysis.ipynb](https://github.com/AusClimateService/rba/blob/master/spei-analysis.ipynb),
[ffdigt99p-analysis.ipynb](https://github.com/AusClimateService/rba/blob/master/ffdigt99p-analysis.ipynb), and
[rx1day-analysis.ipynb](https://github.com/AusClimateService/rba/blob/master/rx1day-analysis.ipynb).

A data file from the [BARRA-R2](https://www.bom.gov.au/government-and-industry/research-and-development/research-and-development-projects/atmospheric-reanalysis)
"observational" dataset is also included for each metric for reference
(e.g. [example_data/wsdi_yr_BARRA-R2_aus-states-cities_1980-2024.csv](https://github.com/AusClimateService/rba/blob/master/example_data/wsdi_yr_BARRA-R2_aus-states-cities_1980-2024.csv)).

### Likelihood calculation

Once the spatial aggregation is complete,
we calculate the likelihood of exceeding a series of percentiles calculated over the 1950-2014 period
(that period was selected to match the
[Climate Data Knowledge Portal](https://climateknowledgeportal.worldbank.org/country/australia/climate-data-projections)).
A likelihood is calculated for every year from 1860-2091,
using a 20-year sliding window centered on those years.
For instance, the ACCESS-CM2 model performed 10 runs of the SSP3-7.0 experiment.
The likelihood of exceeding the reference (1950-2014) 98th percentile in the year 2050
for that model under that emission scenario
is calculated empirically as the fraction of all 200 values across all runs from 2040-2059
that exceed that 98th percentile threshold.

This process is repeated for all years and for a dozen percentile thresholds:

-  Likelihood of exceeding the 90, 91, 92, 93, 94, 95, 96, 96.7, 97, 97.5, 98 and 99 percentile for WSDI, FFDIgt99p and Rx1day
-  Likelihood of not exceeding the 10, 9, 8, 7, 6, 5, 4, 3.3, 3, 2.5, 2 and 1 percentile for the SPEI 

See [example_data/wsdi_yr_98-0p-likelihood_ACCESS-CM2_ssp245_aus-states-cities_1860-2091.csv](https://github.com/AusClimateService/rba/blob/master/example_data/wsdi_yr_98-0p-likelihood_ACCESS-CM2_ssp245_aus-states-cities_1860-2091.csv) for an example of a likelihood data file.
We also archive a data file showing the threshold values for each percentile
(e.g. [example_data/wsdi_yr_percentiles_ACCESS-CM2_ssp245_aus-states-cities_1950-2014.csv](https://github.com/AusClimateService/rba/blob/master/example_data/wsdi_yr_percentiles_ACCESS-CM2_ssp245_aus-states-cities_1950-2014.csv)).

A visualisation of the likelihood data can also be seen in the line graphs in
[wsdi-analysis.ipynb](https://github.com/AusClimateService/rba/blob/master/wsdi-analysis.ipynb),
[spei-analysis.ipynb](https://github.com/AusClimateService/rba/blob/master/spei-analysis.ipynb),
[ffdigt99p-analysis.ipynb](https://github.com/AusClimateService/rba/blob/master/ffdigt99p-analysis.ipynb) and
[rx1day-analysis.ipynb](https://github.com/AusClimateService/rba/blob/master/rx1day-analysis.ipynb).

### Computation

To generate the data submit a job:

```
qsub -v metric=wsdi,model=MPI-ESM1-2-LR,ssp=ssp370,run=r25i1p1f1,grid=gn,version='v*' cmip6.job
```

The csv files from numerous runs can then be merged using `concat_csv.py`
and likelihoods calculated using `likelihoods.py`.

Don't forget to clean up afterwards (i.e. delete all files except the final csv files):

```
bash wsdi_cmip6.sh MPI-ESM1-2-LR ssp370 r25i1p1f1 gn 'v*' -c 
```

(The data generation and clean up steps can be achived by running `run.sh`.)
