# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality for representing time data and related operations in opendatasets."""

from datetime import datetime
from time import mktime, struct_time
from typing import Union

import numpy as np
from dateutil import parser
from pandas import DataFrame as PdDataFrame
from pyspark.sql.dataframe import DataFrame as SparkDataFrame
from pyspark.sql.functions import col, max, min, udf
from pyspark.sql.types import TimestampType

from .._utils.random_utils import random_tag
from ..environ import PandasEnv, SparkEnv
from .customer_data import CustomerData
from .public_data import PublicData


def find_min_max_date(dataset: Union[SparkDataFrame, PdDataFrame], time_col_name: str):
    """Find min and max date from a SPARK dataframe."""
    if isinstance(dataset, SparkDataFrame):
        min_date = dataset.select(min(time_col_name)).collect()[0][0]
        max_date = dataset.select(max(time_col_name)).collect()[0][0]
        return (min_date, max_date)
    else:
        return dataset[time_col_name].min().tz_localize(None).to_pydatetime(),\
            dataset[time_col_name].max().tz_localize(None).to_pydatetime()


def add_datetime_col(dataset: Union[SparkDataFrame, PdDataFrame], time_col_name: str, time_func: object):
    """Add rounded datetime column."""
    datetime_col = 'datetime' + random_tag()
    if isinstance(dataset, SparkDataFrame):
        dataset = dataset.withColumn(datetime_col, time_func(time_col_name))
        return (datetime_col, dataset, [datetime_col])
    else:
        dataset[datetime_col] = dataset[time_col_name].apply(time_func)
        return (datetime_col, dataset, [datetime_col])


def spark_parse_time(time_string):
    """Parse time string and catch exception.

    :param time_string: The time string to parse.
    :type time_string: str
    """
    try:
        time = parser.parse(time_string)
    except ValueError:
        time = None
    return time


def pd_parse_time(time_string):
    """Parse time string and catch exception.

    :param time_string: The time string to parse.
    :type time_string: str
    """
    try:
        time = parser.parse(time_string)
        time = time.replace(tzinfo=None)
    except (TypeError, ValueError):
        time = np.nan
    return time


def extend_time_column(
        dataset: Union[SparkDataFrame, PdDataFrame],
        time_col_name: str,
        timeVal: Union[str, float, struct_time, datetime]):
    """Extend time column for string type."""
    if isinstance(timeVal, datetime):
        return (time_col_name, dataset, [])
    if isinstance(dataset, SparkDataFrame):
        if isinstance(timeVal, str):
            time_udf = udf(lambda x: spark_parse_time(x), TimestampType())
        elif isinstance(timeVal, float):
            time_udf = udf(lambda x: datetime.fromtimestamp(
                float(x)), TimestampType())
        elif isinstance(timeVal, struct_time):
            time_udf = udf(lambda x: datetime.fromtimestamp(
                mktime(x)), TimestampType())
        return add_datetime_col(dataset, time_col_name, time_udf)
    else:
        if isinstance(timeVal, str):
            return add_datetime_col(dataset, time_col_name, pd_parse_time)
        elif isinstance(timeVal, float):
            return add_datetime_col(dataset, time_col_name, datetime.fromtimestamp)
        elif isinstance(timeVal, struct_time):
            (new_time_col_name, dataset, to_be_cleaned_up_columns) = add_datetime_col(
                dataset, time_col_name, mktime)
            return new_time_col_name,\
                dataset[new_time_col_name].apply(datetime.fromtimestamp),\
                to_be_cleaned_up_columns


class TimeData:
    """Defines the base time data class."""

    @property
    def time_column_name(self):
        """Get the time column name."""
        return self.__time_column_name

    @time_column_name.setter
    def time_column_name(self, value):
        """Set the time column name."""
        self.__time_column_name = value

    @property
    def min_date(self):
        """Get the min date."""
        return self.__min_date

    @min_date.setter
    def min_date(self, value):
        """Set the min date."""
        self.__min_date = value

    @property
    def max_date(self):
        """Get the max date."""
        return self.__max_date

    @max_date.setter
    def max_date(self, value):
        """Set the max date."""
        self.__max_date = value


class TimePublicData(PublicData, TimeData):
    """Represents a public dataset with time."""

    def _get_time_val(self, dataset: Union[SparkDataFrame, PdDataFrame]):
        if isinstance(dataset, SparkDataFrame):
            return dataset.select(col(self.time_column_name))\
                .where(col(self.time_column_name).isNotNull()).limit(1)\
                .collect()[0][0]
        return dataset[self.time_column_name][dataset[self.time_column_name] != np.nan].head(1)

    def extend_time_column(self):
        """Extend time column into datetime format if necessary."""
        dataset = self.data
        timeVal = self._get_time_val(dataset)
        (self.time_column_name, self.data, _) = extend_time_column(
            dataset, self.time_column_name, timeVal)

    def filter(self, env: Union[SparkEnv, PandasEnv], min_date: datetime, max_date: datetime):
        """Filter datetime."""
        if isinstance(env, SparkEnv):
            (self.min_date, self.max_date) = (min_date, max_date)
            return self.data.filter(self.data[self.time_column_name] >= self.min_date)\
                .filter(self.data[self.time_column_name] <= self.max_date)
        (self.min_date, self.max_date) = (min_date, max_date)
        return self.data[(self.data[self.time_column_name] >= self.min_date) & (
            self.data[self.time_column_name] <= self.max_date)]


class TimeCustomerData(CustomerData, TimeData):
    """Represents a customer dataset with time."""

    def extend_time_column(self, env: Union[SparkEnv, PandasEnv]):
        """Extend time column into datetime format if necessary."""
        dataset = self.data
        if isinstance(env, SparkEnv):
            timeVal = dataset.select(col(self.time_column_name))\
                .where(col(self.time_column_name).isNotNull()).limit(1).collect()[0][0]
            (self.time_column_name, self.data, to_be_cleaned_up_columns) = extend_time_column(
                dataset, self.time_column_name, timeVal)
            self.to_be_cleaned_up_column_names += to_be_cleaned_up_columns
            (self.min_date, self.max_date) = find_min_max_date(
                dataset, self.time_column_name)
            self.data = dataset
        else:
            timeVal = dataset[dataset[self.time_column_name].notnull(
            )].loc[0, self.time_column_name]
            (self.time_column_name, self.data, to_be_cleaned_up_columns) = extend_time_column(
                dataset, self.time_column_name, timeVal)
            self.to_be_cleaned_up_column_names += to_be_cleaned_up_columns
            (self.min_date, self.max_date) = find_min_max_date(
                dataset, self.time_column_name)
            self.data = dataset

    def filter(self, env: Union[SparkEnv, PandasEnv], min_date: datetime, max_date: datetime):
        """Filter datetime."""
        (self.min_date, self.max_date) = (min_date, max_date)
        if isinstance(env, SparkEnv):
            return self.data.filter(self.data[self.time_column_name] >= self.min_date)\
                .filter(self.data[self.time_column_name] <= self.max_date)
        return self.data[(self.data[self.time_column_name] >= self.min_date) & (
            self.data[self.time_column_name] <= self.max_date)]
