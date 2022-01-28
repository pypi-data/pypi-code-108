# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2021 Comet ML INC
#  This file can not be copied and/or distributed without
#  the express permission of Comet ML Inc.
# *******************************************************

# Don't import comet_ml items here to avoid import cycles

MSG_FORMAT = "COMET %(levelname)s: %(message)s"

FILE_MSG_FORMAT = "[%(process)d-%(processName)s:%(thread)d] %(relativeCreated)d COMET %(levelname)s [%(filename)s:%(lineno)d]: %(message)s"

GO_TO_DOCS_MSG = " \nFor more details, please refer to: https://www.comet.ml/docs/python-sdk/warnings-errors/"

INTERNET_CONNECTION_ERROR = (
    "Failed to establish a connection to Comet server. Please check your internet connection. "
    "Your experiment would not be logged" + GO_TO_DOCS_MSG
)

INVALID_WORKSPACE_NAME = "Workspace %s doesn't exist."

INVALID_PROJECT_NAME = "project_name argument can't be empty."

INVALID_API_KEY = (
    "The given API key %s is invalid, please check it against the dashboard. "
    "Your experiment would not be logged" + GO_TO_DOCS_MSG
)

WAITING_DATA_UPLOADED = "Uploading metrics, params, and assets to Comet before program termination (may take several seconds)"

INVALID_REST_API_KEY = (
    "The given REST API key %s is invalid, please check it against the dashboard. "
)

METRIC_ARRAY_WARNING = (
    "Cannot safely convert %r object to a scalar value, using its string"
    " representation for logging."
)

PARSING_ERR_MSG = """We failed to parse your parameter configuration file.

Type casting will be disabled for this run, please fix your configuration file.
"""

CASTING_ERROR_MESSAGE = """Couldn't cast parameter %r, returning raw value instead.
Please report it to comet.ml and use `.raw(%r)` instead of `[%r]` in the meantime."""

LOG_ASSET_FOLDER_ERROR = (
    "We failed to read directory %s for uploading.\n"
    "Please double-check the file path, permissions, and that it is a directory"
)

LOG_ASSET_FOLDER_EMPTY = (
    "Directory %s is empty; no files were uploaded.\n"
    "Please double-check the directory path and the recursive parameter"
)

UPLOAD_FILE_OS_ERROR = (
    "We failed to read file %s for uploading.\n"
    "Please double-check the file path and permissions"
)

UPLOAD_ASSET_TOO_BIG = "Asset %s is bigger than the upload limit, %s > %s"

LOG_IMAGE_TOO_BIG = "Image %s is bigger than the upload limit, %s > %s"

LOG_FIGURE_TOO_BIG = "Figure number %d is bigger than the upload limit, %s > %s"

LOG_AUDIO_TOO_BIG = "Audio %s is bigger than the upload limit, %s > %s"

NATIVE_STD_WRAPPER_NOT_AVAILABLE = (
    "Native output logging mode is not available, fallbacking on basic output logging"
)

UNKOWN_STD_WRAPPER_SPEC = (
    "Unknown output logging mode: %s, fallbacking on basic output logging"
)

EXPERIMENT_LIVE = "Experiment is live on comet.ml %s\n"

OFFLINE_EXPERIMENT_END = "To upload this offline experiment, run:\n    comet upload %s"

OFFLINE_SENDER_STARTS = "Starting the upload of the experiment"

OFFLINE_SENDER_ENDS = "The offline experiment has been uploaded on comet.ml %s\n"

OFFLINE_SENDER_ENDS_PROCESSING = "Offline Experiment will now be processed---may take some time to appear on the Comet dashboard."

OFFLINE_DATA_DIR_DEFAULT_WARNING = (
    "Using %r path as offline directory. Pass 'offline_directory' parameter into constructor "
    "or set the 'COMET_OFFLINE_DIRECTORY' environment variable to manually choose where to store offline "
    "experiment archives."
)

OFFLINE_DATA_DIR_FAILED_WARNING = (
    "Failed to use offline data directory %r, the experiment will be saved in the temporary directory %r instead.\n"
    "Reason: %s"
)

OFFLINE_UPLOADING_EXPERIMENT_FILE_PROMPT = "Attempting to upload %r..."

OFFLINE_SUCCESS_UPLOADED_EXPERIMENTS = "Number of uploaded experiments: %d"

