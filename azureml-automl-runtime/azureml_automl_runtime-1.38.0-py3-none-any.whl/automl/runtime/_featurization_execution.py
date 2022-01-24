# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for splitting and or featurizing AutoML data."""
import logging
from typing import Any, Dict, Optional, Tuple, Union, cast

import numpy as np
import pandas as pd
from azureml.automl.core._experiment_observer import ExperimentObserver, ExperimentStatus
from azureml.automl.core.constants import SweepingMode
from azureml.automl.core.shared import constants, logging_utilities
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.constants import Transformers
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime import _data_transformation_utilities
from azureml.automl.runtime import _ml_engine as ml_engine
from azureml.automl.runtime import data_transformation
from azureml.automl.runtime._feature_sweeped_state_container import FeatureSweepedStateContainer
from azureml.automl.runtime.data_context import RawDataContext, TransformedDataContext
from azureml.automl.runtime.experiment_store import ExperimentStore
from azureml.automl.runtime.faults_verifier import VerifierManager
from azureml.automl.runtime.featurization import DataTransformer
from azureml.automl.runtime.shared._cv_splits import FeaturizedCVSplit, _CVSplits
from azureml.automl.runtime.shared.cache_store import CacheStore
from azureml.automl.runtime.shared.types import DataInputType, DataSingleColumnInputType
from scipy import sparse

logger = logging.getLogger(__name__)


def _featurize_training_data(
    raw_data_context: RawDataContext,
    working_dir: str,
    experiment_observer: ExperimentObserver,
    verifier: VerifierManager,
    feature_sweeped_state_container: FeatureSweepedStateContainer,
    feature_sweeping_config: Dict[str, Any] = {},
) -> TransformedDataContext:
    """
    Finishes data transformation by running full featurization on the transformers
    identified in the feature sweeping stage.

    This method should only be called for classification and regression cases where streaming
    is not enabled. Additionally this method should not be called in cases where featurization
    is false (either configured by user or when data comes in as sparse).

    Note: Only the training data (i.e. data from which the model learns from) is featurized.

    :param raw_data_context: The raw input data.
    :param working_dir: Working directory to use for featurization/training.
    :param experiment_observer: The experiment observer.
    :param verifier: The verifier to check input data quality.
    :param feature_sweeping_config: The config for feature sweeping. Used for class balancing if required.
    :param feature_sweeped_state_container: Object holding information generated in feature sweeping.
    :return: Transformed data context.
    """
    data_transformer = feature_sweeped_state_container.data_transformer
    transformed_data_context = feature_sweeped_state_container.transformed_data_context
    y_transformer = feature_sweeped_state_container.y_transformer
    y = feature_sweeped_state_container.y

    Contract.assert_value(
        data_transformer,
        "feature_sweeped_state_container.data_transformer",
        reference_code=ReferenceCodes._COMPLETE_FEATURIZATION_DT,
        log_safe=True)

    enable_class_balancing = False
    if transformed_data_context.task_type == constants.Tasks.CLASSIFICATION:
        enable_class_balancing, size_of_smallest_class, name_of_smallest_class = \
            data_transformation._class_balancing_check(y, y_transformer)

    transformer = None

    transformed_data_context.X = _data_transformation_utilities._add_raw_column_names_to_X(
        transformed_data_context.X,
        raw_data_context.x_raw_column_names)

    # fit features and transform data
    transformer, transformed_data_context.X = _get_transformer_x(
        x=transformed_data_context.X,
        y=transformed_data_context.y,
        dt=data_transformer,
        experiment_observer=experiment_observer
    )

    transformed_data_context._set_transformer(x_transformer=transformer)
    # Sweeping for class balancing techniques
    if enable_class_balancing:
        balancing_result = _perform_class_balancing_sweeping(
            transformed_data_context.task_type,
            transformed_data_context.X,
            transformed_data_context.y,
            enable_class_balancing=enable_class_balancing,
            working_dir=working_dir,
            experiment_observer=experiment_observer,
            feature_sweeping_config=feature_sweeping_config,
            is_cross_validation=transformed_data_context._is_cross_validation_scenario()
        )

        if balancing_result is not None and len(balancing_result) > 0:
            for k, v in balancing_result.items():
                if k == "weights":
                    transformed_data_context.sample_weight = v
            class_balancing_fixed = True
            verifier.update_data_verifier_for_class_balancing_validation(
                enable_class_balancing,
                class_balancing_fixed,
                size_of_smallest_class,
                name_of_smallest_class,
                y.shape[0])

    transformed_data_context._set_transformer(
        transformer, y_transformer=y_transformer, ts_transformer=None
    )

    logger.info("The size of transformed data is: " + str(transformed_data_context._get_memory_size()))

    return transformed_data_context


