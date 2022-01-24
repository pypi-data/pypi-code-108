# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Exceptions thrown by AutoML transformers."""

from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.core.shared._error_response_constants import ErrorCodes


class TransformRuntimeException(ClientException):
    """
    An exception related to TransformRuntime.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.TRANSFORMRUNTIME_ERROR


class BadTransformArgumentException(TransformRuntimeException):
    """
    An exception related to BadTransformArgument.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.BADTRANSFORMARGUMENT_ERROR


class InvalidTransformArgumentException(BadTransformArgumentException):
    """
    An exception related to InvalidTransformArgument.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.INVALIDTRANSFORMARGUMENT_ERROR


class DataTransformerUnknownTaskException(InvalidTransformArgumentException):
    """
    An exception related to DataTransformerUnknownTask.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.DATATRANSFORMERUNKNOWNTASK_ERROR


class ModelingBertNoApexInvalidHiddenSizeException(InvalidTransformArgumentException):
    """
    An exception related to ModelingBertNoApexInvalidHiddenSize.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.MODELINGBERTNOAPEXINVALIDHIDDENSIZE_ERROR


class UnrecognizedTransformedFeatureNameException(InvalidTransformArgumentException):
    """
    An exception related to UnrecognizedTransformedFeatureName.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.UNRECOGNIZEDTRANSFORMEDFEATURENAME_ERROR


class UnrecognizedRawFeatureAliasNameException(InvalidTransformArgumentException):
    """
    An exception related to UnrecognizedRawFeatureAliasName.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.UNRECOGNIZEDRAWFEATUREALIASNAME_ERROR


class InvalidTransformArgumentTypeException(BadTransformArgumentException):
    """
    An exception related to InvalidTransformArgumentType.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.INVALIDTRANSFORMARGUMENTTYPE_ERROR


class ModelingBertNoApexNotIntOrStrException(InvalidTransformArgumentTypeException):
    """
    An exception related to ModelingBertNoApexNotIntOrStr.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.MODELINGBERTNOAPEXNOTINTORSTR_ERROR


class NimbusMlTextTargetEncoderFeaturizerInvalidTypeException(InvalidTransformArgumentTypeException):
    """
    An exception related to NimbusMlTextTargetEncoderFeaturizerInvalidType.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.NIMBUSMLTEXTTARGETENCODERFEATURIZERINVALIDTYPE_ERROR


class NimbusMlTextTargetEncoderLearnerInvalidTypeException(InvalidTransformArgumentTypeException):
    """
    An exception related to NimbusMlTextTargetEncoderLearnerInvalidType.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.NIMBUSMLTEXTTARGETENCODERLEARNERINVALIDTYPE_ERROR


class MalformedTransformArgumentException(BadTransformArgumentException):
    """
    An exception related to MalformedTransformArgument.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.MALFORMEDTRANSFORMARGUMENT_ERROR


class EngineeredFeatureNamesNoTransformationsInJsonException(MalformedTransformArgumentException):
    """
    An exception related to EngineeredFeatureNamesNoTransformationsInJson.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.ENGINEEREDFEATURENAMESNOTRANSFORMATIONSINJSON_ERROR


class NotSupportedTransformArgumentException(BadTransformArgumentException):
    """
    An exception related to NotSupportedTransformArgument.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.NOTSUPPORTEDTRANSFORMARGUMENT_ERROR


class EngineeredFeatureNamesUnsupportedIndexException(NotSupportedTransformArgumentException):
    """
    An exception related to EngineeredFeatureNamesUnsupportedIndex.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.ENGINEEREDFEATURENAMESUNSUPPORTEDINDEX_ERROR


class EngineeredFeatureNamesNotSupportedFeatureTypeException(NotSupportedTransformArgumentException):
    """
    An exception related to EngineeredFeatureNamesNotSupportedFeatureType.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.ENGINEEREDFEATURENAMESNOTSUPPORTEDFEATURETYPE_ERROR


class PretrainedTextDnnTransformerFitUnsupportedTaskException(NotSupportedTransformArgumentException):
    """
    An exception related to PretrainedTextDnnTransformerFitUnsupportedTask.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.PRETRAINEDTEXTDNNTRANSFORMERFITUNSUPPORTEDTASK_ERROR


class PretrainedTextDnnTransformerConvertUnsupportedTaskException(NotSupportedTransformArgumentException):
    """
    An exception related to PretrainedTextDnnTransformerConvertUnsupportedTask.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.PRETRAINEDTEXTDNNTRANSFORMERCONVERTUNSUPPORTEDTASK_ERROR


class BlankOrEmptyTransformArgumentException(BadTransformArgumentException):
    """
    An exception related to BlankOrEmptyTransformArgument.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.BLANKOREMPTYTRANSFORMARGUMENT_ERROR


class EngineeredFeatureNamesEmptyJsonException(BlankOrEmptyTransformArgumentException):
    """
    An exception related to EngineeredFeatureNamesEmptyJson.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.ENGINEEREDFEATURENAMESEMPTYJSON_ERROR


class EngineeredFeatureNamesNoRawFeatureTypeException(BlankOrEmptyTransformArgumentException):
    """
    An exception related to EngineeredFeatureNamesNoRawFeatureType.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.ENGINEEREDFEATURENAMESNORAWFEATURETYPE_ERROR


class EngineeredFeatureNamesTransformerNamesNotFoundException(BlankOrEmptyTransformArgumentException):
    """
    An exception related to EngineeredFeatureNamesTransformerNamesNotFound.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.ENGINEEREDFEATURENAMESTRANSFORMERNAMESNOTFOUND_ERROR


class InvalidTransformDataException(TransformRuntimeException):
    """
    An exception related to InvalidTransformData.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.INVALIDTRANSFORMDATA_ERROR


class TransformDataShapeErrorException(InvalidTransformDataException):
    """
    An exception related to TransformDataShapeError.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.TRANSFORMDATASHAPE_ERROR


class DataTransformerInconsistentRowCountException(TransformDataShapeErrorException):
    """
    An exception related to DataTransformerInconsistentRowCount.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.DATATRANSFORMERINCONSISTENTROWCOUNT_ERROR


class TransformerRuntimeNotCalledException(TransformRuntimeException):
    """
    An exception related to TransformerRuntimeNotCalled.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.TRANSFORMERRUNTIMENOTCALLED_ERROR


class CatImputerRuntimeNotCalledException(TransformerRuntimeNotCalledException):
    """
    An exception related to CatImputerRuntimeNotCalled.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.CATIMPUTERRUNTIMENOTCALLED_ERROR


class CrossValidationTargetImputerRuntimeNotCalledException(TransformerRuntimeNotCalledException):
    """
    An exception related to CrossValidationTargetImputerRuntimeNotCalled.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.CROSSVALIDATIONTARGETIMPUTERRUNTIMENOTCALLED_ERROR


class BinTransformerRuntimeNotCalledException(TransformerRuntimeNotCalledException):
    """
    An exception related to BinTransformerRuntimeNotCalled.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    _error_code = ErrorCodes.BINTRANSFORMERRUNTIMENOTCALLED_ERROR
