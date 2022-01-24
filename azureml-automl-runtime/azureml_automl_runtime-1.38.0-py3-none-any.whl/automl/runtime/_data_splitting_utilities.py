# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for splitting datasets into training, validation and test sets."""
import logging
from typing import Tuple, cast, Optional

import numpy as np
import pandas as pd
from azureml.automl.runtime import _validation_strategy_selector
from azureml.automl.runtime.faults_verifier import VerifierManager
from sklearn.model_selection import train_test_split

from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared import constants
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.constants import Tasks, RuleBasedValidation
from azureml.automl.runtime._data_definition import MaterializedTabularData
from azureml.automl.runtime._data_definition.raw_experiment_data import RawExperimentData


logger = logging.getLogger(__name__)


def split_dataset(
        materialized_tabular_data: MaterializedTabularData,
        task_type: str = Tasks.CLASSIFICATION,
        split_ratio: float = RuleBasedValidation.DEFAULT_TRAIN_VALIDATE_TEST_SIZE,
) -> Tuple[MaterializedTabularData, MaterializedTabularData]:
    """
    Split the training_data into train & test datasets, as determined by the split ratio.

    Using stratified split for Classification task types. If the task type is regression, then using normal
    train test split.

    Default percentage for splitting a dataset is 10% (i.e., in the absence of any configuration, 10 percent of the
    training data is used as a test dataset.

    :param materialized_tabular_data: Tabular Data to split
    :type materialized_tabular_data: MaterializedTabularData
    :param task_type: One of 'classification' or 'regression'
    :param split_ratio: Ratio in which to split train & test datasets
    :return: A tuple of training and validation datasets
    """
    Contract.assert_true(
        task_type in {Tasks.CLASSIFICATION, Tasks.REGRESSION},
        message="Failed to split training dataset. Invalid task type was specified - {}".format(task_type),
        target="task_type",
        log_safe=True
    )

    # The random_state (seed) must be the same across all calls
    # to assure that the splits are identical since this method
    # is called more than once during a single AutoML run.
    random_state = RuleBasedValidation.DEFAULT_TRAIN_VALIDATE_RANDOM_STATE

    X_train = materialized_tabular_data.X
    y_train = materialized_tabular_data.y
    sample_weight_train = materialized_tabular_data.weights

    X, y, weights = None, None, None
    X_test, y_test, weights_test = None, None, None
    is_stratified = True

    if task_type == Tasks.CLASSIFICATION:
        logger.info("Performing train/test split using stratified sampling.")
        try:
            if sample_weight_train is None:
                X, X_test, y, y_test = train_test_split(
                    X_train, y_train, stratify=y_train,
                    test_size=split_ratio, random_state=random_state)
            else:
                X, X_test, y, y_test, weights, weights_test = train_test_split(
                    X_train, y_train, sample_weight_train, stratify=y_train,
                    test_size=split_ratio, random_state=random_state)
        except Exception as e:
            failure_cause = " "
            if isinstance(e, ValueError) and RuleBasedValidation.UNIQUE_CLASS_SUBSTR in str(e):
                failure_cause = " Minority class of incidence one detected. "
            elif isinstance(e, TypeError) and RuleBasedValidation.TARGET_TYPE_INCONSISTENCY_SUBSTR in str(e):
                failure_cause = " Inconsistent typing in target values breaks naive '<' comparison. "
            else:  # Unexpected failure reason, so log it as before.
                logging_utilities.log_traceback(e, logger)
            logger.warning("Rule based validation: Stratified split failed."
                           + failure_cause + "Falling back to using random sampling.")
            is_stratified = False

    if task_type == Tasks.REGRESSION or not is_stratified:
        logger.info("Performing train/test split using random sampling.")
        try:
            if sample_weight_train is None:
                X, X_test, y, y_test = train_test_split(
                    X_train, y_train, test_size=split_ratio, random_state=random_state)
            else:
                X, X_test, y, y_test, weights, weights_test = train_test_split(
                    X_train, y_train, sample_weight_train, test_size=split_ratio,
                    random_state=random_state)
        except Exception as e:
            logger.error("Failed to split training data into training and test datasets.")
            logging_utilities.log_traceback(e, logger)
            raise

    X = cast(pd.DataFrame, X)
    y = cast(np.ndarray, y)
    X_test = cast(pd.DataFrame, X_test)
    y_test = cast(np.ndarray, y_test)
    weights_test = cast(np.ndarray, weights_test)

    if not (X is None or y is None or X_test is None or y_test is None):
        info_message = "Extracted train/test split from training data. X: {}, y: {} X_test: {}, y_test: {}"
        info_message = info_message.format(X.shape, y.shape, X_test.shape, y_test.shape)
        logger.info(info_message)

    return MaterializedTabularData(X, y, weights), MaterializedTabularData(X_test, y_test, weights_test)


