# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Exceptions thrown by AutoML."""
import json
import warnings
from typing import Dict, List, Optional, Type, TypeVar, cast

from azureml._common._error_definition import AzureMLError
from azureml._common.exceptions import AzureMLException
from azureml.automl.core.shared._diagnostics.automl_error_definitions import AutoMLInternalLogSafe, InsufficientMemory
from azureml.automl.core.shared.constants import ClientErrors

from ._error_response_constants import ErrorCodes

ExceptionT = TypeVar('ExceptionT', bound='AutoMLException')

NON_PII_MESSAGE = '[Hidden as it may contain PII]'


class ErrorTypes:
    """Possible types of errors."""

    User = "User"
    System = "System"
    Service = "Service"
    Unclassified = "Unclassified"
    All = {User, System, Service, Unclassified}


class AutoMLException(AzureMLException):
    """Exception with an additional field specifying what type of error it is."""

    # todo deprecate fields that can be obtained from AzureMLError
    def __init__(self,
                 exception_message: str = "",
                 target: Optional[str] = None,
                 details: Optional[List[str]] = None,
                 message_format: Optional[str] = None,
                 message_parameters: Optional[Dict[str, str]] = None,
                 reference_code: Optional[str] = None,
                 has_pii: bool = True,
                 azureml_error: Optional[AzureMLError] = None,
                 inner_exception: Optional[BaseException] = None):
        """
        Construct a new AutoMLException.

        :param exception_message: A message describing the error.
        :type exception_message: str
        :param target: The name of the element that caused the exception to be thrown.
        :type target: str
        :param details: Any additional information for the error, such as other error responses or stack traces.
        :type details: builtin.list(str)
        :param message_format: Un-formatted version of the exception_message with no variable substitution.
        :type message_format: str
        :param message_parameters: Value substitutions corresponding to the contents of message_format
        :type message_parameters: Dictionary[str, str]
        :param reference_code: Indicator of the module or code where the failure occurred
        :type reference_code: str
        :param has_pii: Boolean representing whether the Exception message has any PII information.
        :type has_pii: bool
        """
        self._azureml_error = azureml_error
        self._inner_exception = inner_exception
        self._target = None  # type: Optional[str]

        if self._azureml_error:
            super().__init__(exception_message=self._azureml_error.error_message,
                             inner_exception=self._inner_exception,
                             azureml_error=self._azureml_error)
            self._exception_message = self._azureml_error.error_message
            self._target = self._azureml_error.target
            self._reference_code = self._azureml_error.reference_code
            self._message_format = self._azureml_error.log_safe_message_format()
        else:
            # todo This branch to be removed once azureml_error is used across AutoML.
            super(AutoMLException, self).__init__(exception_message=exception_message,
                                                  inner_exception=inner_exception,
                                                  target=target,
                                                  details=details,
                                                  message_format=message_format,
                                                  message_parameters=message_parameters,
                                                  reference_code=reference_code)
            self._exception_message = exception_message
            self._target = target
            self._details = details
            self._message_format = message_format
            self._message_parameters = message_parameters
            self._reference_code = reference_code
            self._has_pii = has_pii
            if has_pii:
                self._generic_msg = None  # type: Optional[str]
            else:
                self._generic_msg = exception_message
                if not self._message_format:
                    self._message_format = exception_message

            # If this exception is unclassified (i.e. doesn't contain enough information to classify the error
            # b/w User or System), add a default system error to this exception
            self._add_default_system_error()

            AutoMLException._warn_deprecations(details, "details")
            AutoMLException._warn_deprecations(message_format, "message_format")
            AutoMLException._warn_deprecations(message_parameters, "message_parameters")
            AutoMLException._warn_deprecations(reference_code, "reference_code")

    def __repr__(self) -> str:
        # This gets all the properties from the exception, intended for developer debugging.
        error_response = self._serialize_json(indent=4)
        return self._exception_msg_format(
            self.__class__.__name__, self._exception_message, error_response, log_safe=False
        )

    def __str__(self):
        """Return string representation of the exception intended for the client (e.g. user)."""
        # This filters out message_format and message_parameters, since users don't need to see those params as
        # the exception message will contain all of it.
        error_response = self._serialize_json(
            indent=4, filter_fields=[AzureMLError.Keys.MESSAGE_FORMAT,
                                     AzureMLError.Keys.MESSAGE_PARAMETERS]
        )
        return self._exception_msg_format(
            self.__class__.__name__, self._exception_message, error_response, log_safe=False
        )

    def _exception_msg_format(
            self, error_name: str, message: str, error_response: Optional[str], log_safe: bool = True) -> str:
        inner_exception_message = None
        if self._inner_exception:
            if log_safe:
                # Only print the inner exception type for a log safe message
                inner_exception_message = self._inner_exception.__class__.__name__
            else:
                inner_exception_message = "{}: {}".format(
                    self._inner_exception.__class__.__name__,
                    str(self._inner_exception)
                )
        return "{}:\n\tMessage: {}\n\tInnerException: {}\n\tErrorResponse \n{}".format(
            error_name,
            message,
            inner_exception_message,
            error_response)

    def get_pii_free_exception_msg_format(self) -> str:
        # Update exception message to be PII free
        # Update inner exception to log exception type only
        # Update Error Response to contain PII free message
        pii_free_msg = self.pii_free_msg()
        error_dict = json.loads(self._serialize_json(filter_fields=[AzureMLError.Keys.MESSAGE_FORMAT,
                                                                    AzureMLError.Keys.MESSAGE_PARAMETERS]))
        error_dict['error']['message'] = pii_free_msg
        return self._exception_msg_format(
            self.__class__.__name__,
            pii_free_msg,
            json.dumps(error_dict, indent=4)
        )

    @classmethod
    def from_exception(cls: 'Type[ExceptionT]',
                       e: BaseException,
                       msg: Optional[str] = None,
                       target: Optional[str] = None,
                       reference_code: Optional[str] = None,
                       has_pii: bool = True) -> 'AutoMLException':
        """
        Convert an arbitrary exception to this exception type. The resulting exception is marked as containing PII.

        :param cls: Class of type :class: `azureml.automl.core.exceptions.AutoMLException`
        :param e: the original exception object
        :param msg: optional message to use instead of the original exception message
        :param target: optional string pointing to the target of the exception
        :param reference_code: Indicator of the module or code where the failure occurred
        :param has_pii: whether this exception contains PII or not
        :return: a new exception of this type, preserving the original stack trace
        """
        if isinstance(e, AutoMLException):
            return e

        # If given exception is not AutoMLException and safe message to override is not given,
        # then mark has_pii = True
        if not isinstance(e, AutoMLException) and not msg:
            has_pii = True

        if isinstance(e, MemoryError):
            new_exception = cast(ExceptionT,
                                 ResourceException._with_error(
                                     AzureMLError.create(
                                         InsufficientMemory,
                                         target=target,
                                         reference_code=reference_code or target,
                                     ), inner_exception=e).with_traceback(e.__traceback__))
        else:
            new_exception = cast(ExceptionT,
                                 cls(exception_message=(msg or str(e)),
                                     target=target,
                                     reference_code=reference_code or target,
                                     has_pii=has_pii).with_traceback(e.__traceback__))

        new_exception._inner_exception = e
        return new_exception

    @classmethod
    def create_without_pii(cls: 'Type[ExceptionT]', msg: str = "",
                           target: Optional[str] = None, reference_code: Optional[str] = None) -> ExceptionT:
        """
        Create an exception that is tagged as not containing PII.

        :param cls: Class of type :class: `azureml.automl.core.exceptions.AutoMLException`
        :param msg: optional message to use instead of the original exception message
        :param target: optional string pointing to the target of the exception
        :param reference_code: Indicator of the module or code where the failure occurred
        :return:
        """
        exception = cls(exception_message=msg,
                        target=target,
                        message_format=msg,
                        reference_code=reference_code or target,
                        has_pii=False)
        return exception

    def with_generic_msg(self: ExceptionT, msg: str) -> ExceptionT:
        """
        Attach a generic error message that will be used in telemetry if this exception contains PII.

        :param msg: the generic message to use
        :return: this object
        """
        self._generic_msg = msg
        # Until we deprecate _generic_msg, copy it over to message_format which also will be pushed to the service
        self._message_format = msg
        self._has_pii = True
        return self

    @property
    def has_pii(self) -> bool:
        """Check whether this exception's message contains PII or not."""
        return cast(bool, getattr(self, '_has_pii', False))

    @property
    def target(self) -> Optional[str]:
        """Name of the element that caused the exception to be thrown."""
        return self._target

    def pii_free_msg(self, scrubbed: bool = True) -> str:
        """
        Fallback message to use for situations where printing PII-containing information is inappropriate.

        :param scrubbed: If true, return a generic '[Hidden as it may contain PII]' as a fallback, else an empty string
        :return: Log safe message for logging in telemetry
        """
        if self._azureml_error is not None:
            result = self._azureml_error.log_safe_message_format()  # type: str
            # For legacy code paths that just populate 'generic_msg', also attach it to the log_safe_message
            if getattr(self, "_generic_msg", None) is not None:
                result = ", ".join([result, cast(str, self._generic_msg)])
            return result

        fallback_message = (getattr(self, '_message_format', None) or
                            getattr(self, '_generic_msg', None) or
                            NON_PII_MESSAGE if scrubbed else '')  # type: str
        message = self._exception_message or fallback_message if not self.has_pii else fallback_message  # type: str
        return message

    @property
    def error_type(self):
        """Get the root error type for this exception."""
        if self._azureml_error:
            return self._azureml_error.error_definition.get_root_error()

        return self._get_all_error_codes()[0]

    @property
    def error_code(self):
        """Get the error code for this exception."""
        if self._azureml_error:
            return self._azureml_error.error_definition.code

        return getattr(self, "_error_code", self.error_type)

    @property
    def message_format(self) -> str:
        """Get a log safe exception message, if any."""
        if self._azureml_error is not None:
            result = self._azureml_error.log_safe_message_format()  # type: str
            return result

        return self._message_format or ""

    def _get_all_error_codes(self) -> List[str]:
        if self._azureml_error:
            return cast(List[str], self._azureml_error.error_definition.code_hierarchy)

        error_response_json = json.loads(self._serialize_json()).get("error")
        if error_response_json is None:
            return [ErrorTypes.Unclassified]
        codes = [error_response_json.get('code', ErrorTypes.Unclassified)]
        inner_error = error_response_json.get(
            'inner_error', error_response_json.get('innerError', None))
        while inner_error is not None:
            code = inner_error.get('code')
            if code is None:
                break
            codes.append(code)
            inner_error = inner_error.get(
                'inner_error', inner_error.get('innerError', None))
        return codes

    def _add_default_system_error(self) -> None:
        """Add a default AzureMLError (as System) to this instance of exception."""
        # For exceptions still using legacy error codes (e.g., via the '_error_codes' attribute), don't convert it into
        # a system error.
        all_error_codes = ".".join(self._get_all_error_codes())
        if ErrorTypes.User in all_error_codes or ErrorTypes.System in all_error_codes:
            # The error is already classified
            return

        # For all other exceptions, default them to a 'AutoMLInternal' system error, for error classification purposes.
        log_safe_message = self.pii_free_msg()
        if log_safe_message == NON_PII_MESSAGE:
            # If there was no log safe message, attach the exception type (and whatever error code that was known)
            known_error_code = all_error_codes if ErrorTypes.Unclassified not in all_error_codes else None
            log_safe_message = "/".join(filter(None, [self.__class__.__name__, known_error_code]))
        self._azureml_error = AzureMLError.create(
            AutoMLInternalLogSafe, error_message=log_safe_message, error_details=self.__str__(),
            target=self.target, reference_code=self._reference_code)

    @staticmethod
    def _warn_deprecations(param, param_name):
        if param:
            warnings.warn("'{}' is deprecated. Please provide an instance of AzureMLError as a keyword argument "
                          "with key 'azureml_error'".format(param_name), DeprecationWarning)


