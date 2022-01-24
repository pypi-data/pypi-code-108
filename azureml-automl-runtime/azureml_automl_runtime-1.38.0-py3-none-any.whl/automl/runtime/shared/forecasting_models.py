# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""A module that contains definitions for naive forecasting models: Naive, SeasonalNaive, Average, SeasonalAverage."""
from typing import Any, cast, Dict

import numpy as np
import pandas as pd

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared import constants
from azureml.automl.core.shared._diagnostics.automl_error_definitions import AutoMLInternal
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.core.shared.types import GrainType

from azureml.automl.runtime.shared import time_series_data_frame
from azureml.automl.runtime.shared._arimax import Arimax
from azureml.automl.runtime.shared._auto_arima import AutoArima
from azureml.automl.runtime.shared._exponential_smoothing import ExponentialSmoothing
from azureml.automl.runtime.shared._prophet_model import ProphetModel
from azureml.automl.runtime.shared._multi_grain_forecast_base import _MultiGrainForecastBase


class _LowCapacityModelStateContainer:
    def __init__(self, series_values: pd.Series):
        self._saves_numpy_array = True

        if self._saves_numpy_array:
            self.series_values = series_values.values
        else:
            self.series_values = series_values

    def _get_saves_numpy_array_safe(self) -> bool:
        return self._saves_numpy_array if hasattr(self, '_saves_numpy_array') else False


class _LowCapacityModelFitMixin:
    def _set_seasonality_safe(self, timeseries_param_dict: Dict[str, Any]) -> None:
        self.seasonality = timeseries_param_dict.get(
            constants.TimeSeries.SEASONALITY,
            constants.TimeSeriesInternal.SEASONALITY_VALUE_NONSEASONAL
        )
        Contract.assert_true(
            isinstance(self.seasonality, int) and self.seasonality >= 1,
            "Seasonality is not a positive integer.",
            log_safe=True
        )

    @staticmethod
    def fit_model(X_fit_grain: time_series_data_frame.TimeSeriesDataFrame) -> Any:
        series_values = X_fit_grain[constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN]
        return _LowCapacityModelStateContainer(series_values)

    @staticmethod
    def in_sample_align(pred: np.ndarray, first_obs_date: pd.Timestamp, last_obs_date: pd.Timestamp,
                        X_pred_grain: time_series_data_frame.TimeSeriesDataFrame,
                        freq: pd.DateOffset) -> np.ndarray:
        try:
            date_filter = X_pred_grain.time_index.values
            date_range = pd.date_range(start=first_obs_date, end=last_obs_date, freq=freq)
            index = np.searchsorted(date_range, date_filter)
            aligned_pred = cast(np.ndarray, pred[index])
        except Exception as e:
            msg = 'Unable to align predictions. Timeseries may not be contiguous.'
            raise ClientException._with_error(
                AzureMLError.create(
                    AutoMLInternal, error_details=msg,
                    inner_exception=e
                )
            )

        return aligned_pred


