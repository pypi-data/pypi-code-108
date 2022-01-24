# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines custom exceptions produced by automated ML."""
import warnings

from azureml._common._error_response._error_response_constants import ErrorCodes
from azureml._common.exceptions import AzureMLException
from azureml.automl.core.shared import exceptions
# For backcompat
from azureml.automl.core.shared.exceptions import ScenarioNotSupportedException
from azureml.exceptions import UserErrorException


class ConfigException(exceptions.ConfigException):
    """An exception related to invalid user configuration.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.
    """

    pass


class AuthorizationException(exceptions.UserException):
    """An exception related to invalid user configuration.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    def __init__(self, exception_message="", target=None, **kwargs):
        """Exception related to invalid user configuration.

        :param exception_message: A message describing the error.
        :type exception_message: str
        """
        warnings.warn("AuthorizationException is deprecated. Please use AutoMLException if you are trying to catch "
                      "AutoML related Authorization exceptions.")
        super().__init__(exception_message, target, **kwargs)


class FeatureUnavailableException(exceptions.UserException):
    """An exception indicating that a specified feature is not available for user workspace type.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    def __init__(self, exception_message="", target=None, **kwargs):
        """Exception indicating that a specified feature is not available for user workspace type.

        :param exception_message: A message describing the error.
        :type exception_message: str
        """
        warnings.warn("FeatureUnavailableException is deprecated. Please use AutoMLException if you are trying to "
                      "catch AutoML feature related exceptions.")
        super().__init__(exception_message, target, **kwargs)


class ValidationException(exceptions.ValidationException):
    """An exception representing errors caught when validating inputs."""

    pass


class BadArgumentException(exceptions.BadArgumentException):
    """An exception related to data validation.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.
    """

    pass


class MissingValueException(exceptions.MissingValueException):
    """An exception related to data validation.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.
    """

    pass


class MalformedValueException(exceptions.MalformedValueException):
    """An exception related to data validation.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.
    """

    pass


# TODO this should move to azureml.exceptions
class DataException(ValidationException, exceptions.DataException):
    """An exception related to data validation.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.INVALIDDATA_ERROR


# TODO this should move to azureml.exceptions
class SystemException(exceptions.AutoMLException, AzureMLException):
    """An exception for internal errors that happen within the SDK.

    :param exception_message: A message describing the error.
    :type exception_message: str
    :param inner_exception: An optional message, for example, from a previously handled exception.
    :type inner_exception: str
    :param target: The name of the element that caused the exception to be raised.
    :type target: str
    :param details: Any additional information about the error such as other error responses or stack traces.
    :type details: str
    """

    _error_code = ErrorCodes.SYSTEM_ERROR


class ServiceException(SystemException):
    """An exception related to the automated ML back end service.

    :param exception_message: A message describing the error.
    :type exception_message: str
    :param inner_exception: An optional message, for example, from a previously handled exception.
    :type inner_exception: str
    :param target: The name of the element that caused the exception to be raised.
    :type target: str
    :param details: Any additional information about the error such as other error responses or stack traces.
    :type details: str
    """

    _error_code = ErrorCodes.SERVICE_ERROR


class ClientException(exceptions.ClientException, AzureMLException):
    """An exception related to a client error.

    :param exception_message: A message describing the error.
    :type exception_message: str
    :param inner_exception: An optional message, for example, from a previously handled exception.
    :type inner_exception: str
    :param target: The name of the element that caused the exception to be raised.
    :type target: str
    :param details: Any additional information about the error such as other error responses or stack traces.
    :type details: str
    """

    _error_code = ErrorCodes.SYSTEM_ERROR


class OnnxConvertException(ClientException):
    """An exception related to ONNX conversion.

    :param exception_message: A message describing the error.
    :type exception_message: str
    :param inner_exception: An optional message, for example, from a previously handled exception.
    :type inner_exception: str
    :param target: The name of the element that caused the exception to be raised.
    :type target: str
    :param details: Any additional information about the error such as other error responses or stack traces.
    :type details: str
    """

    # TODO - define a code for this
    # _error_code = ErrorCodes.ONNX_ERROR


class DataValidationException(ValidationException):
    """An exception for issues caught while validating user data.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.VALIDATION_ERROR