class UserException(AutoMLException):
    """
    Exception related to user error.

    :param exception_message: Details on the exception.
    :param target: The name of the element that caused the exception to be thrown.
    """

    _error_code = ErrorCodes.USER_ERROR

    def __init__(self, exception_message="", target=None, **kwargs):
        """
        Construct a new UserException.

        :param exception_message: Details on the exception.
        :param target: The name of the element that caused the exception to be thrown.
        """
        super().__init__(exception_message, target, **kwargs)


class DataException(UserException):
    """
    Exception related to data validations.

    :param exception_message: Details on the exception.
    :param target: The name of the element that caused the exception to be thrown.
    """

    # Targets
    MISSING_DATA = 'MissingData'

    _error_code = ErrorCodes.INVALIDDATA_ERROR

    def __init__(self, exception_message="", target=None, **kwargs):
        """
        Construct a new DataException.

        :param exception_message: Details on the exception.
        :param target: The name of the element that caused the exception to be thrown.
        """
        super().__init__(exception_message, target, **kwargs)


class ClientException(AutoMLException):
    """
    Exception related to client.

    :param exception_message: Details on the exception.
    :param target: The name of the element that caused the exception to be thrown.
    """

    def __init__(self, exception_message="", target=None, **kwargs):
        """
        Construct a new ClientException.

        :param exception_message: Details on the exception.
        :param target: The name of the element that caused the exception to be thrown.
        """
        super().__init__(exception_message, target, **kwargs)