class SeasonalNaive(_LowCapacityModelFitMixin, _MultiGrainForecastBase):
    """
    The Seasonal Naive forecasting model makes predictions by carrying forward the latest season of target
    values for each time-series in the training data.
    For a given series, the forecast at horizon h, \\hat{y}_{T + h}, is given by:
    \\hat{y}_{T + h} = y_{T + h - m * (k + 1)},
    where y denotes target values from training data, m is the seasonal period and k = floor((h - 1) / m).

    The seasonal period is an integer-type hyperparameter which is automatically detected by default, but can
    also be manually set by the user.
    """

    def __init__(self, timeseries_param_dict: Dict[str, Any]):
        """Create an seasonal naive multi-grain forecasting model."""
        super().__init__(timeseries_param_dict)
        self._set_seasonality_safe(timeseries_param_dict)

    def _fit_single_grain_impl(self, X_fit_grain: time_series_data_frame.TimeSeriesDataFrame,
                               grain_level: GrainType) -> Any:
        """Fit seasonal naive model on one grain.

        :param grain_level:
            is an object that identifies the series by its
            grain group in a TimeSeriesDataFrame. In practice, it is an element
            of X.groupby_grain().groups.keys(). Implementers can use
            the grain_level to store time series specific state needed for
            training or forecasting.

        :param X_fit_grain:
            the context data for the prediction (X_train).

        :Returns:
             a model object that can be used to make predictions."""
        return self.fit_model(X_fit_grain)

    def _get_forecast_single_grain_impl(self,
                                        model: _LowCapacityModelStateContainer,
                                        max_horizon: int,
                                        grain_level: GrainType,
                                        X_pred_grain: time_series_data_frame.TimeSeriesDataFrame) -> np.ndarray:
        """
        Forecast from Seasonal Naive model.

        Respects the X_pred_grain parameter and max_horizon parameter.
        :param model:
            is an object representation of a model. It is the
            object returned by the _fit_single_grain_impl method.

        :param max_horizon:
            int that represents the max horizon.

        :param grain_level:
            is an object that identifies the series by its
            grain group in a TimeSeriesDataFrame. In practice, it is an element
            of X.groupby_grain().groups.keys(). Implementers can use
            the grain_level to store time series specific state needed for
            training or forecasting.
        :param X_pred_grain:
            the context data for the prediction (X_test).

        :Returns:
            a 1-D numpy array of forecasted values for the training data. The data are
            assumed to be in chronological order"""
        model_has_numpy_array = model._get_saves_numpy_array_safe()
        if len(model.series_values) < self.seasonality:
            if model_has_numpy_array:
                pred = np.repeat(model.series_values[-1], max_horizon)
            else:
                pred = np.repeat(model.series_values.tail(1), max_horizon)
        else:
            if model_has_numpy_array:
                pred = np.tile(model.series_values[-self.seasonality:], int(np.ceil(max_horizon / self.seasonality)))
            else:
                pred = np.tile(model.series_values.tail(self.seasonality), int(np.ceil(max_horizon
                                                                                       / self.seasonality)))
        return self.align_out(in_sample=False, pred=pred, X_pred_grain=X_pred_grain,
                              X_fit_grain=time_series_data_frame.TimeSeriesDataFrame(None, None),
                              max_horizon=max_horizon, freq=self._freq)

    def _fit_in_sample_single_grain_impl(self,
                                         model: _LowCapacityModelStateContainer,
                                         grain_level: GrainType,
                                         X_grain: time_series_data_frame.TimeSeriesDataFrame) -> np.ndarray:
        """Fit seasonal naive model on one or multiple grains.

        :param model:
            is an object representation of a model. It is the
            object returned by the _fit_single_grain_impl method.

        :param grain_level:
            is an object that identifies the series by its
            grain group in a TimeSeriesDataFrame. In practice, it is an element
            of X.groupby_grain().groups.keys(). Implementers can use
            the grain_level to store time series specific state needed for
            training or forecasting.

        :param X_grain:
            the context data for the in-sample prediction (X_train).

        :Returns:
            a np.ndarray containing the fitted values in `fitted`."""
        first_obs_date = self._first_observation_dates[grain_level]
        last_obs_date = self._last_observation_dates[grain_level]
        if model._get_saves_numpy_array_safe():
            pred = np.concatenate((np.zeros(self.seasonality), model.series_values))
            align_pred = self.in_sample_align(pred, first_obs_date, last_obs_date, X_grain, freq=self._freq)
        else:
            pred = model.series_values.shift(self.seasonality).fillna(0)
            align_pred = self.align_out(in_sample=True, pred=pred, X_pred_grain=X_grain,
                                        X_fit_grain=model.series_values, max_horizon=None, freq=None)
        return align_pred


