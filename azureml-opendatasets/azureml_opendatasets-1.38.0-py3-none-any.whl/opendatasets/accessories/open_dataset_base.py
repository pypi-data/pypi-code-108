# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Base class for tabular open datasets."""

import logging
from datetime import datetime
from typing import List

import pandas as pd
from azureml.data import FileDataset, TabularDataset
from azureml.exceptions import UserErrorException
from azureml.telemetry.activity import ActivityType

from .._utils.telemetry_utils import get_run_common_properties
from ..dataaccess._blob_accessor import DefaultArgKey
from ..environ import RuntimeEnv, SparkEnv
from ._loggerfactory import _LoggerFactory, track
from .public_data import PublicData

# Refactor & clean PublicData for simple interface

_logger = None


def get_logger(name, verbosity=logging.DEBUG):
    """Get the trace logger."""
    global _logger
    if _logger is None:
        _logger = _LoggerFactory.get_logger(name, verbosity)
    return _logger


class OpenDatasetBase(PublicData):
    """Open Dataset Base Class for inherit."""

    _blob_accessor = None  # type\: BlobAccessor

    @property
    def id(self) -> str:
        """Get the location ID of the open data."""
        if not hasattr(self, 'id_column_name'):
            return None
        return self.id_column_name

    @id.setter
    def id(self, value):
        """Set the location ID of the open data."""
        self.id_column_name = value

    @property
    def registry_id(self) -> str:
        """
        Get the registry ID of this public dataset registered at the backend.

        This registry ID is used to get latest metadata like storage location.
        Expect all public data sub classes to assign _registry_id.

        :return: Registry ID string.
        :rtype: str
        """
        return self._blob_accessor.id

    @property
    def data(self):
        """Get the data of the OpenDataset Object."""
        if self.env is None:
            print(
                "[Error] There is no data loaded until %s.env is set as SparkEnv() or PandasEnv()."
                % self.__class__)
            return None
        if self._data is None:
            if isinstance(self.env, SparkEnv):
                self._data = self.to_spark_dataframe()
            else:
                self._data = self.to_pandas_dataframe()
        return self._data

    @data.setter
    def data(self, value):
        """Set the data of OpenDataset Object."""
        self._data = value

    @property
    def cols(self):
        """Get the column name list to retrieve."""
        return self._cols

    @cols.setter
    def cols(self, value: List[str] = None):
        """Set the column names to retrieve."""
        if value and len(value) > 0:
            self._cols = list(
                set(value + self._blob_accessor.mandatory_columns))
        else:
            self._cols = None

    @property
    def time_column_name(self) -> str:
        """Time column name."""
        return self._blob_accessor.time_column_name

    @property
    def log_properties(self) -> dict:
        """Get log properties."""
        return self._log_properties

    def __init__(
            self,
            cols: List[str] = None,
            enable_telemetry: bool = True,
            **kwargs):
        """
        Construct open datasets.

        :param cols: A list of columns names to load from the dataset, defaults to None
        :type cols: builtin.list[str]
        :param enable_telemetry: Whether to enable telemetry on this dataset, defaults to True
        :type enable_telemetry: bool
        :param kwargs: args for filter
        :type kwargs: dict
        """
        if 'start_date' in kwargs.keys() and not isinstance(kwargs['start_date'], datetime):
            raise UserErrorException("Please ensure input start_date is datetime type.")
        if 'end_date' in kwargs.keys() and not isinstance(kwargs['end_date'], datetime):
            raise UserErrorException("Please ensure input end_date is datetime type.")

        # assign some property for compactable with PublicData
        self.enable_telemetry = enable_telemetry
        # Set up columns
        self.cols = cols
        # Set up telemetry
        self._enable_telemetry = enable_telemetry
        if self._enable_telemetry:
            self._log_properties = self._get_common_log_properties()
            self._log_properties['cols'] = self.cols
            self._log_properties = {**self._log_properties, **kwargs}
        # Set up kwargs
        self._kwargs = kwargs
        self._env = None
        # change get_tabular_dataset for instance
        self.get_tabular_dataset = self._instance_get_tabular_dataset
        self.get_file_dataset = self._instance_get_file_dataset
        # Set up data
        self.data = None

    @track(get_logger(__name__), {}, ActivityType.PUBLICAPI)
    def to_pandas_dataframe(self) -> pd.DataFrame:
        """To pandas dataframe."""
        if self._enable_telemetry:
            self._log_properties['ActivityType'] = ActivityType.PUBLICAPI
            _LoggerFactory.log_event(
                'to_pandas_dataframe_in_worker', **self._log_properties)
        return self._to_pandas_dataframe()

    @track(get_logger(__name__), {}, ActivityType.PUBLICAPI)
    def to_spark_dataframe(self):
        """To spark dataframe."""
        if self._enable_telemetry:
            self._log_properties['ActivityType'] = ActivityType.PUBLICAPI
            _LoggerFactory.log_event(
                'to_spark_dataframe_in_worker', **self._log_properties)
        return self._to_spark_dataframe()

    @classmethod
    @track(get_logger(__name__), {}, ActivityType.PUBLICAPI)
    def get_tabular_dataset(
            cls: type,
            start_date: datetime = None,
            end_date: datetime = None,
            cols: List[str] = None,
            enable_telemetry: bool = True,
            **kwargs
    ) -> TabularDataset:
        """
        Initialize AbstractTabularOpenDataset with blob url.

        :param cls: type name of the Open Dataset.
        :type cls: type
        :param start_date: The start date to query inclusively.
        :type start_date: datetime
        :param end_date: The end date to query inclusively.
        :type end_date: datetime
        :param cols: A list of column names to retrieve. None will get all columns.
        :type cols: builtin.list[str]
        :param enable_telemetry: Whether to enable telemetry, disabled for UT only.
        :type enable_telemetry: bool
        :return: TabularDataset
        :rtype: azureml.data.TabularDataset
        """
        if enable_telemetry:
            log_properties = cls._get_common_log_properties()
            log_properties = {
                **log_properties,
                **{
                    DefaultArgKey.STARTDATE.value: start_date,
                    DefaultArgKey.ENDDATE.value: end_date,
                    "cols": cols}}
            log_properties['ActivityType'] = ActivityType.PUBLICAPI
            _LoggerFactory.log_event(
                'get_tabular_dataset', **log_properties)
        if start_date:
            kwargs[DefaultArgKey.STARTDATE.value] = start_date
        if end_date:
            kwargs[DefaultArgKey.ENDDATE.value] = end_date
        return cls._blob_accessor.get_tabular_dataset(cols, **kwargs)

    def _instance_get_tabular_dataset(
            self,
            start_date: datetime = None,
            end_date: datetime = None,
            cols: List[str] = None,
            enable_telemetry: bool = None,
            **kwargs
    ) -> TabularDataset:
        if not cols:
            cols = self.cols
        start_date = start_date if start_date else self._get_arg(
            DefaultArgKey.STARTDATE.value)
        end_date = end_date if end_date else self._get_arg(
            DefaultArgKey.ENDDATE.value)
        enable_telemetry = enable_telemetry if enable_telemetry is not None \
            else self._enable_telemetry
        kwargs = {**self._kwargs, **kwargs}
        if DefaultArgKey.STARTDATE.value in kwargs:
            kwargs.pop(DefaultArgKey.STARTDATE.value)
        if DefaultArgKey.ENDDATE.value in kwargs:
            kwargs.pop(DefaultArgKey.ENDDATE.value)
        return self.__class__.get_tabular_dataset(
            start_date,
            end_date,
            cols,
            enable_telemetry,
            **kwargs)

    @classmethod
    @track(get_logger(__name__), {}, ActivityType.PUBLICAPI)
    def get_file_dataset(
            cls: type,
            start_date: datetime = None,
            end_date: datetime = None,
            enable_telemetry: bool = True,
            **kwargs) -> FileDataset:
        """
        Get the file dataset for open dataset.

        :param cls: current class
        :type cls: type
        :param start_date: start date, defaults to None
        :type start_date: datetime
        :param end_date: end date, defaults to None
        :type end_date: datetime
        :param enable_telemetry: enable telemetry or not, defaults to True
        :type enable_telemetry: bool
        :return: file dataset
        :rtype: azureml.data.FileDataset
        """
        if enable_telemetry:
            log_properties = cls._get_common_log_properties()
            log_properties = {
                **log_properties,
                **{
                    DefaultArgKey.STARTDATE.value: start_date,
                    DefaultArgKey.ENDDATE.value: end_date
                }}
            log_properties['ActivityType'] = ActivityType.PUBLICAPI
            _LoggerFactory.log_event(
                'get_file_dataset', **log_properties)
        if start_date:
            kwargs[DefaultArgKey.STARTDATE.value] = start_date
        if end_date:
            kwargs[DefaultArgKey.ENDDATE.value] = end_date
        return cls._blob_accessor.get_file_dataset(**kwargs)

    def _instance_get_file_dataset(
            self,
            start_date: datetime = None,
            end_date: datetime = None,
            enable_telemetry: bool = None,
            **kwargs) -> FileDataset:
        start_date = start_date if start_date else self._get_arg(
            DefaultArgKey.STARTDATE.value)
        end_date = end_date if end_date else self._get_arg(
            DefaultArgKey.ENDDATE.value)
        for key, value in self._kwargs.items():
            if key not in kwargs \
                    and key not in (DefaultArgKey.STARTDATE.value, DefaultArgKey.ENDDATE.value):
                kwargs[key] = value
        enable_telemetry = enable_telemetry if enable_telemetry is not None\
            else self._enable_telemetry
        kwargs = {**self._kwargs, **kwargs}
        if DefaultArgKey.STARTDATE.value in kwargs:
            kwargs.pop(DefaultArgKey.STARTDATE.value)
        if DefaultArgKey.ENDDATE.value in kwargs:
            kwargs.pop(DefaultArgKey.ENDDATE.value)
        return self.__class__.get_file_dataset(start_date, end_date, enable_telemetry, **kwargs)

    def _to_spark_dataframe(self):
        """
        To SPARK dataframe, internal to override.

        :return: SPARK dataframe.
        """
        return self._blob_accessor.get_spark_dataframe(
            self.cols,
            **self._kwargs
        )

    def _to_pandas_dataframe(self) -> pd.DataFrame:
        return self._blob_accessor.get_pandas_dataframe(
            self.cols,
            **self._kwargs
        )

    @classmethod
    def _get_common_log_properties(cls):
        props = get_run_common_properties()
        props['RegistryId'] = cls._blob_accessor.id
        return props

    def _filter_time(self, env: RuntimeEnv, min_date: datetime, max_date: datetime):
        self.env = env
        if isinstance(self.env, SparkEnv):
            return self.data.filter(self.data[self.time_column_name] >= min_date)\
                .filter(self.data[self.time_column_name] <= max_date)
        else:
            return self.data[(self.data[self.time_column_name] >= min_date) & (
                self.data[self.time_column_name] <= max_date)]

    def _get_arg(self, arg_name: str):
        if arg_name in self._kwargs:
            return self._kwargs[arg_name]

        return None


class ClassMethodOpenDatasetBase:
    """Base class for class only has class method."""

    _blob_accessor = None  # type\: BlobAccessor

    @classmethod
    def _get_open_dataset(
            cls,
            cols: List[str] = None,
            enable_telemetry: bool = True,
            **kwargs) -> OpenDatasetBase:
        class_name = cls._blob_accessor.id + "_OpenDataset"
        dataset_class = type(class_name, (OpenDatasetBase,),
                             {'_blob_accessor': cls._blob_accessor})
        dataset = dataset_class(cols, enable_telemetry, **kwargs)
        return dataset
