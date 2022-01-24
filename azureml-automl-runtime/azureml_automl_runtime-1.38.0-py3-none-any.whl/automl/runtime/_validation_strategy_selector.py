# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utilities for managing validation strategy for AutoML experiments."""
import collections
import logging
from typing import Any, Optional

import scipy
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.shared import constants
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.runtime.shared.types import DataInputType
from scipy import sparse

logger = logging.getLogger(__name__)

# Data structure to represent the result of finding a validation strategy.
# 'property' is the string that identifies what settings need to be updated.
# 'value' points to the new value to apply to the 'property' identified by the above string.
ValidationStrategy = collections.namedtuple("ValidationStrategy", ["property", "value"])

# Property names for different validation strategies.
CROSS_VALIDATION = "n_cross_validations"
TRAIN_VALID_SPLIT = "validation_size"


def get_auto_validation_strategy(
    automl_settings: AutoMLBaseSettings,
    X: DataInputType,
    X_valid: Optional[DataInputType] = None,
    cv_splits_indices: Any = None,
) -> Optional[ValidationStrategy]:
    """
    Identify a model evaluation strategy between CV or train-valid split based on the size of input data.

    :param automl_settings: The AutoMLSettings object for this experiment
    :param X: Training data.
    :type X: pandas.DataFrame or numpy.ndarray or scipy.sparse
    :param X_valid: validation features.
    :type X_valid: pandas.DataFrame or numpy.ndarray
    :param cv_splits_indices: Indices where to split training data for cross validation
    :type cv_splits_indices: list(int), or list(Dataflow) in which each Dataflow represent a train-valid set
                                where 1 indicates record for training and 0
                                indicates record for validation
    :return: ValidationStrategy with the property that needs an update if a rule based validation strategy needs to
             be applied, None otherwise
    """
    if not _is_validation_strategy_required(
        X_valid,
        automl_settings.n_cross_validations,
        cv_splits_indices,
        automl_settings.validation_size,
        automl_settings.is_timeseries,
        automl_settings.enable_streaming,
    ):
        logger.info("User has validation strategy already defined, no rule based validation needed.")
        return None

    Contract.assert_value(X, "X")

    split_ratio = constants.RuleBasedValidation.DEFAULT_TRAIN_VALIDATE_TEST_SIZE
    random_state = constants.RuleBasedValidation.DEFAULT_TRAIN_VALIDATE_RANDOM_STATE

    number_of_cv = _get_cv_number(X)
    if number_of_cv > 1:  # As CV must be larger than 1, so 1 here means train valid split
        logger.info("Rule based validation: Using rule based cv now with cv {}.".format(str(number_of_cv)))
        return ValidationStrategy(property=CROSS_VALIDATION, value=number_of_cv)
    else:
        logger.info(
            "Rule based validation: Using rule based train/test splits with validation percent as "
            "{} and random seed as {}.".format(split_ratio, random_state)
        )
        return ValidationStrategy(property=TRAIN_VALID_SPLIT, value=split_ratio)


def _is_validation_strategy_required(
    X_valid: Any,
    n_cross_validations: Optional[int] = None,
    cv_splits_indices: Optional[Any] = None,
    validation_size: Optional[float] = None,
    is_timeseries: Optional[bool] = None,
    is_streaming: bool = False,
) -> bool:
    """
    Check whether user input need automated validation settings.

    This function will be true if user has no input validation settings and the training is not timeseries.
    """
    is_needed = not is_streaming
    is_needed = is_needed and not is_timeseries
    is_needed = is_needed and X_valid is None and (validation_size is None or validation_size == 0.0)
    is_needed = is_needed and n_cross_validations is None and cv_splits_indices is None
    return is_needed


def _get_cv_number(X: Any) -> int:
    """Return the number of cross validation is needed. If is 1 using train test splits."""
    if sparse.issparse(X):
        return constants.RuleBasedValidation.SPARSE_N_CROSS_VALIDATIONS
    for rule in constants.RuleBasedValidation.VALIDATION_LIMITS_NO_SPARSE:
        if rule.LOWER_BOUND <= X.shape[0] < rule.UPPER_BOUND:
            return rule.NUMBER_OF_CV
    # by default return constants.RuleBasedValidation.DEFAULT_N_CROSS_VALIDATIONS
    return constants.RuleBasedValidation.DEFAULT_N_CROSS_VALIDATIONS