class ServiceException(ClientException):
    """
    Exception related to JOS.

    :param exception_message: Details on the exception.
    :param target: The name of the element that caused the exception to be thrown.
    """
    def __init__(self, exception_message="", target=None, **kwargs):
        """
        Construct a new ServiceException.

        :param exception_message: Details on the exception.
        :param target: The name of the element that caused the exception to be thrown.
        """
        super().__init__(exception_message, target, **kwargs)


class DataErrorException(ClientException):
    """
    Exception related to errors seen while processing data at training or inference time.

    :param exception_message: Details on the exception.
    :param target: The name of the element that caused the exception to be thrown.
    """

    def __init__(self, exception_message="", target=None, **kwargs):
        """
        Construct a new DataErrorException.

        :param exception_message: Details on the exception.
        :param target: The name of the element that caused the exception to be thrown.
        """
        super().__init__(exception_message, target, **kwargs)


class FitException(ClientException):
    """
    Exception related to fit in external pipelines, models, and transformers.

    :param exception_message: Details on the exception.
    :param target: The name of the element that caused the exception to be thrown.
    """
    def __init__(self, exception_message="", target=None, **kwargs):
        """
        Construct a new FitException.

        :param exception_message: Details on the exception.
        :param target: The name of the element that caused the exception to be thrown.
        """
        super().__init__(exception_message, target, **kwargs)


