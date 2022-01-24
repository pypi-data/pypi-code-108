# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for splitting and or featurizing AutoML data for timeseries tasks."""
from typing import cast, Any, Dict, List, Optional
import logging

import numpy as np
import pandas as pd
from scipy import sparse

from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty

from azureml.automl.core.featurization import FeaturizationConfig
from azureml.automl.core.shared import constants
from azureml.automl.core.shared.exceptions import ConfigException, DataException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    TimeseriesLeadingNans,
    TimeseriesLaggingNans
)
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core._experiment_observer import ExperimentStatus, ExperimentObserver
from azureml.automl.runtime import _data_transformation_utilities, _ml_engine as ml_engine
from azureml.automl.runtime.data_context import RawDataContext, TransformedDataContext
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.runtime.faults_verifier import VerifiedFaultsTypes, VerifierManager, VerifierResults
from azureml.automl.runtime.featurizer.transformer import TimeSeriesPipelineType, TimeSeriesTransformer
from azureml.automl.runtime.featurizer.transformer.timeseries import timeseries_transformer
from azureml.automl.runtime.shared import forecasting_utils
from azureml.automl.runtime.shared._cv_splits import _CVSplits, FeaturizedCVSplit
from sklearn.base import TransformerMixin

_logger = logging.getLogger(__name__)


def featurize_data_timeseries(
    raw_data_context: RawDataContext,
    transformed_data_context: TransformedDataContext,
    experiment_observer: ExperimentObserver,
    verifier: VerifierManager,
    y_transformer: Optional[TransformerMixin] = None
) -> TransformedDataContext:
    """
    Finishes data transformation by running full featurization on the transformers
    identified in the feature sweeping stage.

    This method should only be called during timeseries runs.

    :param raw_data_context: The raw input data.
    :param transformed_data_context: The object which will be transformed.
    :param experiment_observer: The experiment observer.
    :param verifier: The verifier to check input data quality.
    :param y_transformer: The y_transformer object that was created for target data.
    :return: Transformed data context.
    """
    timeseries_param_dict = raw_data_context.timeseries_param_dict
    assert timeseries_param_dict

    if raw_data_context.featurization is not None and \
            raw_data_context.label_column_name is not None and \
            isinstance(raw_data_context.featurization, FeaturizationConfig):
        raw_data_context.featurization._convert_timeseries_target_column_name(
            raw_data_context.label_column_name)

    transformed_data_context.X = _data_transformation_utilities._add_raw_column_names_to_X(
        transformed_data_context.X,
        transformed_data_context.x_raw_column_names,
        timeseries_param_dict.get(constants.TimeSeries.TIME_COLUMN_NAME))

    # Translation from "off" or "auto" happens here.
    featurization_config = FeaturizationConfig()
    if isinstance(raw_data_context.featurization, FeaturizationConfig):
        featurization_config = raw_data_context.featurization

    ts_transformer, transformed_data = _get_ts_transformer_x(
        transformed_data_context.X,
        transformed_data_context.y,
        timeseries_param_dict,
        for_cv=False,
        experiment_observer=experiment_observer,
        featurization_config=featurization_config,
        fault_verifier=verifier
    )

    # Add guard rails for time series.
    _add_forecasting_guardrails_maybe(ts_transformer, verifier)

    # Report heuristic features if any and if experiment_observer is not None.
    _print_heuristics_maybe(experiment_observer, ts_transformer)

    target_column_name = ts_transformer.target_column_name
    Contract.assert_true(target_column_name in transformed_data.columns,
                         'Expected the transformed training set to contain the target column.',
                         log_safe=True)
    transformed_data_context.y = transformed_data.pop(target_column_name).values
    transformed_data_context.X = transformed_data

    if transformed_data_context.X_valid is not None:
        transformed_data_context.X_valid = _data_transformation_utilities._add_raw_column_names_to_X(
            transformed_data_context.X_valid,
            transformed_data_context.x_raw_column_names,
            timeseries_param_dict.get(constants.TimeSeries.TIME_COLUMN_NAME))
        transformed_data_valid = ts_transformer.transform(
            transformed_data_context.X_valid,
            transformed_data_context.y_valid
        )
        # For validation data when lags/rolling windows are enabled, need to select latest origin dates
        # so predictioin from classical forecasting models and regression models alligned in ensemble/scoring.
        if ts_transformer.origin_column_name in transformed_data_valid.index.names:
            transformed_data_valid = ts_transformer._select_latest_origin_dates(transformed_data_valid)
        transformed_data_context.y_valid = transformed_data_valid.pop(target_column_name).values
        transformed_data_context.X_valid = transformed_data_valid

    transformed_data_context.timeseries_param_dict = ts_transformer.parameters
    # Add column names generated from lag_lead and rolling_windows operator to timeseries_param_dict,
    # to be removed later for classical forecasting models and Prophet in _multi_grain_forecast_base.py,
    # since those learners doesn't need those columns, and in fact need to remove them in order to elimitate
    # duplex time index generated from lookback features (lags/rolling windows).
    for name, transformer in ts_transformer.pipeline.steps:
        if name == constants.TimeSeriesInternal.LAG_LEAD_OPERATOR:
            transformed_data_context.timeseries_param_dict[constants.TimeSeriesInternal.LAGGING_COLUMNS] = \
                transformer._lag_columns
        if name == constants.TimeSeriesInternal.ROLLING_WINDOW_OPERATOR:
            transformed_data_context.timeseries_param_dict[constants.TimeSeriesInternal.ROLLING_WINDOW_COLUMNS] = \
                transformer._rolling_window_columns

    if sparse.issparse(transformed_data_context.X):
        transformed_data_context.X = transformed_data_context.X.todense()

    transformed_data_context._set_transformer(
        x_transformer=None, y_transformer=y_transformer, ts_transformer=ts_transformer
    )

    transformed_data_context._update_cache()
    _logger.info("The size of transformed data is: " + str(transformed_data_context._get_memory_size()))

    return transformed_data_context


