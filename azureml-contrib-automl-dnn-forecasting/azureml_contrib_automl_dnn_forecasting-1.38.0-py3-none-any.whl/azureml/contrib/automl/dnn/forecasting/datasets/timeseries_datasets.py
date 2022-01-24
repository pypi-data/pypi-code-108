# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for creating training dataset from dapaprep Dataflow object."""
import abc
import math
from typing import Any, List, Optional, Union

import forecast.data.transforms as tfs
import numpy as np
import pandas as pd
import torch
from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty, NotReady

from forecast.data import FUTURE_DEP_KEY, FUTURE_IND_KEY, PAST_DEP_KEY, PAST_IND_KEY
from forecast.data.sources.data_source import DataSourceConfig
from forecast.data.sources.data_source import EncodingSpec
from torch.utils.data import Dataset

from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.runtime.featurizer.transformer.timeseries.timeseries_transformer import TimeSeriesTransformer
from azureml.automl.runtime.shared import _dataset_binning as binning
from azureml.automl.runtime.column_purpose_detection import ColumnPurposeDetector
from azureml.contrib.automl.dnn.forecasting.wrapper import _wrapper_util

from ..constants import FeatureType, ForecastConstant, DROP_COLUMN_LIST, TCNForecastParameters
from ..types import DataInputType, TargetInputType


class EmbeddingColumnInfo:
    """This class holds a name, index and unique number of items in the column."""

    def __init__(self,
                 name: str,
                 index: int,
                 distinct_values: int):
        """
        Create a structure with grain name, index in the transformed dataset and count of distinct grain values.

        :param name: Name of a column in the timeseries grain.
        :param index: Index of the grain column in the transformed data.
        :param distinct_values: Number of distinct values in the grain column.
        """
        self.name = name
        self.index = index
        self.distinct_values = distinct_values


class _DataGrainItem:
    """This class holds a slice of feature and label."""

    def __init__(self,
                 X_df: pd.DataFrame,
                 y: np.ndarray,
                 lookup_start_ix: int = 0,
                 lookup_end_ix: int = None,
                 offset: int = 0):
        self.X_df = X_df
        self.y = y
        self.lookup_start_ix = lookup_start_ix
        self.lookup_end_ix = lookup_end_ix
        self.offset = offset

        Contract.assert_true(self.X.shape[0] == self.y.shape[-1],
                             "X({}) and y({}) have inconsistent shapes.".format(X_df.shape[0], y.shape[-1]),
                             log_safe=True)

        if lookup_end_ix:
            Contract.assert_true(self.lookup_end_ix > self.lookup_start_ix,
                                 "lookup_end_ix ({}) should be greater than lookup_start_ix ({})".format(
                                     lookup_end_ix, lookup_start_ix), log_safe=True)

    @property
    def X(self):
        """Get the numeric array of data frame needed for training sample."""
        return self.X_df.values


# Copied here temporarily, it will be imported from automl.client.core.runner.model_wrappers.
class ForecastingErrors:
    """Forecasting errors."""

    # Constants for errors and warnings
    # Non recoverable errors.
    FATAL_WRONG_DESTINATION_TYPE = ("The forecast_destination argument has wrong type, "
                                    "it is a {}. We expected a datetime.")
    FATAL_DATA_SIZE_MISMATCH = "The length of y_pred is different from the X_pred"
    FATAL_WRONG_X_TYPE = ("X_pred has unsupported type, x should be pandas.DataFrame, "
                          "but it is a {}.")
    FATAL_WRONG_Y_TYPE = ("y_pred has unsupported type, y should be numpy.array or pandas.DataFrame, "
                          "but it is a {}.")
    FATAL_NO_DATA_CONTEXT = ("No y values were provided for one of grains. "
                             "We expected non-null target values as prediction context because there "
                             "is a gap between train and test and the forecaster "
                             "depends on previous values of target. ")
    FATAL_NO_DESTINATION_OR_X_PRED = ("Input prediction data X_pred and forecast_destination are both None. "
                                      "Please provide either X_pred or a forecast_destination date, but not both.")
    FATAL_DESTINATION_AND_X_PRED = ("Input prediction data X_pred and forecast_destination are both set. "
                                    "Please provide either X_pred or a forecast_destination date, but not both.")
    FATAL_X_Y_XOR = "X_pred and y_pred should both be None or both not None."
    FATAL_NO_LAST_DATE = ("The last training date was not provided."
                          "One of grains in scoring set was not present in training set.")
    FATAL_EARLY_DESTINATION = ("Input prediction data X_pred or input forecast_destination contains dates "
                               "prior to the latest date in the training data. "
                               "Please remove prediction rows with datetimes in the training date range "
                               "or adjust the forecast_destination date.")
    FATAL_NO_TARGET_IN_Y_DF = ("The y_pred is a data frame, "
                               "but it does not contain the target value column")
    FATAL_WRONG_QUANTILE = "Quantile should be a number between 0 and 1 (not inclusive)."
    FATAL_NO_TS_TRANSFORM = ("The time series transform is absent. "
                             "Please try training model again.")

    FATAL_NO_GRAIN_IN_TRAIN = ("One of grains was not present in the training data set. "
                               "Please remove it from the prediction data set to proceed.")
    FATAL_NO_TARGET_IMPUTER = 'No target imputers were found in TimeSeriesTransformer.'
    FATAL_NONPOSITIVE_HORIZON = "Forecast horizon must be a positive integer."