class TransformException(ClientException):
    """
    Exception related to transform in external pipelines and transformers.

    :param exception_message: Details on the exception.
    :param target: The name of the element that caused the exception to be thrown.
    """
    def __init__(self, exception_message="", target=None, **kwargs):
        """
        Construct a new TransformException.

        :param exception_message: Details on the exception.
        :param target: The name of the element that caused the exception to be thrown.
        """
        super().__init__(exception_message, target, **kwargs)


class PredictionException(ClientException):
    """
    Exception related to prediction in external pipelines and transformers.

    :param exception_message: Details on the exception.
    :param target: The name of the element that caused the exception to be thrown.
    """
    def __init__(self, exception_message="", target=None, **kwargs):
        """
        Construct a new PredictionException.

        :param exception_message: Details on the exception.
        :param target: The name of the element that caused the exception to be thrown.
        """
        super().__init__(exception_message, target, **kwargs)


class UntrainedModelException(ClientException):
    """UntrainedModelException."""

    def __init__(self, exception_message="Fit needs to be called before predict.", target=None, **kwargs):
        """
        Create a UntrainedModelException.

        :param exception_message: Details on the exception.
        :param target: The name of the element that caused the exception to be thrown.
        """
        super().__init__("UntrainedModelException: {0}".format(exception_message), target=target, **kwargs)


