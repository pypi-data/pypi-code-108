# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""The wrapper for Exponential Smoothing models."""

from itertools import product
from typing import Any, cast, Dict, List, Optional, Tuple, Union

import logging

import numpy as np
import pandas as pd

import statsmodels.tsa.holtwinters as holtwinters

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared import constants, exceptions, logging_utilities
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared.types import GrainType
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    ForecastingExpoSmoothingNoModel,
    TimeseriesDfInvalidArgForecastHorizon
)
from azureml.automl.core.shared._diagnostics.contract import Contract

from azureml.automl.runtime.shared import model_wrappers, time_series_data_frame
from azureml.automl.runtime.shared._multi_grain_forecast_base import _MultiGrainForecastBase

logger = logging.getLogger(__name__)


class ExponentialSmoothing(_MultiGrainForecastBase):
    """ExponentialSmoothing multigrain forecasting model."""

    def __init__(self, timeseries_param_dict: Dict[str, Any]):
        """Create an ExponentialSmoothing multi-grain forecasting model."""
        super().__init__(timeseries_param_dict)

        self.seasonality = timeseries_param_dict.get(
            constants.TimeSeries.SEASONALITY,
            constants.TimeSeriesInternal.SEASONALITY_VALUE_NONSEASONAL
        )
        Contract.assert_true(
            isinstance(self.seasonality, int) and self.seasonality >= 1,
            "Seasonality is not a positive integer.",
            log_safe=True
        )

    def _fit_in_sample_single_grain_impl(self,
                                         model: Any,
                                         grain_level: GrainType,
                                         X_grain: time_series_data_frame.TimeSeriesDataFrame) -> np.ndarray:
        """
        Retreive in sample fitted values on a single grain from Exponential Smoothing model.

        :param: model: The Exponential Smoothing model.
        :type model: Any.
        :param grain_level: The name of a grain.
        :type grain_level: GrainType.
        :param X_grain: The training data from a single grain.
        :type X_grain: time_series_data_frame.TimeSeriesDataFrame.
        :returns: In sample fitted values on a single grain from Exponential Smoothing model.
        :type: np.ndarry.

        """

        date_filter = X_grain.time_index.values
        date_argmax = self._get_date_argmax_safe(date_filter=date_filter)
        date_range = pd.date_range(
            start=self._first_observation_dates[grain_level],
            end=date_filter[date_argmax],
            freq=self._freq)

        index = np.searchsorted(date_range, date_filter)

        # statsmodels is buggy - so catch exceptions here and default to returning zeros for in-sample preds
        # in-sample predictions are not essential for selection or forecasting so this is the least bad option
        # Don't return NaNs because the runner fails if predictions contain NaN values.
        try:
            pred = model.fittedvalues
        except Exception as ex_na_in_sample_pred:
            pred = np.zeros(date_range.shape[0])
            logger.warning("In sample prediction from Exponential Smoothing fails, and NA's are imputed as zeros.")
            logging_utilities.log_traceback(
                ex_na_in_sample_pred,
                logger,
                is_critical=False
            )

        # In case of unforeseen statsmodels bugs around in-sample prediction,
        # check if we will request invalid indices and prepend zeros if so.
        max_index = index.max()
        if pred.size <= max_index:
            n_more_padding = max_index - pred.size + 1
            more_padding = np.zeros(n_more_padding)
            pred = np.nan_to_num(np.concatenate((more_padding, pred)), copy=False)

        # In case of the in sample prediction of statsmodels didn't fail completely,
        # but still produces some NA's, cast those NA's to zeros.
        return cast(np.ndarray, np.nan_to_num(pred[index], copy=False))

    def _get_forecast_single_grain_impl(self,
                                        model: Any,
                                        max_horizon: int,
                                        grain_level: GrainType,
                                        X_pred_grain: time_series_data_frame.TimeSeriesDataFrame) -> np.ndarray:
        """
        Forecast on a single grain from Exponential Smoothing model.

        :param: model: The Exponential Smoothing model.
        :type model: Any.
        :param max_horizon: The maximum horizon of the forecast.
        :type: max_horizon: int.
        :param grain_level: The name of a grain.
        :type grain_level: GrainType
        :param X_pred_grain: The data frame with one grain.
        :type X_pred_grain: pd.DataFrame
        :returns: The forecast on a single grain from Exponential smoothing model.
        :type: np.ndarray

        """

        # ExponentialSmoothing needs to have a meaningful max horizon
        if max_horizon <= 0:
            raise exceptions.DataException._with_error(
                AzureMLError.create(
                    TimeseriesDfInvalidArgForecastHorizon,
                    reference_code=ReferenceCodes._TSDF_INVALID_ARG_MAX_HORIZON_VAL3
                )
            )

        # Impute NA's in forecast with 0 for now
        pred = np.nan_to_num(model.forecast(steps=int(max_horizon)), copy=False)

        return self.align_out(in_sample=False, pred=pred, X_pred_grain=X_pred_grain,
                              X_fit_grain=time_series_data_frame.TimeSeriesDataFrame(None, None),
                              max_horizon=max_horizon, freq=self._freq)

    def _model_selection_exponential_smoothing(self, X_pred_grain: pd.DataFrame, grain_level: GrainType) -> Any:
        """
        Select the best model from a family of Exponential Smoothing models on one grain,
        by Corrected Akaike's Information Criterion (AICc).

        :param X_pred_grain: The data frame with one grain.
        :type X_pred_grain: pd.DataFrame
        :param grain_level: The name of a grain.
        :type: grain_level: GrainType
        :returns: The Exponential smoothing model.
        :type: Any.
        """

        series_values = X_pred_grain.get(constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN).values.astype(float)

        # Internal function for fitting a statsmodel ExponentialSmoothing model
        #  and determining if a model type should be considered in selection
        # ------------------------------------------------------------------

        def fit_sm(model_type):
            trend_type, seas_type, damped = model_type

            char_to_statsmodels_opt = {'A': 'add', 'M': 'mul', 'N': None}
            exponential_smoothing_model = \
                holtwinters.ExponentialSmoothing(
                    series_values,
                    trend=char_to_statsmodels_opt[trend_type],
                    seasonal=char_to_statsmodels_opt[seas_type],
                    damped=damped,
                    seasonal_periods=self.seasonality)
            try:
                return exponential_smoothing_model.fit()
            except Exception as ex_model_fit_fail:
                logger.warning(
                    "Fitting of an individual exponential smoothing model failed (model selection could still "
                    "be successful if there is at least one successful fit from a family of models.)"
                )
                logging_utilities.log_traceback(
                    ex_model_fit_fail,
                    logger,
                    is_critical=False
                )

        def model_is_valid(model_type, has_zero_or_neg):
            trend_type, seas_type, damped = model_type

            if trend_type == 'N' and damped:
                return False

            if (trend_type == 'M' or seas_type == 'M') \
                    and has_zero_or_neg:
                return False

            return True
        # ------------------------------------------------------------------

        # Make a grid of model types and select the one with minimum aicc
        has_zero_or_neg = (series_values <= 0.0).any()

        # According to Hyndman (the author of fpp3: Forecatsting: Principles and Practice),
        # multiplicative trend models lead to poor forecast and are not considered.
        # The statsmodels Exponential Smoothing (Holt Winters for now) implementation follows Hyndman's book,
        # so the multiplicative trend models are also not included in the model selection.
        trend_grid = ['A', 'N']

        # holtwinters implementation in statsmodels requires seasonality > 1 for seasonal models,
        # so we enforce it here.
        if self.seasonality > 1:
            seasonal_grid = ['A', 'M', 'N']
        else:
            seasonal_grid = ['N']
        damped_grid = [True, False]
        type_grid = product(trend_grid, seasonal_grid, damped_grid)
        fit_models = {
            mtype: fit_sm(mtype) for mtype in type_grid if model_is_valid(mtype, has_zero_or_neg)
        }
        fit_models = {mtype: model for mtype, model in fit_models.items() if model is not None}
        if len(fit_models) == 0:
            raise exceptions.FitException._with_error(
                AzureMLError.create(
                    ForecastingExpoSmoothingNoModel,
                    reference_code=ReferenceCodes._FORECASTING_MODELS_EXPOSMOOTHING_NO_MODEL,
                    time_series_grain_id=grain_level
                )
            )

        best_type, model = min(fit_models.items(), key=lambda it: getattr(it[1], 'aicc', float('inf')))

        return model

    def _fit_single_grain_impl(self, X_pred_grain: pd.DataFrame, grain_level: GrainType) -> Any:
        """
        Train the Exponential Smoothing model on one grain.

        :param X_pred_grain: The data frame with one grain.
        :type X_pred_grain: pd.DataFrame
        :param grain_level: The name of a grain.
        :type: grain_level: GrainType
        :returns: The Exponential smoothing model.
        :type: Any.

        """
        return self._model_selection_exponential_smoothing(X_pred_grain, grain_level)
