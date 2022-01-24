# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Classes and functions to validate the model using Rolling Origin Cross-Validation evaluation strategy."""
import numpy as np
import pandas as pd
from pandas.errors import OutOfBoundsDatetime
from sklearn.model_selection import BaseCrossValidator
from sklearn.utils import indexable
from sklearn.utils.validation import _num_samples

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared.reference_codes import ReferenceCodes

from azureml._common._error_definition.user_error import ArgumentOutOfRange
from azureml.automl.core.shared._diagnostics.automl_error_definitions import InvalidArgumentType, \
    TimeseriesInsufficientDataForCVOrHorizon

from azureml.automl.core.shared.forecasting_exception import ForecastingDataException
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    TimeseriesCannotInferSingleFrequencyForAllTS
)

from azureml.automl.core.shared.exceptions import ConfigException, DataException
from azureml.automl.runtime.shared.time_series_data_frame import TimeSeriesDataFrame


class RollingOriginValidator(BaseCrossValidator):
    """
    A subclass of sklearn.BaseCrossValidator_ which creates temporal splits in rows of data.

    Provides train/test indices to split data in train/test sets for
    rolling forecast origin cross-validation

    Defines rolling forecast origin cross-validation folds for the data
    for use as inputs in machine learning parameter tuning.

    .. _sklearn.BaseCrossValidator: http://scikit-learn.org/stable/modules/cross_validation.html

    :param n_splits: Number of splits. Must be at least 1.
    :type n_splits: int
    :param n_step:
        Number of periods between the origin_time of one CV fold and the next fold. For
        example, if `n_step` = 3 for daily data, the origin time for each fold will be
        three days apart.
    :type n_step: int
    :param max_horizon: The maximum number of periods into the future to include in the testing data.
    :type max_horizon: int

    Examples:
    >>> rollcv = RollingOriginValidator(n_splits=3)
    >>> df = TimeSeriesDataFrame(
    ...    {'category': ['a']*6 + ['b']*6,
    ...    'date': pd.to_datetime(['2017-01-02', '2017-01-03', '2017-01-04',
    ...                            '2017-01-05', '2017-01-06', '2017-01-07']*2),
    ...    'values' : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    ...    'origin': pd.to_datetime(['2017-01-01', '2017-01-02', '2017-01-03',
    ...                              '2017-01-04', '2017-01-05', '2017-01-06']*2)
    ...    }, time_colname='date', grain_colnames= 'category', origin_time_colname='origin')
    >>> splits = rollcv.split(df)

    """

    def __init__(self, n_splits=3, n_step=1, max_horizon=None):
        """Create a RollingOriginValidator."""
        # TODO: add ```max_train_size``` argument later so that previous training
        # data will be dropped when the training data size grows exceeding the
        # max_train_size. This could be helpful for controlling the model
        # training time for data with long history.
        super().__init__()
        self.n_splits = n_splits
        self.max_horizon = max_horizon
        self.n_step = n_step

    @property
    def n_step(self):
        """
        Get the number of periods between the origin of one CV fold and the next.

        For example, if `n_step` = 3 for daily data, the origin time for each fold
        will be three days apart.
        """
        return self.__n_step

    @n_step.setter
    def n_step(self, val):
        if isinstance(val, int):
            if val < 1:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        ArgumentOutOfRange, target="n_step", argument_name="n_step", min=1, max="inf"
                    )
                )
            self.__n_step = val
        elif val is None:
            self.__n_step = val  # type: ignore
        else:
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType, target="n_step", argument="n_step", actual_type=type(val),
                    expected_types="int")
            )

    @property
    def max_horizon(self):
        """
        Max value of horizons for the cross-validation folds.

        If None all data will the same `origin_time` are put into the
        same CV-fold.
        """
        return self.__max_horizon

    @max_horizon.setter
    def max_horizon(self, val):
        if val is None:
            self.__max_horizon = None
        elif isinstance(val, int):
            if val < 1:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        ArgumentOutOfRange, target="max_horizon",
                        argument_name="max_horizon ({})".format(val), min=1, max="inf"
                    )
                )
            self.__max_horizon = val
        else:
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType, target="max_horizon",
                    argument="max_horizon", actual_type=type(val),
                    expected_types="int")
            )

    def get_n_splits(self, X=None, y=None, groups=None):
        """
        Return the number of splitting iterations in the cross-validator.

        :param X: Always ignored, exists for compatibility.
        :type X: object

        :param y: Always ignored, exists for compatibility.
        :type y: object

        :param groups: Always ignored, exists for compatibility.
        :type groups: object

        :return:
            The number of splitting iterations in the cross-validator.
        :rtype: int
        """
        return self.n_splits

    def split(self, X, y=None, groups=None):
        """
        Generate indices to split data into training and test set.

        :param X:
            Training data, where n_samples is the number of samples
            and n_features is the number of features.
        :type X: azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame

        :param y:
            Always ignored, exists for compatibility.

        :param groups:
            Always ignored, exists for compatibility.

        :return:
           Tuple of the training set and testing set indices for that
           split.
        """
        if not isinstance(X, TimeSeriesDataFrame):
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentType, target="X", argument="X",
                    actual_type=type(X), expected_types="TimeSeriesDataFrame")
            )
        time_value = X.time_index
        fcast_index = X.origin_time_index
        freq = X.infer_freq()
        has_origin = True
        if X.infer_single_freq() is None:
            raise ForecastingDataException._with_error(
                AzureMLError.create(TimeseriesCannotInferSingleFrequencyForAllTS,
                                    target='X.infer_single_freq()',
                                    reference_code=ReferenceCodes._TS_CANNOT_INFER_SINGLE_FREQ_FOR_ALL_TS)
            )

        if fcast_index is None:
            if self.max_horizon is None:
                fcast_index = time_value - freq
            else:
                has_origin = False
        # make the arrays indexable for cross-validation
        if has_origin:
            X, y, groups, time_value, fcast_index = indexable(  # pylint: disable=unbalanced-tuple-unpacking
                X, y, groups, time_value, fcast_index)
        else:
            X, y, groups, time_value = indexable(  # pylint: disable=unbalanced-tuple-unpacking
                X, y, groups, time_value)
        n_samples = _num_samples(X)
        n_splits = self.n_splits
        if self.max_horizon is not None:
            num_horizon = self.max_horizon
            time_horizon = self.max_horizon * freq
        else:
            num_horizon = len((fcast_index - time_value).unique())
        n_step = self.n_step if self.n_step is not None else 1
        cur_samples = (n_splits - 1) * n_step + 1 + num_horizon
        if cur_samples > n_samples:
            raise DataException._with_error(AzureMLError.create(
                TimeseriesInsufficientDataForCVOrHorizon, target="X", cur_samples=cur_samples, num_samples=n_samples)
            )
        if has_origin:
            fcast_index_sort = fcast_index.dropna().unique().sort_values()
        else:
            fcast_index_sort = time_value.dropna().unique().sort_values()[:-1]

        index_delta = freq * n_step
        fold_origins = pd.date_range(end=fcast_index_sort[-1], periods=n_splits,
                                     freq=index_delta)

        for fcast_time in fold_origins:
            origin_valid = fcast_index == fcast_time if has_origin else \
                time_value > fcast_time
            if self.max_horizon is not None:
                try:
                    horizon_valid = time_value <= fcast_time + time_horizon
                except (OutOfBoundsDatetime, OverflowError):
                    break
            else:
                horizon_valid = np.array([True] * len(time_value))
            yield (np.array(np.where(time_value <= fcast_time)).flatten(),
                   np.array(np.where(np.logical_and(origin_valid, horizon_valid))).flatten())
