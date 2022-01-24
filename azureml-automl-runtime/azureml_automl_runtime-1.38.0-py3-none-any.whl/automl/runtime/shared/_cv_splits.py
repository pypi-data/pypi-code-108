# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class for processing cross validation strategies for datasets."""
from typing import Any, cast, Iterable, List, Optional

import logging
import numpy as np
import pandas as pd
import uuid

from functools import reduce

from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import BadArgument, ArgumentBlankOrEmpty, ArgumentOutOfRange
from azureml.automl.core.shared._diagnostics.automl_error_definitions import InvalidArgumentType, \
    FeatureUnsupportedForIncompatibleArguments, ConflictingValueForArguments
from azureml.automl.core.shared._diagnostics.contract import Contract
from sklearn import model_selection
from azureml.automl.core.shared import constants, logging_utilities
from azureml.automl.core.shared.exceptions import ConfigException, DataException
from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from azureml.automl.runtime.shared import memory_utilities
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime.shared.rolling_origin_validator import RollingOriginValidator
from azureml.automl.runtime.shared.time_series_data_frame import TimeSeriesDataFrame

logger = logging.getLogger(__name__)


class _CVSplits:

    def __init__(self,
                 X,
                 y,
                 seed=123,
                 frac_test=None,
                 frac_valid=None,
                 CV=None,
                 n_step=None,
                 cv_splits_indices=None,
                 is_time_series=False,
                 timeseries_param_dict=None,
                 test_cutoff=None,
                 task=constants.Tasks.CLASSIFICATION):
        """Initialize the CV splits class and create CV split indices.

        :param X: input data
        :param y: label
        :param seed: random seed to use in spliting data.
        :param frac_test: Fraction of input data to be used as test set
        :param frac_valid: Fraction of input data to be used as validation set
        :param CV: cross validation #
        :param n_step:
            Number of periods between the origin_time of one CV fold and the next fold. For
            example, if `n_step` = 3 for daily data, the origin time for each fold will be
            three days apart.
        :param cv_splits_indices: list of np arrays of train, valid indexes
        :param is_time_series: If true, use time series cross-validation
        :param timeseries_param_dict: Dictionary representing time-series schema
        :param test_cutoff: If is not None, index of start of test set
        :param task: Task type such as classification, regression etc
        """
        # Caching the configuration for CV splits
        self._frac_test = frac_test
        self._frac_valid = frac_valid
        self._CV = CV
        self._n_step = n_step
        self._cv_splits_indices = cv_splits_indices
        self._is_time_series = is_time_series
        self._timeseries_param_dict = timeseries_param_dict

        # Cache the type of cross validation split
        self._cv_split_type = None

        # These will be populated in case percentage of test
        # and validation sets are provided
        self._train_indices = None
        self._valid_indices = None
        self._test_indices = None

        # Featurized data for train, test and validation sets
        self._featurized_train_test_valid_chunks = None     # type: Optional[FeaturizedTrainValidTestSplit]

        # CV splits indices in case of custom CV splits, specific validation size (Monte-Carlo) split
        # and K-folds split.
        self._CV_splits = None

        # Caching the featurized data for CV splits if any
        self._featurized_cv_splits = None   # type: Optional[List[FeaturizedCVSplit]]

        # determine the type of cross validation
        self._cv_split_type = self._find_cv_split_type(
            frac_test, frac_valid, CV, cv_splits_indices,
            test_cutoff=test_cutoff)

        # Validate the CV parameters
        self._validate_cv_parameters(X, frac_test,
                                     frac_valid, CV,
                                     cv_splits_indices, test_cutoff)

        # Create CV splits or train, test and validation sets
        self._create_cv_splits(X, frac_test,
                               frac_valid, CV, cv_splits_indices, n_step, seed,
                               test_cutoff=test_cutoff, y=y, task=task)

    def get_fraction_validation_size(self):
        """Return the fraction of data to be used as validation set."""
        return self._frac_valid

    def get_fraction_test_size(self):
        """Return the fraction of data to be used as test set."""
        return self._frac_test

    def get_num_k_folds(self):
        """Return the number of k-folds."""
        return self._CV

    def get_custom_split_indices(self):
        """Return the custom split indices."""
        return self._cv_splits_indices

    def get_cv_split_type(self):
        """Return the type of cross validation split."""
        return self._cv_split_type

    def get_cv_split_indices(self):
        """Return a list of tuple (train, valid) is a cross validation scenario."""
        return self._CV_splits

    def get_featurized_cv_split_data(self):
        """Return a list of featurized cross validation data."""
        return self._featurized_cv_splits

    def get_train_test_valid_indices(self):
        """Return train, test and validation indices."""
        return self._train_indices, self._test_indices, self._valid_indices

    def get_featurized_train_test_valid_data(self):
        """Return featurized train, test and validation data."""
        self._featurized_train_test_valid_chunks_data = \
            cast(FeaturizedTrainValidTestSplit, self._featurized_train_test_valid_chunks)._recover_from_cache_store()

        featurized_train_chunk = \
            {'X': self._featurized_train_test_valid_chunks_data.
             _X_train_transformed,
             'y': self._featurized_train_test_valid_chunks_data.
             _y_train,
             'sample_weight': self._featurized_train_test_valid_chunks_data.
             _sample_wt_train}
        featurized_test_chunk = \
            {'X': self._featurized_train_test_valid_chunks_data.
             _X_test_transformed,
             'y': self._featurized_train_test_valid_chunks_data.
             _y_test,
             'sample_weight': self._featurized_train_test_valid_chunks_data.
             _sample_wt_test}
        featurized_valid_chunk = \
            {'X': self._featurized_train_test_valid_chunks_data.
             _X_valid_transformed,
             'y': self._featurized_train_test_valid_chunks_data.
             _y_valid,
             'sample_weight': self._featurized_train_test_valid_chunks_data.
             _sample_wt_valid}
        return featurized_train_chunk, featurized_test_chunk, \
            featurized_valid_chunk

    def _find_cv_split_type(self, frac_test, frac_valid,
                            CV, cv_splits_indices,
                            test_cutoff=None):
        """Find the type of cross validation split.

        :param frac_test: Fraction of input data to be used as test set
        :param frac_valid: Fraction of input data to be used as validation set
        :param CV: cross validation #
        :param cv_splits_indices: list of np arrays of train, valid indexes
        :param test_cutoff: If is not None, index of start of test set
        :return: Type of cross validation training
        """
        if CV is None:
            CV = 0

        if self._is_time_series:
            if test_cutoff is not None:
                # Special type for MIRO training
                return _CVType.MiroTrainingTimeSeriesSplit
            else:
                return _CVType.TimeSeriesSplit
        elif cv_splits_indices is not None:
            return _CVType.CustomCrossValidationSplit
        elif test_cutoff:
            return _CVType.TestCutoffCVSplit
        elif CV > 0 and not frac_valid:
            return _CVType.KFoldCrossValidationSplit
        elif CV > 0 and frac_valid:
            return _CVType.MonteCarloCrossValidationSplit
        elif frac_valid and frac_test:
            return _CVType.TrainTestValidationPercSplit
        elif frac_valid:
            return _CVType.TrainValidationPercSplit
        else:
            # This isn't user friendly/actionable.
            raise ConfigException._with_error(
                AzureMLError.create(
                    BadArgument, target="_CVSplits", argument_name="_CVSplits",
                    reference_code=ReferenceCodes._NOT_CV_SCENARIO
                )
            )

    def _validate_cv_parameters(self, X, frac_test, frac_valid, CV,
                                cv_splits_indices, test_cutoff):
        """Validate the cross validation parameters.

        :param X: input data
        :param frac_test: Fraction of input data to be used as test set
        :param frac_valid: Fraction of input data to be used as validation set
        :param CV: number of cross validation folds
        :param cv_splits_indices: List of tuples of the form (train, valid)
                                  where train and valid are both np arrays
        :param test_cutoff: If is not None, index of start of test set
        """
        if self._cv_split_type is _CVType.TimeSeriesSplit:
            if not isinstance(self._timeseries_param_dict, dict):
                raise ConfigException._with_error(
                    AzureMLError.create(
                        InvalidArgumentType, target="timeseries_param_dict",
                        argument="timeseries_param_dict", actual_type=type(self._timeseries_param_dict),
                        expected_types="dict", reference_code=ReferenceCodes._VALIDATE_CV_PARAMETERS_TS_PARAM_DICT)
                )
            if frac_test or frac_valid:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        FeatureUnsupportedForIncompatibleArguments, target="fractional_cv_splits",
                        feature_name='is_timeseries', arguments="fractional_cv_splits",
                        reference_code=ReferenceCodes._VALIDATE_CV_PARAMETERS_TS_FRAC
                    )
                )
            if cv_splits_indices:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        FeatureUnsupportedForIncompatibleArguments, target="cv_splits_indices",
                        feature_name='is_timeseries', arguments="cv_splits_indices",
                        reference_code=ReferenceCodes._VALIDATE_CV_PARAMETERS_TS_CV_SPLITS
                    )
                )
            if test_cutoff is not None:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        FeatureUnsupportedForIncompatibleArguments, target="test_cutoff",
                        feature_name='is_timeseries', arguments="test_cutoff",
                        reference_code=ReferenceCodes._VALIDATE_CV_PARAMETERS_TS_TEST_CUTOFF
                    )
                )
            if CV is None:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        ArgumentBlankOrEmpty, target="cross_validation_folds", argument_name="cross_validation_folds",
                        reference_code=ReferenceCodes._VALIDATE_CV_PARAMETERS_TS_CV
                    )
                )

        if frac_test and frac_test >= 1.0:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentOutOfRange, target="test_set_fraction",
                    argument_name="test_set_fraction", min="0", max="1.0",
                    reference_code=ReferenceCodes._VALIDATE_CV_PARAMETERS_FRAC_TEST
                )
            )

        if frac_valid and frac_valid >= 1.0:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentOutOfRange, target="validation_set_fraction",
                    argument_name="validation_set_fraction", min="0", max="1.0",
                    reference_code=ReferenceCodes._VALIDATE_CV_PARAMETERS_FRAC_VALID
                )
            )

        # sanity check on test and validation set percentage
        if frac_test and frac_valid and frac_test + frac_valid >= 1.0:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentOutOfRange, target="Sum(test_set_fraction, validation_set_fraction)",
                    argument_name="Sum(test_set_fraction, validation_set_fraction)", min="0", max="1.0",
                    reference_code=ReferenceCodes._VALIDATE_CV_PARAMETERS_FRAC_VALID_TEST
                )
            )

        # sanity check on CV
        if CV is not None and CV <= 0:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentOutOfRange, target="n_cross_validations",
                    argument_name="n_cross_validations", min="1", max="inf",
                    reference_code=ReferenceCodes._VALIDATE_CV_PARAMETERS_NEG_CV
                )
            )

        if cv_splits_indices:
            N = X.shape[0]
            # check if the custon split is valid split.
            self._validate_custom_cv_splits(max_size=N,
                                            cv_splits_indices=cv_splits_indices)

    def _validate_custom_cv_splits(self, max_size, cv_splits_indices):
        """Validate the custom split indicies.

        :param max_size:
        :param cv_splits_indices:
        :return:
        """
        for train, valid in cv_splits_indices:
            for (item, target) in zip([train, valid], ["train_cv_splits_indices", "valid_cv_splits_indices"]):
                if not isinstance(item, np.ndarray):
                    raise ConfigException._with_error(
                        AzureMLError.create(
                            InvalidArgumentType, target=target, argument=target, actual_type=type(item),
                            expected_types="List[numpy.array]",
                            reference_code=ReferenceCodes._VALIDATE_CUSTOM_CV_SPLITS_NUMPY_ARRAY_TYPE
                        )
                    )
                if np.max(item) >= max_size or np.min(item) < 0:
                    ref_code = ReferenceCodes._VALIDATE_CUSTOM_CV_SPLITS_MAX_INDEX if np.max(item) >= max_size \
                        else ReferenceCodes._VALIDATE_CUSTOM_CV_SPLITS_MIN_INDEX
                    raise ConfigException._with_error(
                        AzureMLError.create(
                            ArgumentOutOfRange, target=target, argument_name=target,
                            min=0, max=max_size, reference_code=ref_code
                        )
                    )
                if len(np.unique(item)) != item.shape[0]:
                    raise ConfigException._with_error(
                        AzureMLError.create(
                            ConflictingValueForArguments, target=target, arguments=target,
                            reference_code=ReferenceCodes._VALIDATE_CUSTOM_CV_SPLITS_DUPLICATES
                        )
                    )

            if len(train) + len(valid) > max_size:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        ArgumentOutOfRange, target="Sum(len(train_cv_indices), len(valid_cv_indices))",
                        argument_name="Sum(len(train_cv_indices), len(valid_cv_indices))", min=0, max=max_size,
                        reference_code=ReferenceCodes._VALIDATE_CUSTOM_CV_SPLITS_MAX_SIZE
                    )
                )
            if np.intersect1d(train, valid).shape[0] != 0:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        ConflictingValueForArguments, target="cv_splits_indices",
                        arguments=', '.join(['train_cv_splits_indices', 'valid_cv_splits_indices']),
                        reference_code=ReferenceCodes._VALIDATE_CUSTOM_CV_SPLITS_DISJOINT
                    )
                )

    def _create_cv_split_one_timeseries(self, X_tsdf, CV, max_horizon, rownum_colname, n_step):
        """
        Create CV splits for one time-series, i.e. a single-grained TimeSeriesDataFrame.

        :param X_tsdf: Dataframe with a single grain
        :type X_tsdf: azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame
        :param CV: number of CV folds to make
        :param rownum_colname: Name of column holding row numbers
        :param n_step: step size between consecutive CV folds
        :return: list of tuples containing train and validation indices
        """
        # Try to make folds where the validation set has at least max_horizon points.
        # By default, the validation sets made by ROV decrease in size
        # as the fold number increases until there is a single point in the last fold.
        # To get around this, instruct ROV to make "extra" folds and throw away the short ones.
        # This may fail data validation in the split method if the series aren't long enough,
        # so catch the validation exception and try reverting to "short" folds
        try:
            n_splits_extra = max_horizon - 1

            validator = RollingOriginValidator(n_splits=(CV + n_splits_extra),
                                               n_step=n_step,
                                               max_horizon=max_horizon)
            selection = slice(None, -n_splits_extra) \
                if n_splits_extra > 0 else slice(None, None)
            local_splits = list(validator.split(X_tsdf))[selection]
        except DataException:
            validator = RollingOriginValidator(n_splits=CV,
                                               n_step=n_step,
                                               max_horizon=max_horizon)
            local_splits = list(validator.split(X_tsdf))

        # local split indices are only valid for this grain
        # use rownum column to get "global" indices
        global_splits = [(X_tsdf.iloc[tr][rownum_colname].values,
                          X_tsdf.iloc[va][rownum_colname].values)
                         for tr, va in local_splits]

        return global_splits

    def _create_cv_splits(self, X, frac_test, frac_valid, CV,
                          cv_splits_indices, n_step, seed=123,
                          test_cutoff=None, y=None, task=constants.Tasks.CLASSIFICATION):
        """Create the cross validation split indicies.

        :param X: input data
        :param frac_test: Test set percent
        :param frac_valid: validation set percent
        :param CV: cross validation #
        :param cv_splits_indices: list of np arrays of train, valid indexes
        :param n_step: cross validation step size
        :param seed: Integer value to set the random number state
        :param test_cutoff: If is not None, index of start of test set
        :param y: Label data used in case of classification for stratified splits
        :param task: Task type such as classification, regression etc
        """
        if self._cv_split_type is None:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentBlankOrEmpty, target="cv_split_type", argument_name="_cv_split_type",
                    reference_code=ReferenceCodes._CREATE_CV_SPLITS_TYPE
                )
            )

        N = X.shape[0]
        if cv_splits_indices or test_cutoff:
            full_index = np.arange(N)
        else:
            np.random.seed(seed)
            full_index = np.random.permutation(N)

        if self._cv_split_type == _CVType.CustomCrossValidationSplit:
            # User specified custom cross validation splits
            self._CV_splits = cv_splits_indices
        elif self._cv_split_type == _CVType.KFoldCrossValidationSplit:
            # Generate CV splits for k-folds cross validation splits
            splits = []
            # For classification, we would like to use Stratified sampling first.
            if task == constants.Tasks.CLASSIFICATION:
                np.random.seed(seed)
                splits = _CVSplits._get_stratified_kfold_splits(y, CV, full_index)

            # If it's not classification or if stratified hasn't worked, we will fall back to random.
            if not splits:
                np.random.seed(seed)
                kf = model_selection.KFold(n_splits=CV)
                for train_index, valid_index in kf.split(full_index):
                    splits.append((full_index[train_index], full_index[valid_index]))

            self._CV_splits = splits
        elif self._cv_split_type == _CVType.MonteCarloCrossValidationSplit:
            # Generate CV splits for k-folds cross validation splits with
            # user specified validation size
            np.random.seed(seed)
            splits = []
            full_size = len(full_index)
            for i in range(CV):
                full_index = full_index[np.random.permutation(
                    full_size)]
                splits.append((
                    full_index[:int(full_size * (1 - frac_valid))],
                    full_index[int(full_size * (1 - frac_valid)):]))
            self._CV_splits = splits
        elif self._cv_split_type == _CVType.TrainValidationPercSplit:
            # Generate train and validation set indices if
            # validation size is specified
            n_full = len(full_index)
            n_valid = int(frac_valid * N)
            n_train = n_full - n_valid
            np.random.seed(seed)
            shuffled_ind = np.random.permutation(full_index)
            valid_ind = shuffled_ind[n_train:]
            train_ind = shuffled_ind[:n_train]
            self._train_indices = train_ind
            self._valid_indices = valid_ind
        elif self._cv_split_type == _CVType.TrainTestValidationPercSplit:
            # Generate train, test and validation set indices if
            # validation size and test size is specified
            remaining_ind = full_index[:int(N * (1 - frac_test))]
            test_ind = full_index[int(N * (1 - frac_test)):]

            if not frac_valid:
                frac_valid = 0.1
            n_remaining = len(remaining_ind)
            n_valid = int(frac_valid * N)
            n_train = n_remaining - n_valid
            np.random.seed(seed)
            shuffled_ind = np.random.permutation(remaining_ind)
            valid_ind = shuffled_ind[n_train:]
            train_ind = shuffled_ind[:n_train]

            Contract.assert_true(np.intersect1d(train_ind, test_ind).shape[0] == 0,
                                 "Train and test indices are the same.", log_safe=True)
            Contract.assert_true(np.intersect1d(valid_ind, test_ind).shape[0] == 0,
                                 "Train and validation indices are the same.", log_safe=True)

            self._train_indices = train_ind
            self._valid_indices = valid_ind
            self._test_indices = test_ind
        elif self._cv_split_type == _CVType.TimeSeriesSplit:
            # Generate CV splits indices for time series data
            # First, convert X to TimeSeriesDataFrame
            schema = self._timeseries_param_dict
            time_colname = schema[constants.TimeSeries.TIME_COLUMN_NAME]
            origin_colname = schema.get(constants.TimeSeriesInternal.ORIGIN_TIME_COLUMN_NAME,
                                        None)
            grain_colnames = \
                schema.get(constants.TimeSeries.GRAIN_COLUMN_NAMES, None)

            # Check if origin times are present
            origin_present = origin_colname is not None \
                and (origin_colname in X.index.names or origin_colname in X.columns)
            origin_setting = origin_colname if origin_present else None

            X_tsdf = TimeSeriesDataFrame(X, time_colname=time_colname,
                                         grain_colnames=grain_colnames,
                                         origin_time_colname=origin_setting)

            # Make a ROV object and create the split
            max_horizon = \
                schema.get(constants.TimeSeries.MAX_HORIZON, None)
            if not max_horizon:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        ArgumentBlankOrEmpty, target=constants.TimeSeries.FORECAST_HORIZON,
                        argument_name=constants.TimeSeries.FORECAST_HORIZON,
                        reference_code=ReferenceCodes._CREATE_CV_SPLITS_MAX_HORIZON
                    )
                )
            if max_horizon <= 0:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        ArgumentOutOfRange, target=constants.TimeSeries.FORECAST_HORIZON,
                        argument_name="{} ({})".format(constants.TimeSeries.FORECAST_HORIZON, max_horizon),
                        min=1, max="inf", reference_code=ReferenceCodes._CREATE_CV_SPLITS_MAX_HORIZON_NEGATIVE
                    )
                )

            # Get splits for each individual series
            rownum_colname = 'rownum_{}'.format(uuid.uuid4())
            X_tsdf = X_tsdf.assign(**{rownum_colname: np.arange(len(X_tsdf)).astype(int)})
            if grain_colnames is not None:
                splits_by_grain = [self._create_cv_split_one_timeseries(Xgr, CV,
                                                                        max_horizon,
                                                                        rownum_colname,
                                                                        n_step)
                                   for _, Xgr in X_tsdf.groupby_grain()]
            else:
                splits_by_grain = [self._create_cv_split_one_timeseries(X_tsdf, CV,
                                                                        max_horizon,
                                                                        rownum_colname,
                                                                        n_step)]
            # Transpose the splits_by_grain list to get a list of folds
            splits_by_fold = map(list, zip(*splits_by_grain))   # type: Iterable[Iterable[Any]]
            # Merge grain-level indices to get "global" train/validation splits
            self._CV_splits = \
                [tuple(reduce(np.union1d, ind_collect) for ind_collect in zip(*fold))
                 for fold in splits_by_fold]
        elif self._cv_split_type == _CVType.MiroTrainingTimeSeriesSplit:
            # Generate train, test and validation set, and CV splits indices
            # for time series data. Compatible with miro training datasets
            test_ind = full_index[test_cutoff:]
            remaining_ind = full_index[:test_cutoff]
            self._test_indices = test_ind

            kf = model_selection.TimeSeriesSplit(n_splits=CV)
            splits = []
            to_split = remaining_ind
            if frac_valid:
                to_split = remaining_ind[
                    :int(len(remaining_ind) * (1 - frac_valid))]
                self._valid_indices = remaining_ind[
                    int(len(remaining_ind) * (1 - frac_valid)):]
            for train_index, valid_index in kf.split(to_split):
                splits.append(
                    (to_split[train_index], to_split[valid_index]))
            Contract.assert_true(np.intersect1d(splits[-1][0], test_ind).shape[0] == 0,
                                 "Splits and test index are the same.", log_safe=True)
            self._CV_splits = splits
            self._train_indices = to_split
        elif self._cv_split_type == _CVType.TestCutoffCVSplit:
            # Generate train, test and validation set, and CV splits indices
            # for data with explicity test cutoffs. Compatible with miro training datasets
            test_ind = full_index[test_cutoff:]
            remaining_ind = full_index[:test_cutoff]
            self._test_indices = test_ind

            kf = model_selection.KFold(n_splits=CV)
            to_split = remaining_ind
            if frac_valid:
                to_split = remaining_ind[
                    :int(len(remaining_ind) * (1 - frac_valid))]
                self._valid_indices = remaining_ind[
                    int(len(remaining_ind) * (1 - frac_valid)):]
            splits = []
            for train_index, valid_index in kf.split(to_split):
                splits.append(
                    (to_split[train_index], to_split[valid_index]))
            Contract.assert_true(np.intersect1d(splits[-1][0], test_ind).shape[0] == 0,
                                 "Splits and test index are the same.", log_safe=True)
            self._CV_splits = splits
            self._train_indices = to_split

    def apply_CV_splits(self, X, y, sample_weight):
        """Apply all the CV splits of the dataset, if cross validation is specified."""
        if isinstance(X, pd.DataFrame):
            for train_ind, test_ind in self._CV_splits:  # type: ignore
                yield (X.iloc[train_ind], y[train_ind],
                       None if sample_weight is None else sample_weight[
                           train_ind],
                       X.iloc[test_ind], y[test_ind],
                       None if sample_weight is None else sample_weight[
                           test_ind])
        elif isinstance(X, np.ndarray):
            for train_ind, test_ind in self._CV_splits:  # type: ignore
                yield (X[train_ind], y[train_ind],
                       None if sample_weight is None else sample_weight[
                           train_ind],
                       X[test_ind], y[test_ind],
                       None if sample_weight is None else sample_weight[
                           test_ind])

    def get_train_validation_test_chunks(self, X, y, sample_weight):
        """Get all the train, validation and test dataset, if percentage split is specified."""
        X_train = None
        y_train = None
        sample_weight_train = None
        X_test = None
        y_test = None
        sample_weight_test = None
        X_valid = None
        y_valid = None
        sample_weight_valid = None
        if isinstance(X, pd.DataFrame):
            if self._train_indices is not None:
                X_train = X.iloc[self._train_indices]
            if self._test_indices is not None:
                X_test = X.iloc[self._test_indices]
            if self._valid_indices is not None:
                X_valid = X.iloc[self._valid_indices]
        elif isinstance(X, np.ndarray):
            if self._train_indices is not None:
                X_train = X[self._train_indices]
            if self._test_indices is not None:
                X_test = X[self._test_indices]
            if self._valid_indices is not None:
                X_valid = X[self._valid_indices]

        if self._train_indices is not None:
            y_train = y[self._train_indices]
            sample_weight_train = None if sample_weight is None \
                else sample_weight[self._train_indices]

        if self._test_indices is not None:
            y_test = y[self._test_indices]
            sample_weight_test = None if sample_weight is None \
                else sample_weight[self._test_indices]

        if self._valid_indices is not None:
            y_valid = y[self._valid_indices]
            sample_weight_valid = None if sample_weight is None \
                else sample_weight[self._valid_indices]

        return X_train, y_train, sample_weight_train, X_valid, y_valid, \
            sample_weight_valid, X_test, y_test, sample_weight_test

    def _get_memory_size(self):
        """Get total memory size of CV spilt class."""
        total_size = 0
        for k in self.__dict__:
            total_size += memory_utilities.get_data_memory_size(self.__dict__.get(k))

        return total_size

    @staticmethod
    def _get_stratified_kfold_splits(y, CV, full_index):
        """
        Create kfold stratified splits.

        :param y: Label data for creating the splits.
        :param CV: Number of folds.
        :param full_index: Full index for mapping.
        :return: List of train, validation split indices tuples.
        """
        warning_msg = 'Failed to create stratified CV splits.'
        splits = []
        try:
            kf = model_selection.StratifiedKFold(n_splits=CV)
            for train_index, valid_index in kf.split(full_index, y):
                splits.append((full_index[train_index], full_index[valid_index]))
        except Exception as ex:
            logging_utilities.log_traceback(ex, logger, is_critical=False,
                                            override_error_msg=warning_msg)

        if len(splits) != CV:
            logger.info(warning_msg)
            return []
        else:
            return splits


