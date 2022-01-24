# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module containing abstract class for DNNForecastWrapper and DNNParams."""
import copy
from datetime import datetime
import logging
import sys

import azureml.dataprep as dprep
import numpy as np
import pandas as pd
import torch
from typing import Any, Dict, List, Optional, Union
from torch.utils.data import DataLoader

from ..constants import ForecastConstant
from ..datasets.timeseries_inference_datasets import TimeSeriesInferenceDataset
from ..datasets.timeseries_datasets import TimeSeriesDataset
from ..types import DataInputType, TargetInputType
from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty
from azureml.automl.core.shared._diagnostics.automl_error_definitions import TimeseriesNothingToPredict
from azureml.automl.core.shared._diagnostics.validation import Validation
from azureml.automl.core.shared.exceptions import ClientException, DataException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime.featurizer.transformer.timeseries.timeseries_transformer import TimeSeriesTransformer
from azureml.automl.runtime.shared.model_wrappers import ForecastingPipelineWrapper
from azureml.contrib.automl.dnn.forecasting.wrapper import _wrapper_util
from torch.utils.data.distributed import DistributedSampler


class DNNParams:
    """This class is used in storing the DNN parameters for various forecast models."""

    def __init__(self,
                 required: List[str],
                 params: Dict[str, Any],
                 defaults: Optional[Dict[str, Any]] = None):
        """Initialize the object with required, default and passed in parameters.

        :param required: Required parameters for this Model, used in validation.
        :param params:  parameters passed.
        :param defaults: Default parameter if a required parameter is not passed.
        """
        self._required = required.copy() if required else {}
        self._params = params.copy() if params else {}
        self._data_for_inference = None
        self._init_defaults_for_missing_required_parameters(defaults if defaults else {})

    def set_parameter(self, name: str, value: Any) -> None:
        """Set the parameter with the passed in value.

        :param name: name of the parameter to set/update.
        :param value: value to set.
        :return: None
        """
        self._params[name] = value

    def _init_defaults_for_missing_required_parameters(self, defaults) -> None:
        """Set default values for missing required parameters.

        :return:
        """
        for name in self._required:
            if name not in self._params:
                if name in defaults:
                    self._params[name] = defaults[name]
                else:
                    raise ClientException._with_error(AzureMLError.create(
                        ArgumentBlankOrEmpty, target="defaults", argument_name=name,
                        reference_code=ReferenceCodes._TCN_EMPTY_REQUIRED_PARAMETER)
                    )

    def get_value(self, name: str, default_value: Any = None) -> Any:
        """Get the value from the parameter or default dictionary.

        :param name: name of the parameter to get the values for.
        :param default_value: default value to use in case param is unset or not found
        :return:
        """
        if name in self._params:
            value = self._params.get(name)
            if value is None:
                value = default_value
            return value
        return default_value

    def __str__(self) -> str:
        """Return the string printable representation of the DNNParams.

        :return:
        """
        return str(self._params)


class _InferenceGrainContext:
    """This class is used in storing the DNN parameters for various forecast models."""

    def __init__(self,
                 grain: List[str],
                 forecast_origin: datetime,
                 context_grain_df: Optional[pd.DataFrame] = None,
                 transformed_grain_df: Optional[pd.DataFrame] = None):
        """Initialize the object with required, default and passed in parameters.

        :param grain: List of keys for the grain.
        :param grain_df:  a dataframe contains a grain
        :param forecast_origin: forecast origin for the series/grain.
        :param context_grain_df: context for prediction coming from data saved with model for lookback.
        :param transformed_grain_df: context for prediction coming from data saved with model for lookback.
        """
        self.grain = grain
        self.forecast_origin = forecast_origin
        self.context_grain_df = context_grain_df
        self.transformed_grain_df = transformed_grain_df


