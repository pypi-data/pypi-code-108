# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Classes for TimeseriesCVValidationWorker."""
import logging

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    TimeseriesDfInvalidArgNoValidationData, TimeseriesDfInvalidArgParamIncompatible)
from azureml.automl.core.shared.forecasting_exception import ForecastingConfigException
from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared import constants

from ._timeseries_validator import TimeseriesValidationParamName
from ._timeseries_validator import TimeseriesValidationParameter
from ._timeseries_validator import TimeseriesValidationWorkerBase


class TimeseriesCVValidationWorker(TimeseriesValidationWorkerBase):
    """Validation worker for the cross validation."""

    def __init__(self) -> None:
        pass

    @function_debug_log_wrapped(logging.INFO)
    def validate(self, param: TimeseriesValidationParameter) -> None:
        """Abstract method that validate the timeseries config/data."""
        automl_settings = param.params[TimeseriesValidationParamName.AUTOML_SETTINGS]
        X_valid = param.params[TimeseriesValidationParamName.X_VALID]
        cv_splits_indices = param.params[TimeseriesValidationParamName.CV_SPLITS_INDICES]

        # If iterations = 0, Auto featurization is enabled and cv split or validation data will not be required.
        if automl_settings.iterations == constants.RuleBasedValidation.AUTOFEATURIZATION_ITERATION_COUNT:
            return

        if automl_settings.n_cross_validations is None and X_valid is None:
            raise ForecastingConfigException._with_error(
                AzureMLError.create(TimeseriesDfInvalidArgNoValidationData,
                                    target='automl_settings.n_cross_validations, X_valid',
                                    reference_code=ReferenceCodes._TSDF_INVALID_ARG_NO_VALIDATION_DATA)
            )
        elif cv_splits_indices is not None or \
                (automl_settings.validation_size is not None and automl_settings.validation_size > 0.0):
            if cv_splits_indices is not None:
                error_validation_config = "cv_splits_indices"
            else:
                error_validation_config = "validation_size"
            raise ForecastingConfigException._with_error(
                AzureMLError.create(TimeseriesDfInvalidArgParamIncompatible,
                                    target='cv_splits_indices',
                                    reference_code=ReferenceCodes._TSDF_INVALID_ARG_PARAM_INCOMPATIBLE,
                                    param=error_validation_config)
            )