# TODO: How is [X|y] below different from raw_data_context.[X|y]? from transformed_data_context.[X|y]?
def _featurize_all_cv_folds(
    transformed_data_context: TransformedDataContext,
    raw_data_context: RawDataContext,
    X: np.ndarray,
    y: np.ndarray,
    sample_weight: Optional[np.ndarray],
    experiment_observer: ExperimentObserver
) -> None:
    """
    Create featurized data for individual CV splits using the data transformer.
    This method should only be called if creation of cv splits is required (even if featurization is turned off).

    Each cross validation fold is split, featurized and saved into the cache store to free up memory.

    :param raw_data_context: The raw data context.
    :param X: Raw training data
    :param y: Raw output variable data
    :param sample_weight: Sample weight
    :param experiment_observer: The experiment observer.
    :return:
    """
    Contract.assert_value(transformed_data_context.cv_splits, "transformed_data_context.cv_splits")
    cv_splits = cast(_CVSplits, transformed_data_context.cv_splits)

    Contract.assert_true(cv_splits.get_cv_split_indices() is not None,
                         "CV splits should be available before featurizing individual folds.",
                         log_safe=True)

    # A valid data transformer is required to featurize
    Contract.assert_type(
        transformed_data_context.transformers.get(Transformers.X_TRANSFORMER),
        "data_transformer",
        expected_types=DataTransformer,
        log_safe=True
    )
    data_transformer = cast(DataTransformer, transformed_data_context.transformers.get(Transformers.X_TRANSFORMER))

    logger.info("Creating cross validations using {} strategy.".format(str(cv_splits._cv_split_type)))

    experiment_observer.report_status(
        ExperimentStatus.DatasetCrossValidationSplit, "Generating individually featurized CV splits.")

    raw_X = _data_transformation_utilities._add_raw_column_names_to_X(
        X,
        raw_data_context.x_raw_column_names,
        None
    )
    raw_y = y

    logger.info("Creating featurized version of cross validation folds.")

    # Walk all CV split indices and featurize individual train and validation set pair
    cv_splits._featurized_cv_splits = []
    cv_split_index = 0
    for X_train, y_train, sample_wt_train, X_valid, y_valid, sample_wt_valid \
            in cv_splits.apply_CV_splits(raw_X, raw_y, sample_weight):
        logger.info("Processing a CV split at index {}.".format(cv_split_index))

        Contract.assert_true(
            X_valid.shape[0] != 0,
            "Dataset input was empty, resulting in empty validation set",
            target="X",
            reference_code=ReferenceCodes._DATA_TRANSFORMATION_TEST_EMPTY,
            log_safe=True
        )

        logger.info("Running fit_transform on training fold {}.".format(cv_split_index))
        X_train = ml_engine.featurize(X_train, y_train, data_transformer)
        logger.info("Running transform on validation fold {}.".format(cv_split_index))
        X_valid = data_transformer.transform(X_valid)

        # Create the featurized CV split object
        featurized_cv = FeaturizedCVSplit(
            X_train, y_train, sample_wt_train,
            X_valid, y_valid, sample_wt_valid, None)

        logger.info(str(featurized_cv))

        expr_store = ExperimentStore.get_instance()
        expr_store.data.materialized.cv_splits[
            TransformedDataContext.FEATURIZED_CV_SPLIT_KEY_INITIALS + str(cv_split_index)
        ] = featurized_cv

        # Clear the in-memory data for the featurized data and record the cache store and key
        featurized_cv._clear_featurized_data_and_record_cache_store(
            transformed_data_context.cache_store,
            TransformedDataContext.FEATURIZED_CV_SPLIT_KEY_INITIALS + str(cv_split_index))

        cv_train_dataset_cat = data_transformer._get_dataset_categoricals()
        if cv_train_dataset_cat:
            transformed_data_context._set_dataset_categoricals(TransformedDataContext.FEATURIZED_CV_SPLIT_KEY_INITIALS
                                                               + str(cv_split_index), cv_train_dataset_cat)

        cv_split_index += 1

        # Append to the list of featurized CV splits
        cv_splits._featurized_cv_splits.append(featurized_cv)

    logger.info("Completed creating cross-validation folds and featurizing them")


