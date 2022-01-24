# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""NOAA ISD weather."""

from datetime import datetime
from typing import List, Optional

from dateutil import parser
from pyspark.sql.functions import col, udf

from .accessories.location_data import LocationData
from .accessories.open_dataset_base import OpenDatasetBase
from .accessories.time_data import TimeData
from .dataaccess._blob_accessor import BlobAccessorDescriptor
from .enrichers.common_weather_enricher import CommonWeatherEnricher
from .environ import RuntimeEnv, SparkEnv


class NoaaIsdWeather(OpenDatasetBase, LocationData, TimeData):
    """Represents the  National Oceanic and Atmospheric Administration (NOAA) Integrated Surface Dataset (ISD).

    This dataset contains worldwide hourly weather history data (example: temperature, precipitation, wind)
    sourced from the National Oceanic and Atmospheric Administration (NOAA).
    For more information about this dataset, including column descriptions, different ways to access the dataset,
    and examples, see `NOAA Integrated Surface Data <https://azure.microsoft.com/services/open-datasets/
    catalog/noaa-integrated-surface-data/>`_ in the Microsoft Azure Open Datasets catalog.

    .. remarks::

        The example below shows how to use access the dataset.

        .. code-block:: python

            from azureml.opendatasets import NoaaIsdWeather
            from datetime import datetime
            from dateutil.relativedelta import relativedelta


            end_date = datetime.today()
            start_date = datetime.today() - relativedelta(months=1)
            isd = NoaaIsdWeather(start_date=start_date, end_date=end_date)
            isd_df = isd.to_pandas_dataframe()

    :param start_date: The date at which to start loading data, inclusive. If None, the ``default_start_date``
        is used.
    :type start_date: datetime
    :param end_date: The date at which to end loading data, inclusive. If None, the ``default_end_date``
        is used.
    :type end_date: datetime
    :param cols: A list of columns names to load from the dataset. If None, all columns are loaded. For
        information on the available columns in this dataset, see `NOAA Integrated Surface
        Data <https://azure.microsoft.com/services/open-datasets/catalog/noaa-integrated-surface-data/>`__.
    :type cols: builtin.list[str]
    :param enable_telemetry: Whether to enable telemetry on this dataset.
        If not specified, telemetry is enabled.
    :type enable_telemetry: bool
    """

    default_start_date = parser.parse('2008-01-01')
    default_end_date = datetime.today().replace(
        hour=0, minute=0, second=0, microsecond=0)

    latitude_column_name = 'latitude'
    longitude_column_name = 'longitude'
    usaf_column_name = 'usaf'
    wban_column_name = 'wban'
    id_column_name = 'ID'

    _blob_accessor = BlobAccessorDescriptor(
        "isd", [latitude_column_name, longitude_column_name, usaf_column_name, wban_column_name])

    def __init__(
            self,
            start_date: datetime = default_start_date,
            end_date: datetime = default_end_date,
            cols: Optional[List[str]] = None,
            enable_telemetry: bool = True):
        """
        Initialize filtering fields.

        :param start_date: The start date you'd like to query inclusively.
        :type start_date: datetime
        :param end_date: The end date you'd like to query inclusively.
        :type end_date: datetime
        :param cols: A list of column names you'd like to retrieve. None will get all columns.
        :type cols: List[str]
        :param enable_telemetry: Indicates whether to enable telemetry, disabled for UT only.
        :type enable_telemetry: bool
        """
        super(NoaaIsdWeather, self).__init__(
            cols,
            enable_telemetry,
            start_date=start_date,
            end_date=end_date
        )

    def filter(self, env: RuntimeEnv, min_date: datetime, max_date: datetime):
        """Filter time.

        :param env: The runtime environment.
        :type env: azureml.opendatasets.RuntimeEnv
        :param min_date: The min date.
        :type min_data: datetime
        :param max_date: The max date.
        :type max_date: datetime

        :return: filtered data frame.
        """
        self.env = env
        ds = self._filter_time(env, min_date, max_date)
        if isinstance(env, SparkEnv):
            self.data = self.data.na.drop(how='all', subset=self.cols).na.drop(
                how='any', subset=[self.longitude_column_name, self.latitude_column_name])
            # create unique id for weather stations, hardcoded due to id issue in weather dataset
            unique_id_udf = udf(lambda x, y: '-'.join([x, y]))
            self.data = self.data.withColumn(
                self.id_column_name,
                unique_id_udf(col(self.latitude_column_name), col(self.longitude_column_name)))
            if self.cols:
                return ds.select(self.cols + [self.id_column_name])
            return ds
        else:
            ds = ds.dropna(how='all', axis=0, subset=self.cols).dropna(
                how='any', axis=0, subset=[self.longitude_column_name, self.latitude_column_name])
            # create unique id for weather stations, hardcoded due to id issue in weather dataset
            ds[self.id_column_name] = ds[self.latitude_column_name].map(str) + \
                '-' + ds[self.longitude_column_name].map(str)
            if self.cols:
                return ds[self.cols + [self.id_column_name]]
            return ds

    def _get_enricher(self, activity_logger):
        """Get enricher object.

        :param activity_logger: activity logger

        :return: enricher object
        """
        return CommonWeatherEnricher(self, enable_telemetry=self._enable_telemetry)
