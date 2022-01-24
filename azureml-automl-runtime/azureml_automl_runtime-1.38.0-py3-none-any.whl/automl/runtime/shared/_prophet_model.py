# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""The wrapper for Facebook Prophet model."""
import sys
from typing import Optional, Any, Dict, Union, cast

import logging

import numpy as np
import pandas as pd

from azureml.automl.core.shared import (
    constants,
    import_utilities,
    utilities)
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared.types import GrainType
from azureml.automl.runtime.shared import time_series_data_frame
from azureml.automl.runtime.shared._multi_grain_forecast_base import _MultiGrainForecastBase

logger = logging.getLogger(__name__)

IMPORT_ERROR = "Unable to import fbprophet."
try:
    # Optional import of fbprophet.
    import fbprophet
except Exception:
    # If fbprophet is not installed we will throw error during
    # model fitting.
    logger.warning(IMPORT_ERROR)


class ProphetModel(_MultiGrainForecastBase):
    """Prophet multigrain forecasting model."""
    # "ds" and "y" are hard coded name of time and target columns in prophet package.
    PROPHET_TIME_COLUMN = 'ds'
    PROPHET_TARGET_COLUMN = 'y'

    def __init__(self, timeseries_param_dict: Dict[str, Any],
                 prophet_param_dict: Optional[Dict[str, Union[int, str]]] = None):
        """
        Construct an instance of the Prophet forecasting model.

        Accepts external regressors, which must be numeric-encoded
        (using LabelEncode, OneHotEncode, whatever, but not actual categoricals).

        Prophet parameters are accepted as a dictionary passed as a kwarg with key
        'prophet_param_dict' (or what `constants.TimeSeriesInternal.PROPHET_PARAM_DICT` says)
        and value being the actual dictionary of Prophet parameters (?help Prophet)
        """
        super().__init__(timeseries_param_dict)

        self.prophet_param_dict = {}    # type: Dict[str, Union[int, str]]
        if prophet_param_dict:
            self.prophet_param_dict = prophet_param_dict

        # set uncertainty_samples=0 to speed up prophet forecasting step,
        # the point forecast won't be affected and would remain exactly the same
        self.prophet_param_dict['uncertainty_samples'] = 0

        # for saving the prediction intervals
        self._pred_intervals = dict()   # type: Dict[float, Any]

    def get_params(self, deep=True):
        params = super().get_params(deep)
        params["prophet_param_dict"] = self.prophet_param_dict
        return params

    def _fit_in_sample_single_grain_impl(self,
                                         model: Any,
                                         grain_level: GrainType,
                                         X_grain: time_series_data_frame.TimeSeriesDataFrame) -> np.ndarray:
        fitted = self._get_forecast_single_grain_impl(model, 0, grain_level, X_grain)
        return fitted

    def _rename_time_column(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Rename the time column so that it will correspond to prophet notation ("ds").

        *Note:* This method does not create a copy of a data frame.
        :param X: The data frame.
        :return: The data frame with time column replaced to "ds".
        """
        if isinstance(X.index, pd.MultiIndex):
            # Data frame has time and grain columns.
            X.index.rename(names=ProphetModel.PROPHET_TIME_COLUMN,
                           level=self.time_column_name, inplace=True)
        elif isinstance(X.index, pd.DatetimeIndex):
            # Data frame has only time column.
            X.index.rename(ProphetModel.PROPHET_TIME_COLUMN, inplace=True)
        else:
            # Range index. Just rename the time column.
            X.rename(columns={self.time_column_name: ProphetModel.PROPHET_TIME_COLUMN},
                     inplace=True)
        return X

    def _get_forecast_single_grain_impl(self,
                                        model: Any,
                                        max_horizon: int,
                                        grain_level: GrainType,
                                        X_pred_grain: time_series_data_frame.TimeSeriesDataFrame) -> np.ndarray:
        """
        Forecast from Prophet model.

        Respects the X_pred_grain parameter, rather than the max_horizon parameter.
        """
        df = pd.DataFrame(X_pred_grain.copy())
        df = self._rename_time_column(df)
        if constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN in df.columns and \
                constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN in df.index.names:
            df.drop(constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN, axis=1, inplace=True)

        df.reset_index(inplace=True)

        # grain = tuple(df.iloc[0][self.grain_column_names])
        # print("INFO: Scoring Prophet on " + str(grain))

        # TODO: how do forecast with Prophet if the user provides recent values
        # of y in a recent context?

        preds = model.predict(df)

        # TODO: save the effects from the output.  The effect is defined as:
        # "yhat is <effect> higher due to the actual value of the extra
        # regressor
        # than it would be with the "baseline" value of the regressor
        # (which would be the mean if it was standardized as by default).

        # for predict_quantiles, predictive_samples() should be used instead of
        # predict,
        # and quantiles computed on that output

        if len(self._quantiles) == 1 and self._quantiles[0] == 0.5:
            if not X_pred_grain.time_index.is_monotonic:
                # if the input was not sorted, prophet will sort it for us.
                # we need to un-do the reordering in this case.
                index = X_pred_grain.time_index.values.argsort().argsort()
                return cast(np.ndarray, preds['yhat'].values[index])
            else:
                return cast(np.ndarray, preds['yhat'].values)
        else:
            raise NotImplementedError("Quantile forecasts from Prophet are not yet supported")

    def _fit_single_grain_impl(self,
                               series_frame: pd.DataFrame,
                               grain_level: GrainType) -> Any:
        """
        Fit prophet model on one grain.

        :param series_frame: The data frame with one grain.
        :param grain_level: The name of a grain.
        """
        # Make sure fbprophet is installed
        Contract.assert_true(
            'fbprophet' in sys.modules, message="Missing module: fbprophet", target='forecasting_import',
            reference_code=ReferenceCodes._FORECASTING_MODELS_IMPORT, log_safe=True
        )

        # get the data in the shape prophet expects: 'ds' for time and 'y' for
        # target

        # also, series_frame is a TSDF pandas dataframe with time and grain in multi-index
        df = pd.DataFrame(series_frame.copy())
        df = self._rename_time_column(df)

        if constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN in df.columns and \
                constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN in df.index.names:
            df.drop(constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN, axis=1, inplace=True)

        df.reset_index(inplace=True)

        df.rename(
            columns={constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN: ProphetModel.PROPHET_TARGET_COLUMN},
            inplace=True)

        cols_to_ignore = [ProphetModel.PROPHET_TIME_COLUMN,
                          ProphetModel.PROPHET_TARGET_COLUMN] + self.grain_column_names + self.drop_column_names
        list_of_features = [x for x in df.columns if x not in cols_to_ignore]
        # grain = tuple(df.iloc[0][self.grain_column_names])
        # print("INFO: Fitting Prophet on " + str(grain)) # doesn't print anyway even with pytest -s

        model = fbprophet.Prophet(**self.prophet_param_dict)
        if len(list_of_features) > 0:
            for feat in list_of_features:
                model.add_regressor(feat)

        # Catch the FutureWarning from Prophet
        with utilities.suppress_stdout_stderr():
            model.fit(df)

        return model
