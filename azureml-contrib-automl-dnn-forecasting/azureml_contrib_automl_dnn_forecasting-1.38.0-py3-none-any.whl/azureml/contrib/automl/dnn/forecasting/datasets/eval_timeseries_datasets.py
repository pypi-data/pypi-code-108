# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for creating training dataset from dapaprep Dataflow object."""
import abc
import math
from typing import Any, List, Optional, Union

import numpy as np
import pandas as pd

from forecast.data.sources.data_source import DataSourceConfig

from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.runtime.featurizer.transformer.timeseries.timeseries_transformer import TimeSeriesTransformer
from azureml.automl.runtime.shared import _dataset_binning as binning

from ..constants import ForecastConstant
from .timeseries_datasets import TimeSeriesDataset, _DataGrainItem, DNNTimeSeriesDatasetBase


class _EvalDataset:
    """This class holds a X_valid,X_train, y_train, bin_info and ."""

    def __init__(self,
                 X_train: pd.DataFrame,
                 y_train: np.ndarray,
                 X_valid: pd.DataFrame,
                 y_valid: np.ndarray,
                 val_dataset: TimeSeriesDataset,
                 featurizer: TimeSeriesTransformer):
        """
        Create a structure needed to compute the metrics in automl.

        :param X_train: Transformed X_train.
        :param y_train: Transformed y_train.
        :param X_valid: Transformed X_valid.
        :param y_valid: Transformed y_valid.
        :param val_dataset: TIme series dataet that contains one horizon per grain to evaluate or the whole dataset.
        :param featurizer: Trained featurizer.
        """
        self.X_train = X_train
        self.y_train = y_train
        self.X_valid = X_valid
        self.y_valid = y_valid
        self.val_dataset = val_dataset
        self._featurizer = featurizer

        self.bin_info = binning.make_dataset_bins(self.y_valid.shape[-1], self.y_valid)
        y_sum = np.sum(y_train) + np.sum(y_valid)
        y_sum_square = np.sum(y_train ** 2) + np.sum(y_valid ** 2)
        y_count = float(len(y_train) + len(y_valid))
        self.y_std = math.sqrt((y_sum_square / y_count) - (y_sum / y_count) ** 2)
        self.y_min = min(y_train.min(), y_valid.min())
        self.y_max = max(y_train.max(), y_valid.max())

    def get_transformer(self, tranformer_name):
        return self._featurizer

    def get_y_range(self):
        return self.y_min, self.y_max

    def is_timeseries(self):
        return True

    def get_bin_info(self):
        return self.bin_info

    def get_y_std(self):
        return self.y_std

    def get_y_transformer(self):
        return None


class AbstractValidationTimeSeriesDataset(DNNTimeSeriesDatasetBase):
    """This class provides a dataset for validation and metric calculations, contains X_Train, y_train."""

    @abc.abstractclassmethod
    def get_eval_dataset(self, featurizer, cv_index=None):
        """
        Get the evaluation dataset that contains the X_train/X_valid etc for metric calculations.

        :param cv_index : The item in the cv spit to use for prediction
                          /traing is done once excluding all test grains in it.
        :return: returns an _EvalDataset.
        """
        raise NotImplementedError()

    @staticmethod
    def create_eval_dataset(X_train_list: List[pd.DataFrame], X_valid_list: List[pd.DataFrame],
                            tsds: TimeSeriesDataset, featurizer: TimeSeriesTransformer):
        """
        Create the evaluation dataset that contains the X_train/X_valid etc for metric calculations.

        :param X_train_list : list of dataframe containing X_train grains.
        :param X_valid_list : list of dataframe containing X_valid grains.
        :param tsds : A Timeseries that would give the predicted value of the y_valid.
        :param featurizer : Trained featurizer.
        :return: returns an _EvalDataset.
        """
        X_train, y_train = AbstractValidationTimeSeriesDataset._get_X_y(X_train_list)
        X_valid, y_valid = AbstractValidationTimeSeriesDataset._get_X_y(X_valid_list)
        return _EvalDataset(X_train, y_train, X_valid, y_valid, tsds, featurizer)

    @staticmethod
    def _get_X_y(X_list: List[pd.DataFrame]):
        target_column_name = ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN
        df = pd.concat(X_list)
        X = df.drop(target_column_name, axis=1)
        y = df[target_column_name].values
        return X, y