OFFLINE_FAILED_UPLOADED_EXPERIMENTS = "Number of failed experiment uploads: %d"

OFFLINE_UPLOAD_FAILED_UNEXPECTED_ERROR = "Upload failed for %r; unknown error"

OFFLINE_UPLOAD_FAILED_INVALID_API_KEY = (
    "Upload failed because of invalid Comet API key; please set COMET_API_KEY"
)

ADD_TAGS_ERROR = "Failed to add tag(s) %s to the experiment\n"

ADD_SYMLINK_ERROR = "Failed to create symlink to project:%s for experiment\n"

OFFLINE_EXPERIMENT_INVALID_WS_MSG = "An invalid message has been detected"

OFFLINE_EXPERIMENT_INVALID_UPLOAD_MSG = "An invalid upload message has been detected"

OFFLINE_EXPERIMENT_INVALID_PARAMETER_MSG = (
    "An invalid parameter message has been detected"
)

OFFLINE_EXPERIMENT_ALREADY_UPLOADED = "Upload failed for %r; experiment was already uploaded, you can re-upload it by using the --force-reupload flag"

OFFLINE_AT_LEAST_ONE_EXPERIMENT_UPLOAD_FAILED = "At least one experiment failed to upload, check COMET ERROR messages above for more information."

OFFLINE_EXPERIMENT_CREATION_WORKSPACE_OVERRIDDEN_PARAMETER = "Using workspace '%(creation_workspace)s', set by parameter rather than workspace '%(metadata_workspace)s' set in the Offline Experiment Archive"

OFFLINE_EXPERIMENT_CREATION_PROJECT_NAME_OVERRIDDEN_PARAMETER = "Using project_name '%(creation_project_name)s', set by parameter rather than project_name '%(metadata_project_name)s' set in the Offline Experiment Archive"

OFFLINE_EXPERIMENT_CREATION_WORKSPACE_OVERRIDDEN_CONFIG = "Using workspace '%(creation_workspace)s', set in configuration rather than workspace '%(metadata_workspace)s' set in the Offline Experiment Archive"

OFFLINE_EXPERIMENT_CREATION_PROJECT_NAME_OVERRIDDEN_CONFIG = "Using project_name '%(creation_project_name)s', set in configuration rather than project_name '%(metadata_project_name)s' set in the Offline Experiment Archive"

EXPERIMENT_INVALID_STEP = "Passed step value %r is not a number, ignoring it"

EXPERIMENT_INVALID_EPOCH = "Passed epoch value %r is not a number, ignoring it"

EXPERIMENT_INITIAL_DATA_LOGGER_INCOMPLETE = (
    "Not all initial data has been logged for experiment %s, call Experiment.end() "
    "to ensure that all data to have been logged"
)

EXPERIMENT_GET_PARAMETER_SHORT_NAME_DEPRECATION = (
    "Getting a parameter without its full name is deprecated and will be removed in the future, "
    "potential full-names for the '%s' parameter are %s"
)

STREAMER_WAIT_FOR_FINISH_FAILED = (
    "Comet failed to send all the data back (%d messages and %d uploads)"
)

STREAMER_CLOSED_PUT_MESSAGE_FAILED = (
    "Attempting to put message into closed streamer: message ignored! "
    "You need to call Experiment.end() to have everything logged properly."
)

STREAMER_FAILED_TO_PROCESS_ALL_MESSAGES = (
    "Failed to send all messages, metrics and output will likely be incomplete."
)

REGISTER_RPC_FAILED = "Failed to register callback named %r"

WS_SSL_ERROR_MSG = (
    "There's seem to be an issue with your system's SSL certificate bundle."
    "This is likely a system-wide issue that is not related to Comet."
    "Please see more information here:"
    "https://www.comet.ml/docs/python-sdk/warnings-errors/"
)

SEND_NOTIFICATION_FAILED = (
    "Error sending a notification, make sure you have opted-in for notifications"
)

GET_CALLBACK_FAILURE = "Failure to add Comet SDK callback to %s, the run will likely miss parameters and/out metrics"

WS_ON_OPEN_MSG = "WS Socket connection open"

WS_ON_CLOSE_MSG = "WS connection closed %r"

COMET_DISABLED_AUTO_LOGGING_MSG = "COMET_DISABLE_AUTO_LOGGING is 1; ignoring '%s'"