class Naive(SeasonalNaive):
    """
    The Naive forecasting model makes predictions by carrying forward the latest target value
    for each time-series in the training data.
    For a given series, the forecast at horizon h, \\hat{y}_{T + h}, is given by:
    \\hat{y}_{T + h} = y_{T},
    where y denotes target values from training data.
    """

    def __init__(self, timeseries_param_dict: Dict[str, Any]):
        """Create an naive multi-grain forecasting model."""
        super().__init__(timeseries_param_dict)
        self.seasonality = 1


class SeasonalAverage(_LowCapacityModelFitMixin, _MultiGrainForecastBase):
    """
    The Seasonal Average forecasting model makes predictions by carrying forward the average value of the latest
    season of data for each time-series in the training data.
    For a given series, the forecast at horizon h, \\hat{y}_{T + h}, is given by:
    \\hat{y}_{T + h} = 1 / m * \\sum_{i=1}^{m} y_{T - i + 1},
    where y denotes target values from training data and m is the seasonal period.

    The seasonal period is an integer-type hyperparameter which is automatically detected by default, but can
    also be manually set by the user.
    """

    def __init__(self, timeseries_param_dict: Dict[str, Any]):
        """Create an seasonal average multi-grain forecasting model."""
        super().__init__(timeseries_param_dict)
        self._set_seasonality_safe(timeseries_param_dict)
        self.window_size = self.seasonality

    def _fit_single_grain_impl(self, X_fit_grain: time_series_data_frame.TimeSeriesDataFrame,
                               grain_level: GrainType) -> Any:
        """Fit seasonal average model on one grain.

        :param grain_level:
            is an object that identifies the series by its
            grain group in a TimeSeriesDataFrame. In practice, it is an element
            of X.groupby_grain().groups.keys(). Implementers can use
            the grain_level to store time series specific state needed for
            training or forecasting.

        :param X_fit_grain:
            the context data for the prediction (X_train).

        :Returns:
             a model object that can be used to make predictions."""
        return self.fit_model(X_fit_grain)

    def _get_forecast_single_grain_impl(self,
                                        model: _LowCapacityModelStateContainer,
                                        max_horizon: int,
                                        grain_level: GrainType,
                                        X_pred_grain: time_series_data_frame.TimeSeriesDataFrame) -> np.ndarray:
        """
        Forecast from Seasonal Average model.

        Respects the X_pred_grain parameter and max_horizon parameter.
        :param model:
            is an object representation of a model. It is the
            object returned by the _fit_single_grain_impl method.

        :param max_horizon:
            int that represents the max horizon.

        :param grain_level:
            is an object that identifies the series by its
            grain group in a TimeSeriesDataFrame. In practice, it is an element
            of X.groupby_grain().groups.keys(). Implementers can use
            the grain_level to store time series specific state needed for
            training or forecasting.

        :param X_pred_grain:
            the context data for the prediction (X_test).

        :Returns:
            a 1-D numpy array of forecasted values for the training data. The data are
            assumed to be in chronological order"""
        model_has_numpy_array = model._get_saves_numpy_array_safe()
        if self.window_size is None:
            # Set window_size to length of training data
            self.window_size = len(model.series_values)

        if len(model.series_values) < self.window_size:
            if model_has_numpy_array:
                mean_value = np.mean(model.series_values)
            else:
                mean_value = model.series_values.mean()
        else:
            if model_has_numpy_array:
                mean_value = np.mean(model.series_values[-self.window_size:])
            else:
                mean_value = model.series_values.tail(self.window_size).mean()
        pred = np.repeat(mean_value, max_horizon)
        return self.align_out(in_sample=False, pred=pred, X_pred_grain=X_pred_grain,
                              X_fit_grain=time_series_data_frame.TimeSeriesDataFrame(None, None),
                              max_horizon=max_horizon, freq=self._freq)

    def _fit_in_sample_single_grain_impl(self,
                                         model: _LowCapacityModelStateContainer,
                                         grain_level: GrainType,
                                         X_grain: time_series_data_frame.TimeSeriesDataFrame) -> np.ndarray:
        """Fit seasonal average model on one or multiple grains.

        :param model:
            is an object representation of a model. It is the
            object returned by the _fit_single_grain_impl method.

        :param grain_level:
            is an object that identifies the series by its
            grain group in a TimeSeriesDataFrame. In practice, it is an element
            of X.groupby_grain().groups.keys(). Implementers can use
            the grain_level to store time series specific state needed for
            training or forecasting.

        :param X_grain:
            the context data for the in-sample prediction (X_train).

        :Returns:
            a np.ndarray containing the fitted values in `fitted`."""
        if self.window_size is None:
            # Set window_size to length of training data
            self.window_size = len(X_grain)

        first_obs_date = self._first_observation_dates[grain_level]
        last_obs_date = self._last_observation_dates[grain_level]
        if model._get_saves_numpy_array_safe():
            # Compute a rolling-window average of the series values
            csum = np.cumsum(model.series_values, dtype=float)
            rolling_mean = (csum[self.window_size:] - csum[:-self.window_size]) / float(self.window_size)
            csum_start = csum[:self.window_size]
            rolling_start = csum_start / np.arange(1, len(csum_start) + 1, dtype=float)
            pred = np.concatenate((np.zeros(1), rolling_start, rolling_mean))
            align_pred = self.in_sample_align(pred, first_obs_date, last_obs_date, X_grain, freq=self._freq)
        else:
            pred = model.series_values.rolling(window=self.window_size,
                                               min_periods=1).mean().fillna(0)
            align_pred = self.align_out(in_sample=True, pred=pred, X_pred_grain=X_grain,
                                        X_fit_grain=model.series_values, max_horizon=None, freq=None)
        return align_pred


