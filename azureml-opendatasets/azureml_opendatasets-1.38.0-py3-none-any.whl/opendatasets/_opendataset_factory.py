# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""AbstractTabularOpenDataset is the abstract base class of all OpenDataset."""

from datetime import datetime
from typing import List, Optional

import azureml.dataprep as dprep
from azureml.data import TabularDataset
from azureml.data._dataset import _DatasetTelemetryInfo
from azureml.telemetry.activity import ActivityType

from .accessories._loggerfactory import _LoggerFactory


class TabularOpenDatasetFactory:
    """TabularOpenDatasetFactory is the base class of all Tabular OpenDatasets."""

    partition_prep_func = None
    mandatory_columns = []
    fine_grain_timestamp = None
    coarse_grain_timestamp = None

    @classmethod
    def get_tabular_dataset(
            cls: type,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            cols: Optional[List[str]] = None,
            enable_telemetry: bool = True):
        """
        Initialize AbstractTabularOpenDataset with blob url.

        :param cls: type name of the Open Dataset.
        :type cls: type
        :param start_date: start date you'd like to query inclusively.
        :type start_date: datetime
        :param end_date: end date you'd like to query inclusively.
        :type end_date: datetime
        :param cols: a list of column names you'd like to retrieve. None will get all columns.
        :type cols: List[str]
        :param enable_telemetry: whether to enable telemetry, disabled for UT only.
        :type enable_telemetry: bool
        :return: TabularDataset
        :rtype: azureml.data.TabularDataset
        """
        if enable_telemetry:
            log_properties = {}
            log_properties['RegistryId'] = cls._blobInfo.registry_id
            log_properties['Path'] = cls._blobInfo.get_url()
            log_properties['StartDate'] = start_date.strftime(
                "%Y-%m-%dT%H:%M:%S") if start_date is not None else ''
            log_properties['EndDate'] = end_date.strftime(
                "%Y-%m-%dT%H:%M:%S") if end_date is not None else ''
            log_properties['ActivityType'] = ActivityType.PUBLICAPI
            _LoggerFactory.log_event('get_tabular_dataset', **log_properties)
            return cls._get_tabular_dataset(start_date=start_date, end_date=end_date, cols=cols)
        else:
            return cls._get_tabular_dataset(start_date=start_date, end_date=end_date, cols=cols)

    @classmethod
    def _get_tabular_dataset(
            cls: type,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            cols: Optional[List[str]] = None):
        dflow_raw = dprep.Dataflow.get_files(path=cls._blobInfo.get_url())

        if cls.partition_prep_func is not None:
            dflow = cls.partition_prep_func(dflow_raw, start_date, end_date)
        else:
            dflow = dflow_raw

        # Read Blob files.
        dflow = dflow.read_parquet_file()

        # Use dataprep to filter dataset and return the filtered dataset object.
        if hasattr(cls, 'time_column_name') and cls.time_column_name is not None:
            if start_date:
                dflow = dflow.filter(dflow[cls.time_column_name] >= start_date)
            else:
                dflow = dflow.filter(
                    dflow[cls.time_column_name] >= cls.default_start_date)

            if end_date:
                dflow = dflow.filter(dflow[cls.time_column_name] <= end_date)

        if cols is not None and (len(cols) > 1 or cols[0] != '*'):
            dflow = dflow.keep_columns(list(set(cols + cls.mandatory_columns)))

        new_ds = TabularDataset._create(dflow).with_timestamp_columns(
            fine_grain_timestamp=cls.fine_grain_timestamp,
            coarse_grain_timestamp=cls.coarse_grain_timestamp)

        new_ds._telemetry_info = _DatasetTelemetryInfo(
            entry_point='PythonSDK:OpenDataset')

        return new_ds