class DNNForecastWrapper(torch.nn.Module):
    """This is the abstract class for Forecast DNN Wrappers."""

    def __init__(self):
        """Initialize with defaults."""
        super().__init__()
        self.input_channels = None
        self.params = None
        self.output_channels = 1
        self._pre_transform = None
        self._sample_transform = None
        self.forecaster = None
        self._data_for_inference = None
        self.batch_transform = None

    def train(self, n_epochs: int, X: DataInputType = None, y: DataInputType = None,
              X_train: DataInputType = None, y_train: DataInputType = None,
              X_valid: DataInputType = None, y_valid: DataInputType = None,
              featurizer: Union[TimeSeriesTransformer] = None) -> None:
        """Start the DNN training.

        :param n_epochs: number of epochs to try.
        :param X: full set of data for training.
        :param y: fullsetlabel for training.
        :param X_train: training data to use.
        :param y_train: validation data to use.
        :param X_valid: validation data to use.
        :param y_valid: validation target  data to use.
        :param featurizer: The trained featurizer.
        :param automl_settings: dictionary of automl settings.

        :return: Nothing, the model is trained.
        """
        raise NotImplementedError

    def predict(self, X: DataInputType, y: DataInputType, n_samples: int) -> np.ndarray:
        """Return the predictions for the passed in X and y values.

        :param X: data values
        :param y: label for look back and nan for the rest.
        :param n_samples:  number samples to be retured with each prediction.
        :return: a tuple containing one dimentional prediction of ndarray and tranformed X dataframe.
        """
        raise NotImplementedError

    def get_lookback(self):
        """Return the lookback."""
        raise NotImplementedError

    def forecast(self, X: DataInputType, y: Optional[TargetInputType] = None) -> tuple:
        """Return the predictions for the passed in X and y values.

        :param X: data values
        :param y: label for look back and nan for the rest.
        :return: a ndarray of samples X rows X horizon
        """
        Validation.validate_value(X, 'X')
        Validation.validate_type(X, 'X', (pd.DataFrame, dprep.Dataflow))
        settings = self.automl_settings
        time_column = settings[ForecastConstant.time_column_name]
        horizon = self.params.get_value(ForecastConstant.Horizon)
        looback = self.get_lookback()
        target_column = ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN
        saved_data = self._data_for_inference
        y = pd.DataFrame([np.nan] * X.shape[0]) if y is None else y.copy()

        X, y = _wrapper_util.convert_X_y_to_pandas(X, y)
        X = self._try_set_time_column_data_type(X, time_column)
        if not isinstance(y, pd.DataFrame):
            y = pd.DataFrame(y)
        X[target_column] = y.values
        X_orig = X.copy()
        grains = None
        if ForecastConstant.automl_constants.TimeSeries.GRAIN_COLUMN_NAMES in settings:
            grains = settings[ForecastConstant.automl_constants.TimeSeries.GRAIN_COLUMN_NAMES]
        index_names = [time_column] + grains if grains else [time_column]

        # get the forcast origin for each of the grain and grain data frame.
        grain_inf_conext_list = self._get_inference_grain_context_list(grains, X, y, time_column,
                                                                       target_column, saved_data)

        X_predicted_labels = self._recursive_forecast(grain_inf_conext_list, looback,
                                                      horizon, time_column, target_column)
        # set the frames with same data type on date and with no index for merge.
        X_orig.reset_index(inplace=True)
        X_predicted_labels.reset_index(inplace=True)
        X_orig = self._try_set_time_column_data_type(X_orig, time_column)
        X_predicted_labels = self._try_set_time_column_data_type(X_predicted_labels, time_column)
        result = _wrapper_util.align_results(X_orig, X_predicted_labels, target_column, True, index_names)
        return result[target_column].values, result

    def _get_inference_grain_context_list(self, grains: List[str], X: pd.DataFrame, y: pd.DataFrame,
                                          time_column: str, target_column: str,
                                          saved_data: pd.DataFrame) -> List[_InferenceGrainContext]:
        """Return the list of grain details for inference.

        :param X: data values
        :param y: label for look back and nan for the rest.
        :param time_column: time_column name.
        :param target_column: target column nanem.
        :return: a list of InferenceGrainContexts
        """
        grain_inf_conext_list = []
        if grains:
            grouped_X = X.groupby(grains)
            for grain, grain_df in grouped_X:
                forecast_origin = self._get_grain_forecast_origin(grain_df, time_column, target_column)
                grain_inf_conext_list.append(_InferenceGrainContext(grain, forecast_origin))
        else:
            forecast_origin = self._get_grain_forecast_origin(X, time_column, target_column)
            grain_inf_conext_list.append(_InferenceGrainContext(None, forecast_origin))
        # Fix the frequency.
        grains_list = grains if grains else []
        X, y = ForecastingPipelineWrapper.static_preaggregate_data_set(self._pre_transform, time_column,
                                                                       grains_list, X, y)
        X_transformed, y_transformed = _wrapper_util.transform_data(self._pre_transform, X, y)

        if target_column not in X_transformed.columns:
            X_transformed[target_column] = y_transformed.values
            if grains:
                grouped_X_transformed = X_transformed.groupby(grains)
                grouped_saved_data = saved_data.groupby(grains)

            for grain_inf_context in grain_inf_conext_list:
                if grain_inf_context.grain:
                    grain_inf_context.transformed_grain_df = grouped_X_transformed.get_group(grain_inf_context.grain)
                    if grain_inf_context.grain in grouped_saved_data.groups:
                        grain_inf_context.context_grain_df = grouped_saved_data.get_group(grain_inf_context.grain)
                    else:
                        grain_inf_context.context_grain_df = saved_data[0:0]
                else:
                    grain_inf_context.transformed_grain_df = X_transformed
                    grain_inf_context.context_grain_df = saved_data
        return grain_inf_conext_list

    def _recursive_forecast(self, grain_inf_context_list: List[Dict],
                            looback: int, horizon: int, time_column: str, target_column: str) -> pd.DataFrame:
        """Return the predictions for the passed in X and y values.

        :param grain_inf_context: list of inference contexts.
        :param looback: look back of the data.
        :param horizon: horizon related to this model.
        :param time_column: Time column name in the dataset.
        :param target_column: label to predict.
        :return: a data frame contains the prediction in target column.
        """
        result_list = []
        for grain_inf_context in grain_inf_context_list:
            result_list.append(self._recursive_forecast_grain(grain_inf_context, looback,
                                                              horizon, time_column, target_column))
        X_with_predicted_y = result_list[0] if len(result_list) == 1 else pd.concat([item for item in result_list])
        return X_with_predicted_y

    def _recursive_forecast_grain(self, grain_inf_context: Dict,
                                  lookback: int, horizon: int, time_column: str, target_column: str) -> pd.DataFrame:
        """Return the predictions for the passed in X and y values.

        :param grain_inf_context: inference contextx for a grain
        :param looback: look back of the data.
        :param horizon: horizon related to this model.
        :param time_column: time_column name.
        :param target_column: target column nanem.
        :return: a data frame contains the prediction in target column.
        """
        settings = self.automl_settings
        X_transformed = grain_inf_context.transformed_grain_df
        forecast_origin = grain_inf_context.forecast_origin
        required_horizon = (X_transformed.reset_index()[time_column] >= forecast_origin).sum()
        saved_data = grain_inf_context.context_grain_df
        y_transformed = X_transformed.pop(target_column)

        target_column = ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN
        time_column = settings[ForecastConstant.time_column_name]
        y_pred = y_transformed.copy()
        if isinstance(y_pred, pd.DataFrame):
            y_pred = y_pred.values

        window_index = len(y_pred) - required_horizon  # forecast origin for the first horizon.
        horizons_left = required_horizon

        partial_horizon = required_horizon % horizon
        padding_len = 0
        # need to pad X_transform and y_transform to full horizon.
        if (partial_horizon > 0):
            # Since we do not predict the series beyond the required
            # replicating last data item to complete the model horizon
            # as the model predict one horizon at a time and we need less
            # than horizon to return back.
            padding_len = horizon - partial_horizon
            padding_frame = pd.concat([X_transformed[-1:].reset_index()] * padding_len)
            start_time = padding_frame[-1:][time_column].squeeze()
            pad_date = pd.date_range(start_time, periods=padding_len + 1, freq='D')
            padding_frame[time_column] = pad_date[1:]
            padding_frame.set_index(X_transformed.index.names, inplace=True)
            pad_y = np.empty((padding_len,))
            y_pred = np.concatenate((y_pred, pad_y), axis=0)
            X_transformed = X_transformed.append(padding_frame)
        while horizons_left > 0:
            start_index = window_index - lookback if window_index > lookback else 0
            end_index = window_index + horizon
            X_infer = X_transformed.iloc[start_index : end_index]
            y_infer = y_pred[start_index : end_index]
            y_pred_horizon = self._predict_horizon(X_infer, y_infer, lookback, horizon, saved_data)
            y_pred[window_index : window_index + horizon] = y_pred_horizon.reshape(-1)
            horizons_left -= horizon
            window_index += horizon
        X_transformed[target_column] = y_pred
        return X_transformed

    def _predict_horizon(self, X_transformed: pd.DataFrame, y_transformed: pd.DataFrame,
                         looback: int,
                         horizon: int,
                         saved_data) -> np.ndarray:
        """Return the predictions for the passed in X and y values.

        :param X_transformed: Tramsformed DataFrame
        :param y_tranformed: label values corresponding to the transformed data.
        :param looback: look back of the data.
        :param horizon: horizon related to this model.
        :param saved_data: saved context if dataset does not have enough context.
        :return: a ndarray of one horizon predictions
        """
        assert X_transformed.shape[0] >= 1
        inference_dataset = TimeSeriesInferenceDataset(X_transformed, y_transformed, saved_data, horizon, looback,
                                                       None, True, self._sample_transform, **self.automl_settings)
        return self._predict(inference_dataset)

    @classmethod
    def _try_set_time_column_data_type(cls, X: pd.DataFrame, time_column):
        try:
            if X.dtypes[time_column] != np.dtype('datetime64[ns]'):
                X = X.astype({time_column: 'datetime64[ns]'}, )
        except ValueError:
            pass
        return X

    @classmethod
    def _get_grain_forecast_origin(
            cls, X: pd.DataFrame, time_column: str, target_column: str) -> int:
        if np.any(np.isnan(X[target_column])):
            return min(X[pd.isnull(X[target_column])][time_column])
        else:
            raise DataException._with_error(
                AzureMLError.create(TimeseriesNothingToPredict), target="X",
                reference_code=ReferenceCodes._TCN_NOTHING_TO_PREDICT
            )

    def parse_parameters(self) -> DNNParams:
        """Parse parameters from command line.

        :return: returns the  DNN  param object from the command line arguments
        """
        raise NotImplementedError

    def init_model(self, settings: dict = None) -> None:
        """Initialize the model using the command line parse method.

        :param settings: automl settings such as lookback and horizon etc.
        :return:
        """
        self.params = self.parse_parameters()
        for item in settings if settings else {}:
            self.params.set_parameter(item, settings[item])

    def set_transforms(self, input_channels: int, sample_transform: Any = None) -> None:
        """Set the the training data set transformations and channels.

        :param input_channels: Number of features in tne dataset.
        :param sample_transform: transformations applied as part of tcn dataset processing.
        :return:
        """
        if self.input_channels is None:
            self.input_channels = input_channels

        if self._sample_transform is None:
            self._sample_transform = sample_transform

    def create_data_loader(
            self,
            ds: TimeSeriesDataset,
            shuffle: bool,
            batch_size: Optional[int] = None,
            sampler: Optional[DistributedSampler] = None,
            num_workers: Optional[int] = None,
            drop_last: Optional[bool] = False) -> DataLoader:
        """Create the dataloader from time series dataset.

        :param ds: TimeseriesDataset
        :param shuffle: to shuffle the data for batching.
        :param batch_size:  batch size for the training.
        :param sampler: data sampler.
        :param num_workers: number of workers for the data loader.
        :return:
        """
        if batch_size is None:
            batch_size = self.params.get_value(ForecastConstant.Batch_size)

        self.set_transforms(ds.feature_count(), ds.sample_transform)

        if num_workers is None:
            num_workers = self._get_num_workers_data_loader(dataset=ds)

        return DataLoader(
            ds,
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=num_workers,
            pin_memory=True,
            sampler=sampler,
            drop_last=drop_last)

    @staticmethod
    def _get_num_workers_data_loader(dataset: TimeSeriesDataset) -> int:
        """Get count of number of workers to use for loading data.

        :param dataset: TimeseriesDataset that will be loaded with num workers.
        :return: returns number of workers to use
        """
        # on win using num_workers causes spawn of processes which involves pickling
        # loading data in main process is faster in that case
        if sys.platform == 'win32':
            return 0
        num_cpu_core = None
        try:
            import psutil
            num_cpu_core = psutil.cpu_count(logical=False)
        except Exception:
            import os
            num_cpu_core = os.cpu_count()
            if num_cpu_core is not None:
                # heuristics assuming 2 hyperthreaded logical cores per physical core
                num_cpu_core /= 2

        if num_cpu_core is None:
            # Default to 0 to load data in main thread memory
            return 0
        else:
            return int(num_cpu_core)

    @staticmethod
    def get_arg_parser_name(arg_name: str):
        """Get the argument name needed for arg parse.(prefixed with --).

        :param arg_name: argument name to convert to argparser format.
        :return:

        """
        return "--{0}".format(arg_name)

    @property
    def automl_settings(self) -> Dict[str, Any]:
        """Get automl settings for data that model is trained on."""
        settings = self.params.get_value(ForecastConstant.automl_settings)
        return settings.copy() if settings else {}

    @property
    def primary_metric(self) -> str:
        """Get the primary the model is trained on."""
        metric = self.automl_settings.get(ForecastConstant.primary_metric, None)
        if metric is None:
            metric = self.params.get(ForecastConstant.primary_metric)
        return metric

    @property
    def name(self):
        """Name of the Model."""
        raise NotImplementedError

    def __getstate__(self) -> Dict[str, Any]:
        """
        Get state pickle-able objects.

        :return: state
        """
        state = dict(self.__dict__)

        # This is assuming that model is used for inference.
        # callbacks need to be created and set on the forecaster for retraining
        # with the new dataset
        state['loss_dict'] = {}
        state['optimizer_dict'] = {}
        if self.forecaster:
            if self.forecaster.loss:
                state['loss_dict'] = self.forecaster.loss.state_dict()
            if self.forecaster.optimizer:
                state['optimizer_dict'] = self.forecaster.optimizer.state_dict()
        state['forecaster'] = None
        return state

    def __setstate__(self, state) -> None:
        """
        Set state for object reconstruction.

        :param state: pickle state
        """
        self.__dict__.update(state)
