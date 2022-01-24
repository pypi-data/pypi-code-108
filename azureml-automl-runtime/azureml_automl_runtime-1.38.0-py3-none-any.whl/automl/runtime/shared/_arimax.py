# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Union, Dict, Any, List, Optional, Set, Tuple, cast

import copy
import logging
import os
import warnings

import numpy as np
import pandas as pd
import pmdarima as pmd
import statsmodels.regression.linear_model as sm
import statsmodels.tools as st
from joblib import delayed, Parallel
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa import seasonal
from statsmodels.tsa import stattools
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX

from azureml._common._error_definition import AzureMLError
from azureml.automl.core import _codegen_utilities
from azureml.automl.core.shared import constants, exceptions, logging_utilities
from azureml.automl.core.shared.exceptions import FitException, ClientException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared.types import GrainType
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    ARIMAXOLSFitException,
    ARIMAXOLSLinAlgError)

from azureml.automl.runtime.shared import model_wrappers, time_series_data_frame
from azureml.automl.runtime.shared._multi_grain_forecast_base import _MultiGrainForecastBase
logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore")


class Arimax(_MultiGrainForecastBase):
    """The class used to train and use the SARIMAX model."""
    _TREND_TYPE = 'c'  # include intercept / constant into ARIMAX estimation

    def __init__(self,
                 timeseries_param_dict: Dict[str, Any]) -> None:
        """Create an autoarima multi-grain forecasting model."""
        # retrieve the list of raw columns
        super().__init__(timeseries_param_dict)

        # track the newly created exogenous column names for transfer function
        columns = set(timeseries_param_dict.get(constants.TimeSeriesInternal.ARIMAX_RAW_COLUMNS, []))  # type: Set[Any]

        if isinstance(self.grain_column_names, str):
            self._transfer_exogenous_colnames = list(columns - {self.time_column_name}
                                                             - {self.grain_column_names})  # type: List[Any]
        else:
            self._transfer_exogenous_colnames = list(columns - {self.time_column_name} - set(self.grain_column_names))

    def _generate_optimal_pdq(self, series: pd.Series) -> Dict[str, int]:
        """
        For any input series, use pmdarima model to fit and return the optimal combination of p, d, q
        """
        if len(series) < constants.TimeSeriesInternal.ARIMA_TRIGGER_CSS_TRAINING_LENGTH:
            # for short series, uses MLE training via statsmodels SARIMAX class
            autoarima_model = pmd.auto_arima(series, error_action="ignore")
        else:
            # for long series, use CSS training (faster for longer series, less accurrate)
            # note: as of pmdarima 1.5.1, SARIMAX only is provided (no CSS option, slower training)
            autoarima_model = pmd.auto_arima(series, error_action="ignore", seasonal=False, method="CSS")
        order = autoarima_model.order  # tuple(p,d,q)
        dic = {'p': order[0], 'd': order[1], 'q': order[2]}
        return dic

    def _generate_error_series(self, df: time_series_data_frame.TimeSeriesDataFrame) -> pd.Series:
        """
        Extract error series (n_t).
        """
        y = df[constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN]
        X = st.add_constant(df[self._transfer_exogenous_colnames])

        try:
            OLS_model = sm.OLS(y, X)
            results = OLS_model.fit()

        except np.linalg.LinAlgError as e:
            raise FitException._with_error(AzureMLError.create(ARIMAXOLSLinAlgError,
                                                               target='ArimaX_OLS',
                                                               reference_code=ReferenceCodes._ARIMAX_OLS_LIN_ALG,
                                                               error=str(e)),
                                           inner_exception=e) from e

        except Exception as e:
            logging_utilities.log_traceback(e,
                                            logger,
                                            is_critical=True,
                                            override_error_msg='[Masked as it may contain PII]')

            raise FitException._with_error(AzureMLError.create(ARIMAXOLSFitException,
                                                               target='ArimaX_OLS',
                                                               reference_code=ReferenceCodes._ARIMAX_OLS_FIT,
                                                               exception=str(e)),
                                           inner_exception=e) from e
        resid = results.resid  # type: pd.Series
        return resid  # if OLS fails we won't have residuals and arimax will fail

    def _get_forecast_single_grain_impl(self, model: Any, max_horizon: int,
                                        grain: GrainType,
                                        X_pred: time_series_data_frame.TimeSeriesDataFrame) -> np.ndarray:
        # We are using the length of X_pred instead of max_horizon b/c max_horizon uses difference in max and
        # min dates of the test dataset. If there any missing dates, forecast cannot be generated.
        if X_pred.shape[0] <= 0:
            raise exceptions.DataException(model_wrappers.ForecastingPipelineWrapper.FATAL_NONPOSITIVE_HORIZON,
                                           has_pii=False)
        # Save the time index to filter the predictions in future.
        input_index_df = X_pred.time_index.to_frame().reset_index(drop=True)
        input_index_df.columns = [self.time_column_name]
        # forecast dates in prediction instead of index numbers
        X_pred = self._infer_missing_rows(X_pred, grain)
        # Set index to the time_column_name only (tsdf.reset_index()) to use
        X_pred.reset_index(inplace=True, drop=False)
        X_pred.sort_index(inplace=True)  # sort the index
        fcst_start_date = X_pred.time_index.min()
        fcst_end_date = X_pred.time_index.max()

        exg_df = None  # in case exg_df will be empty
        if self._transfer_exogenous_colnames:
            exg_df = X_pred[self._transfer_exogenous_colnames].copy()

        pred = model.get_prediction(
            start=fcst_start_date,
            end=fcst_end_date,
            exog=exg_df,
            dynamic=False).predicted_mean
        # As we have filled the time gap, now we need to remove the extra data points.
        # Create the data frame with predictions.
        pred_df = pd.DataFrame({
            self.time_column_name: pred.index,
            constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN: pred.values})
        # Filter the data frame by existing values.
        pred_df = input_index_df.merge(pred_df, how='inner', on=self.time_column_name)
        # Return the values sorted by the input.
        return cast(np.ndarray, pred_df[constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN].values)

    def _infer_missing_rows(
            self,
            X: time_series_data_frame.TimeSeriesDataFrame,
            grain: GrainType
    ) -> time_series_data_frame.TimeSeriesDataFrame:
        """
        Infer the missing rows.

        **Note**: This code needs to be removed when we will stop removing the
        imputed rows for classical forecasting models.
        :param X: The input data frame.
        :return: The data frame with rows imputed.
        """
        X = X.fill_datetime_gap(self._freq)
        for col in X.columns:
            X[col] = X[col].ffill()
        last_observation_train = self._last_observation_dates.get(grain)
        first_observation = X.time_index.min()
        # we know the freq and last observation date
        if last_observation_train is not None and first_observation is not None and self._freq is not None:
            if last_observation_train + self._freq < first_observation:
                # if there is a gap between training set and test set
                X = X.fill_datetime_gap(self._freq, origin=last_observation_train + self._freq)
                for col in X.columns:
                    X[col] = X[col].bfill()
        return X

    def _fit_single_grain_impl(self, X_pred_grain: time_series_data_frame.TimeSeriesDataFrame,
                               grain_level: GrainType) -> Any:
        """
        Fit ARIMAX on a single grain.

        :param X_pred_grain: The data frame with one grain.
        :param grain_level: The name of a grain."""

        error_series = self._generate_error_series(X_pred_grain)  # Fit the base model and extract the error series
        values = self._generate_optimal_pdq(error_series)  # compute optimal hyperparameter values

        # reset index of the tsdf to utilize forecast by date instead of index numbers
        # TODO: Remove this workaround, when we will stop removing data for the
        # classical forecasting models.
        X_pred_grain = self._infer_missing_rows(X_pred_grain, grain_level)
        X_pred_grain.reset_index(inplace=True)
        exg_df = None  # in case exg_df will be empty
        if self._transfer_exogenous_colnames:
            exg_df = X_pred_grain[self._transfer_exogenous_colnames].copy()
        # fit the model
        target_column_name = constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN
        model = SARIMAX(
            X_pred_grain[target_column_name].copy(),
            order=(values.get('p', 0),
                   values.get('d', 0),
                   values.get('q', 0)),
            trend=Arimax._TREND_TYPE,
            # will add seasonal_order when we introduce seasonality
            exog=exg_df,
            enforce_stationarity=False,
            enforce_invertibility=False,
            freq=self._freq).fit(disp=False)
        return model

    def _fit_in_sample_single_grain_impl(self,
                                         model: Any,
                                         grain_level: GrainType,
                                         X_grain: time_series_data_frame.TimeSeriesDataFrame) -> np.ndarray:
        """
        Return the fitted in-sample values from a model.

        :param model:
            The Arimax model

        :param grain_level:
            is an object that identifies the series by its
            grain group in a TimeSeriesDataFrame. In practice, it is an element
            of X.groupby_grain().groups.keys(). Implementers can use
            the grain_level to store time series specific state needed for
            training or forecasting. See ets.py for examples.
        :param X_grain:
            the context data for the in-sample prediction. The training data from a single grain

        :param start:
            starting frame of the in sample prediction.

        :param end:
            end frame of the in sample prediction.

        :Returns:
            a 1-D numpy array of fitted values for the training data from Arimax model. The data are
            assumed to be in chronological order
        """
        date_filter = X_grain.time_index.values
        date_argmax = self._get_date_argmax_safe(date_filter=date_filter)
        date_range = pd.date_range(
            start=self._first_observation_dates[grain_level],
            end=date_filter[date_argmax],
            freq=self._freq)

        index = np.searchsorted(date_range, date_filter)

        try:
            pred = model.fittedvalues
        except Exception as ex_na_in_sample_pred:
            pred = np.zeros(date_range.shape[0])
            logger.warning("In sample prediction from Arimax fails, and NA's are imputed as zeros.")
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
