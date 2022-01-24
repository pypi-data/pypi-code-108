# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains the public data base class."""

from typing import Any, List, Optional

from azureml.telemetry.activity import ActivityType

from .._utils.telemetry_utils import (get_opendatasets_logger,
                                      get_run_common_properties)
from ..environ import RuntimeEnv
from ._loggerfactory import _LoggerFactory


class PublicData:
    """Defines the base class of public data.

    Public data class contains common properties and methods for each open datasets.

    :param cols: A list of column names to enrich.
    :type cols: builtin.list
    :param enable_telemetry: Indicates whether to send telemetry.
    :type enable_telemetry: bool
    """

    mandatory_columns = []
    _registry_id = ''
    logger = get_opendatasets_logger()

    @property
    def id(self) -> Any:
        """Get the location ID of the open data."""
        return self.__id

    @id.setter
    def id(self, value):
        """Set the location ID of the open data."""
        self.__id = value

    @property
    def cols(self) -> List[str]:
        """Get the column name list to retrieve."""
        return self.__cols

    @cols.setter
    def cols(self, value: List[str]):
        """Set the column names to retrieve."""
        self.__cols = value

    @property
    def env(self) -> RuntimeEnv:
        """Return the runtime environment."""
        return self.__env

    @env.setter
    def env(self, value: RuntimeEnv):
        self.__env = value

    @property
    def registry_id(self) -> str:
        """
        Get the registry ID of this public dataset registered at the backend.

        Azure uses this registry ID to get latest metadata like storage location.
        You should expect all public data sub classes to assign _registry_id.

        :return: The registry ID.
        :rtype: str
        """
        return self._registry_id

    def __init__(self, cols: Optional[List[str]], enable_telemetry: bool = True):
        """
        Initialize with columns.

        :param cols: column name list which the user wants to enrich
        :param enable_telemetry: whether to send telemetry
        """
        self.enable_telemetry = enable_telemetry
        self.cols = list(cols) if cols is not None else None
        if not hasattr(self, 'time_column_name'):
            self.time_column_name = None
        if not hasattr(self, 'start_date'):
            self.start_date = None
        if not hasattr(self, 'end_date'):
            self.end_date = None
        if self.enable_telemetry:
            self.log_properties = self._get_common_log_properties()
            self.log_properties['cols'] = self.cols

        if self.cols is None:
            self.selected_columns = ['*']
        else:
            self.selected_columns = list(
                set(self.cols + self.mandatory_columns))

    def _get_common_log_properties(self):
        """Get common log properties."""
        props = get_run_common_properties()
        props['RegistryId'] = self.registry_id
        return props

    def get_enricher(self):
        """Get enricher."""
        if self.enable_telemetry:
            self.log_properties['ActivityType'] = ActivityType.PUBLICAPI
            _LoggerFactory.log_event('get_enricher', **self.log_properties)
            return self._get_enricher(None)
        else:
            return self._get_enricher(None)

    def _get_enricher(self, activity_logger):
        """
        Get enricher, internal to override.

        :param activity_logger: activity logger, could be None.
        :return: enricher class object.
        """
        return None

    def to_spark_dataframe(self):
        """To spark dataframe."""
        if self.enable_telemetry:
            self.log_properties['ActivityType'] = ActivityType.PUBLICAPI
            _LoggerFactory.log_event(
                'to_spark_dataframe_in_worker', **self.log_properties)
            return self._to_spark_dataframe(None)
        else:
            return self._to_spark_dataframe(None)

    def _to_spark_dataframe(self, activity_logger):
        """
        To SPARK dataframe, internal to override.

        :param activity_logger: activity logger, could be None.
        :return: SPARK dataframe.
        """
        return None

    def to_pandas_dataframe(self):
        """To pandas dataframe."""
        if self.enable_telemetry:
            self.log_properties['ActivityType'] = ActivityType.INTERNALCALL
            _LoggerFactory.log_event(
                'to_pandas_dataframe_in_worker', **self.log_properties)
            return self._to_pandas_dataframe(None)
        else:
            return self._to_pandas_dataframe(None)

    def _to_pandas_dataframe(self, activity_logger):
        """
        To pandas dataframe, internal to override.

        :param activity_logger: activity logger, could be None.
        :return: Pandas dataframe.
        """
        return None
