# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""A collection of error strings used throughout the HyperDrive SDK."""


class HyperDriveErrorStrings:
    """A collection of error strings used throughout the HyperDrive SDK."""

    HYPERDRIVE_RUN_CREATION_FAILED = "Exception occurred while creating the HyperDrive run: [{err}]. " \
                                     "Please try again later."
    HYPERDRIVE_RUN_CANCELLATION_FAILED = "Exception occurred while cancelling HyperDrive run. " \
                                         "Please try again later."
    INVALID_COMPUTE_TARGET = "Automated hyperparameter tuning is not supported for types " \
                             "DatabricksCompute and local."
    INVALID_RUN_HOST = "The new run should have the same host as {type}"
    MISSING_CHOICE_VALUES = "Please specify an input for choice."
    INVALID_CONFIG_SETTING = "{obj} expects {condition}"
    UNEXPECTED_TYPE = "Expected type {exp} for {obj} but got {actual}"
    INVALID_KEY_IN_DICT = "Could not find {key} in {dict}"
    REHYDRATE_POLICY_NOT_FOUND = "Unknown policy {policy}."
    NOT_IMPLEMENTED = "{feature} is not implemented for HyperDrive run"
    REHYDRATE_UNKNOWN_SAMPLING = "Failed to rehydrate run due to unknown sampling method."
    DICT_VALIDATION_INVALID_ARGUMENT = "Invalid arguments received for {method} method"
    DISTRIBUTION_VALIDATION_FAILURE = "Failed to validate a parameter distribution due to {err}"
    RESUME_CHILD_RUNS_CONTAINS_DUPLICATE = "resume_child_runs cannot contain duplicate runs."
    FOUND_CHILD_RUN_NOT_IN_TERMINAL_STATE = "All resume_child_runs should be in a terminal state. " \
                                            "Found a run with state '{state}'."
    RESUME_CHILD_RUN_WITHOUT_PARENT_RUN = "Every run in resume_child_runs should have a parent run."
    RESUME_CHILD_RUNS_COME_FROM_TOO_MANY_PARENT_RUNS = "resume_child_runs should not come " \
                                                       "from more than {max_num} unique parents. " \
                                                       "{found} unique parents were found."
    WARM_START_RUNS_DONT_MATCH = "{obj} should be the same for all runs. {additional_info}"