def split_and_featurize_data_timeseries(
    transformed_data_context: TransformedDataContext,
    raw_data_context: RawDataContext,
    X: np.ndarray,
    y: np.ndarray,
    sample_weight: Optional[np.ndarray],
    experiment_observer: ExperimentObserver
) -> None:
    """
    Create featurized data for individual CV splits using the timeseries transformer.

    This method should only be called if creation of cv splits is required.

    :param raw_data_context: The raw data context.
    :param X: Raw training data
    :param y: Raw output variable data
    :param sample_weight: Sample weight
    :return:
    """
    _logger.info("Creating cross validations")
    experiment_observer.report_status(
        ExperimentStatus.DatasetCrossValidationSplit,
        "Generating individually featurized CV splits."
    )

    time_colname = raw_data_context.timeseries_param_dict.get(constants.TimeSeries.TIME_COLUMN_NAME)
    raw_X = _data_transformation_utilities._add_raw_column_names_to_X(X, raw_data_context.x_raw_column_names,
                                                                      time_colname)
    raw_y = y

    # If we have a timeseries dataframe with heuristic parameters, we need to replace these parameters.
    # If it is not a time series, just set ts_param_dict_copy to be a
    # reference on raw_data_context.timeseries_param_dict
    ts_param_dict_copy = raw_data_context.timeseries_param_dict
    # If raw_data_context.timeseries_param_dict contains data, swap all auto parameters to be
    # inferenced parameters.
    _logger.info("Timeseries param dict contains data, inferencing parameters.")
    ts_param_dict_copy = raw_data_context.timeseries_param_dict.copy()
    tst = transformed_data_context.transformers.get(constants.Transformers.TIMESERIES_TRANSFORMER)
    if tst is not None:
        # Swap the auto parameters by theit inferenced values.
        if ts_param_dict_copy.get(constants.TimeSeries.MAX_HORIZON) == constants.TimeSeries.AUTO:
            ts_param_dict_copy[constants.TimeSeries.MAX_HORIZON] = tst.max_horizon
        if ts_param_dict_copy.get(constants.TimeSeriesInternal.WINDOW_SIZE) == constants.TimeSeries.AUTO:
            rw_transform = forecasting_utils.get_pipeline_step(
                tst.pipeline, constants.TimeSeriesInternal.ROLLING_WINDOW_OPERATOR)
            if rw_transform is not None:
                ts_param_dict_copy[constants.TimeSeriesInternal.WINDOW_SIZE] = rw_transform.window_size
        lags_dict = cast(Dict[str, Any], ts_param_dict_copy.get(constants.TimeSeriesInternal.LAGS_TO_CONSTRUCT))
        if lags_dict and lags_dict.get(tst.target_column_name) == [constants.TimeSeries.AUTO]:
            lag_lead = forecasting_utils.get_pipeline_step(
                tst.pipeline, constants.TimeSeriesInternal.LAG_LEAD_OPERATOR)
            if lag_lead is not None:
                ts_param_dict_copy[constants.TimeSeriesInternal.LAGS_TO_CONSTRUCT] = lag_lead.lags_to_construct
        # If the short grains will be removed from the series, we need to make sure that the corresponding
        # grains will not get to the rolling origin validator, and it will not fail.
        short_series_processor = forecasting_utils.get_pipeline_step(
            tst.pipeline, constants.TimeSeriesInternal.SHORT_SERIES_DROPPEER)
        # Despite ts_param_dict_copy should return Optional[str], we know that grains internally
        # are represented by Optional[List[str]].
        grains = cast(Optional[List[str]], ts_param_dict_copy.get(constants.TimeSeries.GRAIN_COLUMN_NAMES))
        # If short series are being dropped and if there are grains, drop them.
        # Note: if there is no grains i.e. data set contains only one grain, and it have to be dropped,
        # we will show error on the initial data transformation.
        if short_series_processor is not None and short_series_processor.has_short_grains_in_train \
                and grains is not None and len(grains) > 0:
            # Preprocess raw_X so that it will not contain the short grains.
            dfs = []
            raw_X[constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN] = raw_y
            for grain, df in raw_X.groupby(grains):
                if grain in short_series_processor.grains_to_keep:
                    dfs.append(df)
            raw_X = pd.concat(dfs)
            raw_y = raw_X.pop(constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN).values
            del dfs

    # Create CV splits object
    transformed_data_context.cv_splits = \
        _CVSplits(raw_X, raw_y,
                  frac_valid=transformed_data_context.validation_size,
                  CV=transformed_data_context.num_cv_folds,
                  n_step=transformed_data_context.n_step,
                  cv_splits_indices=transformed_data_context.cv_splits_indices,
                  is_time_series=raw_data_context.timeseries,
                  timeseries_param_dict=ts_param_dict_copy,
                  task=raw_data_context.task_type)
    _logger.info("Found cross validation type: " + str(transformed_data_context.cv_splits._cv_split_type))

    # "If featurization was enabled and we created a time series transformer, then feautrize the individual CV splits
    ts_transformer = transformed_data_context.transformers.get(constants.Transformers.TIMESERIES_TRANSFORMER)
    if ts_transformer:
        if transformed_data_context.cv_splits.get_cv_split_indices() is not None:
            _logger.info("Creating featurized version of CV splits data")

            # Walk all CV split indices and featurize individual train and validation set pair
            transformed_data_context.cv_splits._featurized_cv_splits = []
            cv_split_index = 0
            for X_train, y_train, sample_wt_train, X_valid, y_valid, sample_wt_valid \
                    in transformed_data_context.cv_splits.apply_CV_splits(raw_X, raw_y, sample_weight):
                _logger.info("Processing a CV split at index {}.".format(cv_split_index))

                if X_valid.shape[0] == 0:
                    raise DataException._with_error(AzureMLError.create(
                        TimeseriesLaggingNans, target="X_valid",
                        reference_code=ReferenceCodes._DATA_TRANSFORMATION_TEST_EMPTY_TS)
                    )

                Contract.assert_true(
                    raw_data_context.timeseries_param_dict is not None,
                    "Expected non-none timeseries parameter dict", log_safe=True
                )
                _logger.info("Time series transformer present, running transform operations.")
                # Need to do pipeline introspection on ts_transformer for CV featurization.
                # For compatibility with old SDK versions, re-compute the ts_transformer feature graph
                # if it is not set
                ts_transformer._create_feature_transformer_graph_if_not_set(raw_X, y=raw_y)

                # Get list of time index features used on full train set fit
                non_holiday_features = ts_transformer.time_index_non_holiday_features
                ts_split_param_dict = raw_data_context.timeseries_param_dict.copy()
                # Make sure we use the frequency inferred on all the data frame, but not on
                # smaller validation part.
                ts_split_param_dict[constants.TimeSeries.FREQUENCY] = ts_transformer.freq_offset
                ts_split_param_dict[constants.TimeSeries.SEASONALITY] = ts_transformer.seasonality
                ts_split_param_dict[constants.TimeSeriesInternal.FORCE_TIME_INDEX_FEATURES_NAME] = \
                    non_holiday_features

                featurization_config = FeaturizationConfig()
                if isinstance(raw_data_context.featurization, FeaturizationConfig):
                    featurization_config = raw_data_context.featurization

                ts_split_transformer, X_train = \
                    _get_ts_transformer_x(
                        X_train,
                        y_train,
                        ts_split_param_dict,
                        featurization_config=featurization_config,
                        for_cv=True,
                        experiment_observer=experiment_observer,
                    )
                # Join with full featurized set to get re-useable features
                X_train = TimeSeriesTransformer._join_reusable_features_for_cv(
                    ts_split_transformer,
                    X_train,
                    ts_transformer,
                    transformed_data_context.X
                )

                Contract.assert_true(
                    ts_split_transformer.target_column_name in X_train.columns,
                    'Expected the transformed train split to contain the target column.',
                    log_safe=True
                )
                y_train = X_train.pop(ts_split_transformer.target_column_name).values

                # For the purpose of removing nans brought by look-back features for regression based models but not
                # for classical forecasting models, we omitted the step which removes those nans for all models at the
                # end of featurization for time series data, and resume it before training/forecast/model explanation
                # for the necessary models instead. However, the exception should still be raised since the CV split
                # would be empty for regression-based models. So we mimick the behavior of removing those nans here.
                # Look-back features were brought from the full pipeline, so we use ts_transfromer to remove the nans.
                X_train_nans_removed, y_train_nans_removed = X_train.copy(), y_train.copy()
                X_train_nans_removed, y_train_nans_removed = ts_transformer._remove_nans_from_look_back_features(
                    X_train_nans_removed, y_train_nans_removed)
                if X_train_nans_removed.shape[0] == 0:
                    # This can happen only if we have long target_lag or rolling window size
                    # and leading NaNs which were not trimmed during pre processing step.
                    raise DataException._with_error(AzureMLError.create(
                        TimeseriesLeadingNans, target="X",
                        reference_code=ReferenceCodes._DATA_TRANSFORMATION_TRAIN_EMPTY)
                    )

                # Add the target column to the test dataframe prior to transform
                # to ensure the target stays aligned with the transformed features
                X_valid[ts_split_transformer.target_column_name] = y_valid
                X_valid = ts_split_transformer.transform(X_valid)
                X_valid = TimeSeriesTransformer._join_reusable_features_for_cv(
                    ts_split_transformer,
                    X_valid,
                    ts_transformer,
                    transformed_data_context.X
                )

                # Need to apply some corrections when data has horizon-dependent features (i.e. Lags/RW)
                if ts_transformer.origin_column_name in X_valid.index.names:
                    # X_valid may have some origin times later than the latest known train times
                    latest_known_dates = \
                        {gr: df.index.get_level_values(ts_transformer.time_column_name).max()
                         for gr, df in X_train.groupby(ts_transformer.grain_column_names)}
                    X_valid = (X_valid.groupby(ts_transformer.grain_column_names, group_keys=False)
                               .apply(lambda df:
                                      ts_transformer._select_known_before_date(df, latest_known_dates[df.name],
                                                                               ts_transformer.freq_offset)))

                    # To match forecasting logic, select predictions made from most recent origin times
                    X_valid = ts_transformer._select_latest_origin_dates(X_valid)
                    if X_valid.shape[0] == 0:
                        # This happens when we do not have enough data points
                        # at the end of data set to generate lookback features for
                        # validation set (trimmed in _select_latest_origin_dates).
                        raise DataException._with_error(AzureMLError.create(
                            TimeseriesLaggingNans, target="X_valid",
                            reference_code=ReferenceCodes._DATA_TRANSFORMATION_TS_INSUFFICIENT_DATA)
                        )
                # We expect that the target is in the transformed test data
                # Pop it out to ensure y_valid is aligned with transformed X_valid
                Contract.assert_true(
                    ts_split_transformer.target_column_name in X_valid.columns,
                    'Expected the transformed test split to contain the target column.',
                    log_safe=True
                )
                y_valid = X_valid.pop(ts_split_transformer.target_column_name).values

                # Create the featurized CV split object
                featurized_cv = FeaturizedCVSplit(
                    X_train, y_train, sample_wt_train,
                    X_valid, y_valid, sample_wt_valid, None)

                expr_store = ExperimentStore.get_instance()
                expr_store.data.materialized.cv_splits[
                    TransformedDataContext.FEATURIZED_CV_SPLIT_KEY_INITIALS + str(cv_split_index)
                ] = featurized_cv

                _logger.info(str(featurized_cv))

                # Clear the in-memory data for the featurized data and record the cache store and key
                featurized_cv._clear_featurized_data_and_record_cache_store(
                    transformed_data_context.cache_store,
                    TransformedDataContext.FEATURIZED_CV_SPLIT_KEY_INITIALS + str(cv_split_index))

                cv_split_index += 1

                # Append to the list of featurized CV splits
                transformed_data_context.cv_splits._featurized_cv_splits.append(featurized_cv)
        else:
            # Timeseries should always use the cv split code path.
            raise ConfigException._with_error(AzureMLError.create(
                ArgumentBlankOrEmpty, argument_name="n_cross_validations", target="n_cross_validations")
            )

    _logger.info("Completed creating cross-validation folds and featurizing them")