class InvalidArgumentException(ClientException):
    """Exception related to arguments that were not expected by a component.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.
    """

    def __init__(self, exception_message="", target=None, **kwargs):
        warnings.warn("InvalidArgumentException is deprecated. Consumers of this exception should catch "
                      "ValidationException, and producers should raise the same, while including an `azureml_error` "
                      "field for error classification purposes if needed", DeprecationWarning)
        super().__init__(exception_message, target, **kwargs)


class RawDataSnapshotException(ClientException):
    """
    Exception related to capturing the raw data snapshot to be used at the inference time.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.

    :param exception_message: Details on the exception.
    :param target: The name of the element that caused the exception to be thrown.
    """
    def __init__(self, exception_message="", target=None, **kwargs):
        warnings.warn("RawDataSnapshotException is deprecated. Consumers of this exception should catch "
                      "ClientException, and producers should raise the same, while including an `azureml_error` "
                      "field for error classification purposes if needed", DeprecationWarning)
        super().__init__(exception_message, target, **kwargs)


class ResourceException(UserException):
    """
    Exception related to insufficient resources on the user compute.

    :param exception_message: Details on the exception.
    :param target: The name of the element that caused the exception to be thrown.
    """

    def __init__(self, exception_message="", target=None, **kwargs):
        """
        Construct a new ResourceException.

        :param exception_message: Details on the exception.
        :param target: The name of the element that caused the exception to be thrown.
        """
        super().__init__(exception_message, target, **kwargs)


class OnnxConvertException(ClientException):
    """Exception related to ONNX convert."""

    # TODO - define a code for this
    # _error_code = ErrorCodes.ONNX_ERROR


class DataprepException(ClientException):
    """Exceptions related to Dataprep."""

    # TODO - define a code for this
    # _error_code = ErrorCodes.DATAPREPVALIDATION_ERROR


class DeleteFileException(ClientException):
    """Exceptions related to file cleanup."""

    def __init__(self, exception_message="", target=None, **kwargs):
        """
        Construct a new DeleteFileException.

        :param exception_message: Details on the exception.
        :param target: The name of the element that caused the exception to be thrown.
        """
        super().__init__(exception_message, target, **kwargs)


class LabelMissingException(DataException):
    """Exception related to label missing from input data.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.

    :param exception_message: Details on the exception.
    :param target: The name of the element that caused the exception to be thrown.
    """

    def __init__(self, exception_message="", target=None, **kwargs):
        warnings.warn("LabelMissingException is deprecated. Consumers of this exception should catch "
                      "DataException, and producers should raise the same, while including an `azureml_error` "
                      "field for error classification purposes if needed")
        super().__init__(exception_message, target, **kwargs)


class FeaturizationOffException(DataException):
    """Exception related to featurization not being enabled.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.

    :param exception_message: Details on the exception.
    :param target: The name of the element that caused the exception to be thrown.
    """

    def __init__(self, exception_message="", target=None, **kwargs):
        warnings.warn("FeaturizationOffException is deprecated. Consumers of this exception should catch "
                      "DataException, and producers should raise the same, while including an `azureml_error` "
                      "field for error classification purposes if needed")
        super().__init__(exception_message, target, **kwargs)


class DataSamplesSizeException(DataException):
    """Exception related to X and y having different number of samples.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.

    :param exception_message: Details on the exception.
    :param target: The name of the element that caused the exception to be thrown.
    """

    def __init__(self, exception_message="", target=None, **kwargs):
        warnings.warn("DataSamplesSizeException is deprecated. Consumers of this exception should catch "
                      "DataException, and producers should raise the same, while including an `azureml_error` "
                      "field for error classification purposes if needed")
        super().__init__(exception_message, target, **kwargs)


class EmptyDataException(DataException):
    """Exception related to the input data is empty.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.

    :param exception_message: Details on the exception.
    :param target: The name of the element that caused the exception to be thrown.
    """

    def __init__(self, exception_message="", target=None, **kwargs):
        warnings.warn("EmptyDataException is deprecated. Consumers of this exception should catch "
                      "AutoMLException, and producers should raise the same, while including an `azureml_error` "
                      "field for error classification purposes if needed")
        super().__init__(exception_message, target, **kwargs)