LOG_DATASET_ERROR = "Failed to create dataset hash"

OS_PACKAGE_MSG_SENDING_ERROR = "Error sending os_packages message, got %d %r"

MODEL_GRAPH_MSG_SENDING_ERROR = "Error sending model graph message, got %d %r"

CLOUD_DETAILS_MSG_SENDING_ERROR = "Error sending cloud details messages, got %d %r"

OPTIMIZER_KWARGS_CONSTRUCTOR_DEPRACETED = "Passing Experiment through Optimizer constructor is deprecated; pass them to Optimizer.get_experiments or Optimizer.next"

BACKEND_VERSION_CHECK_ERROR = "Failed to check backend version at URL: %r"

INVALID_CONFIG_MINIMAL_BACKEND_VERSION = "Invalid configured `comet.rest_v2_minimal_backend_version` value %r, skipping backend version check"

MLFLOW_NESTED_RUN_UNSUPPORTED = "MLFlow Nested Runs are not tracked in Comet.ml SDK."

MLFLOW_OFFLINE_EXPERIMENT_FALLBACK = "No Comet API Key was found, creating an OfflineExperiment. Set up your API Key to get the full Comet experience https://www.comet.ml/docs/python-sdk/advanced/#python-configuration"

MLFLOW_RESUMED_RUN = "Resumed MLFlow run are tracked as new Comet.ml Experiments"

ONLINE_EXPERIMENT_THROTTLED = "Experiment has been throttled. Some data (like experiment metrics) might be missing. Mission-critical data, like Artifacts, are never throttled."

TF_KERAS_FALLBACK_FAILED = (
    "Keras is not available; attempted to fallback to tensorflow.keras but still failed"
)

TF_KERAS_CALLBACK_WARNING_CLOSED_EXPERIMENT = "A Keras callback is trying to report to a un-alive experiment object (it was either ended or the creation failed) from the %s callback method, data will not be logged."

CONFUSION_MATRIX_ERROR = "Error creating confusion matrix: %s; ignoring"

CONFUSION_MATRIX_GENERAL_ERROR = "Error logging confusion matrix; ignoring"

CONFUSION_MATRIX_ERROR_WRONG_LENGTH = (
    "y_true and y_predicted should have the same lengths (%d != %d)"
)

CONFUSION_MATRIX_ERROR_RESULTING_LENGTH = (
    "Resulting len(y_true) != len(y_predicted) (%s != %s)"
)

CONFUSION_MATRIX_ERROR_MUST_GIVE_BOTH = (
    "if you give y_true OR y_predicted you must give both"
)
CODECARBON_NOT_INSTALLED = "codecarbon package not installed; skipping co2 tracking"

CODECARBON_START_FAILED = "Failed to set-up CO2 logger"

CODECARBON_STOP_FAILED = "Failed to shutdown the CO2Tracker properly"

CODECARBON_DIR_CREATION_FAILED = "Failed to create the temporary CO2 tracker directory %r; skipping CO2 tracking; error %r"

CONFUSION_MATRIX_INDEX_TO_EXAMPLE_ERROR = (
    "%r failed for index %s; example not generated"
)
CONFUSION_MATRIX_EXAMPLE_NONE = "%r returned None for index %s; example not generated"

CONFUSION_MATRIX_EXAMPLE_DICT_INVALID_FORMAT = "%r returned an invalid dict for index %s, must match {'sample': ..., 'assetId': ...}"

CONFUSION_MATRIX_EXAMPLE_INVALID_TYPE = "%r returned invalid type %r at index %s, must return an int, string, URL, or {'sample': string, 'assetId': string}"

MISSING_PANDAS_LOG_DATAFRAME = "pandas is required to log a dataframe; ignoring"

MISSING_PANDAS_PROFILING = "pandas_profiling is required to log profile; ignoring"

NOT_PANDAS_DATAFRAME = "dataframe must be a pandas DataFrame; ignoring"

DATAFRAME_PROFILE_ERROR = "unable to profile dataframe; ignoring"

LOG_CODE_CALLER_NOT_FOUND = "unable to find caller source code; ignoring"

LOG_CODE_CALLER_JUPYTER = (
    "unable to find caller source code in a jupyter notebook; ignoring"
)

