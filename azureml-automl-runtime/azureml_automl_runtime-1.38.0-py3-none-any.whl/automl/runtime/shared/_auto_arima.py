# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""The wrapper for pyramid-arima model."""

from typing import List, Tuple, Any, Optional, Dict, Union, cast

import logging

import pmdarima
import numpy as np
import os
import pandas as pd
import sys

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared import constants, exceptions, logging_utilities
from azureml.automl.core.shared.types import GrainType
from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared._diagnostics.automl_error_definitions import ForecastingArimaNoModel

from azureml.automl.runtime.shared import model_wrappers, time_series_data_frame
from azureml.automl.runtime.shared._multi_grain_forecast_base import _MultiGrainForecastBase

logger = logging.getLogger(__name__)


class AutoArima(_MultiGrainForecastBase):
    """AutoArima multigrain forecasting model."""

    def __init__(self, timeseries_param_dict):
        """Create an autoarima multi-grain forecasting model."""
        super().__init__(timeseries_param_dict)

    def _fit_in_sample_single_grain_impl(self,
                                         model: Any,
                                         grain_level: GrainType,
                                         X_grain: time_series_data_frame.TimeSeriesDataFrame) -> np.ndarray:
        date_filter = X_grain.time_index.values
        date_argmax = self._get_date_argmax_safe(date_filter=date_filter)
        date_range = pd.date_range(
            start=self._first_observation_dates[grain_level],
            end=date_filter[date_argmax],
            freq=self._freq)

        index = np.searchsorted(date_range, date_filter)
        if model.seasonal_order is None:
            # When seasonal_order isn't set in the pmdarima model, we should be dealing with statsmodel Arima
            # instead of SARIMAX
            # statsmodels is buggy - so catch exceptions here and default to returning zeros for in-sample preds
            # in-sample predictions are not essential for selection or forecasting so this is the least bad option
            # Don't return NaNs because the runner fails if predictions contain NaN values.
            try:
                n_ar, n_diff, _ = model.order
                if n_diff > 0:
                    # pmdarima can only return predictions from the differenced series here, so call statsmodels
                    # ARIMAResults object directly with the 'levels' arg to force the desired output
                    pred = model.arima_res_.predict(typ='levels')
                else:
                    pred = model.arima_res_.predict()
                n_padding = n_ar + n_diff
                if n_padding > 0:
                    # ARIMA predictions aren't available for the beginning of the series if the model
                    # has autoregressive components and/or has been differenced, so pad the beginning with zeros
                    # in order to align prediction output with the date grid
                    padding = np.zeros(n_padding)
                    pred = np.concatenate((padding, pred))
            except Exception:
                pred = np.zeros(date_range.shape[0])
        else:
            pred = model.predict_in_sample(start=0, end=date_range.shape[0])

        # In case of unforeseen statsmodels bugs around in-sample prediction,
        # check if we will request invalid indices and prepend zeros if so.
        max_index = index.max()
        if pred.size <= max_index:
            n_more_padding = max_index - pred.size + 1
            more_padding = np.zeros(n_more_padding)
            pred = np.concatenate((more_padding, pred))

        return cast(np.ndarray, pred[index])

    def _get_forecast_single_grain_impl(self,
                                        model: Any,
                                        max_horizon: int,
                                        grain_level: GrainType,
                                        X_pred_grain: time_series_data_frame.TimeSeriesDataFrame) -> np.ndarray:

        # ARIMA (unlike Prophet) needs to have a meaningful max horizon
        if max_horizon <= 0:
            raise exceptions.DataException(model_wrappers.ForecastingPipelineWrapper.FATAL_NONPOSITIVE_HORIZON,
                                           has_pii=False)

        if len(X_pred_grain.columns) > 1:
            import warnings
            warnings.warn('ARIMA(not-X) ignoring extra features, only predicting from the target')

        pred = model.predict(n_periods=int(max_horizon))

        aligned_pred = self.align_out(in_sample=False, pred=pred, X_pred_grain=X_pred_grain,
                                      X_fit_grain=time_series_data_frame.TimeSeriesDataFrame(None, None),
                                      max_horizon=max_horizon, freq=self._freq)

        return aligned_pred

    def _fit_single_grain_impl(self, X_pred_grain: pd.DataFrame, grain_level: GrainType) -> Any:
        """
        Fit ARIMA model on one grain.

        :param X_pred_grain: The data frame with one grain.
        :param grain_level: The name of a grain.
        """
        # Let's warn for now, eventually we'll get the metadata on what the
        # target column is (if different from dummy) and then we can decide
        #  to ignore the rest or incorporate into ARIMAX
        try:
            if len(X_pred_grain.columns) > 1:
                import warnings
                warnings.warn('ARIMA can only predict from training data forward and does not take extra features')

            series_values = X_pred_grain[constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN].values.astype(float)
            if len(series_values) < constants.TimeSeriesInternal.ARIMA_TRIGGER_CSS_TRAINING_LENGTH:
                # for short series, uses MLE training via statsmodels SARIMAX class
                model = pmdarima.auto_arima(series_values, error_action="ignore")
            else:
                # for long series, use CSS training (faster for longer series, less accurrate)
                # note: as of pmdarima 1.5.1, SARIMAX only is provided (no CSS option, slower training)
                model = pmdarima.auto_arima(series_values, error_action="ignore", seasonal=False, method="CSS")

        except Exception as arima_model_fit_fail:
            logger.warning('Fitting Arima model failed on one grain.')
            logging_utilities.log_traceback(arima_model_fit_fail, logger, is_critical=True,
                                            override_error_msg='[Masked as it may contain PII]')
            code_name = ReferenceCodes._FORECASTING_MODELS_ARIMA_NO_MODEL
            raise exceptions.ClientException._with_error(AzureMLError.create(ForecastingArimaNoModel,
                                                         target='pmdarima_internal',
                                                         reference_code=code_name))
        return model