class InvalidDataTypeException(DataException):
    """Exception related to the input data type is invalid.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.

    :param exception_message: Details on the exception.
    :param target: The name of the element that caused the exception to be thrown.
    """

    def __init__(self, exception_message="", target=None, **kwargs):
        warnings.warn("InvalidDataTypeException is deprecated. Consumers of this exception should catch "
                      "DataException, and producers should raise the same, while including an `azureml_error` "
                      "field for error classification purposes if needed")
        super().__init__(exception_message, target, **kwargs)


class ValidationException(AutoMLException):
    """An exception representing errors caught when validating inputs."""
    def __init__(self, exception_message="", target=None, **kwargs):
        super().__init__(exception_message=exception_message, target=target, **kwargs)


class ArgumentException(ValidationException):
    """
    Exception related to invalid user config.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.

    :param exception_message: Details on the exception.
    :param target: The name of the element that caused the exception to be thrown.
    """

    def __init__(self, exception_message="", target=None, **kwargs):
        warnings.warn("ArgumentException is deprecated. Consumers of this exception should catch "
                      "ValidationException, and producers should raise the same, while including an `azureml_error` "
                      "field for error classification purposes if needed")
        super().__init__(exception_message, target, **kwargs)


class BadArgumentException(ValidationException):
    """An exception related to data validation.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.

    :param exception_message: Details on the exception.
    :param target: The name of the element that caused the exception to be thrown.
    """

    def __init__(self, exception_message="", target=None, **kwargs):
        warnings.warn("BadArgumentException is deprecated. Consumers of this exception should catch "
                      "ValidationException, and producers should raise the same, while including an `azureml_error` "
                      "field for error classification purposes if needed")
        super().__init__(exception_message, target, **kwargs)


class MissingValueException(ValidationException):
    """An exception related to data validation.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    def __init__(self, exception_message="", target=None, **kwargs):
        warnings.warn("MissingValueException is deprecated. Consumers of this exception should catch "
                      "ValidationException, and producers should raise the same, while including an `azureml_error` "
                      "field for error classification purposes if needed")
        super().__init__(exception_message, target, **kwargs)


class ConfigException(ValidationException):
    """Exception related to invalid user config."""

    # Having `_error_code` is solely for backwards compatibility. Once all exceptions that extend ConfigException are
    # updated to use azureml_error, we should remove this field
    # work item: https://msdata.visualstudio.com/Vienna/_workitems/edit/798213


class MalformedValueException(ValidationException):
    """An exception related to data validation.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    def __init__(self, exception_message="", target=None, **kwargs):
        warnings.warn("MalformedValueException is deprecated. Consumers of this exception should catch "
                      "ValidationException, and producers should raise the same, while including an `azureml_error` "
                      "field for error classification purposes if needed")
        super().__init__(exception_message, target, **kwargs)


class OutOfRangeException(ValidationException):
    """An exception related to value out of range.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    def __init__(self, exception_message="", target=None, **kwargs):
        warnings.warn("OutOfRangeException is deprecated. Consumers of this exception should catch "
                      "ValidationException, and producers should raise the same, while including an `azureml_error` "
                      "field for error classification purposes if needed")
        super().__init__(exception_message, target, **kwargs)


class MissingArgumentException(ConfigException):
    """An exception related to missing required argument.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    def __init__(self, exception_message="", target=None, **kwargs):
        warnings.warn("MissingArgumentException is deprecated. Consumers of this exception should catch "
                      "ValidationException, and producers should raise the same, while including an `azureml_error` "
                      "field for error classification purposes if needed")
        super().__init__(exception_message, target, **kwargs)


class ScenarioNotSupportedException(ConfigException):
    """An exception related to scenario not supported.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.
    """

    def __init__(self, exception_message="", target=None, **kwargs):
        warnings.warn("ScenarioNotSupportedException is deprecated. Consumers of this exception should catch "
                      "ConfigException, and producers should raise the same, while including an `azureml_error` "
                      "field for error classification purposes if needed", DeprecationWarning)
        super().__init__(exception_message, target, **kwargs)