def _add_forecasting_guardrails_maybe(ts_transformer: TimeSeriesTransformer,
                                      verifier: VerifierManager) -> None:
    """
    Add guardrails for the forecasting lookback features.

    :param ts_transformer: The fitted TimeSeriesTransformer.
    :param verifier: The VerifierManager to add guardrails to.
    """
    lags = constants.TimeSeriesInternal.LAGS_TO_CONSTRUCT in ts_transformer.parameters.keys()
    rw = constants.TimeSeriesInternal.WINDOW_SIZE in ts_transformer.parameters.keys()
    verifier.update_data_verifier_lookback_feature(
        lags=lags,
        rw=rw,
        passed=not ts_transformer.lookback_features_removed)
    # The guardrails for the short series handling.
    if ts_transformer.parameters[constants.TimeSeries.SHORT_SERIES_HANDLING_CONFIG] is None:
        # If we have a short grain and there is no handling, we have to fail before this stage.
        verifier.update_data_verifier_short_grain_handling([], [])
    elif not verifier.has_fault_member(VerifiedFaultsTypes.TIMESERIES_SHORT_SERIES_HANDLING):
        if ts_transformer.pipeline is None:
            ts_dropper = None
        else:
            ts_dropper = forecasting_utils.get_pipeline_step(
                ts_transformer.pipeline, constants.TimeSeriesInternal.SHORT_SERIES_DROPPEER)
        if ts_dropper is not None:
            verifier.update_data_verifier_short_grain_handling([], ts_dropper.short_grains_in_train_names)
        else:
            verifier.update_data_verifier_short_grain_handling([], [])


