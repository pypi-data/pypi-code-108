from typing import List
from typing import Set

from tecton.fco import Fco
from tecton.tecton_errors import TectonInternalError
from tecton.tecton_errors import TectonValidationError

# Generic
INTERNAL_ERROR = lambda message: TectonInternalError(
    f"We seem to have encountered an error. Please contact support for assistance. Error details: {message}"
)
MDS_INACCESSIBLE = lambda host_port: TectonInternalError(
    f"Failed to connect to Tecton cluster at {host_port}, please check your connectivity or contact support"
)
VALIDATION_ERROR_FROM_MDS = lambda message, trace_id: TectonValidationError(f"{message}, trace ID: {trace_id}")
INTERNAL_ERROR_FROM_MDS = lambda message, trace_id: TectonInternalError(
    f"Internal Tecton server error, please contact support with error details: {message}, trace ID: {trace_id}"
)
TIME_KEY_TYPE_ERROR = lambda timestamp_key, found_type: TectonValidationError(
    f"Column '{timestamp_key}' must be Spark type 'TimestampType'. Found '{str(found_type)}'"
)
# Add a link to reference explaining time/duration formats
TIME_PARSING_ERROR = lambda param_name, time_str: TectonValidationError(
    f"Error parsing time '{time_str}' in '{param_name}'"
)
ERROR_RESOLVING_COLUMN = lambda column_name: TectonValidationError(f"Error resolving column '{column_name}'")
FLOATING_POINT_JOIN_KEY = lambda column_name: TectonValidationError(
    f"Floating point types are not allowed for join_key '{column_name}'"
)
INVALID_SPINE_TYPE = lambda t: TectonValidationError(
    f"Invalid type of spine '{t}'. Spine must be an instance of [pyspark.sql.dataframe.DataFrame, " "pandas.DataFrame]."
)
UNSUPPORTED_OPERATION = lambda op, reason: TectonValidationError(f"Operation '{op}' is not supported: {reason}")
INVALID_SPINE_TIME_KEY_TYPE = lambda t: TectonValidationError(
    f"Invalid type of timestamp_key column in the given spine. Expected TimestampType, got {t}"
)
MISSING_SPINE_COLUMN = lambda param, col, existing_cols: TectonValidationError(
    f"TectonValidationError: {param} column is missing from the spine. Expected to find '{col}' among available spine columns: '{', '.join(existing_cols)}'."
)
MISSING_REQUEST_DATA_IN_SPINE = lambda key, existing_cols: TectonValidationError(
    f"TectonValidationError: Request context key '{key}' not found in spine schema. Expected to find '{key}' among available spine columns: '{', '.join(existing_cols)}'."
)
INVALID_DATETIME_PARTITION_COLUMNS = lambda datepart: TectonValidationError(
    f'TectonValidationError: Invalid set of DatetimePartitionColumns: missing "{datepart}"'
)
DURATION_NEGATIVE_OR_AMBIGUOUS = lambda param_name, param_value: TectonValidationError(
    f"{param_name} must be a positive value and must not contain ambiguous durations such as months and years. Instead got {param_value}"
)
NONEXISTENT_WORKSPACE = lambda name, workspaces: TectonValidationError(
    f'Workspace "{name}" not found. Possible values: {workspaces}'
)
INCORRECT_MATERIALIZATION_ENABLED_FLAG = lambda user_set_bool, server_side_bool: TectonValidationError(
    f"'is_live={user_set_bool}' argument does not match the value on the server: {server_side_bool}"
)
UNSUPPORTED_OPERATION_IN_DEVELOPMENT_WORKSPACE = lambda op: TectonValidationError(
    f"Operation '{op}' is not supported in a development workspace"
)
INVALID_JOIN_KEYS_TYPE = lambda t: TectonValidationError(
    f"Invalid type for join_keys. Expected Dict[str, Union[int, str, bytes]], got {t}"
)
INVALID_REQUEST_DATA_TYPE = lambda t: TectonValidationError(
    f"Invalid type for request_data. Expected Dict[str, Union[int, str, bytes, float]], got {t}"
)
INVALID_REQUEST_CONTEXT_TYPE = lambda t: TectonValidationError(
    f"Invalid type for request_context_map. Expected Dict[str, Union[int, str, bytes, float]], got {t}"
)
CONTEXT_REQUIRED = lambda: TectonValidationError("Expected `context` to be a `MaterializationContext` but got `None`.")