class Average(SeasonalAverage):
    """
    The Average forecasting model makes predictions by carrying forward the average of the target values
    for each time-series in the training data.
    For a given series, the forecast at horizon h, \\hat{y}_{T + h}, is given by:
    \\hat{y}_{T + h} = 1 / n * \\sum_{i=1}^{n} y_{T - i + 1},
    where y denotes target values from training data and n is the length of the training series.
    """

    def __init__(self, timeseries_param_dict: Dict[str, Any]):
        """Create an average multi-grain forecasting model."""
        super().__init__(timeseries_param_dict)
        self.window_size = None

    def _fit_in_sample_single_grain_impl(self,
                                         model: _LowCapacityModelStateContainer,
                                         grain_level: GrainType,
                                         X_grain: time_series_data_frame.TimeSeriesDataFrame) -> np.ndarray:
        """Fit averaage model on one or multiple grains.

        :param model:
            is an object representation of a model. It is the
            object returned by the _fit_single_grain_impl method.

        :param grain_level:
            is an object that identifies the series by its
            grain group in a TimeSeriesDataFrame. In practice, it is an element
            of X.groupby_grain().groups.keys(). Implementers can use
            the grain_level to store time series specific state needed for
            training or forecasting.

        :param X_grain:
            the context data for the in-sample prediction (X_train).

        :Returns:
            a np.ndarray containing the fitted values in `fitted`."""
        first_obs_date = self._first_observation_dates[grain_level]
        last_obs_date = self._last_observation_dates[grain_level]
        if model._get_saves_numpy_array_safe():
            # Compute an expanding window average of the series values
            csum = np.cumsum(model.series_values, dtype=float)
            expanding_mean = csum / np.arange(1, len(csum) + 1, dtype=float)
            pred = np.concatenate((np.zeros(1), expanding_mean))
            aligned_pred = self.in_sample_align(pred, first_obs_date, last_obs_date, X_grain, freq=self._freq)
        else:
            pred = model.series_values.rolling(window=len(model.series_values), min_periods=1).mean()
            aligned_pred = self.align_out(in_sample=True, pred=pred, X_pred_grain=X_grain,
                                          X_fit_grain=model.series_values, max_horizon=None, freq=None)
        return aligned_pred
