# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import warnings
from typing import cast, Optional, Tuple, Union

import numpy as np
import pandas as pd
from azureml.automl.runtime._ml_engine.validation import common_data_validations
from scipy import sparse

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.constants import FeaturizationConfigMode
from azureml.automl.core.featurization import FeaturizationConfig
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    DatasetsFeatureCountMismatch, ExperimentTimeoutForDataSize, InsufficientSampleSize,
    NCrossValidationsExceedsTrainingRows, NonOverlappingColumnsInTrainValid, PositiveLabelMissing,
)
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared._diagnostics.error_strings import AutoMLErrorStrings
from azureml.automl.core.shared._diagnostics.validation import Validation
from azureml.automl.core.shared.constants import AutoMLValidation, Tasks
from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime._data_definition import MaterializedTabularData, RawExperimentData
from azureml.automl.runtime._ml_engine.validation import (
    FeaturizationConfigDataValidator, MaterializedTabularDataValidator
)
from azureml.automl.runtime._ml_engine.validation.validators import AbstractRawExperimentDataValidator, \
    AbstractTabularDataValidator
from azureml.automl.runtime._runtime_params import ExperimentControlSettings
from azureml.automl.runtime.shared import utilities as runtime_utilities

logger = logging.getLogger(__name__)


class RawExperimentDataValidatorSettings:

    def __init__(self, automl_settings: AutoMLBaseSettings):
        self.control_settings = ExperimentControlSettings(automl_settings)
        self.enable_onnx_compatible_models = automl_settings.enable_onnx_compatible_models
        self.experiment_timeout_minutes = automl_settings.experiment_timeout_minutes
        self.n_cross_validations = automl_settings.n_cross_validations


