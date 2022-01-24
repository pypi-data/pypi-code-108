# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality for consuming Azure Open Datasets as dataframes and for enriching customer data.

Azure Open Datasets are curated public datasets that you can use to add scenario-specific features to machine
learning solutions for more accurate models. You can convert these public datasets into Spark and pandas dataframes
with filters applied. For some datasets, you can use an enricher to join the public data with your data. For
example, you can join your data with weather data by longitude and latitude or zip code and time.

Included in Azure Open Datasets are public-domain data for weather,
census, holidays, public safety, and location that help you train machine learning models and enrich predictive
solutions. Open Datasets are in the cloud on Microsoft Azure and are integrated into Azure Machine Learning.
For more information about working with Azure Open Datasets, see [Create datasets with Azure Open
Datasets](https://docs.microsoft.com/azure/machine-learning/how-to-create-register-datasets#).

For general information about Azure Open Datasets, see [Azure Open Datasets
Documentation](https://docs.microsoft.com/azure/open-datasets/).
"""

from ._boston_safety import BostonSafety
from ._chicago_safety import ChicagoSafety
from ._diabetes import Diabetes
from ._mnist import MNIST
from ._noaa_gfs_weather import NoaaGfsWeather
from ._noaa_isd_weather import NoaaIsdWeather
from ._nyc_safety import NycSafety
from ._nyc_tlc_fhv import NycTlcFhv
from ._nyc_tlc_green import NycTlcGreen
from ._nyc_tlc_yellow import NycTlcYellow
from ._oj_sales_simulated import OjSalesSimulated
from ._public_holidays import PublicHolidays
from ._public_holidays_offline import PublicHolidaysOffline
from ._sanfrancisco_safety import SanFranciscoSafety
from ._seattle_safety import SeattleSafety
from ._us_labor_cpi import UsLaborCPI
from ._us_labor_ehe_national import UsLaborEHENational
from ._us_labor_ehe_state import UsLaborEHEState
from ._us_labor_laus import UsLaborLAUS
from ._us_labor_lfs import UsLaborLFS
from ._us_labor_ppi_commodity import UsLaborPPICommodity
from ._us_labor_ppi_industry import UsLaborPPIIndustry
from ._us_population_county import UsPopulationCounty
from ._us_population_zip import UsPopulationZip
from ._bing_covid_19_data import BingCOVID19Data
from ._covid_19_open_research import COVID19OpenResearch
from ._covid_tracking_project import COVIDTrackingProject
from ._ecdc_covid_19_cases import EcdcCOVIDCases

from ._city_safety import CitySafety
from ._no_parameter_open_dataset_base import NoParameterOpenDatasetBase
from ._nyc_taxi_base import NycTaxiBase
from ._sample_dataset_base import SampleDatasetBase


__all__ = [
    'BingCOVID19Data',
    'BostonSafety',
    'ChicagoSafety',
    "COVID19OpenResearch",
    "COVIDTrackingProject",
    'Diabetes',
    "EcdcCOVIDCases",
    'MNIST',
    'NoaaGfsWeather',
    'NoaaIsdWeather',
    'NycSafety',
    'NycTlcFhv',
    'NycTlcGreen',
    'NycTlcYellow',
    'OjSalesSimulated',
    'PublicHolidays',
    'PublicHolidaysOffline',
    'SanFranciscoSafety',
    'SeattleSafety',
    'UsPopulationCounty',
    'UsPopulationZip',
    'UsLaborCPI',
    'UsLaborEHENational',
    'UsLaborEHEState',
    'UsLaborLAUS',
    'UsLaborPPICommodity',
    'UsLaborPPIIndustry',
    'UsLaborLFS',
    # Below are classes that were not intended to be exposed, but doc generation fails without them
    'CitySafety',
    'NoParameterOpenDatasetBase',
    'NycTaxiBase',
    'SampleDatasetBase'
]