def INVALID_INDIVIDUAL_JOIN_KEY_TYPE(key: str, type_str: str):
    return TectonValidationError(
        f"Invalid type for join_key '{key}'. Expected either type int, str, or bytes, got {type_str}"
    )


def EMPTY_ARGUMENT(argument: str):
    return TectonValidationError(f"Argument '{argument}' can not be empty.")


def EMPTY_ELEMENT_IN_ARGUMENT(argument: str):
    return TectonValidationError(f"Argument '{argument}' can not have an empty element.")


def WRONG_ARGUMENT_TYPE(argument, expected_type):
    return TectonValidationError(f"Argument '{argument}' must be of type '{expected_type}'")


def DUPLICATED_ELEMENTS_IN_ARGUMENT(argument: str):
    return TectonValidationError(f"Argument '{argument}' can not have duplicated elements.")


def FCO_NOT_FOUND(fco: Fco, fco_reference: str):
    raise TectonValidationError(
        f"{fco._fco_type_name_singular_capitalized()} '{fco_reference}' not found. "
        f"Try running `tecton.list_{fco._fco_type_name_plural_snake_case()}()` to view all registered "
        f"{fco._fco_type_name_plural_capitalized()}"
    )


def FEATURE_DEFINITION_NOT_FOUND(fco_reference: str):
    raise TectonValidationError(
        f"'{fco_reference}' not found. "
        "Try running tecton.list_feature_views() to view all registered FeatureViews "
        " and tecton.list_feature_tables() to view all registered FeatureTables."
    )


def DATA_SOURCE_NOT_FOUND(fco_reference: str):
    raise TectonValidationError(
        f"Data source '{fco_reference}' not found. "
        f"Try running `tecton.list_data_sources()` to view all registered BatchDataSource/StreamDataSource."
    )


def FCO_NOT_FOUND_WRONG_TYPE(fco: Fco, fco_reference: str, expected_method):
    raise TectonValidationError(
        f"{fco._fco_type_name_singular_capitalized()} '{fco_reference}' not found. "
        f"Did you mean tecton.{expected_method}?"
    )


def UNKNOWN_REQUEST_CONTEXT_KEY(keys, key):
    return TectonValidationError(f"Unknown request context key '{key}', expected one of: {keys}")


FV_TIME_KEY_MISSING = lambda fv_name: TectonValidationError(
    f"Argument 'timestamp_key' is required for the feature definition '{fv_name}'"
)
FV_NEEDS_TO_BE_MATERIALIZED = lambda fv_name: TectonValidationError(
    f"FeatureView '{fv_name}' has not been configured for materialization. "
    + f"Set offline_enabled=True in the FeatureView definition to enable this feature."
)
FV_NO_MATERIALIZED_DATA = lambda fv_name: TectonValidationError(
    f"Feature definition '{fv_name}' doesn't have any materialized data. "
    "Materialization jobs may not have updated the offline feature store yet. "
    "Please monitor using materialization_status() or use from_source=True to compute from source data."
)

FV_NOT_SUPPORTED_GET_FEATURE_DF = TectonValidationError(
    "This method cannot be used with this type of Feature Definition. Please use get_feature_dataframe(spine)."
)
FD_PREVIEW_NO_MATERIALIZED_OFFLINE_DATA = TectonValidationError(
    f"No materialized offline data found. If this Feature Definition was recently created,"
    + " its materialization backfill may still be in progress. This can be monitored using materialization_status()."
    + " In the meantime, you can set use_materialized_data=False on preview() to compute features directly from data sources."
)
FV_GET_FEATURE_DF_NO_SPINE = TectonValidationError("get_feature_dataframe() requires a 'spine' argument.")
FT_DF_TOO_LARGE = TectonValidationError(
    "Dataframe too large for a single ingestion, consider splitting into smaller ones"
)
FV_BFC_SINGLE_FROM_SOURCE = TectonValidationError(
    f"Computing features from source is not supported for Batch Feature Views with single_batch_schedule_interval_per_job backfill mode"
)

