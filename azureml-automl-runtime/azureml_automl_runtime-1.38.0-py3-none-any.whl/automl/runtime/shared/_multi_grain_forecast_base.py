# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""The abstract class for fitting one model per grain."""

from abc import abstractmethod
from typing import List, Tuple, Any, Optional, Dict, Union, cast, Set

import logging
import os
import uuid

import numpy as np
import pandas as pd

from joblib import Parallel, delayed

from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.automl.core import _codegen_utilities
from azureml.automl.core.shared import constants, exceptions
from azureml.automl.core.shared.types import GrainType
from azureml.automl.core.shared.exceptions import FitException, ResourceException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared._diagnostics.automl_error_definitions import InsufficientMemoryWithHeuristics

from azureml.automl.runtime.shared import (
    forecasting_utils,
    time_series_data_frame,
    memory_utilities,
    model_wrappers
)

logger = logging.getLogger(__name__)


class _MultiGrainForecastBase:
    """
    Multi-grain forecast base class.

    Enables multi-grain fit and predict on learners that normally can only operate on a single timeseries.
    """

    def __init__(self,
                 timeseries_param_dict: Dict[str, Any]):
        self.timeseries_param_dict = timeseries_param_dict
        self.time_column_name = self.timeseries_param_dict[constants.TimeSeries.TIME_COLUMN_NAME]
        self.grain_column_names = self.timeseries_param_dict.get(constants.TimeSeries.GRAIN_COLUMN_NAMES, [])
        self.grain_column_names = [constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN] if \
            self.grain_column_names is None or len(self.grain_column_names) == 0 else self.grain_column_names
        self.drop_column_names = self.timeseries_param_dict.get(constants.TimeSeries.DROP_COLUMN_NAMES, []) or []
        self._max_cores_per_iteration = self.timeseries_param_dict.get(constants.TimeSeries.MAX_CORES_PER_ITERATION, 1)

        # model state
        self._grain_levels = []  # type: List[GrainType]
        self._models = {}  # type: Dict[GrainType, Any]
        self._last_observation_dates = {}  # type: Dict[GrainType, pd.Timestamp]
        self._first_observation_dates = {}  # type: Dict[GrainType, pd.Timestamp]
        self._last_observation_values = {}  # type: Dict[GrainType, float]
        self._freq = None  # type: Optional[pd.DateOffset]
        self._is_fit = False
        self._estimator_type = constants.TimeSeriesInternal.FORECASTER_ESTIMATOR_TYPE  # type: str

        # what to predict
        self._quantiles = [.5]

    def __repr__(self) -> str:
        params = self.get_params(deep=False)
        return _codegen_utilities.generate_repr_str(self.__class__, params)

    def get_params(self, deep: bool = True) -> Dict[str, Any]:
        return {
            "timeseries_param_dict": self.timeseries_param_dict
        }

    def _get_imports(self):
        return [
            (np.array.__module__, "array", np.array)
        ]

    # TODO: duplicates code from RegressionPipeline
    # /src/automl_client_core_runtime/automl/client/core/runtime/model_wrappers.py
    # Perhaps we should make a QuantileMixin.
    @property
    def quantiles(self) -> List[float]:
        """Quantiles for the model to predict."""
        return self._quantiles

    @quantiles.setter
    def quantiles(self, quantiles: Union[float, List[float]]) -> None:
        if not isinstance(quantiles, list):
            quantiles = [quantiles]

        for quant in quantiles:
            if quant == 0:
                raise FitException(
                    "Quantile 0 is not supported.", target="quantiles",
                    reference_code="forecasting_models._MultiGrainForecastBase.quantiles.equal_0",
                    has_pii=False)
            if quant == 1:
                raise FitException(
                    "Quantile 1 is not supported.", target="quantiles",
                    reference_code="forecasting_models._MultiGrainForecastBase.quantiles.equal_1",
                    has_pii=False)
            if quant < 0 or quant > 1:
                raise FitException(
                    "Quantiles must be strictly less than 1 and greater than 0.", target="quantiles",
                    reference_code="forecasting_models._MultiGrainForecastBase.quantiles.out_of_range",
                    has_pii=False)

        self._quantiles = quantiles

    @staticmethod
    def _get_num_parallel_process(
            len_grain_levels: int,
            max_cores_per_iteration: Optional[int],
            data_set_size: int,
            avail_memory: int,
            all_memory: int) -> int:
        """Get num of process for joblib parallelism when fitting models for the grains.

        :param len_grain_levels: length of grain_levels list
        :type len_grain_levels: int
        :param max_cores_per_iteration: max_cores_per_iteration parameter input from timeseries_param_dict
        :type max_cores_per_iteration: Optional[int]
        :param data_set_size: The size of data set in bytes.
        :type data_set_size: int
        :param avail_memory: The memory available for the process.
        :type avail_memory: int
        :param all_memory: All virtual memory on the machine.
        :type all_memory: int
        :return: number of process used for joblib parallelism
        :rtype: int
        """
        # First calculate how many processors do we have.
        cpu_cnt = os.cpu_count()
        num_par_process = 1
        if cpu_cnt is not None:
            num_par_process = max(1, cpu_cnt)
        if max_cores_per_iteration is not None and max_cores_per_iteration != -1:
            num_par_process = min(num_par_process, max_cores_per_iteration)
        num_par_process = min(num_par_process, len_grain_levels)
        # Calculate if we have enough memory to branch out the num_par_process processes.
        # The amount of memory required to branch one process is approximately
        # 5 times more than memory occupied by the data set because of pickling.
        memory_per_process = data_set_size * 5 / len_grain_levels
        if num_par_process > 1:
            if data_set_size > avail_memory and memory_per_process > avail_memory:
                raise ResourceException._with_error(
                    AzureMLError.create(
                        InsufficientMemoryWithHeuristics,
                        target='available_memory',
                        reference_code=ReferenceCodes._FORECASTING_MODELS_MEM_CPU_CNT,
                        avail_mem=avail_memory,
                        total_mem=all_memory,
                        min_mem=data_set_size
                    ))
            num_par_process = min(num_par_process, int(avail_memory // memory_per_process))
            if num_par_process < 1:
                num_par_process = 1

        return num_par_process

    def fit(self,
            X: pd.DataFrame,
            y: np.ndarray,
            **kwargs: Any) -> None:
        """Fit the model.

        :param X: Training data.
        :type X: pd.DataFrame
        :param y: Training label
        :type y: np.ndarray
        :return: Nothing
        :rtype: None
        """
        ds_mem = memory_utilities.get_data_memory_size(X) + memory_utilities.get_data_memory_size(y)
        avail_mem = memory_utilities.get_available_physical_memory()
        all_mem = memory_utilities.get_all_ram()
        if avail_mem < ds_mem:
            raise ResourceException._with_error(
                AzureMLError.create(
                    InsufficientMemoryWithHeuristics,
                    target='available_memory',
                    reference_code=ReferenceCodes._FORECASTING_MODELS_MEM_FIT,
                    avail_mem=avail_mem,
                    total_mem=all_mem,
                    min_mem=ds_mem
                ))
        tsdf = self._construct_tsdf(X, y)
        # Make sure, we are accurate on the amount of memory uaed by data set.
        ds_mem = memory_utilities.get_data_memory_size(tsdf)

        tsdf_bygrain = tsdf.groupby_grain()
        self._grain_levels = list(tsdf_bygrain.groups)

        # Initialize the models and state variables
        self._models = {lvl: None for lvl in self._grain_levels}
        self._last_observation_dates = {
            lvl: None for lvl in self._grain_levels}
        self._first_observation_dates = {
            lvl: None for lvl in self._grain_levels}

        # compute number of parallel process in this scenario
        num_par_process = self._get_num_parallel_process(
            len(self._grain_levels),
            self._max_cores_per_iteration,
            ds_mem, avail_mem, all_mem
        )

        # if num_par_process ==1, bypass the joblib parallel fitting code since it
        # just introduces overhead
        if num_par_process == 1:
            for lvl, series_frame in tsdf_bygrain:
                lvl, first_date, last_date, last_value, model = \
                    _MultiGrainForecastBase._fit_single_grain(self, lvl, series_frame)
                self._first_observation_dates[lvl] = first_date
                self._last_observation_dates[lvl] = last_date
                self._last_observation_values[lvl] = last_value
                self._models[lvl] = model

        # if num_par_process >1, parallel model fitting for each grain
        # Note, we need to copy the data frame, obtained from the groupby
        # object, because it is implicitly generating a weakref object
        # and it will cause the pikling error when joblib will create the
        # new process.
        self._freq = tsdf.infer_freq()
        if num_par_process > 1:
            results = Parallel(n_jobs=num_par_process)(delayed(_MultiGrainForecastBase._fit_single_grain)(
                self,
                lvl[0],
                lvl[1].copy()) for lvl in tsdf_bygrain)
            # Parse results received from Parallell
            for result in results:
                lvl, first_date, last_date, last_value, model = result
                self._first_observation_dates[lvl] = first_date
                self._last_observation_dates[lvl] = last_date
                self._last_observation_values[lvl] = last_value
                self._models[lvl] = model

        self._is_fit = True

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self._is_fit:
            raise exceptions.UntrainedModelException()

        tsdf = self._construct_tsdf(X)

        max_horizons = self._get_forecast_horizons(tsdf)
        # Make a dataframe of forecasts
        fcast_df = self._get_forecast(tsdf, max_horizons)

        # Get rows containing in-sample data if any
        in_sample_data = pd.DataFrame()
        in_sample_dfs = []  # type: List[pd.DataFrame]
        for g, X_group in tsdf.groupby_grain():
            if g in self._grain_levels:
                in_sample_dfs.append(X_group.loc[X_group.time_index <= self._last_observation_dates[g]])
        in_sample_data = pd.concat(in_sample_dfs)
        del in_sample_dfs

        # Get fitted results for in-sample data
        if in_sample_data.shape[0] > 0:
            in_sample_fitted = self._fit_in_sample(in_sample_data)
            in_sample_fitted = in_sample_fitted.loc[:, fcast_df.columns]
            fcast_df = pd.concat([in_sample_fitted, fcast_df])

        # We're going to join the forecasts to the input - but first:
        # Convert X to a plain data frame and drop the prediction
        #  columns if they already exist
        point_name = constants.TimeSeriesInternal.DUMMY_PREDICT_COLUMN
        X_df = pd.DataFrame(tsdf, copy=False).drop(axis=1,
                                                   labels=[point_name],
                                                   errors='ignore')

        # Left join the forecasts into the input;
        #  the join is on the index levels
        pred_df = X_df.merge(fcast_df, how='left',
                             left_index=True, right_index=True)

        return cast(np.ndarray, pred_df[constants.TimeSeriesInternal.DUMMY_PREDICT_COLUMN].values)

    def _construct_tsdf(
        self,
        X: pd.DataFrame,
        y: Optional[np.ndarray] = None
    ) -> time_series_data_frame.TimeSeriesDataFrame:
        X = X.copy()
        # Add the Dummy grain column only if it was not already added.
        if self.grain_column_names == [constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN] and\
           self.grain_column_names[0] not in X.index.names and self.grain_column_names[0] not in X.columns:
            X[constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN] = constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN

        tsdf_kwargs = {'grain_colnames': self.grain_column_names}
        if y is not None:
            X[constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN] = y
            tsdf_kwargs['ts_value_colname'] = constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN

        X_no_origin = self._remove_origin_dependant_info_for_classical_forecasting_algo(X)

        # Handle the situation, when we have the time index with the same name as column.
        temp_column_name = None
        if isinstance(X_no_origin.index, pd.DatetimeIndex) and X_no_origin.index.names[0] == self.time_column_name:
            # DatetimeIndex is one column representing datetime.
            # We will temporary rename it and after TSDF creation we will revert the change.
            temp_column_name = str(uuid.uuid1())
            X_no_origin.rename({self.time_column_name: temp_column_name}, inplace=True, axis=1)

        tsdf_no_origin = time_series_data_frame.TimeSeriesDataFrame(
            X_no_origin,
            self.time_column_name,
            **tsdf_kwargs)
        if temp_column_name is not None:
            tsdf_no_origin.rename({temp_column_name: self.time_column_name}, inplace=True, axis=1)

        # Dropping the origin/horizon_origin index/column has to happen here, instead of inside the
        # _remove_origin_dependant_info_for_classical_forecasting_algo() function, for two reasons.
        # First, there are cases where origin/horizon_origin is the only index level before converted
        # to tsdf, and couldn't be dropped. After converted to tsdf, it's guaranteed that they're not
        # the only index level.
        # Second, converting to tsdf changes if a origin/horizon_origin is an index or a column, so the
        # drop level/columns must happen in the same place so we don't miss dropping any of them.
        for index_name in tsdf_no_origin.index.names:
            if (index_name == constants.TimeSeriesInternal.HORIZON_NAME
                    or index_name == constants.TimeSeriesInternal.ORIGIN_TIME_COLNAME_DEFAULT):
                tsdf_no_origin = tsdf_no_origin.droplevel(index_name)
        columns_to_drop = []
        for column_name in tsdf_no_origin.columns:
            if (column_name == constants.TimeSeriesInternal.HORIZON_NAME
                    or column_name == constants.TimeSeriesInternal.ORIGIN_TIME_COLNAME_DEFAULT):
                columns_to_drop.append(column_name)
        tsdf_no_origin.drop(columns_to_drop, axis=1, inplace=True)

        return tsdf_no_origin

    def _fit_in_sample(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Return the fitted values from a the RecursiveForecaster model.

        :param X:
            A TimeSeriesDataFrame defining the data for which fitted values
            are desired.  Inputting the same data used to fit the model will
            return all fitted data.
        :type X: azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame

        :Returns:
            a ForecastDataFrame containing the fitted values in `pred_point`.
        """
        point_name = constants.TimeSeriesInternal.DUMMY_PREDICT_COLUMN
        origin_name = constants.TimeSeriesInternal.ORIGIN_TIME_COLUMN_NAME

        fitted_df = pd.DataFrame()
        for g, X_grain in X.groupby_grain():
            origin_time = self._last_observation_dates[g]
            fitted = self._fit_in_sample_single_grain_impl(self._models[g], g, X_grain)
            assign_dict = {origin_name: origin_time,
                           point_name: fitted}
            X_grain = X_grain.assign(**assign_dict)

            fitted_df = pd.concat([fitted_df, X_grain])

        fitted_df = fitted_df.loc[X.index, :]

        return fitted_df

    def _get_forecast_horizons(self, X: time_series_data_frame.TimeSeriesDataFrame) -> Dict[Tuple[Any], int]:
        """
        Find maximum horizons to forecast in the prediction frame X.

        Returns a dictionary, grain -> max horizon.
        Horizons are calculated relative to the latest training
        dates for each grain in X.
        If X has a grain that isn't present in the training data,
        this method returns a zero for that grain.
        """
        # Internal function for getting horizon for a single grain

        import warnings

        def horizon_by_grain(gr, Xgr):
            try:
                horizon = len(pd.date_range(start=self._last_observation_dates[gr],
                                            end=Xgr.time_index.max(),
                                            freq=self._freq)) - 1
                # -1 because this will INCLUDE the
                # last obs date
            except KeyError:
                horizon = 0

            return horizon
        # ------------------------------------------

        fcast_horizon = {gr: horizon_by_grain(gr, Xgr)
                         for gr, Xgr in X.groupby_grain()}

        negatives = [h <= 0 for h in list(fcast_horizon.values())]
        if any(negatives):
            warnings.warn(('Non-positive forecast horizons detected. Check data for time '
                           'overlap between train and test and/or grains in test data '
                           'that are not present in training data. Failures may occur.'))

        return fcast_horizon

    def _get_forecast(self,
                      X: time_series_data_frame.TimeSeriesDataFrame,
                      max_horizon: Dict[Tuple[Any], int]) -> pd.DataFrame:
        """
        Generate forecasts up to max_horizon for each grain in X.

        The max_horizon parameter can be a single integer or
        a dictionary mapping each grain in X to an integer.

        Returns a pandas DataFrame. The index of this data frame
        will have the same levels as the input, X.
        The ouput will have the following:
        time, grain(s), origin time, point forecast.
        """
        # Get column names from X
        point_name = constants.TimeSeriesInternal.DUMMY_PREDICT_COLUMN
        origin_time_colname = constants.TimeSeriesInternal.ORIGIN_TIME_COLUMN_NAME

        grouped = X.groupby_grain()

        # Make max_horizon forecasts for each grain
        # Note: the whole prediction dataframe needs to be passed,
        # not just the grain name.

        fcast_df = pd.concat([
            self._get_forecast_single_grain(gr,
                                            grain_ctx.loc[grain_ctx.time_index > self._last_observation_dates[gr]],
                                            max_horizon[gr],
                                            X.time_colname,
                                            X.grain_colnames,
                                            origin_time_colname,
                                            point_name)
            for gr, grain_ctx in grouped])

        return fcast_df.set_index(X.index.names)

    def _get_forecast_single_grain(self,
                                   grain_level: GrainType,
                                   grain_ctx: pd.DataFrame,
                                   max_horizon: int,
                                   time_colname: str,
                                   grain_colnames: List[str],
                                   origin_time_colname: str,
                                   pred_point_colname: str) -> pd.DataFrame:
        """
        Generate forecasts up to max_horizon for a single grain.

        Returns a plain pandas Dataframe with the following columns:
        time, grain(s), origin time, point forecast,
        distribution forecast (optional).
        """
        if grain_level not in self._grain_levels or not self._models[grain_level]:

            raise exceptions.DataException(model_wrappers.ForecastingPipelineWrapper.FATAL_NO_GRAIN_IN_TRAIN,
                                           has_pii=False)
        # ---------------------------------------------------------------

        # Origin date/time is the latest training date, by definition

        # Note: this does not support the newer forecast interface which
        # allows using a training model away from training data as long
        # as sufficient context is provided.  origin data should instead
        # be computed from the prediction context dataframe (X).
        origin_date = self._last_observation_dates[grain_level]

        # Retrieve the trained model and make a point forecast
        if max_horizon <= 0:
            fcast_dict = {time_colname: np.empty(0),
                          origin_time_colname: np.empty(0),
                          pred_point_colname: np.empty(0)}
        else:
            trained_model = self._models[grain_level]
            point_fcast = self._get_forecast_single_grain_impl(trained_model,
                                                               max_horizon,
                                                               grain_level,
                                                               grain_ctx)
            # Check if any predictions from the model are missing or infinite
            problem_points = np.logical_or(np.isnan(point_fcast), np.isinf(point_fcast))
            if problem_points.any():
                # Fill problem values with a Naive forecast. ClientRunner will fail if any predictions are NaN
                # Retrieving the value needs to be wrapped in a try-catch for SDK version compatibility.
                msg = ('Prediction from {} model contained NaN or Inf values. Defaulting to Naive forecast.'
                       .format(type(self).__name__))
                logger.warning(msg)
                try:
                    last_observed_value = self._last_observation_values[grain_level]
                    if np.isnan(last_observed_value) or np.isinf(last_observed_value):
                        logger.warning('Naive forecast is NaN or Inf. Defaulting to zeros.')
                        last_observed_value = 0.0
                except Exception:
                    # If for some reason we cannot retrieve last observed value, default to zero
                    logger.warning('Unable to retrieve Naive forecast. Defaulting to zeros.')
                    last_observed_value = 0.0
                point_fcast[problem_points] = last_observed_value

            # Construct the time axis that aligns with the forecasts
            fcast_dates = grain_ctx.index.get_level_values(self.time_column_name)
            fcast_dict = {time_colname: fcast_dates,
                          origin_time_colname: origin_date,
                          pred_point_colname: point_fcast}

        if grain_colnames is not None:
            fcast_dict.update(forecasting_utils.grain_level_to_dict(grain_colnames,
                                                                    grain_level))
        return pd.DataFrame(fcast_dict)

    def _get_date_argmax_safe(self, date_filter: np.ndarray) -> int:
        """
        Get the argmax of the date filter safely.

        Note: at some point of the call frame for the local run scenario,
        the below line date_filter.argmax() will raise the below error:
        TypeError: Cannot cast array data from dtype('<M8[ns]') to dtype('<M8[us]').
        This error seems to be depending on the call frame branches and only occur rarely.
        Here we do the protection to make sure the argmax() can succeed.
        :param date_filter: The date filter array.
        :return: The argmax result.
        """
        try:
            date_argmax = date_filter.argmax()  # type: int
        except TypeError:
            if np.issubdtype(date_filter.dtype, np.datetime64):
                date_filter = date_filter.astype('datetime64[us]')
            date_argmax = date_filter.argmax()
        return date_argmax

    @staticmethod
    def _fit_single_grain(untrained_model: '_MultiGrainForecastBase',
                          lvl: GrainType,
                          series_frame: time_series_data_frame.TimeSeriesDataFrame,
                          ) -> Tuple[GrainType, pd.Timestamp, pd.Timestamp, float, Any]:
        """
        Fit the model for a single grain.

        **Note:** this method calls _fit_single_grain_impl internally.
        :param lvl: The grain level.
        :param series_frame: The data frame representing this grain.
        :return: The tuple with grain level, first date, last date and the trained model.
        """
        series_frame.sort_index()
        model = untrained_model._fit_single_grain_impl(series_frame, lvl)

        # Gather the last observation date if time_colname is set
        last = series_frame.time_index.max()
        first = series_frame.time_index.min()
        # Get the last observation value

        select_last = (series_frame.time_index == last)
        last_value = float(series_frame[select_last][constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN].iloc[0])

        return lvl, first, last, last_value, model

    @abstractmethod
    def _fit_in_sample_single_grain_impl(self,
                                         model: Any,
                                         grain_level: GrainType,
                                         X_grain: time_series_data_frame.TimeSeriesDataFrame) -> np.ndarray:
        """
        Return the fitted in-sample values from a model.

        :param model:
            is an object representation of a model. It is the
            object returned by the _fit_single_grain_impl method.

        :param grain_level:
            is an object that identifies the series by its
            grain group in a TimeSeriesDataFrame. In practice, it is an element
            of X.groupby_grain().groups.keys(). Implementers can use
            the grain_level to store time series specific state needed for
            training or forecasting. See ets.py for examples.
        :param X_grain:
            the context data for the in-sample prediction.

        :param start:
            starting frame of the in sample prediction.

        :param end:
            end frame of the in sample prediction.

        :Returns:
            a 1-D numpy array of fitted values for the training data. The data are
            assumed to be in chronological order
        """
        raise NotImplementedError()

    @abstractmethod
    def _get_forecast_single_grain_impl(self,
                                        model: Any,
                                        max_horizon: int,
                                        grain_level: GrainType,
                                        X_pred_grain: time_series_data_frame.TimeSeriesDataFrame) -> np.ndarray:
        """
        Return the forecasted value for a single grain.

        :param model:
            trained model.
        :param max_horizon:
            int that represents the max horizon.
        :param grain_level:
            tuple that identifies the timeseries the model belongs to.
        :param X_pred_grain
            a dataframe containing the prediction context
        :Returns:
            a 1-D numpy array of fitted values for the training data. The data are
            assumed to be in chronological order
        """
        raise NotImplementedError

    @abstractmethod
    def _fit_single_grain_impl(self,
                               series_values: time_series_data_frame.TimeSeriesDataFrame,
                               grain_level: GrainType) -> Any:
        """
        Return a fitted model for a single timeseries.

        :param series_values:
            an array that represents the timeseries.
        :param grain_level:
            tuple that identifies the timeseries the model belongs to.
        :Returns:
            a model object that can be used to make predictions.
        """
        raise NotImplementedError

    def align_out(self, in_sample: bool, pred: np.ndarray, X_pred_grain: time_series_data_frame.TimeSeriesDataFrame,
                  X_fit_grain: time_series_data_frame.TimeSeriesDataFrame, max_horizon: Union[int, None],
                  freq: Union[pd.DateOffset, None]) -> np.ndarray:
        date_filter = X_pred_grain.time_index.values
        if in_sample:
            date_range = X_fit_grain.reset_index()[X_pred_grain.time_colname]
        else:
            date_min = date_filter.min()
            date_range = pd.date_range(start=date_min, periods=max_horizon, freq=freq)
        index = np.searchsorted(date_range, date_filter)
        return cast(np.ndarray, pred[index])

    def _remove_origin_dependant_info_for_classical_forecasting_algo(
        self,
        X: pd.DataFrame
    ) -> pd.DataFrame:

        """
        Drop the origin-dependant info (both rows and columns) that are not useful for classical forecasting models.

        :param X:
            the featurized data that potentially contains origin-dependent lags/rolling windows,
            thus the presense of duplicated time index values is possible.
        :type X: pd.DataFrame
        :Returns:
            data with lags/rolling windows/origin columns dropped, and the time index values are unqiue.
        :rtype: pd.Dataframe
        """
        X = X.copy()

        # Drop look-back features if any, since classical forecasting models do not need them.
        timeseries_param_dict = self.timeseries_param_dict
        lagging_columns = timeseries_param_dict.get(constants.TimeSeriesInternal.LAGGING_COLUMNS, [])
        rolling_window_columns = timeseries_param_dict.get(constants.TimeSeriesInternal.ROLLING_WINDOW_COLUMNS, [])
        columns_to_drop = lagging_columns + rolling_window_columns

        X.drop(columns_to_drop, axis=1, inplace=True)

        # Our reset_index() method overrides the pandas.reset_index() method and forbids resetting the time
        # index, so we manually reset index to remove duplicates w.r.t time + grain combination.
        # The pandas groupby() function changes X's index which creates problems, and will not be used here.
        if self.time_column_name in X.index.names:
            X_index = pd.DataFrame({'_temp_time_column': X.index.get_level_values(self.time_column_name)})
        elif self.time_column_name in X.columns:
            X_index = pd.DataFrame({'_temp_time_column': X[self.time_column_name]})
        else:
            # In a normal train/forecasting settings, X is a timeseries dataframe and has to have a time column.
            # The only exception currently is when X is dump into json row by row in model explanation code.
            # Since it's a single row, remove duplicated time index wouldn't work. So just return here.
            return X
        for grain_column in self.grain_column_names:
            if grain_column == constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN and grain_column not in X.index.names:
                X_index[grain_column] = constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN
            elif grain_column in X.index.names:
                X_index[grain_column] = X.index.get_level_values(grain_column)
            elif grain_column in X.columns:
                X_index[grain_column] = X[grain_column].values
        X = X[(~X_index.duplicated()).tolist()]
        return X

    def __setstate__(self, state):
        """
        Deserialize the _MultiGrainForecastBase object from the state dict.

        :param state: a dictionary of attributes of the transformer.
        :type state: Dict[str, Any]
        """
        if '_estimator_type' not in state:
            state['_estimator_type'] = constants.TimeSeriesInternal.FORECASTER_ESTIMATOR_TYPE
        self.__dict__.update(state)
