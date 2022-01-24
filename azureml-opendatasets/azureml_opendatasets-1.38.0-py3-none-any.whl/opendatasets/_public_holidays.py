# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Public holiday."""

from datetime import datetime
from typing import List, Optional, Union

from dateutil import parser

from .accessories.open_dataset_base import OpenDatasetBase
from .dataaccess._blob_accessor import BlobAccessorDescriptor
from .enrichers.holiday_enricher import HolidayEnricher
from .environ import PandasEnv, SparkEnv


class PublicHolidays(OpenDatasetBase):
    """Represents the Public Holidays public dataset.

    This datasets contains worldwide public holiday data sourced from PyPI holidays package and Wikipedia,
    covering 38 countries or regions from 1970 to 2099. Each row indicates the holiday info for a specific
    date, country or region, and whether most people have paid time off. For more information about this dataset,
    including column descriptions, different ways to access the dataset, and examples, see `Public
    Holidays <https://azure.microsoft.com/services/open-datasets/catalog/public-holidays/>`_ in the
    Microsoft Azure Open Datasets catalog.

    .. remarks::

        The example below shows how to access the dataset.

        .. code-block:: python

            from azureml.opendatasets import PublicHolidays
            from datetime import datetime
            from dateutil.relativedelta import relativedelta


            end_date = datetime.today()
            start_date = datetime.today() - relativedelta(months=1)
            hol = PublicHolidays(start_date=start_date, end_date=end_date)
            hol_df = hol.to_pandas_dataframe()

    :param country_or_region: The country or region to return data for.
    :type country_or_region: str
    :param start_date: The date at which to start loading data, inclusive. If None, the ``default_start_date``
        is used.
    :type start_date: datetime
    :param end_date: The date at which to end loading data, inclusive. If None, the ``default_end_date``
        is used.
    :type end_date: datetime
    :param cols: A list of columns names to load from the dataset. If None, all columns are loaded. For
        information on the available columns in this dataset, see `Public
        Holidays <https://azure.microsoft.com/services/open-datasets/catalog/public-holidays/>`_.
    :type cols: builtin.list[str]
    :param enable_telemetry: Whether to enable telemetry on this dataset.
    :type enable_telemetry: bool
    """

    default_start_date = parser.parse('2008-01-01')
    default_end_date = datetime.today().replace(
        hour=0, minute=0, second=0, microsecond=0)
    default_max_end_date = parser.parse('2099-01-01')

    countrycode_column_name = 'countryRegionCode'
    country_or_region_column_name = 'countryOrRegion'

    _blob_accessor = BlobAccessorDescriptor(
        "public_holiday", [country_or_region_column_name,
                           countrycode_column_name])

    def __init__(
            self,
            country_or_region: str = '',
            start_date: datetime = default_start_date,
            end_date: datetime = default_end_date,
            cols: Optional[List[str]] = None,
            enable_telemetry: bool = True):
        """
        Initialize filtering fields.

        :param country_or_region: The country or region you'd like to query against.
        :type country_or_region: str
        :param start_date: The start date you'd like to query inclusively.
        :type start_date: datetime
        :param end_date: The end date you'd like to query inclusively.
        :type end_date: datetime
        :param cols: A list of column names you'd like to retrieve. None will get all columns.
        :type cols: Optional[List[str]]
        :param enable_telemetry: Indicates whether to send telemetry.
        :type enable_telemetry: bool
        """
        super(PublicHolidays, self).__init__(
            cols,
            enable_telemetry,
            start_date=start_date,
            end_date=end_date,
            countryRegionCode=country_or_region
        )

    def filter(self, env: Union[SparkEnv, PandasEnv], min_date: datetime, max_date: datetime):
        """Filter time.

        :param env: The runtime environment.
        :type env: RuntimeEnv
        :param min_date: The min date.
        :type min_date: datetime
        :param max_date: The max date.
        :type min_date: datetime

        :return: The filtered data frame.
        """
        self.env = env
        ds = self._filter_time(env, min_date, max_date)
        if isinstance(env, SparkEnv):
            ds = ds.na.drop(how='all', subset=self.cols).na.drop(
                how='any', subset=[self.time_column_name])
        else:
            ds = ds.dropna(how='all', axis=0, subset=self.cols).dropna(
                how='any', axis=0, subset=[self.time_column_name])
        return ds

    def _get_enricher(self, activity_logger):
        """Get enricher object."""
        return HolidayEnricher(self, enable_telemetry=self.enable_telemetry)