FD_GET_MATERIALIZED_FEATURES_FROM_DEVELOPMENT_WORKSPACE = lambda fd_name, workspace: TectonValidationError(
    f"Feature Definition {fd_name} is in workspace {workspace}, which is a development workspace (does not have materialization enabled). "
    "Please use from_source=True when getting features (not applicable for Feature Tables) or "
    "alternatively configure offline materialization for this Feature Definition in a live workspace."
)

FD_GET_MATERIALIZED_FEATURES_FROM_DEVELOPMENT_WORKSPACE_GFD = lambda fd_name, workspace: TectonValidationError(
    f"Feature View {fd_name} is in workspace {workspace}, which is a development workspace (does not have materialization enabled). "
    "Please use use_materialized_data=False when getting features or "
    "alternatively configure offline materialization for this Feature View in a live workspace."
)

FD_GET_FEATURES_MATERIALIZATION_DISABLED = lambda fd_name: TectonValidationError(
    f"Feature Definition {fd_name} does not have offline materialization turned on. "
    f"Try calling this function with 'from_source=True' (not applicable for Feature Tables) "
    "or alternatively configure offline materialization for this Feature Definition."
)

FD_GET_FEATURES_MATERIALIZATION_DISABLED_GFD = lambda fd_name: TectonValidationError(
    f"Feature View {fd_name} does not have offline materialization turned on. "
    f"Try calling this function with 'use_materialized_data=False' "
    "or alternatively configure offline materialization for this Feature View."
)


def FT_UPLOAD_FAILED(reason):
    return TectonValidationError(f"Failed to upload dataframe: {reason}")


# DataSources
def DS_STREAM_BATCH_SCHEMA_MISMATCH(columns):
    return TectonValidationError(
        f"Streaming data source schema has column(s) that are not present in the batch data source schema: {columns}"
    )


def DS_INVALID_TABLE_COLUMN(column_name, existing_columns):
    return TectonValidationError(f"Column '{column_name}' is not among table columns {existing_columns}")


def DS_INVALID_TABLE_PARTITION(partition_name, existing_partitions):
    return TectonValidationError(f"Column '{partition_name}' is not among table partitions {existing_partitions}")


def DS_NAME_EQUALS_HIVE_TABLE_NAME(name):
    return TectonValidationError(
        f"DataSource name '{name}' is not allowed because a Glue (or Hive) table with the same name exists. "
        f"This is a current system limitation. Please rename your DataSource to, for instance, '{name}_ds'"
    )


def DS_NAME_CANNOT_CONTAIN_DOT(name):
    return TectonValidationError(f"DataSource name '{name}' cannot contain a dot. Please, remove it and try again.")


def DS_TIMESTAMP_COLUMN_MISSING_FOR_LOOKBACK(name):
    return TectonValidationError(
        "Setting data_lookback requires your upstream data source to specify a timestamp column to enable Tecton to "
        "filter your raw data according to the time range specified by data_lookback. Please specify 'timestamp_column'"
        f" on the batch_ds_config of your DataSource {name} or unset data_lookback to disable Tecton's "
        "raw data filtering."
    )


DS_TIME_KEY_MISSING_ERROR = lambda timestamp_key, all_cols: TectonValidationError(
    f"Timestamp column '{timestamp_key}' missing from Schema. Found columns {all_cols}"
)

DS_STREAM_PREVIEW_ON_NON_STREAM = TectonValidationError("'start_stream_preview' called on non-streaming data source")

DS_DATAFRAME_NO_TIMESTAMP = TectonValidationError(
    "Cannot find timestamp column for this data source. Please call 'get_dataframe' without parameters 'start_time' or 'end_time'."
)

DS_RAW_DATAFRAME_NO_TIMESTAMP_FILTER = TectonValidationError(
    "The method 'get_dataframe()' cannot filter on timestamps when 'apply_translator' is False. "
    "'start_time' and 'end_time' must be None."
)


def DS_DEDUPLICATION_COLUMN_MISSING(column, schema_columns):
    return TectonValidationError(
        f"Deduplication column '{column}' not present in the translated stream schema {schema_columns}"
    )


def FS_SPINE_JOIN_KEY_OVERRIDE_INVALID(spine_key, fv_key, possible_columns):
    return TectonValidationError(
        f"Spine join key '{spine_key}' (mapped from FeatureView join key '{fv_key}') not found in spine schema {possible_columns}"
    )