class ValidationTimeSeriesDatasetFromTrainValid(AbstractValidationTimeSeriesDataset):
    """This class provides a dataset for validation and metric calculations, contains X_Train, y_train."""

    def __init__(self, X_train: TimeSeriesDataset, X_valid: TimeSeriesDataset):
        """
        Take a X_train and X_test and provide an evaluation dataset for evalutaion and metric compute.

        :param X_train : list of datagrains.
        :param X_valid: .
        """
        self.cross_validation = False
        self.X_valid = X_valid
        self.X_train = X_train

        DNNTimeSeriesDatasetBase.__init__(self,
                                          horizon=X_train.horizon,
                                          lookback=X_train.lookback,
                                          sample_count=X_valid._len,
                                          dset_config=X_valid.dset_config,
                                          step=X_valid.step,
                                          has_past_regressors=X_train.has_past_regressors,
                                          sample_transform=X_train.sample_transform,
                                          fetch_y_only=X_valid.fetch_y_only,
                                          data_grains=X_valid._data_grains,)

    def get_eval_dataset(self, featurizer: TimeSeriesTransformer, cv_index: int = None):
        """
        Get the evaluation dataset that contains the X_train/X_valid etc for metric calculations.

        :param featurizer : Trained featurizer.
        :param cv_index : The item in the cv spit to use for prediction
                          /traing is done once excluding all test grains in it.
        :return: returns an _EvalDataset.
        """
        X_train_list = []
        X_valid_list = []

        for item in self.X_train._data_grains:
            train_grain = item.X_df
            X_train_list.append(train_grain)

        for item in self.X_valid._data_grains:
            start_index = self.lookback
            end_index = start_index + self._len * self.horizon
            valid_grain = item.X_df
            if valid_grain.shape[0] > start_index + self.horizon:
                valid_grain = item.X_df.iloc[start_index : end_index]
            else:
                valid_grain = valid_grain.iloc[-self.horizon :]
            X_valid_list.append(valid_grain)

        return AbstractValidationTimeSeriesDataset.create_eval_dataset(
            X_train_list, X_valid_list, self.X_valid, featurizer)


class ValidationTimeSeriesDataset(AbstractValidationTimeSeriesDataset):
    """This class provides a dataset for validation and metric calculations, contains X_Train, y_train."""

    def __init__(self, data_grains: List[_DataGrainItem],
                 horizon: int,
                 lookback: int,
                 len: int,
                 dset_config: DataSourceConfig,
                 step: int = 1,
                 has_past_regressors: bool = False,
                 transform: Any = None,
                 fetch_y_only: bool = False,
                 cross_validation: int = None):
        """
        Take a list of grains amd and provides access to windowed subseries for torch DNN training.

        :param data_grains : list of datagrains.
        :param horizon: Number of time steps to forecast.
        :param lookback: look back to use with in examples.
        :param len: number of samples in the grains.
        :param step: Time step size between consecutive examples.
        :param dset_config: dataset config
        :param has_past_regressors: data to populate past regressors for each sample
        :param transform: feature transforms to use
        :param fetch_y_only: whether fetch_y_only
        :param cross_validation: cros validation secified
        """
        DNNTimeSeriesDatasetBase.__init__(self,
                                          horizon=horizon,
                                          lookback=lookback,
                                          sample_count=len,
                                          dset_config=dset_config,
                                          step=step,
                                          has_past_regressors=has_past_regressors,
                                          sample_transform=transform,
                                          fetch_y_only=fetch_y_only,
                                          data_grains=data_grains,
                                          cross_validation=cross_validation)

    def get_eval_dataset(self, featurizer: TimeSeriesTransformer, cv_index: int = None):
        """
        Get the evaluation dataset that contains the X_train/X_valid etc for metric calculations.

        :param featurizer: Trained featurizer.
        :param cv_index : The item in the cv spit to use for prediction
                          /traing is done once excluding all test grains in it.
        :return: returns an _EvalDataset.
        """
        X_train_list = []
        X_valid_list = []
        new_grains = []
        val_len = 0
        if self.cross_validation:
            Contract.assert_true(cv_index < self.cross_validation or cv_index <= 0,
                                 "cv_index {} is out of range for cross_validation {}."
                                 .format(cv_index, self.cross_validation),
                                 log_safe=True)
        else:
            Contract.assert_true(cv_index is None,
                                 "cv_index {} is passed when cv is not used while creating dataset."
                                 .format(cv_index),
                                 log_safe=True)
        for item in self._data_grains:
            if cv_index is None:
                # tcn prediction starts after the lookup(context), offset is separating the training samples from test.
                val_start_index = item.offset + self.lookback
                val_end_index = val_start_index + (item.lookup_end_ix - item.lookup_start_ix) * self.horizon
            else:
                # if cv prediction is there are cv + horizon - 1 rows left for validation
                # for each cv one horizon per grain is predicted and slide by one row for next prediction.
                val_start_index = item.offset + self.lookback + cv_index  # target one horizon location for this grain.
                val_end_index = val_start_index + self.horizon  # look only one horizon.
                if val_end_index > item.y.shape[1]:
                    val_end_index = item.y.shape[1]
                    val_start_index = val_end_index - self.horizon
                # create a new item to create a new dataset iterator that releases one sample per grain.
                val_item = _DataGrainItem(item.X_df, item.y, val_len, val_len + 1, item.offset + cv_index)
                new_grains.append(val_item)
                val_len = val_len + 1
            train_grain = item.X_df.iloc[: val_start_index]
            valid_grain = item.X_df.iloc[val_start_index : val_end_index]
            X_train_list.append(train_grain)
            X_valid_list.append(valid_grain)

        if cv_index is not None:
            tsds = DNNTimeSeriesDatasetBase(horizon=self.horizon,
                                            lookback=self.lookback,
                                            sample_count=val_len,
                                            dset_config=self.dset_config,
                                            step=1,
                                            has_past_regressors=self.has_past_regressors,
                                            sample_transform=self.transform,
                                            fetch_y_only=self.fetch_y_only,
                                            data_grains=new_grains)
        else:
            tsds = self
        return AbstractValidationTimeSeriesDataset.create_eval_dataset(X_train_list, X_valid_list, tsds, featurizer)
