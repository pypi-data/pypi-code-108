# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""A module that contains definitions of custom exception classes."""

import warnings

from azureml.automl.core.shared._error_response_constants import ErrorCodes
from azureml.automl.core.shared.exceptions import ClientException, ConfigException, DataException


class ForecastingExceptionConstants:
    """Constants for the forecasting exception module."""

    _DEPRECATION_MESSAGE_TEMPLATE = (
        "{} is deprecated. Consumers of this exception should catch "
        "ForecastingException, and producers should raise the same, while including an `azureml_error` "
        "field for error classification purposes if needed.")


class PipelineException(ClientException):
    """
    Exception raised for errors in AzureMLForecastPipeline.

    Attributes:
        message: terse error message as defined in 'Messages' class of the
            'verify' module
        error_detail: optional, detailed error message

    """

    def __init__(self, exception_message, error_detail=None, **kwargs):
        """Create a PipelineException."""
        warnings.warn(ForecastingExceptionConstants._DEPRECATION_MESSAGE_TEMPLATE.format(
            self.__class__.__name__))
        if error_detail is not None:
            super().__init__(exception_message="{}: {}, {}".format(
                self.__class__.__name__, exception_message, error_detail),
                **kwargs)
        else:
            super().__init__(exception_message="{}: {}".format(self.__class__.__name__, exception_message), **kwargs)


class ForecastingTransformException(ClientException):
    """
    Exception raised for errors in a transform class in the AzureML Forecasting SDK.

    Attributes:
        message: terse error message as defined in 'Messages' class of the 'verify' module
        error_detail: optional, detailed error message

    """

    def __init__(self, exception_message, error_detail=None, **kwargs):
        """Create a ForecastingTransformException."""
        warnings.warn(ForecastingExceptionConstants._DEPRECATION_MESSAGE_TEMPLATE.format(
            self.__class__.__name__))
        if error_detail is not None:
            super().__init__(
                exception_message="{}: {}, {}".format(
                    self.__class__.__name__, exception_message, error_detail), **kwargs)
        else:
            super().__init__(
                exception_message="{}: {}".format(
                    self.__class__.__name__, exception_message),
                **kwargs)


class TransformValueException(ForecastingTransformException):
    """
    Exception raised for value errors in a transform class in the AzureML Forecasting SDK.

    :param message:
        terse error message as defined in 'Messages'
        class of the 'verify' module
    :type message: str

    :param error_detail: optional, detailed error message
    :type error_detail: str
    """

    def __init__(self, exception_message, error_detail=None, **kwargs):
        """Create a TransformValueException."""
        warnings.warn(ForecastingExceptionConstants._DEPRECATION_MESSAGE_TEMPLATE.format(
            self.__class__.__name__))
        super().__init__(exception_message, error_detail, **kwargs)


class NotTimeSeriesDataFrameException(ClientException):
    """
    Exception raised if the data frame is not of TimeSeriesDataFrame.

    Attributes:
        message: terse error message as defined in 'Messages' class of the 'verify' module
        error_detail: optional, detailed error message

    """

    def __init__(self, exception_message, error_detail=None, **kwargs):
        """Create a NotTimeSeriesDataFrameException."""
        warnings.warn(ForecastingExceptionConstants._DEPRECATION_MESSAGE_TEMPLATE.format(
            self.__class__.__name__))
        if error_detail is not None:
            super().__init__(exception_message="{}: {}, {}".format(
                self.__class__.__name__, exception_message, error_detail), **kwargs)
        else:
            super().__init__(exception_message="{}: {}".format(self.__class__.__name__,
                                                               exception_message),
                             **kwargs)


class DataFrameTypeException(DataException):
    """DataFrameTypeException."""

    def __init__(self, exception_message, **kwargs):
        """Create a DataFrameTypeException."""
        warnings.warn(ForecastingExceptionConstants._DEPRECATION_MESSAGE_TEMPLATE.format(
            self.__class__.__name__))
        super().__init__("Data frame type is invalid. {0}".format(exception_message), **kwargs)


class DataFrameValueException(ClientException):
    """DataFrameValueException."""

    def __init__(self, exception_message, has_pii=True, **kwargs):
        """Create a DataFrameValueException."""
        warnings.warn(ForecastingExceptionConstants._DEPRECATION_MESSAGE_TEMPLATE.format(
            self.__class__.__name__))
        super().__init__("Data frame value is invalid. {0}".format(exception_message), has_pii=has_pii, **kwargs)


class ForecastingDataException(DataException):
    """The data exception, accepting both generic and private information-containing exception."""

    def __init__(self, exception_message, pii_message=None, target=None, **kwargs):
        """Create a DataFrameFrequencyException."""
        if pii_message is not None:
            kwargs['has_pii'] = True
            super().__init__(pii_message, target, **kwargs)
            self.with_generic_msg(exception_message)
        else:
            super().__init__(exception_message, target, **kwargs)


class DataFrameFrequencyException(ForecastingDataException):
    """DataFrameFrequencyException."""

    _error_code = ErrorCodes.TIMEFREQUENCYCANNOTBEINFERRABLE_ERROR

    def __init__(self, exception_message, **kwargs):
        warnings.warn(ForecastingExceptionConstants._DEPRECATION_MESSAGE_TEMPLATE.format(
            self.__class__.__name__))
        super().__init__(exception_message, **kwargs)