LOG_CODE_FILE_NAME_FOLDER_MUTUALLY_EXCLUSIVE = "Experiment.log_code either only one of code, file_name or folder, not several; ignoring"

# LOG_CLOUD_POINTS_3D

INVALID_CLOUD_POINTS_3D = "Invalid 3d points list: %r; ignoring"

INVALID_SINGLE_CLOUD_POINT_3D_LENGTH = "Invalid single 3d point length: %r, it should be a list or equivalent of size 3 minimum; ignoring"

INVALID_SINGLE_CLOUD_POINT_3D = (
    "Invalid single 3d point: %r, it should be a list or equivalent; ignoring"
)

INVALID_BOUNDING_BOX_3D = (
    "Invalid box %r, it should be a dict in the documented format; ignoring"
)

INVALID_BOUNDING_BOXES_3D = "Invalid list of boxes %r, it should be a list of dict in the documented format; ignoring it"

LOG_CLOUD_POINTS_3D_NO_VALID = "No valid points or valid boxes logged; ignoring"

SET_CODE_FILENAME_DEPRECATED = "Experiment.set_code(filename=...) is deprecated, use Experiment.log_code(file_name=...) instead"

SET_CODE_CODE_DEPRECATED = "Experiment.set_code(code=...) is deprecated, use Experiment.log_code(code=..., code_name=...) instead"

LOG_CODE_MISSING_CODE_NAME = "code_name is mandatory when passing in `code`; ignoring"

LOG_PARAMS_EMPTY_MAPPING = "Empty mapping given to log_params(%r); ignoring"

LOG_PARAMS_EMPTY_CONVERTED_MAPPING = (
    "%r passed to log_params converted to an empty maping; ignoring"
)

API_KEY_IS_NOT_SET = "Comet API key is not set. You'll have to provide it explictly to experiments and API"

API_KEY_IS_VALID = "Comet API key is valid"

API_KEY_IS_INVALID = (
    "Invalid Comet API key for %s\n"
    + "You will not be able to create online Experiments\n"
    + "Please see https://www.comet.ml/docs/command-line/#comet-check for more information.\n"
    + "Use: comet_ml.init() to try again"
)

API_KEY_CHECK_FAILED = "Unable to verify Comet API key at this time"

JUPYTER_NEEDS_END = "As you are running in a Jupyter environment, you will need to call `experiment.end()` when finished to ensure all metrics and code are logged before exiting."

ARTIFACT_VERSION_CREATED_WITH_PREVIOUS = (
    "Artifact %r version %s created (previous was: %s)"
)

ARTIFACT_VERSION_CREATED_WITHOUT_PREVIOUS = "Artifact %r version %s created"

GET_ARTIFACT_WORKSPACE_GIVEN_TWICE = "Workspace was given both explicitly %r and as part of the fully-qualified artifact name %r, using the explicit value"

GET_ARTIFACT_VERSION_OR_ALIAS_GIVEN_TWICE = "Version_or_alias was given both explicitly %r and as part of the fully-qualified artifact name %r, using the explicit value"

ARTIFACT_DOWNLOAD_FILE_OVERWRITTEN = (
    "File %r has been overwritten by asset %s of artifact version %s"
)

ARTIFACT_DOWNLOAD_FILE_PRESERVED = 'File %r is different from asset %s of artifact version %s, but was kept because overwrite_strategy="PRESERVE" was set'

ARTIFACT_UPLOAD_STARTED = "Artifact '%s/%s:%s' has started uploading asynchronously"

ARTIFACT_UPLOAD_FINISHED = "Artifact '%s/%s:%s' has been fully uploaded successfully"

ARTIFACT_ASSET_UPLOAD_FAILED = "Asset %r of artifact '%s/%s:%s' upload failed"

ARTIFACT_PREVIEW_FEATURE_FLAG = (
    "Artifact is currently a preview feature, contact us to get access to it."
)

LOG_ARTIFACT_IN_PROGESS_MESSAGE = (
    "Still scheduling the upload of %d assets, remaining size %s"
)

FILE_UPLOADS_PROMPT = (
    "Waiting for completion of the file uploads (may take several seconds)"
)

FILE_UPLOAD_MANAGER_MONITOR_FIRST_MESSAGE = (
    "Still uploading %d file(s), remaining %s/%s"
)