def _get_ts_transformer_x(x,
                          y,
                          timeseries_param_dict,
                          featurization_config,
                          for_cv=False,
                          experiment_observer=None,
                          fault_verifier=None):
    """
    Given data, compute transformations and transformed data.

    :param x: input data
    :param y: labels
    :param timeseries_param_dict: timeseries metadata
    :param logger: logger object for logging data from pre-processing
    :param featurization_config: The customized featurization configurations.
    :param fault_verifier: The fault verifier manager.
    :return: transformer, transformed_x
    """
    pipeline_type = TimeSeriesPipelineType.CV_REDUCED if for_cv else TimeSeriesPipelineType.FULL
    (
        forecasting_pipeline,
        timeseries_param_dict,
        lookback_removed,
        time_index_non_holiday_features
    ) = ml_engine.suggest_featurizers_timeseries(
        x,
        y,
        featurization_config,
        timeseries_param_dict,
        pipeline_type
    )
    tst = TimeSeriesTransformer(
        forecasting_pipeline,
        pipeline_type,
        featurization_config,
        time_index_non_holiday_features,
        lookback_removed,
        **timeseries_param_dict
    )

    if fault_verifier is not None:
        drop_columns = timeseries_param_dict.get(constants.TimeSeries.DROP_COLUMN_NAMES, [])
        if featurization_config.drop_columns is not None and \
                len(featurization_config.drop_columns) > 0:
            drop_columns_set = set(drop_columns)
            for col in featurization_config.drop_columns:
                if col not in drop_columns_set:
                    drop_columns.append(col)
        fault_verifier.update_data_verifier_for_missing_values_dataframe(
            x,
            timeseries_transformer._get_numerical_columns(
                x,
                constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN,
                drop_columns,
                featurization_config
            ),
            tst._featurization_config,
            drop_columns
        )

    if experiment_observer is not None:
        message = 'Beginning to featurize the CV split.' if for_cv else 'Beginning to featurize the dataset.'
        experiment_observer.report_status(
            ExperimentStatus.DatasetFeaturization, message)

    x_transform = ml_engine.featurize(x, y, tst)

    if experiment_observer is not None:
        message = 'Completed featurizing the CV split.' if for_cv else 'Completed featurizing the dataset.'
        experiment_observer.report_status(
            ExperimentStatus.DatasetFeaturizationCompleted, message)

    return tst, x_transform