def _featurize_validation_dataset(
        data_transformer: DataTransformer, X_valid: pd.DataFrame, x_raw_column_names: np.ndarray
) -> Union[pd.DataFrame, sparse.spmatrix]:
    """
    Featurize the validation dataset.

    :param data_transformer:
    :param X_valid: Validated, raw and a cleaned (e.g. of NaNs) version of validation dataset
    :param x_raw_column_names: Feature names as mapped to the raw training (or validation) dataset
    :return: Transformed data after running the pipeline defined by data_transformer.
    """
    Contract.assert_value(X_valid, "X_valid should be non-null for a non-CV scenario.")
    Contract.assert_value(data_transformer, "data_transformer")

    result = _data_transformation_utilities._add_raw_column_names_to_X(X_valid, x_raw_column_names)
    result = data_transformer.transform(result)

    logger.info("Completed featurizing validation dataset.")
    return result


def _get_transformer_x(
    x: DataInputType,
    y: np.ndarray,
    dt: DataTransformer,
    experiment_observer: Optional[ExperimentObserver] = None
) -> Tuple[DataTransformer, Any]:
    """
    Given data, compute transformations and transformed data.

    :param x: input data
    :param y: labels
    :param dt:
    :param experiment_observer:
    :return:
    """
    if experiment_observer is not None:
        experiment_observer.report_status(
            ExperimentStatus.DatasetFeaturization, "Beginning to fit featurizers and featurize the dataset.")

    x_transform = ml_engine.featurize(x, y, dt)

    if experiment_observer is not None:
        experiment_observer.report_status(
            ExperimentStatus.DatasetFeaturizationCompleted, "Completed fit featurizers and featurizing the dataset.")

    return dt, x_transform


def _perform_class_balancing_sweeping(task_type: str, df: DataInputType,
                                      y: DataSingleColumnInputType,
                                      enable_class_balancing: bool,
                                      working_dir: str,
                                      experiment_observer: Optional[ExperimentObserver] = None,
                                      feature_sweeping_config: Dict[str, Any] = {},
                                      is_cross_validation: bool = False) -> Dict[str, Any]:
    """
    Perform sweeping over balancing strategies and return name of balancing strategies which outperforms
    the original metrics.

    :param task_type: Task type.
    :param df: Input data frame.
    :param y: Input labels.
    :param enable_class_balancing: Boolean
    :param feature_sweeping_config: Enable or disable balancing.
    :param is_cross_validation: Whether to do the cross validation
    :return: Use class weight, class weight
    """
    if experiment_observer is not None:
        experiment_observer.report_status(ExperimentStatus.DatasetBalancing,
                                          "Performing class balancing sweeping")
    try:
        if enable_class_balancing:
            logger.info("Performing class balancing sweeping")

            from azureml.automl.runtime.sweeping.meta_sweeper import MetaSweeper

            balancing_sweeper = MetaSweeper(task=task_type,
                                            timeout_sec=3600,
                                            is_cross_validation=is_cross_validation,
                                            feature_sweeping_config=feature_sweeping_config)

            balancing_result = balancing_sweeper.sweep(working_dir, df, y, sweeping_mode=SweepingMode.Balancing)
            logger.info("Finished class balancing sweeping")
            if balancing_result is not None:
                for balancer in balancing_result:
                    if balancer == "ClassWeight":
                        logger.info("Adding class weight to data context")
                        weights = data_transformation._compute_sample_weight(y)
                        return {'weights': weights}
            return {}
    except Exception as e:
        # Never fail the main run even if sweeping fails.
        logging_utilities.log_traceback(e, logger)

    return {}