class ForecastingDataException(DataValidationException):
    """An exception related to malformed data for a forecasting scenario.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    # TODO - define a code for this
    # _error_code = ErrorCodes.INVALIDFORECASTINGDATA_ERROR


class DataPrepValidationException(DataValidationException):
    """An exception related to the dataprep validation service.

    :param exception_message: A message describing the error.
    :type exception_message: str
    :param inner_exception: An optional message, for example, from a previously handled exception.
    :type inner_exception: str
    :param target: The name of the element that caused the exception to be raised.
    :type target: str
    :param details: Any additional information about the error such as other error responses or stack traces.
    :type details: str
    """

    # TODO - define a code for this
    # _error_code = ErrorCodes.DATAPREPVALIDATION_ERROR


class DataScriptException(DataValidationException):
    """An exception for issues with user's get_data script.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    # TODO - define a code for this
    # _error_code = ErrorCodes.DATASCRIPT_ERROR


class EarlyTerminationException(UserErrorException):
    """An exception raised for a user-generated interrupt.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.EARLYTERMINATION_ERROR


class AutoMLExperimentException(SystemException):
    """An exception representing an error that occurred during AutoML runtime.

    :param exception_message: A message describing the error.
    :type exception_message: str
    :param inner_exception: An optional message, for example, from a previously handled exception.
    :type inner_exception: str
    :param target: The name of the element that caused the exception to be raised.
    :type target: str
    :param details: Any additional information about the error such as other error responses or stack traces.
    :type details: str
    """

    # TODO - define a code for this
    # _error_code = ErrorCodes.EXPERIMENTRUN_ERROR


class PreTrainingException(AutoMLExperimentException):
    """An exception raised for anything that goes wrong before fitting a model.

    :param exception_message: A message describing the error.
    :type exception_message: str
    :param inner_exception: An optional message, for example, from a previously handled exception.
    :type inner_exception: str
    :param target: The name of the element that caused the exception to be raised.
    :type target: str
    :param details: Any additional information about the error such as other error responses or stack traces.
    :type details: str
    """

    # TODO - define a code for this
    # _error_code = ErrorCodes.PRETRAINING_ERROR


class CacheException(PreTrainingException):
    """An exception raised for cache issues.

    :param exception_message: A message describing the error.
    :type exception_message: str
    :param inner_exception: An optional message, for example, from a previously handled exception.
    :type inner_exception: str
    :param target: The name of the element that caused the exception to be raised.
    :type target: str
    :param details: Any additional information about the error such as other error responses or stack traces.
    :type details: str
    """

    # TODO - define a code for this
    # _error_code = ErrorCodes.CACHE_ERROR


class FeaturizationException(PreTrainingException):
    """An exception for issues that arise during featurization.

    :param exception_message: A message describing the error.
    :type exception_message: str
    :param inner_exception: An optional message, for example, from a previously handled exception.
    :type inner_exception: str
    :param target: The name of the element that caused the exception to be raised.
    :type target: str
    :param details: Any additional information about the error such as other error responses or stack traces.
    :type details: str
    """

    # TODO - define a code for this
    # _error_code = ErrorCodes.FEATURIZATION_ERROR


class ProblemInfoException(PreTrainingException):
    """An exception raised during the calculation data characteristics.

    :param exception_message: A message describing the error.
    :type exception_message: str
    :param inner_exception: An optional message, for example, from a previously handled exception.
    :type inner_exception: str
    :param target: The name of the element that caused the exception to be raised.
    :type target: str
    :param details: Any additional information about the error such as other error responses or stack traces.
    :type details: str
    """

    # TODO - define a code for this
    # _error_code = ErrorCodes.PROBLEMINFO_ERROR


class TrainingException(AutoMLExperimentException):
    """An exception for issues that arise during model training.

    :param exception_message: A message describing the error.
    :type exception_message: str
    :param inner_exception: An optional message, for example, from a previously handled exception.
    :type inner_exception: str
    :param target: The name of the element that caused the exception to be raised.
    :type target: str
    :param details: Any additional information about the error such as other error responses or stack traces.
    :type details: str
    """

    # TODO - define a code for this
    # _error_code = ErrorCodes.TRAINING_ERROR


class MetricCalculationException(TrainingException):
    """An exception raised when a metric can't be calculated.

    :param exception_message: A message describing the error.
    :type exception_message: str
    :param inner_exception: An optional message, for example, from a previously handled exception.
    :type inner_exception: str
    :param target: The name of the element that caused the exception to be raised.
    :type target: str
    :param details: Any additional information about the error such as other error responses or stack traces.
    :type details: str
    """

    # TODO - define a code for this
    # _error_code = ErrorCodes.METRICCALCULATION_ERROR


class ModelFitException(TrainingException):
    """An exception for failure to fit the model.

    :param exception_message: A message describing the error.
    :type exception_message: str
    :param inner_exception: An optional message, for example, from a previously handled exception.
    :type inner_exception: str
    :param target: The name of the element that caused the exception to be raised.
    :type target: str
    :param details: Any additional information about the error such as other error responses or stack traces.
    :type details: str
    """

    # TODO - define a code for this
    #  _error_code = ErrorCodes.MODELFIT_ERROR


class PostTrainingException(AutoMLExperimentException):
    """An exception for failures after a model has already been fitted.

    :param exception_message: A message describing the error.
    :type exception_message: str
    :param inner_exception: An optional message, for example, from a previously handled exception.
    :type inner_exception: str
    :param target: The name of the element that caused the exception to be raised.
    :type target: str
    :param details: Any additional information about the error such as other error responses or stack traces.
    :type details: str
    """

    # TODO - define a code for this
    # _error_code = ErrorCodes.POSTTRAINING_ERROR


class ModelExplanationException(PostTrainingException):
    """An exception for failures while trying to explain the model.

    :param exception_message: A message describing the error.
    :type exception_message: str
    :param inner_exception: An optional message, for example, from a previously handled exception.
    :type inner_exception: str
    :param target: The name of the element that caused the exception to be raised.
    :type target: str
    :param details: Any additional information about the error such as other error responses or stack traces.
    :type details: str
    """

    # TODO - define a code for this
    # _error_code = ErrorCodes.MODELEXPLANATION_ERROR


class OnnxException(PostTrainingException):
    """An exception for failures while trying to run ONNX operations.

    :param exception_message: A message describing the error.
    :type exception_message: str
    :param inner_exception: An optional message, for example, from a previously handled exception.
    :type inner_exception: str
    :param target: The name of the element that caused the exception to be raised.
    :type target: str
    :param details: Any additional information about the error such as other error responses or stack traces.
    :type details: str
    """

    # TODO - define a code for this
    # _error_code = ErrorCodes.ONNX_ERROR


class DataprepException(ClientException):
    """An exception related to Dataprep.

    :param exception_message: A message describing the error.
    :type exception_message: str
    :param inner_exception: An optional message, for example, from a previously handled exception.
    :type inner_exception: str
    :param target: The name of the element that caused the exception to be raised.
    :type target: str
    :param details: Any additional information about the error such as other error responses or stack traces.
    :type details: str
    """

    # TODO - define a code for this
    # _error_code = ErrorCodes.DATAPREPVALIDATION_ERROR


# TODO this should move to azureml.exceptions
class NotFoundException(ValidationException):
    """An exception raised when a resource could not be found.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.NOTFOUND_ERROR