def update_training_data_splits(
        raw_experiment_data: RawExperimentData,
        automl_settings: AutoMLBaseSettings,
        verifier: Optional[VerifierManager] = None
) -> None:
    """
    Apply any validation strategy, if required, by splitting the original training data.
    If user requested a train-test split, split off the training data from original training data. The rest of the
    data splitting working set becomes the new training data (i.e. post split)
    If user requested a train-valid split via. validation_size, then we do the split here to set the right X_valid.

    If rule based validations were required (e.g. user did not define any model evaluation strategy), the chosen
    strategy is applied, either via. updating the AutoMLSettings provided as arguments (e.g. n_cross_validations),
    or via. splitting the training data and updating the validation data (e.g. X_valid) in raw_experiment_data.

    Note: This function can mutate the following arguments - raw_experiment_data, automl_settings

    :param raw_experiment_data: The user input data
    :param automl_settings: Settings to use for the experiment
    :param verifier: Instance of verifier manager to record guardrails
    :return: None
    """
    if automl_settings.iterations == constants.RuleBasedValidation.AUTOFEATURIZATION_ITERATION_COUNT:
        logger.info("User has chosen Auto featurization, no rule based validation needed.")
        return

    # TODO: Move streaming related splitting from data preparer in here.
    if automl_settings.enable_streaming:
        # Currently, data is already split in data preparer if streaming was enabled
        return

    # If a test split is specified then split the training dataset
    # in to train/test and throw away the test set since it is not needed.
    # An identical call will be made in the test run which only keeps the test
    # dataset from the train/test split. Note, this requires that the split
    # is repeatable across runs.
    if automl_settings.test_size > 0.0 and not automl_settings.is_timeseries:
        logger.info("Splitting training data into train-test data "
                    "using split ratio of: {}".format(automl_settings.test_size))
        tabular_data = MaterializedTabularData(
            raw_experiment_data.X, raw_experiment_data.y, raw_experiment_data.weights)
        train_data, _ = split_dataset(tabular_data, automl_settings.task_type, automl_settings.test_size)
        raw_experiment_data.X = train_data.X
        raw_experiment_data.y = train_data.y
        raw_experiment_data.weights = train_data.weights

    is_train_valid_split_required, split_ratio = False, 0.0
    validation_strategy = None  # type: Optional[_validation_strategy_selector.ValidationStrategy]

    if automl_settings.validation_size > 0.0 and not automl_settings.n_cross_validations:
        # User has requested a train-valid split for model comparisons, using a custom validation size.
        # `n_cross_validations == 0 | None` ensures we aren't in a Monte-Carlo CV mode.
        Contract.assert_true(
            raw_experiment_data.X_valid is None,
            "X_valid should not be set when alternate validation strategies are already provided. "
            "validation_size={}; n_cross_validations={}".format(
                automl_settings.validation_size, automl_settings.n_cross_validations),
            target='X_valid', log_safe=True
        )
        is_train_valid_split_required, split_ratio = True, automl_settings.validation_size
    else:
        # Identifying if a rule based validation strategy can be applied
        validation_strategy = _validation_strategy_selector.get_auto_validation_strategy(
            automl_settings, raw_experiment_data.X, raw_experiment_data.X_valid, raw_experiment_data.cv_splits_indices
        )

        if validation_strategy is not None:
            # Rule based validation strategy needs to applied
            if validation_strategy.property == _validation_strategy_selector.TRAIN_VALID_SPLIT:
                is_train_valid_split_required, split_ratio = True, validation_strategy.value
            elif validation_strategy.property == _validation_strategy_selector.CROSS_VALIDATION:
                automl_settings.n_cross_validations = validation_strategy.value
                raw_experiment_data.n_cross_validations = validation_strategy.value
                if verifier is not None:
                    verifier.update_data_verifier_for_cv(validation_strategy.value)
            else:
                logger.warning("Unable to apply an unknown validation strategy: {}, value: {}".format(
                    validation_strategy.property, validation_strategy.value))

    if is_train_valid_split_required and split_ratio > 0.0:
        logger.info("Splitting training data into train-valid data using split ratio of: {}".format(split_ratio))
        tabular_data = MaterializedTabularData(
            raw_experiment_data.X, raw_experiment_data.y, raw_experiment_data.weights)
        train_data, validation_data = split_dataset(tabular_data, automl_settings.task_type, split_ratio)

        # Update the original raw experiment data with updated train valid datasets
        raw_experiment_data.X, raw_experiment_data.y, raw_experiment_data.weights = \
            train_data.X, train_data.y, train_data.weights
        raw_experiment_data.X_valid, raw_experiment_data.y_valid, raw_experiment_data.weights_valid = \
            validation_data.X, validation_data.y, validation_data.weights

        if validation_strategy is not None and verifier is not None:
            # Update guardrails, since rule based validation was applied
            verifier.update_data_verifier_for_train_test_validation(
                raw_experiment_data.X.shape[0], raw_experiment_data.X_valid.shape[0]
            )