def _print_heuristics_maybe(experiment_observer: ExperimentObserver,
                            tst: TimeSeriesTransformer) -> None:
    """Print out heuristics to experiment observer."""
    if experiment_observer is not None:
        auto_settings = []
        if tst.get_auto_lag() is not None:
            auto_settings.append('Target_Lag = \'{}\''.format(tst.get_auto_lag()))

        if tst.get_auto_window_size() is not None:
            auto_settings.append('Target_Rolling_Window = \'{}\''.format(tst.get_auto_window_size()))

        if tst.get_auto_max_horizon() is not None:
            auto_settings.append('Max_Horizon = \'{}\''.format(tst.get_auto_max_horizon()))

        if auto_settings:
            message = "Heuristic parameters: {}.\n".format(', '.join(auto_settings))
            if hasattr(experiment_observer, 'file_handler') and experiment_observer.file_handler is not None:
                # Local run
                # Directly output message to console.
                cast(Any, experiment_observer).file_handler.write(message)
            if experiment_observer.run_instance:  # type: ignore
                # Remote run.
                # Put the 'auto' tag to the run to use it later.
                cast(Any, experiment_observer).run_instance.set_tags({constants.TimeSeries.AUTO: message})
        # Set the automatic parameters anyways.
        if experiment_observer.run_instance:  # type: ignore
            # Set potentially heuristic parameters to run,
            # so they will be shown in the UI.
            properties_dict = {
                constants.TimeSeriesInternal.RUN_TARGET_LAGS: str(tst.get_target_lags()),
                constants.TimeSeriesInternal.RUN_WINDOW_SIZE: str(tst.get_target_rolling_window_size()),
                constants.TimeSeriesInternal.RUN_MAX_HORIZON: str(tst.max_horizon),
                constants.TimeSeriesInternal.RUN_FREQUENCY: str(tst.freq)
            }
            cast(Any, experiment_observer).run_instance.add_properties(properties_dict)