def FS_SPINE_TIMESTAMP_KEY_INVALID(timestamp_key, possible_columns):
    return TectonValidationError(f"Spine timestamp key '{timestamp_key}' not found in spine schema {possible_columns}")


def FS_BACKEND_ERROR(message):
    return TectonInternalError(f"Error calling Feature Service backend: {message}")


def FS_AMBIGUOUS_TIMESTAMP_KEY(keys):
    return TectonValidationError(f"Multiple default timestamp keys found: {keys}. Parameter timestamp_key must be set.")


FS_GET_FEATURE_VECTOR_REQUIRED_ARGS = TectonValidationError(
    "get_feature_vector requires at least one of join_keys or request_context_map"
)

FS_API_KEY_MISSING = TectonValidationError(
    "API key is required for online feature requests, but was not found in the environment. Please generate a key and set TECTON_API_KEY "
    + "using https://docs.tecton.ai/v2/examples/fetch-real-time-features.html#generating-an-api-key"
)

# Snowflake
SNOWFLAKE_TABLE_QUERY_SET_ERROR = TectonValidationError("Exactly one of table and query sources must be set")

# Entity
def ENTITY_INVALID_JOIN_KEYS_OVERRIDE(entity_name: str):
    return TectonValidationError(
        f"New join_keys must have the same amount of columns as existing join_keys for entity '{entity_name}'."
    )


def FV_INVALID_MOCK_INPUTS(mock_inputs: Set[str], inputs: Set[str]):
    input_names = str(mock_inputs) if mock_inputs else "{}"
    return TectonValidationError(f"Mock input names {input_names} do not match FeatureView's inputs {inputs}")


def FV_INVALID_MOCK_INPUTS_NUM_ROWS(num_rows: List[int]):
    return TectonValidationError(
        f"Number of rows are not equal across all mock_inputs. Num rows found are {str(num_rows)}."
    )


def FV_INVALID_MOCK_INPUT_SCHEMA(input_name: str, mock_columns: Set[str], expected_columns: Set[str]):
    return TectonValidationError(
        f"mock_inputs['{input_name}'] has mismatch schema columns {mock_columns}, expected {expected_columns}"
    )


def FV_UNSUPPORTED_ARG(invalid_arg_name: str):
    return TectonValidationError(f"Argument '{invalid_arg_name}' is not supported for this FeatureView type.")


def FV_INVALID_ARG_VALUE(arg_name: str, value: str, expected: str):
    return TectonValidationError(f"Invalid argument value '{arg_name}={value}', supported value(s): '{expected}'")


def FV_INVALID_ARG_COMBO(arg_names: List[str]):
    return TectonValidationError(f"Invalid argument combinations; {str(arg_names)} cannot be used together.")


FT_UNABLE_TO_ACCESS_SOURCE_DATA = lambda fv_name: TectonValidationError(
    f"The source data for FeatureTable {fv_name} does not exist. "
    "Please use from_source=False when calling this function."
)


class InvalidTransformationMode(TectonValidationError):
    def __init__(self, name: str, got: str, allowed_modes: List[str]):
        super().__init__(f"Transformation mode for '{name}' got '{got}', must be one of: {', '.join(allowed_modes)}")


class InvalidConstantType(TectonValidationError):
    def __init__(self, value, allowed_types):
        allowed_types = [str(allowed_type) for allowed_type in allowed_types]
        super().__init__(
            f"Tecton const value '{value}' must have one of the following types: {', '.join(allowed_types)}"
        )


class InvalidTransformInvocation(TectonValidationError):
    def __init__(self, transformation_name: str, got: str):
        super().__init__(
            f"Allowed arguments for Transformation '{transformation_name}' are: "
            f"tecton.const, tecton.materialization_context, transformations, and DataSource inputs. Got: '{got}'"
        )


# Dataset
DATASET_SPINE_COLUMNS_NOT_SET = TectonValidationError(
    "Cannot retrieve spine DF when DataFrame was created without a " "spine."
)

# Feature Retrevial
def GET_HISTORICAL_FEATURES_WRONG_PARAMS(params: List[str], if_statement: str):
    return TectonValidationError("Cannot provide parameters " + ", ".join(params) + f" if {if_statement}")


