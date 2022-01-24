# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional, Union, cast

import numpy as np
import pandas as pd
from scipy import sparse

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.shared._diagnostics.automl_error_definitions import NCrossValidationsExceedsTrainingRows
from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.runtime import _time_series_training_utilities
from azureml.automl.runtime._data_definition import RawExperimentData
from azureml.automl.runtime._ml_engine.validation import MaterializedTabularDataValidator
from azureml.automl.runtime._ml_engine.validation.timeseries_materialized_tabular_data_validator import \
    TimeseriesMaterializedTabularDataValidator
from azureml.automl.runtime.featurizer.transformer.timeseries._validation import _get_df_or_raise

from .raw_experiment_data_validator import RawExperimentDataValidator, RawExperimentDataValidatorSettings


class TimeseriesRawExperimentDataValidator(RawExperimentDataValidator):
    """
    Validator for validating the raw experiment data for a timeseries task.
    """
    def __init__(self, automl_settings: AutoMLBaseSettings) -> None:
        validation_settings = RawExperimentDataValidatorSettings(automl_settings)
        super(TimeseriesRawExperimentDataValidator, self).__init__(validation_settings)
        self._automl_settings = automl_settings
        # TODO: Move the timeseries task parameters into the constructor here

    # override
    def validate_raw_experiment_data(self, raw_experiment_data: RawExperimentData) -> None:
        # Do base validations first
        super().validate_raw_experiment_data(raw_experiment_data)

        # Timeseries specific validations
        self._validate_timeseries(raw_experiment_data=raw_experiment_data)

    def _validate_timeseries(self, raw_experiment_data: RawExperimentData) -> None:
        x_raw_column_names = raw_experiment_data.feature_column_names
        X = _get_df_or_raise(raw_experiment_data.X, x_raw_column_names)
        y = raw_experiment_data.y
        sample_weight = raw_experiment_data.weights

        X_valid = raw_experiment_data.X_valid
        y_valid = raw_experiment_data.y_valid
        sample_weight_valid = raw_experiment_data.weights_valid

        cv_splits_indices = raw_experiment_data.cv_splits_indices

        _time_series_training_utilities.validate_timeseries_training_data(
            self._automl_settings,
            X,
            y,
            X_valid,
            y_valid,
            sample_weight,
            sample_weight_valid,
            cv_splits_indices,
            cast(np.ndarray, x_raw_column_names),
        )

    # override
    def _check_data_minimal_size(
            self, X: Union[pd.DataFrame, sparse.spmatrix], X_valid: Optional[Union[pd.DataFrame, sparse.spmatrix]]
    ) -> None:
        """Validate whether the training and validation datasets have a desired minimum number of samples."""
        number_of_training_rows = X.shape[0]
        if self._validation_settings.n_cross_validations is not None:
            if number_of_training_rows < self._validation_settings.n_cross_validations:
                raise DataException(
                    azureml_error=AzureMLError.create(
                        NCrossValidationsExceedsTrainingRows,
                        target="n_cross_validations",
                        training_rows=number_of_training_rows,
                        n_cross_validations=self._validation_settings.n_cross_validations,
                    )
                )

        # TODO: Move other timeseries specific data minimal size checks here

    # override
    def get_tabular_data_validator(self) -> MaterializedTabularDataValidator:
        """Create an appropriate tabular data validator given the configuration."""
        return TimeseriesMaterializedTabularDataValidator(
            primary_metric=self._validation_settings.control_settings.primary_metric)
