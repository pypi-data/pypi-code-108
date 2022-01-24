# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines custom exceptions produced by azureml-interpret."""

# For detailed info on error handling design, see spec:
# https://msdata.visualstudio.com/Vienna/_git/specs?path=%2FErrorHandling%2Ferror-handling-in-azureml-sdk.md
# For error codes see:
# <root>\src\azureml-core\azureml\_common\_error_response\_generate_constants\error_codes.json
from azureml._common._error_response._error_response_constants import ErrorCodes
from azureml.exceptions import UserErrorException, AzureMLException


class SerializationException(UserErrorException):
    """An exception related to invalid serialized data.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.MALFORMED_ERROR


class MissingPackageException(UserErrorException):
    """An exception related to a missing Python package required for method.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.OPTIONALSCENARIONOTENABLED_ERROR


class UnsupportedModelException(UserErrorException):
    """An exception indicating that the given model is not supported.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.VALIDATION_ERROR


class SamplesExceededException(UserErrorException):
    """An exception indicating that the number of samples exceeded the supported maximum.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.NUMBEROFSAMPLESEXCEEDED_ERROR


class ExplanationNotFoundException(UserErrorException):
    """An exception indicating that the explanation could not be found.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.NOTFOUND_ERROR


class ConflictingRawTransformationsException(UserErrorException):
    """An exception indicating that both feature map and transformations were incorrectly passed.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.CONFLICTINGSETTINGS_ERROR


class InitDatasetMissingException(UserErrorException):
    """An exception indicating that the initialization dataset is missing.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.INVALID_ERROR


class MissingExplainException(UserErrorException):
    """An exception indicating that the current state is invalid possibly due to a missing explain call.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.INVALIDRUNSTATE_ERROR


class MissingRawTransformationsException(UserErrorException):
    """An exception indicating that the raw feature map was not passed for the scenario.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.CONFLICTINGSETTINGS_ERROR


class MissingEvalDataException(UserErrorException):
    """An exception indicating that the evaluation dataset was not passed for the scenario.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.CONFLICTINGSETTINGS_ERROR


class MissingExplanationTypesException(UserErrorException):
    """An exception indicating that the explanation types were not passed.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.INVALID_ERROR


class DirectoryExistsException(UserErrorException):
    """An exception indicating that the directory already exists.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.FILE_ERROR


class NoExperimentNameOrIdException(UserErrorException):
    """An exception indicating that the run's experiment has no ID or name properties.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.BADARGUMENT_ERROR


class DimensionMismatchException(UserErrorException):
    """An exception indicating that dimensions of user input data and user's model output don't match.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.DATASHAPE_ERROR


class OptionalDependencyMissingException(AzureMLException):
    """An exception indicating that an optional dependency is missing.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.OPTIONALDEPENDENCYMISSING_ERROR


class ScenarioNotSupportedException(AzureMLException):
    """An exception indicating that some scenario is not supported.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.SCENARIONOTSUPORTED_ERROR


class InvalidExplanationException(UserErrorException):
    """An exception indicating that the data type of explanation was unexpected.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.INVALIDDATATYPE_ERROR