class DataFrameFrequencyChanged(ForecastingDataException):
    """Frequency is different in train and test/validate set."""

    _error_code = ErrorCodes.FREQUENCIESMISMATCH_ERROR

    def __init__(self, exception_message, **kwargs):
        warnings.warn(ForecastingExceptionConstants._DEPRECATION_MESSAGE_TEMPLATE.format(
            self.__class__.__name__))


class DataFrameTimeNotContinuous(ForecastingDataException):
    """There is a gap between train and test."""

    _error_code = ErrorCodes.TIMENOTCONTINUOUS_ERROR

    def __init__(self, exception_message, **kwargs):
        warnings.warn(ForecastingExceptionConstants._DEPRECATION_MESSAGE_TEMPLATE.format(
            self.__class__.__name__))


class DataFrameMissingColumnException(ForecastingDataException):
    """DataFrameMissingColumnException."""

    _error_code = ErrorCodes.MISSINGCOLUMN_ERROR

    GENERIC_MSG = "Data frame is missing a column."

    TIME_COLUMN = "Time"
    GRAIN_COLUMN = "TimeSeriesId"
    GROUP_COLUMN = "Group"
    ORIGIN_COLUMN = "Origin"
    VALUE_COLUMN = "TargetValue"
    REGULAR_COLUMN = "Regular"

    def __init__(self, pii_message=None, target=REGULAR_COLUMN, **kwargs):
        """Create a DataFrameMissingTimeColumnException."""
        warnings.warn(ForecastingExceptionConstants._DEPRECATION_MESSAGE_TEMPLATE.format(
            self.__class__.__name__))
        if kwargs.get('exception_message'):
            super().__init__(kwargs.pop('exception_message'), pii_message, target, **kwargs)
        else:
            super().__init__("Data frame is missing a column.", pii_message, target, **kwargs)


class DataFrameIncorrectFormatException(ForecastingDataException):
    """DataFrameIncorrectFormatException."""

    def __init__(self, exception_message, **kwargs):
        warnings.warn(ForecastingExceptionConstants._DEPRECATION_MESSAGE_TEMPLATE.format(
            self.__class__.__name__))
        super().__init__(exception_message, **kwargs)


class DuplicatedIndexException(ForecastingDataException):
    """DuplicatedIndexException."""

    _error_code = ErrorCodes.DUPLICATEDINDEX_ERROR

    def __init__(self, exception_message, **kwargs):
        warnings.warn(ForecastingExceptionConstants._DEPRECATION_MESSAGE_TEMPLATE.format(
            self.__class__.__name__))
        super().__init__(exception_message, **kwargs)


class ForecastingConfigException(ConfigException):
    """The config exceptions related to forecasting tasks."""

    _error_code = ErrorCodes.FORECASTINGCONFIG_ERROR


class ColumnTypeNotSupportedException(ForecastingConfigException):
    """ColumnTypeNotSupportedException."""

    _error_code = ErrorCodes.COLUMNNAMENOTSUPPORTED_ERROR

    def __init__(self, exception_message, error_detail=None, **kwargs):
        """Create a ColumnTypeNotSupportedException."""
        warnings.warn(ForecastingExceptionConstants._DEPRECATION_MESSAGE_TEMPLATE.format(
            self.__class__.__name__))
        if error_detail is not None:
            super().__init__("{}: {}, {}".format(self.__class__.__name__, exception_message, error_detail),
                             **kwargs)
        else:
            super().__init__("{}: {}".format(self.__class__.__name__, exception_message), **kwargs)


class DropSpecialColumn(ForecastingConfigException):
    """DropSpecialColumn."""

    _error_code = ErrorCodes.SPECIALCOLUMNDROP_ERROR

    def __init__(self, exception_message, **kwargs):
        warnings.warn(ForecastingExceptionConstants._DEPRECATION_MESSAGE_TEMPLATE.format(
            self.__class__.__name__))


class GrainAndTimeOverlapException(ForecastingConfigException):
    """GrainAndTimeOverlapException."""

    _error_code = ErrorCodes.TIMEANDGRAINSOVERLAP_ERROR

    def __init__(self, exception_message, **kwargs):
        warnings.warn(ForecastingExceptionConstants._DEPRECATION_MESSAGE_TEMPLATE.format(
            self.__class__.__name__))
        super().__init__(exception_message, **kwargs)


class InvalidTsdfArgument(ConfigException):
    """Invalid tsdf argument."""

    _error_code = ErrorCodes.BADARGUMENT_ERROR

    def __init__(self, exception_message, **kwargs):
        warnings.warn(ForecastingExceptionConstants._DEPRECATION_MESSAGE_TEMPLATE.format(
            self.__class__.__name__))


class WrongShapeDataError(ForecastingDataException):
    """The class of errors related to the data frame shape."""

    _error_code = ErrorCodes.DATASHAPE_ERROR

    def __init__(self, exception_message, **kwargs):
        warnings.warn(ForecastingExceptionConstants._DEPRECATION_MESSAGE_TEMPLATE.format(
            self.__class__.__name__))


class GrainAbsent(ForecastingDataException):
    """The class of errors when grain is present in test/validate, but not in train set."""

    _error_code = ErrorCodes.GRAINISABSENT_ERROR

    def __init__(self, exception_message, **kwargs):
        warnings.warn(ForecastingExceptionConstants._DEPRECATION_MESSAGE_TEMPLATE.format(
            self.__class__.__name__))