class UnhashableEntryException(DataException):
    """An exception related to unhashable entry in the input data.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.
    """

    def __init__(self, exception_message="", target=None, **kwargs):
        warnings.warn("UnhashableEntryException is deprecated. Consumers of this exception should catch "
                      "DataException, and producers should raise the same, while including an `azureml_error` "
                      "field for error classification purposes if needed", DeprecationWarning)
        super().__init__(exception_message, target, **kwargs)


class InsufficientDataException(DataException):
    """An exception related to insufficient input data.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.
    """

    def __init__(self, exception_message=None, target=None, **kwargs):
        warnings.warn("InsufficientDataException is deprecated. Consumers of this exception should catch "
                      "DataException, and producers should raise the same, while including an `azureml_error` "
                      "field for error classification purposes if needed")
        super().__init__(exception_message, target, **kwargs)


class OutOfBoundDataException(DataException):
    """An exception related to infinity input data.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.
    """

    def __init__(self, exception_message=None, target=None, **kwargs):
        warnings.warn("OutOfBoundDataException is deprecated. Consumers of this exception should catch "
                      "DataException, and producers should raise the same, while including an `azureml_error` "
                      "field for error classification purposes if needed")
        super().__init__(exception_message, target, **kwargs)


class DataFormatException(DataException):
    """Exception related to input data not being in the expected format.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.
    """

    def __init__(self, exception_message=None, target=None, **kwargs):
        warnings.warn("DataFormatException is deprecated. Consumers of this exception should catch "
                      "DataException, and producers should raise the same, while including an `azureml_error` "
                      "field for error classification purposes if needed")
        super().__init__(exception_message, target, **kwargs)


class AllLabelsMissingException(DataException):
    """Exception related to input data missing all labels.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.
    """

    def __init__(self, exception_message=None, target=None, **kwargs):
        warnings.warn("AllLabelsMissingException is deprecated. Consumers of this exception should catch "
                      "DataException, and producers should raise the same, while including an `azureml_error` "
                      "field for error classification purposes if needed")
        super().__init__(exception_message, target, **kwargs)


class DiskSpaceUnavailableException(UserException):
    """Exception related to insufficient disk space.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.
    """

    def __init__(self, exception_message=None, target=None, **kwargs):
        warnings.warn("DiskSpaceUnavailableException is deprecated. Consumers of this exception should catch "
                      "ResourceException, and producers should raise the same, while including an `azureml_error` "
                      "field for error classification purposes if needed")
        message = ClientErrors.EXCEEDED_MEMORY if exception_message is None else exception_message
        super().__init__(message, target, **kwargs)


class CacheStoreCorruptedException(UserException):
    """Exception related to corrupted cache store.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.
    """

    def __init__(self, exception_message=None, target=None, **kwargs):
        warnings.warn("CacheStoreCorruptedException is deprecated. Consumers of this exception should catch "
                      "CacheException, and producers should raise the same, while including an `azureml_error` "
                      "field for error classification purposes if needed")
        message = ClientErrors.EXCEEDED_MEMORY if exception_message is None else exception_message
        super().__init__(message, target, **kwargs)


class AutoMLEnsembleException(ClientException):
    """Exception for AutoML ensembling related errors."""

    # Targets
    CONFIGURATION = 'Configuration'
    MISSING_MODELS = 'MissingModels'
    MODEL_NOT_FIT = 'ModelNotFit'

    def __init__(self, exception_message, error_detail=None, target=None, **kwargs):
        """Create an AutoMLEnsemble exception."""
        if error_detail is not None:
            super().__init__(
                exception_message="AutoMLEnsembleException: {0}, {1}".format(exception_message, error_detail),
                target=target, **kwargs)
        else:
            super().__init__(exception_message="AutoMLEnsembleException: {0}".format(exception_message), **kwargs)


