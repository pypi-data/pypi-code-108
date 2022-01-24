# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for creating training dataset from dapaprep Dataflow object."""
from typing import Any, Optional
from azureml.automl.core.shared.exceptions import ArgumentException

import numpy as np
import pandas as pd
from azureml.contrib.automl.dnn.forecasting.wrapper import _wrapper_util

from ..constants import ForecastConstant
from ..types import DataInputType, TargetInputType
from .timeseries_datasets import TimeSeriesDataset, DNNTimeSeriesDatasetBase
from .eval_timeseries_datasets import ValidationTimeSeriesDataset, ValidationTimeSeriesDatasetFromTrainValid


class DNNTimeseriesDatasets:
    """This class provides a dnn timeseries datasets for training and validations."""

    def __init__(self,
                 X_train: DataInputType,
                 y_train: TargetInputType,
                 X_valid: DataInputType,
                 y_valid: TargetInputType,
                 horizon: int,
                 step: int = 1,
                 has_past_regressors: bool = False,
                 one_hot: bool = False,
                 save_last_lookback_data: bool = False,
                 **settings: Any) -> TimeSeriesDataset:
        """
        Create timeseries datasets for training and validation.

        :param X_train: Training features in DataPrep DataFlow form(numeric data of shape(row_count, feature_count).
        :param y_train: Training label in DataPrep DataFlow for with shape(row_count, 1).
        :param X_valid: Training features in DataPrep DataFlow form(numeric data of shape(row_count, feature_count).
        :param y_valid: Training label in DataPrep DataFlow for with shape(row_count, 1).
        :param horizon: Number of time steps to forecast.
        :param step: Time step size between consecutive examples.
        :param has_past_regressors: data to populate past regressors for each sample
        :param one_hot: one_hot encode or not
        :param save_last_lookback_data: to save the last lookbackup items for future inferene when contsxt missing.
        :param min_grain_for_embedding: number of samples in the grain to enable embedding.
        :param grain_feature_col_prefix: prefix column name of transformed grains.
        :param settings: automl timeseries settings
        """
        self.settings = settings
        X_df, y_df = _wrapper_util.convert_X_y_to_pandas(X_train, y_train)
        self._X_df = X_df.copy()
        self._y_df = y_df.copy()
        self._lookback = None
        self.inference_lookback = None
        self._horizon = horizon
        self._X_valid_df, self._y_valid_df = None, None
        self._save_last_lookback_data = save_last_lookback_data
        self._step = step

        if X_valid is not None:
            self._X_valid_df, self._y_valid_df = _wrapper_util.convert_X_y_to_pandas(X_valid, y_valid)

        self.dataset = TimeSeriesDataset(X_df,
                                         y_df,
                                         horizon,
                                         step,
                                         has_past_regressors=has_past_regressors,
                                         one_hot=one_hot,
                                         save_last_lookback_data=save_last_lookback_data,
                                         **settings)
        self.ds_train = self.dataset
        self.ds_valid = None
        grains = settings.get(ForecastConstant.grain_column_names, None) if settings else None
        self._grains = [grains] if isinstance(grains, str) else grains
        self._time_column = settings.get(ForecastConstant.automl_constants.TimeSeries.TIME_COLUMN_NAME)

    def set_lookback(self, lookback: int):
        """
        Set the lookback for the datasets, so the samples for training can be generated.

        :param lookback: lookback to create samples.
        """
        self._lookback = lookback
        self.dataset.set_lookback(lookback)
        if self._X_valid_df is not None:
            self._X_valid_df, self._y_valid_df = prepend_lookback_to_validation_set(self._X_valid_df,
                                                                                    self._y_valid_df,
                                                                                    self.dataset, self.settings)
        self._set_train_valid_datasets()

    def _set_train_valid_datasets(self):
        """Set the train and validation sets based on the training config."""
        if self._X_valid_df is not None:
            ds_valid = TimeSeriesDataset(self._X_valid_df, self._y_valid_df, self._horizon, self._horizon,
                                         sample_transform=self.dataset.sample_transform, embedding_enabled=False,
                                         save_last_lookback_data=True,
                                         **self.settings)
            ds_valid.set_lookback(self._lookback)

            self.ds_train = self.dataset
            self.ds_valid = ValidationTimeSeriesDatasetFromTrainValid(self.ds_train, ds_valid)
        else:
            self.ds_train, self.ds_valid = self.dataset.get_train_test_split()
            self.ds_valid = self.convert_to_validation_dataset(self.ds_valid)

    def get_last_lookback_items(self):
        """Get the lookback items(history) to be used with inference when lookback is missing."""
        if self.inference_lookback is None:
            train_lookup = self.dataset.get_last_lookback_items()
            if self.ds_valid is not None:
                valid_lookup = self.dataset.get_last_lookback_items()
                if self._grains:
                    train_gpby = train_lookup.groupby(self._grains)
                    valid_gpby = valid_lookup.groupby(self._grains)
                    grain_list = [df.reset_index() for _, df in valid_gpby]
                    for key, gpby_train_df in train_gpby:
                        if key not in valid_gpby:
                            grain_list.append(gpby_train_df.reset_index())
                    inf_df = pd.concat(grain_list) if len(grain_list) > 1 else grain_list[0]
                else:
                    inf_df = valid_lookup
            else:
                inf_df = train_lookup
            self.inference_lookback = inf_df
        return self.inference_lookback

    def __len__(self):
        """Return the number of samples in the dataset.

        :return: number of samples.
        """
        return len(self.dataset)

    def convert_to_validation_dataset(self, val_dataset: DNNTimeSeriesDatasetBase):
        """
        Convert the dataset into a ValidationTimeseriesDataset for eveluation.

        :param val_dataset: the dataset to be converted.
        """
        # convert to ValidationDataset for evaluation.
        return ValidationTimeSeriesDataset(val_dataset._data_grains, val_dataset.horizon, val_dataset.lookback,
                                           len(val_dataset), val_dataset.dset_config, val_dataset.step,
                                           val_dataset.has_past_regressors, val_dataset.sample_transform,
                                           val_dataset.fetch_y_only, val_dataset.cross_validation)

    @property
    def dset_config(self):
        """Dataset configs used in this training."""
        return self.dataset.dset_config

    @property
    def embedding_col_infos(self):
        """List of embedding candidate columns."""
        return self.dataset.embedding_col_infos


