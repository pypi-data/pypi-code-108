# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml._common._error_definition.user_error import (
    ArgumentBlankOrEmpty, ArgumentInvalid, ArgumentMismatch, ArgumentOutOfRange,
    Conflict, InvalidDimension, MalformedArgument, MissingData, NotFound,
    InvalidData)
from azureml.interpret.common._errors.error_strings import ErrorStrings


class ClassNumberMismatch(ArgumentMismatch):
    """ClassNumberMismatch error."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.CLASS_NUMBER_MISMATCH


class DeserializationFailure(MalformedArgument):
    """DeserializationFailure error."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.DESERIALIZATION_FAILURE


class DirectoryAlreadyExists(Conflict):
    """DirectoryAlreadyExists error."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.DIRECTORY_ALREADY_EXISTS


class EvalDataMismatch(ArgumentMismatch):
    """EvalDataMismatch error."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.EVAL_DATA_SHAPE_MISMATCH


class EvalDatasetMissing(MissingData):
    """EvalDatasetMissing error."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.EVAL_DATASET_MISSING


class ExperimentMissingIdAndName(NotFound):
    """ExperimentMissingIdAndName error."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.EXPERIMENT_MISSING_ID_AND_NAME


class ExplainBeforeUploadConflict(Conflict):
    """ExplainBeforeUploadConflict error."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.EXPLAIN_BEFORE_UPLOAD_CONFLICT


class ExplanationFilterNotFound(NotFound):
    """ExplanationFilterNotFound error."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.EXPLANATION_FILTER_NOT_FOUND


class ExplanationFiltersNotFound(NotFound):
    """ExplanationFiltersNotFound error."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.EXPLANATION_FILTERS_NOT_FOUND


class ExplanationNotFound(NotFound):
    """ExplanationNotFound error."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.EXPLANATION_NOT_FOUND


class InitDatasetMissing(MissingData):
    """InitDatasetMissing error."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.INIT_DATASET_MISSING


class InvalidExplanationTypes(ArgumentInvalid):
    """InvalidExplanationTypes error."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.EXPLANATION_TYPES_INVALID


class InvalidYTrueDimension(InvalidDimension):
    """InvalidYTrueDimension error."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.INVALID_Y_TRUE_DIMENSION


class MissingFeatureMapGettingRaw(ArgumentBlankOrEmpty):
    """MissingFeatureMapGettingRaw error."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.MISSING_FEATURE_MAP_GETTING_RAW


class ModelNotKeras(ArgumentInvalid):
    """ModelNotKeras error."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.MODEL_NOT_KERAS


class ModelNotSerializable(ArgumentInvalid):
    """ModelNotSerializable error."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.MODEL_NOT_SERIALIZABLE


class OptionalDependencyMissing(NotFound):
    """OptionalDependencyMissing error."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.OPTIONAL_DEPENDENCY_MISSING


class RawTransformArgumentMismatch(ArgumentMismatch):
    """RawTransformArgumentMismatch error."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.RAW_TRANSFORM_ARGUMENT_MISMATCH


class SampleLimitExceeded(ArgumentOutOfRange):
    """SampleLimitExceeded error."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.SAMPLE_LIMIT_EXCEEDED


class InvalidExplanationDataType(InvalidData):
    """InvalidExplanationDataType error."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.INVALID_EXPLANATION_DATA_TYPE