class PipelineRunException(ClientException):
    """Exception for pipeline run related errors."""

    # Targets
    PIPELINE_RUN_REQUIREMENTS = 'PipelineRunRequirements'
    PIPELINE_RUN = 'PipelineRun'
    PIPELINE_OUTPUT = 'PipelineOutput'

    def __init__(self, exception_message, error_detail=None, target=None, **kwargs):
        """Create a PipelineRunException exception."""
        if error_detail is not None:
            super().__init__(
                exception_message="PipelineRunException: {0}, {1}".format(exception_message, error_detail),
                target=target, **kwargs)
        else:
            super().__init__(exception_message="PipelineRunException: {0}".format(exception_message),
                             target=target, **kwargs)


class JasmineServiceException(ServiceException):
    """
    Exception related to the class of errors by Jasmine.

    :param exception_message: Details on the exception.
    :param target: The name of the element that caused the exception to be thrown.
    """

    def __init__(self, exception_message="", target=None, **kwargs):
        """
        Construct a new JasmineServiceException.

        :param exception_message: Details on the exception.
        :param target: The name of the element that caused the exception to be thrown.
        """
        super().__init__(exception_message, target, **kwargs)


class RunStateChangeException(ServiceException):
    """
    Exception related to failing to change the state of the run.

    :param exception_message: Details on the exception.
    :param target: The name of the element that caused the exception to be thrown.
    """

    def __init__(self, exception_message="", target=None, **kwargs):
        """
        Construct a new RunStateChangeException.

        :param exception_message: Details on the exception.
        :param target: The name of the element that caused the exception to be thrown.
        """
        super().__init__(exception_message, target, **kwargs)


class CacheException(ClientException):
    """
    Exception related to cache store operations.

    :param exception_message: Details on the exception.
    :param target: The name of the element that caused the exception to be thrown.
    """
    def __init__(self, exception_message="", target=None, **kwargs):
        """
        Construct a new CacheException.

        :param exception_message: Details on the exception.
        :param target: The name of the element that caused the exception to be thrown.
        """
        super().__init__(exception_message, target, **kwargs)


class MemorylimitException(ResourceException):
    """Exception to raise when memory exceeded.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.
    """

    _error_code = ErrorCodes.INSUFFICIENTMEMORY_ERROR

    def __init__(self, exception_message=None, target=None, **kwargs):
        warnings.warn("MemorylimitException is deprecated. Consumers of this exception should catch "
                      "ResourceException, and producers should raise the same, while including an `azureml_error` "
                      "field for error classification purposes if needed")
        message = ClientErrors.EXCEEDED_MEMORY if exception_message is None else exception_message
        super().__init__(message, target, **kwargs)


class OptionalDependencyMissingException(ConfigException):
    """An exception raised when an a soft dependency is missing.

    Dev Note: This is Deprecated, and will shortly be removed. Please use one of the other exceptions.
    """

    def __init__(self, exception_message="", target=None, **kwargs):
        warnings.warn("OptionalDependencyMissingException is deprecated. Consumers of this exception should catch "
                      "ConfigException, and producers should raise the same, while including an `azureml_error` "
                      "field for error classification purposes if needed", DeprecationWarning)
        super().__init__(exception_message, target, **kwargs)


class ManagedEnvironmentCorruptedException(ClientException):
    """An exception raised when managed environment has issues with package dependencies.

    :param exception_message: Details on the exception.
    :param target: The name of the element that caused the exception to be thrown.
    """
    def __init__(self, exception_message="", target=None, **kwargs):
        """
        Construct a new ManagedEnvironmentCorruptedException.

        :param exception_message: Details on the exception.
        :param target: The name of the element that caused the exception to be thrown.
        """
        super().__init__(exception_message, target, **kwargs)


class InvalidOperationException(ValidationException):
    """Exception raised when an attempt is made to perform an illegal operation."""

    def __init__(self, exception_message, **kwargs):
        super().__init__(exception_message=exception_message, **kwargs)


class InvalidValueException(ValidationException):
    """
    Exception raised when an argument is expected to have a non-null (or an accepted) value,
    but is actually null (or something else).
    """

    def __init__(self, exception_message, **kwargs):
        super().__init__(exception_message=exception_message, **kwargs)


class InvalidTypeException(ValidationException):
    """
    Exception raised when when an argument is expected to be of one type, but is actually something else.
    """

    def __init__(self, exception_message, **kwargs):
        super().__init__(exception_message=exception_message, **kwargs)
