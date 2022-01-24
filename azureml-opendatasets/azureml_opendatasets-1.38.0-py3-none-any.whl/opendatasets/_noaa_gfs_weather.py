# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""NOAA GFS weather."""

from datetime import datetime
from typing import List, Optional

from dateutil import parser
from pyspark.sql.functions import col, udf

from .accessories.open_dataset_base import OpenDatasetBase
from .dataaccess._blob_accessor import BlobAccessorDescriptor
from .environ import RuntimeEnv, SparkEnv


class NoaaGfsWeather(OpenDatasetBase):
    """Represents the National Oceanic and Atmospheric Administration (NOAA) Global Forecast System (GFS) dataset.

    This dataset contains 15-day US hourly weather forecast data (example: temperature, precipitation, wind)
    produced by the Global Forecast System (GFS) from the National Oceanic and Atmospheric Administration (NOAA).
    For information about this dataset, including column descriptions, different ways to access the dataset, and
    examples, see `NOAA Global Forecast System <https://azure.microsoft.com/services/open-datasets/catalog/
    noaa-global-forecast-system/>`_ in the Microsoft Azure Open Datasets catalog.

    .. remarks::

        The example below shows how to use access the dataset.

        .. code-block:: python

            from azureml.opendatasets import NoaaGfsWeather
            from datetime import datetime
            from dateutil.relativedelta import relativedelta


            end_date = datetime.today()
            start_date = datetime.today() - relativedelta(months=1)
            gfs = NoaaGfsWeather(start_date=start_date, end_date=end_date)
            gfs_df = gfs.to_pandas_dataframe()

    :param start_date: The date at which to start loading data, inclusive. If None, the ``default_start_date``
        is used.
    :type start_date: datetime
    :param end_date: The date at which to end loading data, inclusive. If None, the ``default_end_date``
        is used.
    :type end_date: datetime
    :param cols: A list of columns names to load from the dataset. If None, all columns are loaded. For
        information on the available columns in this dataset, see `NOAA Global Forecast
        System <https://azure.microsoft.com/services/open-datasets/catalog/noaa-global-forecast-system/>`__.
    :type cols: builtin.list[str]
    :param limit: A value indicating the number of days of data to load with ``to_pandas_dataframe()``.
        If not specified, the default of -1 means no limit on days loaded.
    :type limit: int
    :param enable_telemetry: Whether to enable telemetry on this dataset.
    :type enable_telemetry: bool
    """

    default_start_date = parser.parse('2018-01-01')
    default_end_date = datetime.today().replace(
        hour=0, minute=0, second=0, microsecond=0)

    latitude_column_name = 'latitude'
    longitude_column_name = 'longitude'
    id_column_name = 'ID'

    _blob_accessor = BlobAccessorDescriptor(
        "gfs", [latitude_column_name, longitude_column_name])

    def __init__(
            self,
            start_date: datetime = default_start_date,
            end_date: datetime = default_start_date,
            cols: Optional[List[str]] = None,
            limit: Optional[int] = -1,
            enable_telemetry: bool = True):
        """
        Initialize filtering fields.

        :param start_date: The start date you'd like to query inclusively.
        :type start_date: datetime
        :param end_date: The end date you'd like to query inclusively.
        :type end_date: datetime
        :param cols: A list of column names you'd like to retrieve. None will get all columns.
        :type cols: List[str]
        :param limit: to_pandas_dataframe() will load only "limit" days of data. -1 means no limit.
        :type limit: int
        :param enable_telemetry: Indicates whether to send telemetry.
        :type enable_telemetry: bool
        """
        super(NoaaGfsWeather, self).__init__(
            cols,
            enable_telemetry,
            start_date=start_date,
            end_date=end_date,
            limit=limit
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
        ds = self._filter_time(env, min_date, max_date)
        if isinstance(env, SparkEnv):
            ds = self.data.na.drop(how='all', subset=self.cols).na.drop(
                how='any', subset=[self.longitude_column_name, self.latitude_column_name])
            # create unique id for weather stations, hardcoded due to id issue in weather dataset
            unique_id_udf = udf(lambda x, y: '-'.join([x, y]))
            ds = ds.withColumn(
                self.id_column_name,
                unique_id_udf(col(self.latitude_column_name), col(self.longitude_column_name)))
            return ds
        else:
            ds = ds.dropna(how='all', axis=0, subset=self.cols).dropna(
                how='any', axis=0, subset=[self.longitude_column_name, self.latitude_column_name])
            # create unique id for weather stations, hardcoded due to id issue in weather dataset
            ds[self.id_column_name] = ds[self.latitude_column_name] + \
                '-' + ds[self.longitude_column_name]
            return ds
