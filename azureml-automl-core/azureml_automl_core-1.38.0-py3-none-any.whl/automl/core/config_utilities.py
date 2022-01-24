# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility methods for interacting with AutoMLConfig."""
from typing import Any, Optional, List

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import ConflictingValueForArguments
from azureml.automl.core.shared._diagnostics.validation import Validation
from azureml.automl.core.shared.exceptions import ConfigException
from azureml.data import TabularDataset


def _check_validation_config(
        X_valid: Any,
        y_valid: Any,
        sample_weight: Any,
        sample_weight_valid: Any,
        cv_splits_indices: Any,
        n_cross_validations: Optional[int] = None,
        validation_size: Optional[float] = None,
        validation_data: Optional[TabularDataset] = None,
        cv_split_column_names: Optional[List[str]] = None,
) -> None:
    """
    Validate that validation parameters have been correctly provided.

    :param X_valid: Validation dataset (feature columns)
    :param y_valid: Validation dataset (target column)
    :param sample_weight: Sample weight data
    :param sample_weight_valid: Validation dataset for sample weights
    :param cv_splits_indices: Indices for cross validation folds
    :param n_cross_validations: Integer representing the number of cross folds requested
    :param validation_size: Percentage of training data to withhold for validation dataset
    :param validation_data: Validation dataset (combined features + target)
    :param cv_split_column_names: Column names representing the data for generating cross validation folds
    """
    is_validation_dataset_provided = X_valid is not None or validation_data is not None
    is_cv_data_provided = cv_splits_indices is not None or bool(cv_split_column_names)

    if is_validation_dataset_provided:
        if X_valid is not None:
            Validation.validate_value(y_valid, "y_valid")
        if sample_weight is not None:
            Validation.validate_value(sample_weight_valid, "sample_weight_valid")

    if y_valid is not None:
        Validation.validate_value(X_valid, "X_valid")

    if sample_weight_valid is not None and X_valid is None:
        raise ConfigException._with_error(
            AzureMLError.create(
                ConflictingValueForArguments, target="sample_weight_valid",
                arguments=', '.join(['sample_weight_valid', 'X_valid'])
            )
        )

    if is_validation_dataset_provided:
        if n_cross_validations is not None and n_cross_validations > 0:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ConflictingValueForArguments, target="n_cross_validations",
                    arguments=', '.join(['validation_data/X_valid', 'n_cross_validations'])
                )
            )
        if validation_size is not None and validation_size > 0.0:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ConflictingValueForArguments, target="validation_size",
                    arguments=', '.join(['validation_data/X_valid', 'validation_size'])
                )
            )

    if is_cv_data_provided:
        target = "cv_splits_indices" if cv_splits_indices is not None else "cv_split_column_names"
        if n_cross_validations is not None and n_cross_validations > 0:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ConflictingValueForArguments, target=target, arguments=', '.join([target, 'n_cross_validations'])
                )
            )
        if validation_size is not None and validation_size > 0.0:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ConflictingValueForArguments, target=target, arguments=', '.join([target, 'validation_size'])
                )
            )
        if is_validation_dataset_provided:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ConflictingValueForArguments, target=target,
                    arguments=', '.join([target, 'validation_data/X_valid'])
                )
            )