FILE_UPLOAD_MANAGER_MONITOR_WAITING_BACKEND_ANSWER = (
    "All files uploaded, waiting for confirmation they have been all received"
)

FILE_UPLOAD_MANAGER_MONITOR_PROGRESSION = (
    "Still uploading %d file(s), remaining %s/%s, Throughput %s/s, ETA ~%ss"
)

FILE_UPLOAD_MANAGER_MONITOR_PROGRESSION_UNKOWN_ETA = (
    "Still uploading %d file(s), remaining %s/%s, Throughput %s/s, ETA unknown"
)

ARTIFACT_DOWNLOAD_START_MESSAGE = (
    "Artifact '%s/%s:%s' download has been started asynchronously"
)

ARTIFACT_DOWNLOAD_FINISHED = "Artifact '%s/%s:%s' has been successfully downloaded"

ARTIFACT_ASSET_DOWNLOAD_FAILED = "Asset %r of the artifact '%s/%s:%s' download failed"

FILE_DOWNLOAD_MANAGER_COMPLETED = "All files downloaded"

FILE_DOWNLOAD_MANAGER_MONITOR_FIRST_MESSAGE = (
    "Still downloading %d file(s), remaining %s/%s"
)

FILE_DOWNLOAD_MANAGER_MONITOR_PROGRESSION_UNKNOWN_ETA = (
    "Still downloading %d file(s), remaining %s/%s, Throughput %s/s, ETA unknown"
)

FILE_DOWNLOAD_MANAGER_MONITOR_PROGRESSION = (
    "Still downloading %d file(s), remaining %s/%s, Throughput %s/s, ETA ~%ss"
)

INITIAL_DATA_LOGGER_FLUSHING_EXPERIMENT_INTERRUPTED_BY_USER = "Experiment was interrupted by user while waiting for the initial data logger to be flushed."

INITIAL_DATA_LOGGER_FLUSHING_FAILED = (
    "Unexpected failure while waiting for the initial data logger to be flushed."
)

LOG_GIT_METADATA_ERROR = "Failed to log git metadata"

LOG_GIT_PATCH_ERROR = "Failed to log git patch"

GIT_REPO_NOT_FOUND = "Couldn't find a Git repository in %r nor in any parent directory. You can override where Comet is looking for a Git Patch by setting the configuration `COMET_GIT_DIRECTORY`"

GIT_LOGGING_ERROR = "Error logging git-related information"

REPORTING_ERROR = "Failing to report %s"

OFFLINE_EXPERIMENT_NAME_ACCESS = "Experiment Name is generated at upload time for Offline Experiments unless set explicitly with Experiment.set_name"

IN_COLAB_WITHOUT_DRIVE_DIRECTORY1 = (
    "running in Google Colab, but can't find mounted drive. Using HOME instead"
)
IN_COLAB_WITHOUT_DRIVE_DIRECTORY2 = (
    "if drive is mounted, set COMET_CONFIG to save config there"
)

START_PARAMETERS_DONT_MATCH_EXISTING_EXPERIMENT = "An experiment already exists %r but all its parameters don't match comet_ml.start, closing it and recreating one"

START_RUNNING_EXPERIMENT_IGNORED_PARAMETER = "Parameter '%s' with value '%s' was ignored while checking if Experiment instance %r matched the start parameters"

LOG_COLAB_NOTEBOOK_ERROR = "Couldn't retrieve Google Colab notebook content"

CONVERT_TABLE_INVALID_FORMAT = "Tabular filename must end with '.tsv' or '.csv', not %r"

CONVERT_DATAFRAME_INVALID_FORMAT = (
    "Tabular dataframe filename must end with 'json', 'csv', 'md', or 'html', not %r"
)

LOG_TABLE_NONE_VALUES = "Either tabular_data or a valid file-path are required when calling log_table; ignoring"

LOG_TABLE_FILENAME_AND_HEADERS = (
    "Headers are ignored when calling log_table with a filename"
)

DATAFRAME_CONVERSION_ERROR = "dataframe conversion to %r failed; ignored"

METRIC_NONE_WARNING = "The given value of the metric %s was None; ignoring"

LATE_IMPORT_DEGRADED_MODE = "Comet has disabled auto-logging functionality as it has been imported after the following ML modules: %s. Metrics and hyperparameters can still be logged using comet_ml.log_metrics() and comet_ml.log_parameters()"
