# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Custom errors for model analysis."""

# For detailed info on error handling design, see spec:
# https://msdata.visualstudio.com/Vienna/_git/specs?path=%2FErrorHandling%2Ferror-handling-in-azureml-sdk.md
# For error codes see:
# <root>\src\azureml-core\azureml\_common\_error_response\_generate_constants\error_codes.json


class ErrorStrings:
    """
    All un-formatted error strings that accompany the common error codes for azureml-responsibleai.

    Dev note: Please keep this list sorted on keys.
    """

    # region common

    ARGUMENT_INVALID_TYPE = "Argument {arg_name} has invalid type {type}. Valid types: {type_list}."
    ARTIFACT_MISSING_FIELD = "Artifact {artifact} missing required field: {field}."
    ASSET_NOT_FOUND = "No {asset_type} asset found with attributes {attributes}."
    DUPLICATE_TARGET_NAME = "Column for y also named in {arg_name}"
    INVALID_DATASET_TYPE = "Datasets must be AzureML Dataset objects or Dataset IDs, received type {actual_type}."
    INVALID_EXPERIMENT_TYPE = "Experiments must be AzureML Experiment objects or Experiment names, " \
                              "received type {actual_type}."
    INVALID_MODEL_TYPE = "Models must be AzureML Model objects or Model IDs, received type {actual_type}."
    INVALID_RAI_TOOL = "RAI tool {tool_name} is not a known tool."
    MISSING_DATASTORE = "Must supply a datastore (may use workspace.get_default_datastore().name)"
    SCHEMA_VERSION_NOT_SUPPORTED = "Schema version {version} is not supported for artifact {artifact}"

    # endregion common

    # region model-analysis

    ARTIFACT_SIZE_LIMIT_EXCEEDED = "Artifact size of {actual} bytes exceeded the {limit} bytes limit."
    ANALYSIS_INIT_FAILED = "The model analysis initialization has failed. " \
                           "You can find the root error logs in the portal. {portal_url}"
    ANALYSIS_INIT_NOT_COMPLETED = "The model analysis initialization is still in progress, this process needs to " \
                                  "finish before continuing on. Progress can be tracked in the portal. {portal_url}"
    ANALYSIS_INIT_NOT_EXECUTED = "The model analysis initialization has not been submitted yet. " \
                                 "You can submit that by passing this config to the experiment.submit such as\n " \
                                 "'experiment.submit(ModelAnalysisConfig(**settings))'"

    DATASET_TOO_LARGE = "Dataset '{dataset_name}' contains {actual_count} rows, which is greater " \
                        "than the limit of {limit_count} rows. The '{length_arg_name}' " \
                        "argument can raise this limit, but performance may be affected."
    DUPLICATE_ID = "Found multiple items of {item_type} with id {id}"

    MISMATCHED_EXPERIMENT_NAME = "Mismatched experiment name. Expected '{expected}' but got '{actual}'"
    MISMATCHED_WORKSPACE_NAME = "Mismatched workpace name. Expected '{expected}' but got '{actual}'"

    UNEXPECTED_OBJECT_TYPE = "Loaded object of type {actual} but expected {expected}"
    SUBSAMPLE_ERROR = "Failed to generate subsample of the data."

    # endregion model-analysis

    # region fairness

    DASHBOARD_DOWNLOAD_ERROR = "{full_message}"

    DASHBOARD_VALIDATION = "{full_message}"

    # endregion fairness

    # region interpret

    INVALID_ENUM_ELEMENT = "The value {value} does not exist in the enum {enum_name}."

    # endregion interpret