def featurize_train_valid_data(
        X: DataInputType,
        y: np.ndarray,
        raw_data_context: RawDataContext,
        working_dir: str,
        experiment_observer: ExperimentObserver,
        feature_sweeped_state_container: FeatureSweepedStateContainer,
        feature_sweeping_config: Dict[str, Any],
        verifier: VerifierManager) -> TransformedDataContext:
    """
    Transform the training and validation datasets, using the data transformer within feature_sweeped_state_container.

    Used only by Classification and Regression task types

    :param X: Raw training data
    :param y: Raw output variable data
    :param raw_data_context: The raw data context.
    :param working_dir: Directory to store intermediate data
    :param experiment_observer: Instance of ExperimentObserver to report on experiment progress
    :param feature_sweeped_state_container: State container to describe the state of feature sweeping
    :param feature_sweeping_config: Configuration that was used for feature sweeping
    :param verifier: VerifierManager for registering guardrails
    :return:
    """
    # First featurize the training data. This will be the complete data in case of CV, and just the 'X'
    # (i.e. training data) in case of train-valid splits
    td_ctx = _featurize_training_data(
        raw_data_context,
        working_dir=working_dir,
        experiment_observer=experiment_observer,
        verifier=verifier,
        feature_sweeped_state_container=feature_sweeped_state_container,
        feature_sweeping_config=feature_sweeping_config
    )

    Contract.assert_type(
        td_ctx.transformers.get(Transformers.X_TRANSFORMER),
        "data_transformer",
        expected_types=DataTransformer,
        log_safe=True
    )
    data_transformer = cast(DataTransformer, td_ctx.transformers.get(Transformers.X_TRANSFORMER))

    x_dataset_cat = data_transformer._get_dataset_categoricals()
    if x_dataset_cat:
        td_ctx._set_dataset_categoricals("X", x_dataset_cat)

    logger.info("featurize_train_valid_data set the dataset categoricals " + str(x_dataset_cat))

    # Auto featurization check, no validation split required. // is autofeaturization
    if td_ctx._is_autofeaturization_scenario():
        return td_ctx

    if td_ctx._is_cross_validation_scenario():
        # For CV scenarios, X_valid will be None. Featurization of cross-validation folds is required.
        Contract.assert_true(td_ctx.X_valid is None, "X_valid should not be set for CV scenarios.")
        # TODO: Plumb data_transformer from above into the below call
        _featurize_all_cv_folds(
            td_ctx,
            raw_data_context,
            X,
            y,
            td_ctx.sample_weight,
            experiment_observer
        )
        # Refit transformers
        # Only do this for CV since for train-valid this is incorrect, see 507941s
        # TODO: evaluate if this refit is even necessary
        #  CV as a fit on all the data is already done above, see 518786
        raw_X = _data_transformation_utilities._add_raw_column_names_to_X(
            X,
            raw_data_context.x_raw_column_names,
            None)
        td_ctx._refit_transformers(raw_X, y)
    else:
        td_ctx.X_valid = _featurize_validation_dataset(
            data_transformer, td_ctx.X_valid, raw_data_context.x_raw_column_names)
        dataset_cat = data_transformer._get_dataset_categoricals()
        if dataset_cat:
            td_ctx._set_dataset_categoricals("X_valid", dataset_cat)
    return td_ctx
