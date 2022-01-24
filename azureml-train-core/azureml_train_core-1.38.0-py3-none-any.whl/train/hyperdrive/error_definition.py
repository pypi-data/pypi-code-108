# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Error code definitions for HyperDrive SDK."""

from azureml._common._error_definition import error_decorator  # type: ignore
from azureml._common._error_definition.system_error import ClientError  # type: ignore
from azureml._common._error_definition.user_error import (  # type: ignore
    ArgumentBlankOrEmpty, ArgumentInvalid)
from azureml.train.hyperdrive.error_strings import HyperDriveErrorStrings


class HyperDriveTrainingError(ClientError):
    """Error code definition for HyperDriveTrainingError."""

    @property
    def message_format(self) -> str:
        """Error message for HyperDriveTrainingError."""
        return HyperDriveErrorStrings.HYPERDRIVE_RUN_CREATION_FAILED


class HyperDriveRunCancellationError(ClientError):
    """Error code definition for HyperDriveRunCancellationError."""

    @property
    def message_format(self) -> str:
        """Error message for HyperDriveRunCancellationError."""
        return HyperDriveErrorStrings.HYPERDRIVE_RUN_CANCELLATION_FAILED


@error_decorator(use_parent_error_code=True,
                 details_uri="https://docs.microsoft.com/en-us/python/api/azureml-train-core/"
                             "azureml.train.hyperdrive.hyperdriveconfig?view=azure-ml-py")
class InvalidComputeTarget(ArgumentInvalid):
    """Error code definition for InvalidComputeTarget."""

    @property
    def message_format(self) -> str:
        """Error message for InvalidComputeTarget."""
        return HyperDriveErrorStrings.INVALID_COMPUTE_TARGET


@error_decorator(use_parent_error_code=True,
                 details_uri="https://docs.microsoft.com/en-us/python/api/azureml-train-core/"
                             "azureml.train.hyperdrive.hyperdriveconfig?view=azure-ml-py")
class InvalidRunHost(ArgumentInvalid):
    """Error code definition for InvalidRunHost."""

    @property
    def message_format(self) -> str:
        """Error message for InvalidRunHost."""
        return HyperDriveErrorStrings.INVALID_RUN_HOST


@error_decorator(use_parent_error_code=True,
                 details_uri="https://docs.microsoft.com/en-us/python/api/azureml-train-core/"
                             "azureml.train.hyperdrive.hyperdriveconfig?view=azure-ml-py")
class MissingChoiceValues(ArgumentBlankOrEmpty):
    """Error code definition for MissingChoiceValues."""

    @property
    def message_format(self) -> str:
        """Error message for MissingChoiceValues."""
        return HyperDriveErrorStrings.MISSING_CHOICE_VALUES


@error_decorator(use_parent_error_code=True,
                 details_uri="https://docs.microsoft.com/en-us/python/api/azureml-train-core/"
                             "azureml.train.hyperdrive.hyperdriveconfig?view=azure-ml-py")
class InvalidConfigSetting(ArgumentInvalid):
    """Error code definition for InvalidConfigSetting."""

    @property
    def message_format(self) -> str:
        """Error message for InvalidConfigSetting."""
        return HyperDriveErrorStrings.INVALID_CONFIG_SETTING


@error_decorator(use_parent_error_code=True,
                 details_uri="https://docs.microsoft.com/en-us/python/api/azureml-train-core/"
                             "azureml.train.hyperdrive.hyperdriveconfig?view=azure-ml-py")
class InvalidType(ArgumentInvalid):
    """Error code definition for InvalidType."""

    @property
    def message_format(self) -> str:
        """Error message for InvalidType."""
        return HyperDriveErrorStrings.UNEXPECTED_TYPE


@error_decorator(use_parent_error_code=True,
                 details_uri="https://docs.microsoft.com/en-us/python/api/azureml-train-core/"
                             "azureml.train.hyperdrive.hyperdriveconfig?view=azure-ml-py")
class InvalidKeyInDict(ArgumentInvalid):
    """Error code definition for InvalidKeyInDict."""

    @property
    def message_format(self) -> str:
        """Error message for InvalidKeyInDict."""
        return HyperDriveErrorStrings.INVALID_KEY_IN_DICT


@error_decorator(use_parent_error_code=True,
                 details_uri="https://docs.microsoft.com/en-us/python/api/azureml-train-core/"
                             "azureml.train.hyperdrive.hyperdriveconfig?view=azure-ml-py")
class RehydratePolicyNotFound(ArgumentInvalid):
    """Error code definition for RehydratePolicyNotFound."""

    @property
    def message_format(self) -> str:
        """Error message for RehydratePolicyNotFound."""
        return HyperDriveErrorStrings.REHYDRATE_POLICY_NOT_FOUND


@error_decorator(use_parent_error_code=True,
                 details_uri="https://docs.microsoft.com/en-us/python/api/azureml-train-core/"
                             "azureml.train.hyperdrive.hyperdriveconfig?view=azure-ml-py")