class RawExperimentDataValidator(AbstractRawExperimentDataValidator):
    """
    Run all necessary data validations on the experiment data, to make sure we can produce a machine learning
    model on it.
    """
    # A reference code for errors originating from this class.
    _REFERENCE_CODE = ReferenceCodes._RAW_EXPERIMENT_DATA_VALIDATOR_GENERIC

    def __init__(self, validation_settings: RawExperimentDataValidatorSettings) -> None:
        """
        Initialize a RawExperimentDataValidator

        :param automl_settings: The settings for the experiment.
        """
        self._validation_settings = validation_settings
        self._n_cross_validations = validation_settings.n_cross_validations
        self._experiment_timeout_minutes = validation_settings.experiment_timeout_minutes
        self._featurization = validation_settings.control_settings.featurization
        self._is_timeseries = validation_settings.control_settings.is_timeseries
        self._task_type = validation_settings.control_settings.task_type
        self._primary_metric = validation_settings.control_settings.primary_metric
        self._is_onnx_enabled = validation_settings.enable_onnx_compatible_models

    def validate_raw_experiment_data(self, raw_experiment_data: RawExperimentData) -> None:
        """
        Given raw experiment data, check if it is valid to run through the featurization and model training pipelines

        :param raw_experiment_data: RawExperimentData, as provided by the user
        :return: None
        :raises: DataException, ValidationException
        """
        # Validate that required values are provided, and are of the right types
        self._validate_basic(raw_experiment_data)

        # Get the training and validation tabular datasets
        train_data, validation_data = self._get_train_valid_data(raw_experiment_data)

        # Check if the number of samples in the training (and validation) data are sufficient
        self._check_data_minimal_size(train_data.y, validation_data.y if validation_data else None)

        # For classification task, check if positive label exists in y label
        if self._validation_settings.control_settings.task_type == Tasks.CLASSIFICATION:
            self._check_positive_label(train_data.y)

        if self._validation_settings.experiment_timeout_minutes is not None:
            # Check if the number of samples in X is ok to be processed within the defined experiment timeout
            self._check_experiment_timeout_for_train_data(
                train_data.X, self._validation_settings.experiment_timeout_minutes
            )

        if isinstance(self._featurization, FeaturizationConfig):
            featurization_config_data_validator = self.get_featurization_config_data_validator()
            featurization_config_data_validator.validate(raw_experiment_data)

        tabular_data_validator = self.get_tabular_data_validator()  # type: AbstractTabularDataValidator

        # The rest of validations on training dataset happen separately
        tabular_data_validator.validate(train_data)

        if validation_data is not None:
            # Run rest of the validations plus any validations *across* train-valid datasets
            tabular_data_validator.validate(validation_data)

            # The rest of the train valid validations happen in this function
            self.validate_train_valid_data(train_data, validation_data)

    def validate_train_valid_data(
            self, train_data: MaterializedTabularData, validation_data: MaterializedTabularData
    ) -> None:
        """
        Validate data across training and validation datasets.

        :param train_data: The data to train the model on.
        :param validation_data: The data to validate the predictability of the model against.
        :return:
        """
        X = train_data.X
        X_valid = validation_data.X

        Contract.assert_true(type(X) == type(X_valid), "X & X_valid are of different types.", log_safe=True,
                             reference_code=RawExperimentDataValidator._REFERENCE_CODE)

        self._check_train_valid_data_has_same_columns(X, X_valid)
        self._check_train_valid_dimensions(X, X_valid)

    def get_tabular_data_validator(self) -> AbstractTabularDataValidator:
        """Create an appropriate tabular data validator given the configuration."""
        is_featurization_required = self._validation_settings.control_settings.is_timeseries or \
            (self._validation_settings.control_settings.featurization != FeaturizationConfigMode.Off)
        tabular_data_validator = MaterializedTabularDataValidator(
            task_type=self._validation_settings.control_settings.task_type,
            primary_metric=self._validation_settings.control_settings.primary_metric,
            is_onnx_enabled=self._validation_settings.enable_onnx_compatible_models,
            is_featurization_required=is_featurization_required,
        )
        return tabular_data_validator

    def get_featurization_config_data_validator(self) -> FeaturizationConfigDataValidator:
        """Create a featurization config data validator."""
        return FeaturizationConfigDataValidator(
            cast(FeaturizationConfig, self._featurization), self._validation_settings.control_settings.is_timeseries)

    def _check_train_valid_data_has_same_columns(
            self, X: Union[pd.DataFrame, sparse.spmatrix], X_valid: Union[pd.DataFrame, sparse.spmatrix]
    ) -> None:
        """Validate if training and validation datasets have the same columns."""
        if isinstance(X, pd.DataFrame):
            if len(X.columns.intersection(X_valid.columns)) != len(X.columns):
                x_column_list = list(X.columns)
                x_valid_column_list = list(X_valid.columns)
                missing_columns = set([col for col in x_column_list if x_valid_column_list.count(col) == 0])
                raise DataException(
                    azureml_error=AzureMLError.create(
                        NonOverlappingColumnsInTrainValid, target="X", missing_columns=", ".join(missing_columns)
                    )
                )

    def _check_train_valid_dimensions(
            self, X: Union[pd.DataFrame, sparse.spmatrix], X_valid: Union[pd.DataFrame, sparse.spmatrix]
    ) -> None:
        # todo not sure what does this validation actually checks?
        if len(X.shape) > 1:
            if len(X_valid.shape) > 1 and X.shape[1] != X_valid.shape[1]:
                raise DataException(
                    azureml_error=AzureMLError.create(
                        DatasetsFeatureCountMismatch,
                        target="X/X_Valid",
                        first_dataset_name="X",
                        first_dataset_shape=X.shape[1],
                        second_dataset_name="X_valid",
                        second_dataset_shape=X_valid.shape[1],
                    )
                )
            elif len(X_valid.shape) == 1 and X.shape[1] != 1:
                raise DataException(
                    azureml_error=AzureMLError.create(
                        DatasetsFeatureCountMismatch,
                        target="X/X_Valid",
                        first_dataset_name="X",
                        first_dataset_shape=X.shape[1],
                        second_dataset_name="X_valid",
                        second_dataset_shape=1,
                    )
                )
        elif len(X_valid.shape) > 1 and X_valid.shape[1] != 1:
            raise DataException(
                azureml_error=AzureMLError.create(
                    DatasetsFeatureCountMismatch,
                    target="X/X_Valid",
                    first_dataset_name="X",
                    first_dataset_shape=X.shape[1],
                    second_dataset_name="X_valid",
                    second_dataset_shape=X_valid.shape[1],
                )
            )

    def _check_data_minimal_size(self, y: np.ndarray, y_valid: Optional[np.ndarray]) -> None:
        """Validate whether the training and validation datasets have a desired minimum number of samples."""
        Contract.assert_type(y, "y", expected_types=np.ndarray)
        if y_valid is not None:
            Contract.assert_type(y_valid, "y_valid", expected_types=np.ndarray)

        len_training_rows = y.shape[0]

        # Rows with NaN or null values aren't very helpful for learning, so considering the number of 'learn-able'
        # training rows as the baseline for data minimal calculations
        len_nan_rows = runtime_utilities._get_indices_missing_labels_output_column(y).shape[0]
        len_usable_training_rows = len_training_rows - len_nan_rows

        if self._validation_settings.n_cross_validations is not None:
            if len_usable_training_rows < self._validation_settings.n_cross_validations:
                raise DataException(
                    azureml_error=AzureMLError.create(
                        NCrossValidationsExceedsTrainingRows,
                        target="n_cross_validations",
                        training_rows=len_usable_training_rows,
                        n_cross_validations=self._validation_settings.n_cross_validations,
                    )
                )

        if len_usable_training_rows < SmallDataSetLimit.MINIMAL_TRAIN_SIZE:
            raise DataException(
                azureml_error=AzureMLError.create(
                    InsufficientSampleSize,
                    target="training_data",
                    data_object_name="training_data",
                    sample_count=len_usable_training_rows,
                    minimum_count=SmallDataSetLimit.MINIMAL_TRAIN_SIZE,
                )
            )
        if len_usable_training_rows < SmallDataSetLimit.WARNING_SIZE:
            warnings.warn(AutoMLErrorStrings.INSUFFICIENT_SAMPLE_SIZE.format(
                data_object_name="training_data",
                sample_count=len_usable_training_rows,
                minimum_count=SmallDataSetLimit.WARNING_SIZE)
            )

        if y_valid is not None:
            len_validation_rows = y_valid.shape[0]
            len_nan_validation_rows = runtime_utilities._get_indices_missing_labels_output_column(y_valid).shape[0]
            len_usable_validation_rows = len_validation_rows - len_nan_validation_rows
            if len_usable_validation_rows < SmallDataSetLimit.MINIMAL_VALIDATION_SIZE:
                raise DataException(
                    azureml_error=AzureMLError.create(
                        InsufficientSampleSize,
                        target="validation_data",
                        data_object_name="validation_data",
                        sample_count=len_usable_validation_rows,
                        minimum_count=SmallDataSetLimit.MINIMAL_VALIDATION_SIZE,
                    )
                )

    def _validate_basic(self, raw_experiment_data: RawExperimentData) -> None:
        """
        Ensure that:
            - X, y are non-null
            - X, y & weights are of the right types
            - If X_valid is provided, y_valid must also be provided
            - X_valid, y_valid and weights_valid are of the right types
        """
        # training data checks
        Validation.validate_value(raw_experiment_data.X, "X")
        Validation.validate_value(raw_experiment_data.y, "y")
        # supported types for 'X'
        if not sparse.issparse(raw_experiment_data.X):
            Validation.validate_type(raw_experiment_data.X, "X", (pd.DataFrame, np.ndarray))
        # supported types for 'y'
        Validation.validate_type(raw_experiment_data.y, "y", np.ndarray)
        if raw_experiment_data.weights is not None:
            Validation.validate_type(raw_experiment_data.weights, "sample_weight", expected_types=np.ndarray)

        # validation data checks
        if raw_experiment_data.X_valid is not None:
            Validation.validate_type(raw_experiment_data.X_valid, "X_valid", (pd.DataFrame, np.ndarray))
            Validation.validate_value(raw_experiment_data.y_valid, "y_valid")
            Validation.validate_type(raw_experiment_data.y_valid, "y_valid", np.ndarray)
            if raw_experiment_data.weights is not None:
                Validation.validate_value(raw_experiment_data.weights_valid, "weights_valid")
                Validation.validate_type(raw_experiment_data.weights_valid, "weights_valid", expected_types=np.ndarray)

    def _get_train_valid_data(
            self, raw_experiment_data: RawExperimentData
    ) -> Tuple[MaterializedTabularData, Optional[MaterializedTabularData]]:
        """
        Return the training/validation dataset pair from raw experiment data.

        This does not **currently split** the data, it will simply return any validation data if it was
        present in the data dictionary with which this class was initialized (i.e. if the user provided one)

        :return: training and validation tabular datasets
        :raises InvalidValueException, InvalidTypeException, DataShapeException, InvalidDimensionException
        """
        train_data = None  # type: Optional[MaterializedTabularData]
        valid_data = None  # type: Optional[MaterializedTabularData]

        try:
            # Attempt to create train and valid tabular datasets. Any discrepancies in the data will be raised
            # as exceptions, which is wrapped as user errors and re-thrown
            train_data = MaterializedTabularData(
                raw_experiment_data.X, raw_experiment_data.y, raw_experiment_data.weights, reduce_mem=False
            )

            if raw_experiment_data.X_valid is not None and raw_experiment_data.y_valid is not None:
                valid_data = MaterializedTabularData(
                    raw_experiment_data.X_valid, raw_experiment_data.y_valid,
                    raw_experiment_data.weights_valid, reduce_mem=False
                )
        except Exception as e:
            # Convert known exceptions into user errors
            common_data_validations.materialized_tabular_data_user_error_handler(e)

        return train_data, valid_data

    def _check_experiment_timeout_for_train_data(
            self, X: Union[pd.DataFrame, sparse.spmatrix], experiment_timeout_minutes: int
    ) -> None:
        """
        Check if there is sufficient time configured for experiment depending on the number of samples present in
        the training data.
        """
        Contract.assert_value(X, "X", reference_code=RawExperimentDataValidator._REFERENCE_CODE)

        if sparse.issparse(X):
            return

        minimum_timeout_required = 60
        n_rows = X.shape[0]
        n_cols = 1 if len(X.shape) < 2 else X.shape[1]
        # For 1M rows, the timeout needs to be at least 60 min
        if n_rows * n_cols > AutoMLValidation.TIMEOUT_DATA_BOUND and \
                experiment_timeout_minutes < minimum_timeout_required:
            raise DataException(azureml_error=AzureMLError.create(
                ExperimentTimeoutForDataSize, target="experiment_timeout_minutes",
                minimum=minimum_timeout_required, maximum="{:,}".format(AutoMLValidation.TIMEOUT_DATA_BOUND),
                rows=n_rows, columns=n_cols, total=n_rows * n_cols,
                reference_code=ReferenceCodes._VALIDATE_EXP_TIMEOUT_WITH_DATA)
            )

    def _check_positive_label(self, y: np.ndarray) -> None:
        """
        Check if positive class label exists in given label column
        """
        if self._validation_settings.control_settings.positive_label is None:
            return

        class_labels = np.unique(y)
        positive_label = self._validation_settings.control_settings.positive_label
        if positive_label not in class_labels:
            # TODO: capture Dataset converted labels
            raise DataException(azureml_error=AzureMLError.create(
                PositiveLabelMissing, target="positive_label",
                positive_label=positive_label)
            )


class SmallDataSetLimit:
    """Constants for the small dataset limit."""

    WARNING_SIZE = 100
    MINIMAL_TRAIN_SIZE = 50
    MINIMAL_VALIDATION_SIZE = int(MINIMAL_TRAIN_SIZE / 10)