class DNNTimeSeriesDatasetBase(Dataset):
    """This class provides a base class for Time Series datasets."""

    @staticmethod
    def _drop_extra_columns(X: pd.DataFrame, inplace: bool = False) -> pd.DataFrame:
        drop_columns = []
        for col in X.columns:
            if col in DROP_COLUMN_LIST:
                drop_columns.append(col)
        if drop_columns:
            return X.drop(drop_columns, inplace=inplace, axis=1)
        return X

    def __init__(self,
                 horizon: int,
                 lookback: int,
                 step: int = 1,
                 thinning: float = 1.0,
                 has_past_regressors: bool = False,
                 sample_transform: Any = None,
                 fetch_y_only: bool = False,
                 training_data: tuple = None,
                 dset_config: DataSourceConfig = None,
                 data_grains: List[_DataGrainItem] = None,
                 embedding_col_infos: List[EmbeddingColumnInfo] = [],
                 sample_count: int = None,
                 cross_validation: int = None
                 ):
        """
        Take a training data(X) and label(y) and provides access to windowed subseries for torch DNN training.

        :param horizon: Number of time steps to forecast.
        :param lookback: lookback for this class.
        :param step: Time step size between consecutive examples.
        :param thinning: Fraction of examples to include.
        :param has_past_regressors: data to populate past regressors for each sample
        :param sample_transform: per-sample feature transforms to use
        :param fetch_y_only: Get only the target value.
        :param training_data: X and Y and settings saved in dataset if needed to created lookback.
        :param dset_config: Get only the target value.
        :param data_grain: Slices of data grain and the indexes to lookup the training sample.
        :param embedding_col_infos: List of grain columns index, count and name.
        :param sample_count: Number of samples in the dataset(with lookback and horizon).
        :param cross_validation: Sliding test data used for metrics.
        """
        self.horizon = horizon
        self.step = step
        self.thinning = thinning
        self.sample_transform = sample_transform
        self._keep_untransformed = False
        self.has_past_regressors = has_past_regressors
        self._len = sample_count
        self.lookback = lookback
        self.fetch_y_only = fetch_y_only
        self._training_data = training_data
        self.dset_config = dset_config
        self._cache = {}
        self._data_grains = data_grains
        self.embedding_col_infos = embedding_col_infos
        self.cross_validation = cross_validation
        # The `forecast` submodule / library requires this property to be set
        self.transform = None

    @property
    def keep_untransformed(self):
        """Whether to return data untransformed."""
        return self._keep_untransformed

    def __len__(self) -> int:
        """Return the number of samples in the dataset.

        :return: number of samples.
        """
        return self._len

    def __getitem__(self, idx: int) -> dict:
        """
        Get the idx-th training sample item from the dataset.

        :param idx: the item to get the sample.
        :return: returns the idx-th sample.
        """
        if self._len is None:
            raise ClientException._with_error(AzureMLError.create(
                NotReady, argument_name="Dataset not initialized, lookback for the dataset is not set",
                target="lookback", reference_code=ReferenceCodes._TCN_LOOKBACK_DATASET_NOT_SET)
            )
        idx2, X, y = self._get_index_grain_from_lookup(idx)
        sample = self. _getitem_from_df(X, y, idx2)
        return sample

    def _get_data_grain_for_sample_idx(self, idx: int) -> _DataGrainItem:
        """
        Get the data grain corresponding to the idx-th sample index.

        This logic was pulled from / inspired by
        https://github.com/python/cpython/blob/6a1e9c26736259413b060b01d1cb52fcf82c0385/Lib/bisect.py#L26-L35.
        """
        lo = 0
        hi = len(self._data_grains)
        while lo < hi:
            mid = (lo + hi) // 2
            if idx < self._data_grains[mid].lookup_end_ix:
                hi = mid
            else:
                lo = mid + 1

        data_grain = self._data_grains[lo]
        Contract.assert_true(
            data_grain.lookup_start_ix <= idx < data_grain.lookup_end_ix,
            "Located data grain with lookup_start_idx ({}) and lookup_end_ix ({}) does not contain the \
                requested sample index ({}).".format(data_grain.lookup_start_ix, data_grain.lookup_end_ix, idx),
            log_safe=True)

        return data_grain

    def _get_index_grain_from_lookup(self, idx) -> tuple:
        located_grain = self._get_data_grain_for_sample_idx(idx)

        # lookup index from the grain is the offset +
        # steps size * distance to the index from lookup start.
        lookup_index = located_grain.offset + self.step * (idx - located_grain.lookup_start_ix)
        return lookup_index, located_grain.X, located_grain.y

    def _getitem_from_df(self, X, y, idx: int) -> dict:
        """
        Get the idx-th training sample item from the dataset.

        :param X: feature ndarray
        :param y: target array
        :param idx: the item to get the sample.
        :return: returns the idx-th sample.
        """
        # Get time series
        # The data values are transformed so the result is of the shape nfeatures X lookback for X
        # and 1 X horizon for y
        start_index = idx
        X_past = None
        X_fut = None
        if self.has_past_regressors:
            if X.shape[0] < self.lookback + self.horizon:
                X = X.T  # matrix transorm X as needed for training TCN.
                # If the time series is too short, zero-pad on the left
                if not self.fetch_y_only:
                    X_past = X[1:, :-self.horizon]
                    X_past = np.pad(
                        X_past,
                        pad_width=((0, 0), (self.lookback - X_past.shape[-1], 0)),
                        mode='constant',
                        constant_values=0
                    )
                    X_fut = X[1:, -self.horizon:]

                    X_past = torch.tensor(X_past.astype(np.float32), dtype=torch.float)
                    X_fut = torch.tensor(X_fut.astype(np.float32), dtype=torch.float)

                y_past = y[:, :-self.horizon]
                y_past = np.pad(
                    y_past,
                    pad_width=((0, 0), (self.lookback - y_past.shape[-1], 0)),
                    mode='constant',
                    constant_values=0
                )
                y_fut = y[:, -self.horizon:]

                y_past = torch.tensor(y_past.astype(np.float32), dtype=torch.float)
                y_fut = torch.tensor(y_fut.astype(np.float32), dtype=torch.float)
            else:
                end_index = start_index + self.lookback + self.horizon
                if not self.fetch_y_only:
                    X_item = X[start_index:end_index, 1:].T
                    X_past = torch.tensor(X_item[:, :self.lookback].astype(np.float32), dtype=torch.float)
                    X_fut = torch.tensor(X_item[:, self.lookback:].astype(np.float32), dtype=torch.float)

                y_item = y[:, start_index:end_index]
                y_past = torch.tensor(y_item[:, :self.lookback].astype(np.float32), dtype=torch.float)
                y_fut = torch.tensor(y_item[:, self.lookback:].astype(np.float32), dtype=torch.float)

            # Create the input and output for the sample
            if self.fetch_y_only:
                sample = {PAST_DEP_KEY: y_past,
                          FUTURE_DEP_KEY: y_fut}
            else:
                sample = {PAST_IND_KEY: X_past,
                          PAST_DEP_KEY: y_past,
                          FUTURE_IND_KEY: X_fut,
                          FUTURE_DEP_KEY: y_fut}
        else:
            X = None
            if not self.fetch_y_only:
                X_item = X[:, start_index:start_index + self.lookback]
                X = torch.tensor(X_item.astype(np.float32), dtype=torch.float)
            y_item = y[:, start_index + self.lookback:start_index + self.lookback + self.horizon]
            y = torch.tensor(y_item.astype(np.float32), dtype=torch.float)
            # Create the input and output for the sample
            sample = {'X': X, 'y': y}
        if self.sample_transform and not self.keep_untransformed:
            sample = self.sample_transform(sample)
        return sample

    def is_small_dataset(self) -> bool:
        """Return true if dataset is small."""
        if self._len is not None:
            return self._len < ForecastConstant.SMALL_DATASET_MAX_ROWS
        return True

    def feature_count(self) -> int:
        """Return the number of features in the dataset."""
        return self._data_grains[0].X_df.shape[1]

    def set_lookback(self, lookback: int) -> None:
        """
        Set lookback to be used with this dataset.

        :param lookback: Number of time steps used as input for forecasting.
        """
        self.lookback = lookback
        self._len = 0
        for item in self._data_grains:
            start_index = self._len
            size = self._get_size(item.y)
            self._len += size
            item.lookup_start_ix = start_index
            item.lookup_end_ix = self._len

    @property
    def grain_count(self) -> int:
        """Return the number of grains in the dataset."""
        return len(self._data_grains)