class _CVType:
    """Class for getting the different types of cross validation splits."""

    TrainValidationPercSplit = "TrainValidationPercSplit"
    TrainTestValidationPercSplit = "TrainTestValidationPercSplit"
    CustomCrossValidationSplit = "CustomCrossValidationSplit"
    KFoldCrossValidationSplit = "KFoldCrossValidationSplit"
    MonteCarloCrossValidationSplit = "MonteCarloCrossValidationSplit"
    TimeSeriesSplit = "TimeSeriesSplit"
    MiroTrainingTimeSeriesSplit = "MiroTrainingTimeSeriesSplit"
    TestCutoffCVSplit = "TestCutoffCVSplit"

    FULL_SET = {TrainValidationPercSplit,
                TrainTestValidationPercSplit,
                CustomCrossValidationSplit,
                KFoldCrossValidationSplit,
                MonteCarloCrossValidationSplit,
                TimeSeriesSplit,
                MiroTrainingTimeSeriesSplit,
                TestCutoffCVSplit}


class FeaturizedCVSplit:
    """Class for keeping track of the featurized version of CV splits train and validation sets."""

    def __init__(self, X_train_transformed, y_train, sample_wt_train,
                 X_test_transformed, y_test, sample_wt_test,
                 data_transformer=None):
        """Constructor."""
        self._X_train_transformed = X_train_transformed
        self._y_train = y_train
        self._sample_wt_train = sample_wt_train
        self._X_test_transformed = X_test_transformed
        self._y_test = y_test
        self._sample_wt_test = sample_wt_test
        self._data_transformer = data_transformer
        self._pickle_key = None
        self._cache_store = None

    def _clear_featurized_data_and_record_cache_store(self, cache_store=None, pickle_key=None):
        self._X_train_transformed = None
        self._y_train = None
        self._sample_wt_train = None
        self._X_test_transformed = None
        self._y_test = None
        self._sample_wt_test = None
        self._data_transformer = None
        self._pickle_key = pickle_key
        self._cache_store = cache_store

    def _recover_from_cache_store(self):
        if self._should_load_from_pickle():
            retrieve_data_list = self._cache_store.get([self._pickle_key])  # type: ignore
            featurized_cv_split = retrieve_data_list.get(self._pickle_key)
            return featurized_cv_split
        else:
            return self

    def _should_load_from_pickle(self):
        return self._X_train_transformed is None

    def __str__(self):
        """Return the string version of the members in this class."""
        some_str = "_X_train_transformed: " + str(self._X_train_transformed.shape) + "\n"
        some_str += "y_train: " + str(self._y_train.shape) + "\n"
        if self._sample_wt_train is not None:
            some_str += "sample_wt_train: " + str(self._sample_wt_train.shape) + "\n"
        if self._X_test_transformed is not None:
            some_str += "X_test_transformed: " + str(self._X_test_transformed.shape) + "\n"
        if self._y_test is not None:
            some_str += "y_test: " + str(self._y_test.shape) + "\n"
        if self._sample_wt_test is not None:
            some_str += "sample_wt_test: " + str(self._sample_wt_test.shape) + "\n"
        some_str += "size of split is: " + str(self._get_memory_size()) + "\n"
        return some_str

    def _get_memory_size(self):
        """Get total memory size of featurized CV split object."""
        total_size = 0
        for k in self.__dict__:
            total_size += memory_utilities.get_data_memory_size(self.__dict__.get(k))

        return total_size