def create_timeseries_datasets(X_train: DataInputType,
                               y_train: TargetInputType,
                               X_valid: DataInputType,
                               y_valid: TargetInputType,
                               horizon: int,
                               step: int = 1,
                               has_past_regressors: bool = False,
                               one_hot: bool = False,
                               save_last_lookback_data: bool = False,
                               **settings: Any) -> DNNTimeseriesDatasets:
    """
    Create a timeseries dataset.

    :param X_train: Training features in DataPrep DataFlow form(numeric data of shape(row_count, feature_count).
    :param y_train: Training label in DataPrep DataFlow for with shape(row_count, 1).
    :param X_valid: Training features in DataPrep DataFlow form(numeric data of shape(row_count, feature_count).
    :param y_valid: Training label in DataPrep DataFlow for with shape(row_count, 1).
    :param horizon: Number of time steps to forecast.
    :param step: Time step size between consecutive examples.
    :param has_past_regressors: data to populate past regressors for each sample
    :param one_hot: one_hot encode or not
    :param save_last_lookback_data: to save the last lookbackup items for future inferene when contsxt missing.
    :param min_grain_for_embedding: number of samples in the grain to enable embedding.
    :param grain_feature_col_prefix: prefix column name of transformed grains.
    :param settings: automl timeseries settings
    """
    X_df, y_df = _wrapper_util.convert_X_y_to_pandas(X_train, y_train)
    X_valid_df, y_valid_df = None, None

    if X_valid is not None:
        X_valid_df, y_valid_df = _wrapper_util.convert_X_y_to_pandas(X_valid, y_valid)

    return DNNTimeseriesDatasets(X_df,
                                 y_df,
                                 X_valid_df,
                                 y_valid_df,
                                 horizon,
                                 step,
                                 has_past_regressors=has_past_regressors,
                                 one_hot=one_hot,
                                 save_last_lookback_data=save_last_lookback_data,
                                 **settings)


def prepend_lookback_to_validation_set(X_valid: pd.DataFrame, y_valid: pd.DataFrame,
                                       X_train_ds: TimeSeriesDataset, settings: dict):
    """
    Add the lookbacks for the validation dataset.

    :param X_valid: Validation feature dataframe to add the lookback.
    :param y_valid: Validation label dataframe to add the lookback.
    :param X_train_ds: Training dataset to take the lookup from.
    :param settings: Automl settings for the training.
    """
    grains = settings.get(ForecastConstant.grain_column_names, None) if settings else None
    lookup = X_train_ds.get_last_lookback_items()
    val_index = X_valid.index.names
    dummy_target_column_name = ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN
    X_valid.insert(0, dummy_target_column_name, y_valid.values)
    if grains is None:
        X_valid = X_valid.append(lookup.reset_index().set_index(val_index))
    else:
        X_valid = X_valid.copy()
        X_valid_groupby = X_valid.groupby(grains)
        lookup_groupby = lookup.groupby(grains)
        lookup_dict = {key: df for key, df in lookup_groupby}
        X_list = []
        for key in X_valid_groupby.groups:
            if key in lookup_dict:
                lookup = lookup_dict[key].reset_index().set_index(val_index)
                X_list.append(lookup)
        if len(X_list) > 0:
            X_list.append(X_valid)
        X_valid = pd.concat(X_list)
    y_valid = X_valid.pop(dummy_target_column_name)
    return X_valid, y_valid
