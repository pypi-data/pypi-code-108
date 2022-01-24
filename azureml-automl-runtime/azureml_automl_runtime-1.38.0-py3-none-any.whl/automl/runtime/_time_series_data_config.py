# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""The class to contain the forecasting data set and the main parameters."""
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
from azureml.automl.core.shared.constants import TimeSeriesInternal
from azureml.automl.core.featurization.featurizationconfig import FeaturizationConfig
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from pandas.tseries.frequencies import to_offset


class TimeSeriesDataConfig(object):
    """
    The lightweight class holding information about forecasting data set.

    :param X: The data frame to be analyzed.
    :param y: The array of target values.
    :param time_column_name: The name of a time column name.
    :param time_series_id_column_names: The name of columns identifying individual series.
    :param freq: Forecasting frequency.
    :param target_aggregation_function: Target aggregation function.
    :param featurization_config: The featurization config.
    """

    def __init__(self, X: pd.DataFrame, y: Optional[np.ndarray], time_column_name: str,
                 time_series_id_column_names: Optional[Union[str, List[str]]], freq: Optional[pd.DateOffset],
                 target_aggregation_function: Optional[str],
                 featurization_config: Union[str, Dict[str, Any], FeaturizationConfig]):
        """
        Create anew instance of the ForecastingDataConfig.

        :param X: The data frame to be analyzed.
        :param y: The array of target values.
        :param time_column_name: The name of a time column name.
        :param time_series_id_column_names: The name of columns identifying individual series.
        :param freq: Forecasting frequency.
        :param target_aggregation_function: Target aggregation function.
        :param featurization_config: The featurization config.
        """
        self._X = X  # type: pd.DataFrame
        if y is None:
            self._y = np.repeat(np.NaN, len(X))  # type: np.ndarray
        else:
            self._y = y
        self._time_column_name = time_column_name
        if (time_series_id_column_names == TimeSeriesInternal.DUMMY_GRAIN_COLUMN
                or time_series_id_column_names == [TimeSeriesInternal.DUMMY_GRAIN_COLUMN]) and \
                TimeSeriesInternal.DUMMY_GRAIN_COLUMN not in X.columns:
            self._time_series_id_column_names = None
        else:
            if isinstance(time_series_id_column_names, str):
                self._time_series_id_column_names = [time_series_id_column_names]
            else:
                self._time_series_id_column_names = time_series_id_column_names
        self._freq = freq  # type: Optional[pd.DateOffset]
        self._target_aggregation_function = target_aggregation_function  # type: Optional[str]
        if isinstance(featurization_config, FeaturizationConfig):
            self._featurization = featurization_config  # type: FeaturizationConfig
        else:
            self._featurization = FeaturizationConfig()
            if isinstance(featurization_config, dict):
                self._featurization._from_dict(featurization_config)

    @property
    def data_x(self) -> pd.DataFrame:
        """Return the data frame with features."""
        return self._X

    @property
    def data_y(self) -> np.ndarray:
        """Return target values."""
        return self._y

    @property
    def time_column_name(self) -> str:
        """Return time column name."""
        return self._time_column_name

    @property
    def time_series_id_column_names(self) -> Optional[List[str]]:
        """Return time series id column names."""
        return self._time_series_id_column_names

    @property
    def freq(self) -> Optional[pd.DateOffset]:
        """Return the forecast frequency."""
        return self._freq

    @property
    def target_aggregation_function(self) -> Optional[str]:
        """Return the target aggregation function."""
        return self._target_aggregation_function

    @property
    def featurization(self) -> FeaturizationConfig:
        """Return the featurization config."""
        return self._featurization

    @staticmethod
    def from_settings(X: pd.DataFrame,
                      y: Optional[np.ndarray],
                      settings: AutoMLBaseSettings) -> 'TimeSeriesDataConfig':
        """
        Get the TimeSeriesDataConfig from settings.

        :param X: The input data frame.
        :param y: the target column.
        :param settings: The settigs object to copy the meta information from.
        :return: The TimeSeriesDataConfig object.
        """
        return TimeSeriesDataConfig(
            X, y, settings.time_column_name,
            settings.grain_column_names, to_offset(settings.freq),
            settings.target_aggregation_function,
            settings.featurization)
