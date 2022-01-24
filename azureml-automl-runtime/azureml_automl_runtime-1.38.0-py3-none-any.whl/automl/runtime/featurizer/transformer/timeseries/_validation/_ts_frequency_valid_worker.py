# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Classes for TimeseriesFrequencyValidationWorker."""
import logging

from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from azureml.automl.core.shared.reference_codes import ReferenceCodes

from azureml.automl.runtime import frequency_fixer
from ._timeseries_validator import TimeseriesValidationParamName
from ._timeseries_validator import TimeseriesValidationParameter
from ._timeseries_validator import TimeseriesValidationWorkerBase


class TimeseriesFrequencyValidationWorker(TimeseriesValidationWorkerBase):
    """Validation worker for the frequency."""

    def __init__(self) -> None:
        pass

    @function_debug_log_wrapped(logging.INFO)
    def validate(self, param: TimeseriesValidationParameter) -> None:
        """Abstract method that validate the timeseries config/data."""
        automl_settings = param.params[TimeseriesValidationParamName.AUTOML_SETTINGS]

        if automl_settings.freq is not None:
            frequency_fixer.str_to_offset_safe(automl_settings.freq,
                                               ReferenceCodes._TRAINING_UTILITIES_CHECK_FREQ)
