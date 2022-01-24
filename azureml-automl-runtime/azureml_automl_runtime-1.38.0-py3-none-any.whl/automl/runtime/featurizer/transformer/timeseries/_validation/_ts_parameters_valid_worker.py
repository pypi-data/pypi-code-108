# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Classes for TimeseriesParametersValidationWorker."""
import logging

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared import utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import BadArgument
from azureml.automl.core.shared.forecasting_exception import ForecastingConfigException
from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from azureml.automl.core.shared.reference_codes import ReferenceCodes

from azureml.automl.runtime.featurizer.transformer.timeseries._validation._timeseries_validator import (
    TimeseriesValidationParamName, TimeseriesValidationParameter, TimeseriesValidationWorkerBase)


class TimeseriesParametersValidationWorker(TimeseriesValidationWorkerBase):
    """Validation worker for the ts parameters."""

    def __init__(self) -> None:
        pass

    @function_debug_log_wrapped(logging.INFO)
    def validate(self, param: TimeseriesValidationParameter) -> None:
        """Abstract method that validate the timeseries config/data."""
        automl_settings = param.params[TimeseriesValidationParamName.AUTOML_SETTINGS]

        timeseries_param_dict = utilities._get_ts_params_dict(automl_settings)
        if timeseries_param_dict is None:
            raise ForecastingConfigException._with_error(
                AzureMLError.create(BadArgument,
                                    target='timeseries_param_dict',
                                    reference_code=ReferenceCodes._TSDF_INVALID_ARG_CHK_INPUT,
                                    argument_name='timeseries_param_dict')
            )

        # Set the timeseries_param_dict to the validation parameter, for later workers use.
        param.params[TimeseriesValidationParamName.TIMESERIES_PARAM_DICT] = timeseries_param_dict