class HyperDriveNotImplemented(ArgumentInvalid):
    """Error code definition for HyperDriveNotImplemented."""

    @property
    def message_format(self) -> str:
        """Error message for HyperDriveNotImplemented."""
        return HyperDriveErrorStrings.NOT_IMPLEMENTED


@error_decorator(use_parent_error_code=True,
                 details_uri="https://docs.microsoft.com/en-us/python/api/azureml-train-core/"
                             "azureml.train.hyperdrive.hyperdriveconfig?view=azure-ml-py")
class RehydrateUnknownSampling(ArgumentInvalid):
    """Error code definition for RehydrateUnknownSampling."""

    @property
    def message_format(self) -> str:
        """Error message for RehydrateUnknownSampling."""
        return HyperDriveErrorStrings.REHYDRATE_UNKNOWN_SAMPLING


@error_decorator(use_parent_error_code=True,
                 details_uri="https://docs.microsoft.com/en-us/python/api/azureml-train-core/"
                             "azureml.train.hyperdrive.hyperdriveconfig?view=azure-ml-py")
class DictValidationInvalidArgument(ArgumentInvalid):
    """Error code definition for DictValidationInvalidArgument."""

    @property
    def message_format(self) -> str:
        """Error message for DictValidationInvalidArgument."""
        return HyperDriveErrorStrings.DICT_VALIDATION_INVALID_ARGUMENT


@error_decorator(use_parent_error_code=True,
                 details_uri="https://docs.microsoft.com/en-us/python/api/azureml-train-core/"
                             "azureml.train.hyperdrive.hyperdriveconfig?view=azure-ml-py")
class DistributionValidationFailure(ArgumentInvalid):
    """Error code definition for DistributionValidationFailure."""

    @property
    def message_format(self) -> str:
        """Error message for DistributionValidationFailure."""
        return HyperDriveErrorStrings.DISTRIBUTION_VALIDATION_FAILURE


@error_decorator(use_parent_error_code=True,
                 details_uri="https://docs.microsoft.com/en-us/python/api/azureml-train-core/"
                             "azureml.train.hyperdrive.hyperdriveconfig?view=azure-ml-py")
class ResumeChildRunsContainsDuplicate(ArgumentInvalid):
    """Error code definition for ResumeChildRunsContainsDuplicate."""

    @property
    def message_format(self) -> str:
        """Error message for ResumeChildRunsContainsDuplicate."""
        return HyperDriveErrorStrings.RESUME_CHILD_RUNS_CONTAINS_DUPLICATE


@error_decorator(use_parent_error_code=True,
                 details_uri="https://docs.microsoft.com/en-us/python/api/azureml-train-core/"
                             "azureml.train.hyperdrive.hyperdriveconfig?view=azure-ml-py")
class ResumeChildRunsNotInTerminalState(ArgumentInvalid):
    """Error code definition for ResumeChildRunsNotInTerminalState."""

    @property
    def message_format(self) -> str:
        """Error message for ResumeChildRunsNotInTerminalState."""
        return HyperDriveErrorStrings.FOUND_CHILD_RUN_NOT_IN_TERMINAL_STATE


@error_decorator(use_parent_error_code=True,
                 details_uri="https://docs.microsoft.com/en-us/python/api/azureml-train-core/"
                             "azureml.train.hyperdrive.hyperdriveconfig?view=azure-ml-py")
class ResumeChildRunsWithoutParentRun(ArgumentInvalid):
    """Error code definition for ResumeChildRunsWithoutParentRun."""

    @property
    def message_format(self) -> str:
        """Error message for ResumeChildRunsWithoutParentRun."""
        return HyperDriveErrorStrings.RESUME_CHILD_RUN_WITHOUT_PARENT_RUN


@error_decorator(use_parent_error_code=True,
                 details_uri="https://docs.microsoft.com/en-us/python/api/azureml-train-core/"
                             "azureml.train.hyperdrive.hyperdriveconfig?view=azure-ml-py")
class ResumeChildRunsFromTooManyParentRuns(ArgumentInvalid):
    """Error code definition for ResumeChildRunsFromTooManyParentRuns."""

    @property
    def message_format(self) -> str:
        """Error message for ResumeChildRunsFromTooManyParentRuns."""
        return HyperDriveErrorStrings.RESUME_CHILD_RUNS_COME_FROM_TOO_MANY_PARENT_RUNS


@error_decorator(use_parent_error_code=True,
                 details_uri="https://docs.microsoft.com/en-us/python/api/azureml-train-core/"
                             "azureml.train.hyperdrive.hyperdriveconfig?view=azure-ml-py")
class WarmStartRunsDontMatch(ArgumentInvalid):
    """Error code definition for WarmStartRunsDontMatch."""

    @property
    def message_format(self) -> str:
        """Error message for WarmStartRunsDontMatch."""
        return HyperDriveErrorStrings.WARM_START_RUNS_DONT_MATCH