class InvalidRunState(ScenarioNotSupportedException):
    """An exception when trying to use a run that is not in a valid state for the given operation.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.INVALIDRUNSTATE_ERROR


class ApiInvocationException(ServiceException):
    """An exception raised when API invocation fails.

    :param exception_message: A message describing the error.
    :type exception_message: str
    :param inner_exception: An optional message, for example, from a previously handled exception.
    :type inner_exception: str
    :param target: The name of the element that caused the exception to be raised.
    :type target: str
    :param details: Any additional information about the error such as other error responses or stack traces.
    :type details: str
    """

    _error_code = ErrorCodes.APIINVOCATION_ERROR


class UnhashableEntryException(DataException, exceptions.DataException):
    """An exception related to unhashable entry in the input data.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    def __init__(self, exception_message="", target=None, **kwargs):
        """Exception related to unhashable entry in the input data.

        :param exception_message: A message describing the error.
        :type exception_message: str
        """
        warnings.warn("UnhashableEntryException is deprecated. Consumers of this exception should catch "
                      "DataException, and producers should raise the same, while including an `azureml_error` "
                      "field for error classification purposes if needed", DeprecationWarning)
        super().__init__(exception_message, target, **kwargs)


class FileNotFoundException(exceptions.AutoMLException):
    """
    An exception related to a file not found.

    :param exception_message: Details on the exception.
    """

    _error_code = ErrorCodes.FILENOTFOUND_ERROR


class FetchNextIterationException(exceptions.JasmineServiceException):
    """An exception related to failing to fetch the next iteration in automated ML."""


class DatasetServiceException(ServiceException):
    """An exception related to failing dataset service API calls."""