class TimeSeriesDataset(DNNTimeSeriesDatasetBase):
    """This class provides a dataset for training timeseries model with dataprep features and label."""

    def __init__(self,
                 X_df: pd.DataFrame,
                 y_df: pd.DataFrame,
                 horizon: int,
                 step: int = 1,
                 thinning: float = 1.0,
                 has_past_regressors: bool = False,
                 one_hot: bool = False,
                 sample_transform: Any = None,
                 fetch_y_only: bool = False,
                 save_last_lookback_data: bool = False,
                 embedding_enabled: Optional[bool] = True,
                 **settings: Any
                 ):
        """
        Take a training data(X) and label(y) and provides access to windowed subseries for torch DNN training.

        :param X_dflow: Training features in pandas dataframe.
        :param y_dflow: Training label in in pandas dataframe with shape(row_count, 1).
        :param horizon: Number of time steps to forecast.
        :param step: Time step size between consecutive examples.
        :param thinning: Fraction of examples to include.
        :param has_past_regressors: data to populate past regressors for each sample
        :param one_hot: one_hot encode or not
        :param sample_transform: feature transforms to use
        :param fetch_y_only: read y only, so the rest of features are not untransformed.
        :param save_last_lookback_data: save last lookbackup from training for inference.
        :param embedding_enabled: embeding state, embedding will only applied if the embedding_calc_type is set
        :param settings:  series settings
        """
        super(TimeSeriesDataset, self).__init__(horizon,
                                                None,
                                                step=step,
                                                thinning=thinning,
                                                has_past_regressors=has_past_regressors,
                                                sample_transform=sample_transform,
                                                fetch_y_only=fetch_y_only,
                                                )

        if save_last_lookback_data:
            self._training_data = (X_df.copy(), y_df.copy(), settings)

        get_encodings, encodings = False, []
        if ForecastConstant.cross_validations in settings and settings[ForecastConstant.cross_validations] is not None:
            self.cross_validation = int(settings[ForecastConstant.cross_validations])
        if one_hot:
            get_encodings = True
        self._drop_extra_columns(X_df, inplace=True)

        grains = settings.get(ForecastConstant.grain_column_names, None) if settings else None

        if get_encodings:
            encodings = self._get_encoding(X_df)

        if embedding_enabled:
            self.embedding_col_infos = self._get_embedding(X_df, TCNForecastParameters.EMBEDDING_THRESHOLD)

        self.dset_config = DataSourceConfig(feature_channels=X_df.shape[1],
                                            forecast_channels=1,
                                            encodings=encodings)

        self._data_grains = []

        if grains is not None:
            if isinstance(grains, str):
                grains = [grains]
            assert ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN not in X_df
            X_df.insert(0, ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN,
                        y_df.values)
            groupby = X_df.groupby(grains)
            for _, X_df in groupby:
                y_df = X_df[ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN]
                y = y_df.values
                y = y.reshape((1, y.shape[0]))
                self._data_grains.append(_DataGrainItem(X_df, y))
        else:
            X_df.insert(0, ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN, y_df.values)
            y = y_df.values
            y = y.reshape((1, y.shape[0]))
            self._data_grains.append(_DataGrainItem(X_df, y))

        self.has_past_regressors = has_past_regressors
        if self.sample_transform is None and not self.fetch_y_only:
            self.sample_transform = self._get_sample_transform(one_hot)

    def get_last_lookback_items(self, X_valid_df: Optional[pd.DataFrame] = None,
                                y_valid_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Return the lookback items from each grain in dataset."""
        if not self._training_data:
            raise ClientException._with_error(
                AzureMLError.create(
                    ArgumentBlankOrEmpty, target="save_data", argument_name="X_df/y_df/settings",
                    reference_code=ReferenceCodes._TCN_EMPTY_SAVE_DATA)
            )
        if self.lookback is None:
            raise ClientException._with_error(
                AzureMLError.create(
                    ArgumentBlankOrEmpty, target="lookback", argument_name="lookback",
                    reference_code=ReferenceCodes._TCN_EMPTY_LOOKBACK)
            )
        X_df, y_df, settings = self._training_data
        if settings is None:
            raise ClientException._with_error(
                AzureMLError.create(
                    ArgumentBlankOrEmpty, target="time_column", argument_name="settings",
                    reference_code=ReferenceCodes._TCN_EMPTY_SETTINGS)
            )

        if X_valid_df is not None:
            X_df = X_df.append(X_valid_df)
            y_df = y_df.append(y_valid_df)

        grains, index = None, None
        if ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN not in X_df:
            X_df[ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN] = y_df.values

        if ForecastConstant.automl_constants.TimeSeries.TIME_COLUMN_NAME in settings:
            index = settings[ForecastConstant.automl_constants.TimeSeries.TIME_COLUMN_NAME]
            if ForecastConstant.automl_constants.TimeSeries.GRAIN_COLUMN_NAMES in settings:
                grains = settings[ForecastConstant.automl_constants.TimeSeries.GRAIN_COLUMN_NAMES]
        if index is None:
            ret_df = X_df[-self.lookback:]
        else:
            if grains:
                ret_df = []
                groupby = X_df.groupby(grains)
                for grain in groupby.groups:
                    X_df = groupby.get_group(grain)
                    ret_df.append(X_df[-self.lookback:])
                ret_df = pd.concat(ret_df).reset_index()
            else:
                ret_df = X_df[-self.lookback:].reset_index()
        return ret_df.set_index(X_df.index.names)[X_df.columns]

    def _get_size(self, y) -> None:
        """
        Set lookback to be used with this dataset.

        :param lookback: Number of time steps used as input for forecasting.
        """
        # If timeseries is smaller than lookback + horizon, we would need to pad
        if y.shape[-1] < self.lookback + self.horizon:
            sample_count = 1
        else:
            sample_count = (y.shape[-1] - self.lookback - self.horizon + self.step) // self.step
        return max(1, int(self.thinning * sample_count))

    @staticmethod
    def _get_embedding(data: pd.DataFrame, threshold: int) -> List[EncodingSpec]:

        if data.columns[0] == ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN:
            index = 0
        else:
            index = 1
        embedding_infos = []
        column_purpose_detector = ColumnPurposeDetector()
        column_purpose = column_purpose_detector.get_raw_stats_and_column_purposes(data)
        for stats, featureType, name in column_purpose:
            if featureType == FeatureType.Categorical and stats.num_unique_vals > threshold:
                if name != ForecastConstant.automl_constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN:
                    max_num_features = math.ceil(data[name].max()) + 1
                    embedding_info = EmbeddingColumnInfo(name,
                                                         index,
                                                         max_num_features)
                    embedding_infos.append(embedding_info)
            index = index + 1
        return embedding_infos

    @staticmethod
    def _get_encoding(data: pd.DataFrame) -> List[EncodingSpec]:
        index = 0
        encodings = []
        column_purpose_detector = ColumnPurposeDetector()
        column_purpose = column_purpose_detector.get_raw_stats_and_column_purposes(data)
        for stats, featureType, name in column_purpose:
            if featureType == FeatureType.Categorical and stats.num_unique_vals > 2:
                # TODO remove this and replace this with label encoder
                max_num_features = int(data[name].max().astype(int) + 1)
                # embedding = EncodingSpec(feature_index=index, num_vals=stats.num_unique_vals)
                embedding = EncodingSpec(feature_index=index, num_vals=max_num_features)
                encodings.append(embedding)
            index = index + 1
        return encodings

    def _get_sample_transform(self, one_hot) -> tfs.ComposedTransform:
        if one_hot and self.dset_config.encodings:
            drop_first = False
            drop = True if drop_first else False
            tf_list = [tfs.OneHotEncode([e.feature_index for e in self.dset_config.encodings],
                                        [e.num_vals for e in self.dset_config.encodings],
                                        drop_first=drop),
                       tfs.OneHotEncode([e.feature_index for e in self.dset_config.encodings],
                                        [e.num_vals for e in self.dset_config.encodings],
                                        drop_first=drop,
                                        key=FUTURE_IND_KEY)]
            return tfs.ComposedTransform(tf_list)
        return None

    def _get_test_size(self, grain_size, validation_percent):
        if self.cross_validation is not None:
            # horizon itself is one part of the validation split, so we need only extra cv - 1
            # rows to slide and get cv parts. Say horizon 3 and cv 2 we need only 4 rows to get
            # we need only 4 rows to get two consecutive parts(0-2 and 1-3) with 3 rows each.
            grain_test_size = self.horizon + self.cross_validation - 1
            # Number of samples to be at least cv count to be included in validation set..
            # total number of samples in the dataset should be more that test size
            # with one horizon gap so that the training set have no horizon in common
            # with test data.
            if grain_size <= grain_test_size + self.horizon:
                grain_test_size = 0
        else:
            grain_test_size = max(1, math.floor(grain_size * validation_percent))
            if grain_size == grain_test_size + self.horizon:
                grain_test_size = 0
        return grain_test_size

    def get_train_test_split(self, validation_percent: float = 0.1):
        """
        Split the dataset into train and test as per the validtaion percent.

        :param validation_percent: percentage of data to be used as validation.
        """
        if self.lookback is None:
            raise ClientException._with_error(
                AzureMLError.create(
                    ArgumentBlankOrEmpty, target="lookback", argument_name="lookback",
                    reference_code=ReferenceCodes._TCN_EMPTY_LOOKBACK_GET_SPLIT))
        train_size = 0
        test_size = 0
        test_data_grains = []
        train_data_grains = []
        step = 1 if self.cross_validation else self.horizon
        for item in self._data_grains:
            # total samples in the grain.
            grain_size = item.lookup_end_ix - item.lookup_start_ix
            grain_test_size = self._get_test_size(grain_size, validation_percent)
            grain_train_size = grain_size
            if grain_test_size != 0:
                grain_train_size -= (grain_test_size + self.horizon)
            train_item = _DataGrainItem(item.X_df, item.y, train_size, train_size + grain_train_size)
            train_size += grain_train_size
            train_data_grains.append(train_item)
            if grain_test_size > 0:
                if self.cross_validation:  # if cross validation and if enough data present then cv = test grain size.
                    grain_test_size = self.cross_validation
                else:
                    grain_test_size = max(1, math.ceil(grain_test_size / step))

                # offset of test grain starts after the grain_train_size + horizon.
                test_item = _DataGrainItem(item.X_df, item.y, test_size, test_size + grain_test_size,
                                           offset=grain_train_size + self.horizon)
                test_size += grain_test_size
                test_data_grains.append(test_item)

        if len(test_data_grains) == 0:
            # not enough data for full test and train, take the one sample from a grain that has at least twice
            # horizon and remove last horizon from training data + cv.
            grainitem_to_split = train_data_grains[0]
            for item in train_data_grains:
                if item.X_df.shape[0] >= 2 * self.horizon + self.cross_validation:
                    grainitem_to_split = item
            test_item = _DataGrainItem(grainitem_to_split.X_df, grainitem_to_split.y, 0,
                                       self.cross_validation, offset=0)

            number_of_items_needed_for_validation = self.horizon + self.cross_validation - 1
            if grainitem_to_split.X_df.shape[0] > number_of_items_needed_for_validation:
                grainitem_to_split.X_df = grainitem_to_split.X_df.iloc[: -number_of_items_needed_for_validation, :]
                grainitem_to_split.y = grainitem_to_split.y[:, : -number_of_items_needed_for_validation]
                test_data_grains.append(test_item)
                test_size += self.cross_validation

        train_dataset = DNNTimeSeriesDatasetBase(horizon=self.horizon,
                                                 lookback=self.lookback,
                                                 sample_count=train_size,
                                                 dset_config=self.dset_config,
                                                 step=self.step,
                                                 has_past_regressors=self.has_past_regressors,
                                                 sample_transform=self.sample_transform,
                                                 fetch_y_only=self.fetch_y_only,
                                                 data_grains=train_data_grains)

        valid_dataset = DNNTimeSeriesDatasetBase(horizon=self.horizon,
                                                 lookback=self.lookback,
                                                 sample_count=test_size,
                                                 dset_config=self.dset_config,
                                                 step=step,
                                                 has_past_regressors=self.has_past_regressors,
                                                 sample_transform=self.sample_transform,
                                                 fetch_y_only=self.fetch_y_only,
                                                 cross_validation=self.cross_validation,
                                                 data_grains=test_data_grains)

        assert len(test_data_grains) <= len(train_data_grains)
        if len(test_data_grains) == 0:
            msg = "length of test grain {0}, train size = {1}".\
                format(len(test_data_grains), len(train_data_grains))
            assert len(test_data_grains) > 0, msg

        return train_dataset, valid_dataset
