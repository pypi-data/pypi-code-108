# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml._common._error_definition.user_error import (
    ArgumentBlankOrEmpty, ArgumentInvalid, DuplicateArgument, UserError)
from azureml._common._error_definition.system_error import SystemError
from azureml.responsibleai.common._errors.error_strings import ErrorStrings


# region common

class ArgumentInvalidTypeError(ArgumentInvalid):
    """The supplied argument is not of the correct type."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.ARGUMENT_INVALID_TYPE


class ArtifactMissingFieldError(UserError):
    """The insights artifact was missing a required field."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.ARTIFACT_MISSING_FIELD


class AssetNotFoundError(UserError):
    """Asset was not found."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.ASSET_NOT_FOUND


class DuplicateTargetNameError(DuplicateArgument):
    """The y_column_name appears in another list."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.DUPLICATE_TARGET_NAME


class InvalidDatasetTypeError(ArgumentInvalid):
    """Dataset type is invalid."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.INVALID_DATASET_TYPE


class InvalidExperimentTypeError(ArgumentInvalid):
    """Experiment type is invalid."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.INVALID_EXPERIMENT_TYPE


class InvalidModelTypeError(ArgumentInvalid):
    """Model type is invalid."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.INVALID_MODEL_TYPE


class InvalidRAIToolError(ArgumentInvalid):
    """Invalid RAI tool was passed."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.INVALID_RAI_TOOL


class MissingDatastoreError(ArgumentBlankOrEmpty):
    """The user has not supplied a datastore."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.MISSING_DATASTORE


class SchemaVersionNotSupportedError(ArgumentInvalid):
    """Schema version not supported."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.SCHEMA_VERSION_NOT_SUPPORTED


# endregion common


# region model-analysis

class ArtifactSizeLimitExceededError(UserError):
    """Artifact file size was too large."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.ARTIFACT_SIZE_LIMIT_EXCEEDED


class AnalysisInitFailedUserError(UserError):
    """Model analysis initialization failed due to a user error."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.ANALYSIS_INIT_FAILED


class AnalysisInitFailedSystemError(SystemError):
    """Model analysis initialization failed due to a system error."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.ANALYSIS_INIT_FAILED


class AnalysisInitNotCompletedError(UserError):
    """Model analysis initialization is still in progress."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.ANALYSIS_INIT_NOT_COMPLETED


class AnalysisInitNotExecutedError(UserError):
    """Model analysis not yet initialized."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.ANALYSIS_INIT_NOT_EXECUTED


class DatasetTooLargeError(UserError):
    """User passed a dataset which exceeds our performance limits."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.DATASET_TOO_LARGE


class DuplicateItemFoundError(SystemError):
    """Somehow have found two items with same GUID."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.DUPLICATE_ID


class MismatchedExperimentName(UserError):
    """Did not get submitted to expected experiment."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.MISMATCHED_EXPERIMENT_NAME


class MismatchedWorkspaceName(UserError):
    """Did not get submitted to expected workspace."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.MISMATCHED_WORKSPACE_NAME


class UnexpectedObjectType(SystemError):
    """Deserialised file did not return expected type of object."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.UNEXPECTED_OBJECT_TYPE


class SubsamplingError(SystemError):
    """Errors when taking a subsample of the data."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.SUBSAMPLE_ERROR

# endregion model-analysis


# region fairness

class DashboardDownloadError(SystemError):
    """Error downloading a dashboard."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.DASHBOARD_DOWNLOAD_ERROR


class DashboardValidationError(UserError):
    """Error in dashboard validation."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.DASHBOARD_VALIDATION

# endregion fairness


# region interpret

class InvalidEnumElementError(ArgumentInvalid):
    """String is not in the enum."""
    @property
    def message_format(self) -> str:
        return ErrorStrings.INVALID_ENUM_ELEMENT

# endregion interpret