class FeaturizedTrainValidTestSplit(FeaturizedCVSplit):
    """Class for keeping track of the featurized version of train, test and validation sets."""

    def __init__(self, X_train_transformed, y_train, sample_wt_train,
                 X_valid_transformed, y_valid, sample_wt_valid,
                 X_test_transformed, y_test, sample_wt_test,
                 data_transformer=None):
        """Constructor."""
        super().__init__(X_train_transformed, y_train, sample_wt_train,
                         X_test_transformed, y_test, sample_wt_test,
                         data_transformer)

        self._X_valid_transformed = X_valid_transformed
        self._y_valid = y_valid
        self._sample_wt_valid = sample_wt_valid

    def _clear_featurized_data_and_record_cache_store(self, cache_store=None, pickle_key=None):
        super()._clear_featurized_data_and_record_cache_store(cache_store, pickle_key)
        self._X_valid_transformed = None
        self._y_valid = None
        self._sample_wt_valid = None

    def __str__(self):
        """Return the string version of the members in this class."""
        some_str = "_X_train_transformed: " + str(self._X_train_transformed.shape) + "\n"
        some_str += "y_train: " + str(self._y_train.shape) + "\n"
        if self._sample_wt_train is not None:
            some_str += "sample_wt_train: " + str(self._sample_wt_train.shape) + "\n"
        if self._X_test_transformed is not None:
            some_str += "X_test_transformed: " + \
                str(self._X_test_transformed.shape) + "\n"
        if self._y_test is not None:
            some_str += "y_test: " + str(self._y_test.shape) + "\n"
        if self._sample_wt_test is not None:
            some_str += "sample_wt_test: " + str(self._sample_wt_test.shape) + "\n"
        if self._X_valid_transformed is not None:
            some_str += "X_valid_transformed: " + str(self._X_valid_transformed.shape) + "\n"
        if self._y_valid is not None:
            some_str += "y_valid: " + str(self._y_valid.shape) + "\n"
        if self._sample_wt_valid is not None:
            some_str += "sample_wt_valid: " + str(self._sample_wt_valid.shape) + "\n"
        some_str += "size of split is: " + str(self._get_memory_size()) + "\n"

        return some_str