FV_NOT_SUPPORTED_GET_HISTORICAL_FEATURES = TectonValidationError(
    "A spine must be provided to perform this method on an On Demand Feature View. Please use get_historical_features(spine=spine)."
)

GET_ONLINE_FEATURES_REQUIRED_ARGS = TectonValidationError(
    "get_online_features requires at least one of join_keys or request_data"
)

GET_ONLINE_FEATURES_ODFV_JOIN_KEYS = TectonValidationError(
    "get_online_features requires the 'join_keys' argument for this Feature View as it has dependent Feature Views as inputs"
)

GET_ONLINE_FEATURES_FS_JOIN_KEYS = TectonValidationError(
    "get_online_features requires the 'join_keys' argument for this Feature Service"
)

GET_FEATURE_VECTOR_FS_JOIN_KEYS = TectonValidationError(
    "get_feature_vector requires the 'join_keys' argument for this Feature Service"
)

FS_GET_ONLINE_FEATURES_REQUIRED_ARGS = TectonValidationError(
    "get_online_features requires at least one of join_keys or request_data"
)


def GET_ONLINE_FEATURES_MISSING_REQUEST_KEY(keys: Set[str]):
    return TectonValidationError(
        f"Missing the following required keys in request_data input: "
        + ", ".join(keys)
        + ". Please provide a value for the keys in request_data."
    )


def GET_FEATURE_VECTOR_MISSING_REQUEST_KEY(keys: Set[str]):
    return TectonValidationError(
        f"Missing the following required keys in request_context_map input: "
        + ", ".join(keys)
        + ". Please provide a value for the keys in request_context_map."
    )


def GET_ONLINE_FEATURES_FS_NO_REQUEST_DATA(keys: List[str]):
    return TectonValidationError(
        "get_online_features requires the 'request_data' argument for this Feature Service. Expected the following request data keys: "
        + ", ".join(keys)
    )


def GET_FEATURE_VECTOR_FS_NO_REQUEST_DATA(keys: List[str]):
    return TectonValidationError(
        "get_feature_vector requires the 'request_context_map' argument for this Feature Service. Expected the following request context keys: "
        + ", ".join(keys)
    )


def GET_ONLINE_FEATURES_FV_NO_REQUEST_DATA(keys: List[str]):
    return TectonValidationError(
        "get_online_features requires the 'request_data' argument for this OnDemand Feature View. Expected the following request data keys: "
        + ", ".join(keys)
    )


def GET_FEATURE_VECTOR_FV_NO_REQUEST_DATA(keys: List[str]):
    return TectonValidationError(
        "get_feature_vector requires the 'request_context_map' argument for this OnDemand Feature View. Expected the following request context keys: "
        + ", ".join(keys)
    )


def GET_ONLINE_FEATURES_MISSING_JOIN_KEYS(missing_key: str):
    return TectonValidationError(f"Join key {missing_key} not found in parameter 'join_keys'")


FROM_SOURCE_WITH_FT = TectonValidationError(
    f"Computing features from source is not supported for Feature Tables. Try calling this method with from_source=False."
)

USE_MATERIALIZED_DATA_WITH_FT = TectonValidationError(
    f"Computing features from source is not supported for Feature Tables. Try calling this method with use_materialized_data=True."
)


FS_WITH_FT_DEVELOPMENT_WORKSPACE = TectonValidationError(
    f"This Feature Service contains a Feature Table and fetching historical features for Feature Tables is not supported in a development workspace. Try calling this method in a live workspace."
)


FV_WITH_FT_DEVELOPMENT_WORKSPACE = TectonValidationError(
    f"This Feature View has a Feature Table input and fetching historical features for Feature Tables is not supported in a development workspace. Try calling this method in a live workspace."
)


# Backfill Config Validation
BFC_MODE_SINGLE_REQUIRED_FEATURE_END_TIME_WHEN_START_TIME_SET = TectonValidationError(
    "feature_end_time is required when feature_start_time is set, for a FeatureView with "
    + "single-batch-schedule-per-job backfill mode."
)

BFC_MODE_SINGLE_INVALID_FEATURE_TIME_RANGE = TectonValidationError(
    "Run with single_batch_schedule_interval_per_job backfill mode only supports time range equal to batch_schedule"
)
