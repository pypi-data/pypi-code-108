"""Helper module for creating spark data source operations such as creating DataFrames and
registering temp views. Methods within this class should exclusively operate on proto
representations of the data model.
"""
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from urllib.parse import urlencode

import pendulum
from pyspark.sql import DataFrame
from pyspark.sql import functions
from pyspark.sql import SparkSession
from pyspark.sql.functions import coalesce
from pyspark.sql.functions import to_timestamp
from pyspark.sql.types import ArrayType
from pyspark.sql.types import DateType
from pyspark.sql.types import MapType
from pyspark.sql.types import StringType
from pyspark.sql.types import StructField
from pyspark.sql.types import StructType

from tecton_proto.args.data_source_config_pb2 import INITIAL_STREAM_POSITION_LATEST
from tecton_proto.args.data_source_config_pb2 import INITIAL_STREAM_POSITION_TRIM_HORIZON
from tecton_proto.args.data_source_config_pb2 import INITIAL_STREAM_POSITION_UNSPECIFIED
from tecton_proto.data.batch_data_source_pb2 import BatchDataSource
from tecton_proto.data.batch_data_source_pb2 import FileDataSourceFormat
from tecton_proto.data.stream_data_source_pb2 import StreamDataSource
from tecton_proto.data.virtual_data_source_pb2 import VirtualDataSource
from tecton_spark import conf
from tecton_spark import errors
from tecton_spark import function_serialization
from tecton_spark.data_source_credentials import get_kafka_secrets
from tecton_spark.feature_definition_wrapper import FeatureDefinitionWrapper as FeatureDefinition
from tecton_spark.id_helper import IdHelper
from tecton_spark.spark_schema_wrapper import SparkSchemaWrapper

INITIAL_STREAM_POSITION_STR_TO_ENUM = {
    "latest": INITIAL_STREAM_POSITION_LATEST,
    "trim_horizon": INITIAL_STREAM_POSITION_TRIM_HORIZON,
}

INITIAL_STREAM_POSITION_ENUM_TO_STR: Dict[str, Optional[str]] = {
    v: k for k, v in INITIAL_STREAM_POSITION_STR_TO_ENUM.items()
}
INITIAL_STREAM_POSITION_ENUM_TO_STR[INITIAL_STREAM_POSITION_UNSPECIFIED] = None


def _is_running_on_emr() -> bool:
    import os

    return "EMR_RELEASE_LABEL" in os.environ


def _validate_data_source_proto(data_source: BatchDataSource):
    if data_source.HasField("hive_table"):
        assert data_source.hive_table.HasField("database"), "Invalid HiveTableDataSource: no database provided"
        assert data_source.hive_table.HasField("table"), "Invalid HiveTableDataSource: no table provided"
    elif data_source.HasField("file"):
        pass
    elif data_source.HasField("redshift_db"):
        redshift = data_source.redshift_db
        assert redshift.HasField("endpoint"), "Invalid RedshiftDataSource: no endpoint provided"
        assert redshift.HasField("table") or redshift.HasField(
            "query"
        ), "Invalid RedshiftDataSource: no table or query provided"
    elif data_source.HasField("snowflake"):
        snowflake = data_source.snowflake.snowflakeArgs
        required_args = ["url", "database", "schema", "warehouse"]
        for arg in required_args:
            assert snowflake.HasField(arg), f"Invalid SnowflakeDataSource: no {arg} provided"
        assert snowflake.HasField("table") or snowflake.HasField(
            "query"
        ), "Invalid SnowflakeDataSource: no table or query provided"
    else:
        assert False, "BatchDataSource must set hive_table, file, redshift_db, or snowflake"


def _get_raw_hive_table_dataframe(spark: SparkSession, database: str, table: str) -> DataFrame:
    spark.sql("USE {}".format(database))
    return spark.table(table)


def get_raw_dataframe(
    spark: SparkSession, data_source: BatchDataSource, called_for_schema_computation=False
) -> DataFrame:
    """Returns a DataFrame of the raw, untranslated data defined by the given BatchDataSource proto.

    :param spark: Spark session.
    :param data_source: BatchDataSource proto.
    :param called_for_schema_computation: If set, optimizations are applied for faster schema computations.
                                          i.e. FileDSConfig.schema_uri is used to avoid expensive partition discovery.

    :return: The DataFrame for the raw data.
    """
    _validate_data_source_proto(data_source)
    if data_source.HasField("hive_table"):
        df = _get_raw_hive_table_dataframe(spark, data_source.hive_table.database, data_source.hive_table.table)
    elif data_source.HasField("redshift_db"):
        df = get_redshift_dataframe(
            spark,
            data_source.redshift_db.endpoint,
            data_source.redshift_db.temp_s3,
            table=data_source.redshift_db.table,
            query=data_source.redshift_db.query,
        )
    elif data_source.HasField("snowflake"):
        df = get_snowflake_dataframe(
            spark,
            data_source.snowflake.snowflakeArgs.url,
            data_source.snowflake.snowflakeArgs.database,
            data_source.snowflake.snowflakeArgs.schema,
            data_source.snowflake.snowflakeArgs.warehouse,
            data_source.snowflake.snowflakeArgs.role,
            data_source.snowflake.snowflakeArgs.table,
            data_source.snowflake.snowflakeArgs.query,
        )
    else:
        # FileDataSource
        reader = spark.read
        uri = data_source.file.uri
        if called_for_schema_computation and data_source.file.HasField("schema_uri"):
            # Setting basePath includes the path-based partitions in the DataFrame schema.
            # https://spark.apache.org/docs/latest/sql-data-sources-parquet.html#partition-discovery
            reader = reader.option("basePath", data_source.file.uri)
            uri = data_source.file.schema_uri

        if data_source.file.HasField("schema_override"):
            schema = SparkSchemaWrapper.from_proto(data_source.file.schema_override)
            reader = reader.schema(schema.unwrap())

        if data_source.file.format == FileDataSourceFormat.FILE_DATA_SOURCE_FORMAT_JSON:
            action = lambda: reader.json(uri)
        elif data_source.file.format == FileDataSourceFormat.FILE_DATA_SOURCE_FORMAT_PARQUET:
            action = lambda: reader.parquet(uri)
        elif data_source.file.format == FileDataSourceFormat.FILE_DATA_SOURCE_FORMAT_CSV:
            action = lambda: reader.csv(uri, header=True)
        else:
            raise AssertionError(f"Unsupported file format '{data_source.file.format}'")

        df = errors.handleDataAccessErrors(action, data_source.file.uri)
        if data_source.file.convert_to_glue_format:
            df = convert_json_like_schema_to_glue_format(spark, df)

    return df


def get_table_dataframe(
    spark: SparkSession, data_source: BatchDataSource, called_for_schema_computation=False
) -> DataFrame:
    """Returns a DataFrame for a table defined by given BatchDataSource proto.

    :param spark: Spark session.
    :param data_source: BatchDataSource proto.
    :param called_for_schema_computation: If set, optimizations are applied for faster schema computations.
                                          i.e. FileDSConfig.schema_uri is used to avoid expensive partition discovery.

    :return: The DataFrame created from the data source.
    """
    df = get_raw_dataframe(spark, data_source, called_for_schema_computation)
    if data_source.HasField("raw_batch_translator"):
        translator_fn = function_serialization.from_proto(data_source.raw_batch_translator)
        df = translator_fn(df)
    if data_source.HasField("timestamp_column_properties"):
        ts_format = None
        if data_source.timestamp_column_properties.HasField("format"):
            ts_format = data_source.timestamp_column_properties.format
        df = apply_timestamp_column(df, data_source.timestamp_column_properties.column_name, ts_format)

    return df


def get_redshift_dataframe(
    spark: SparkSession, endpoint: str, temp_s3: str, table: Optional[str] = None, query: Optional[str] = None
) -> DataFrame:
    """Returns a DataFrame for a Redshift table defined by given RedshiftDataSource proto.

    :param table: The table name in redshift
    :param temp_s3: The s3 URI for temp data
    :param endpoint: The connection endpoint for redshift (without user or password)
    :param spark: Spark session.

    :return: The DataFrame created from the data source.
    """

    if _is_running_on_emr():
        spark_format = "io.github.spark_redshift_community.spark.redshift"
        params = {"user": conf.get_or_none("REDSHIFT_USER"), "password": conf.get_or_none("REDSHIFT_PASSWORD")}
        full_connection_string = f"jdbc:redshift://{endpoint};user={params['user']};password={params['password']}"
    else:
        spark_format = "com.databricks.spark.redshift"
        params = {"user": conf.get_or_none("REDSHIFT_USER"), "password": conf.get_or_none("REDSHIFT_PASSWORD")}
        encoded_params = urlencode(params)
        full_connection_string = f"jdbc:postgresql://{endpoint}?{encoded_params}"

    df_reader = (
        spark.read.format(spark_format)
        .option("url", full_connection_string)
        .option("tempdir", temp_s3)
        .option("forward_spark_s3_credentials", "true")
    )

    if table and query:
        raise AssertionError(f"Should only specify one of table and query sources for redshift")
    if not table and not query:
        raise AssertionError(f"Missing both table and query sources for redshift, exactly one must be present")

    if table:
        df_reader = df_reader.option("dbtable", table)
    else:
        df_reader = df_reader.option("query", query)

    df = df_reader.load()
    return df


def get_snowflake_dataframe(
    spark: SparkSession,
    url: str,
    database: str,
    schema: str,
    warehouse: str,
    role: Optional[str] = None,
    table: Optional[str] = None,
    query: Optional[str] = None,
) -> DataFrame:
    """Returns a DataFrame for a Snowflake table defined by given SnowflakeDataSource proto.

    :param spark: Spark session.
    :param url: The table name in Snowflake


    :return: The DataFrame created from the data source.
    """

    if table and query:
        raise AssertionError(f"Should only specify one of table and query sources for Snowflake")
    if not table and not query:
        raise AssertionError(f"Missing both table and query sources for Snowflake, exactly one must be present")

    user = conf.get_or_none("SNOWFLAKE_USER")
    password = conf.get_or_none("SNOWFLAKE_PASSWORD")
    if not user or not password:
        raise AssertionError("User and password need to be set")

    options = {
        "sfUrl": url,
        "sfUser": user,
        "sfPassword": password,
        "sfDatabase": database,
        "sfSchema": schema,
        "sfWarehouse": warehouse,
        "APPLICATION": "tecton-ai",
    }

    if role:
        options["sfRole"] = role

    df_reader = spark.read.format("snowflake").options(**options)

    if table:
        df_reader = df_reader.option("dbtable", table)
    else:
        df_reader = df_reader.option("query", query)

    df = df_reader.load()
    return df


def apply_timestamp_column(df: DataFrame, ts_column: str, ts_format: Optional[str]) -> DataFrame:
    # Verify the raw source's timestamp column is of type "string"
    column_names = df.schema.names
    if ts_column not in column_names:
        raise AssertionError(f"Timestamp column '{ts_column}' not found in schema. Found: {column_names}")

    ts_type = df.schema[ts_column].dataType.jsonValue()
    if ts_type != "timestamp":
        assert ts_type == "string", f"Column '{ts_column}' has type '{ts_type}', expected 'string' or 'timestamp'"
        # Apply timestamp transform

        # Here we use coalesce to first try transforming string to timestamp using the user provided format,
        # and if it doesn't work we'll instead let Spark figure it out. This is a temporary measure to unbreak
        # existing use cases with bad timestamp formats.
        # TODO: Once all use cases have been fixed, we'll remove coalesce operator and the 2nd part of the equation.
        df = df.withColumn(ts_column, coalesce(to_timestamp(df[ts_column], ts_format), to_timestamp(df[ts_column])))

    return df


def apply_partition_and_timestamp_filter(
    df: DataFrame, data_source: BatchDataSource, raw_data_time_limits: pendulum.Period
) -> DataFrame:
    """Applies a partition and timestamp filters if the respective column names are set.

    :return: The DataFrame with filter applied.
    """

    # backward compatibility. If we wanted to deprecate, this could be replaced by
    # datetime_partition_columns containing [col_name, "%Y-%m-%d", 24 * 60 * 60]
    if data_source.HasField("date_partition_column"):
        date_start = raw_data_time_limits.start.to_date_string()
        date_end = raw_data_time_limits.end.to_date_string()
        date_partition_column = functions.col(data_source.date_partition_column)
        df = df.where((date_start <= date_partition_column) & (date_partition_column <= date_end))
    # add datetime partition filters
    elif len(data_source.datetime_partition_columns) > 0:
        partition_filter = _build_partition_filter(data_source.datetime_partition_columns, raw_data_time_limits)
        df = df.where(partition_filter)
    # add timestamp filter
    if data_source.HasField("timestamp_column_properties"):
        ts_column = functions.col(data_source.timestamp_column_properties.column_name)
        df = df.where((ts_column >= raw_data_time_limits.start) & (ts_column < raw_data_time_limits.end))
    if not data_source.HasField("timestamp_column_properties"):
        raise Exception(f"DataSource {data_source.fco_metadata.name} requires timestamp column name for FeatureView")
    return df


# Generate filter on time_range with at most OR of 2 filters.
# This means we could end up scanning more partitions than necessary, but number extra scanned will be at most
# 3x.
# Worst case: time_range = 367 days across 3 years, we scan entire 3 years.
#             time_range = 365 days, we scan up to 2 years including that 1 year range
#             time_range = 28.1 days, we could scan all of January + February + March = 90 days
#
# 2 cases to consider
# Example: partition cols y, m, d, h: in both examples, the time range is between day and month, so we don't add any
# filters on hour, even though it would be possible to scan some fewer partitions if we did
# (A)Time range: 2020 Jan 10 10:00:00 AM - 2020 Jan 15 5:00:00 AM
#  --> (y = start.year & m = start.month & d >= start.day & d <= end.day)
# (B)Time range: 2019 Dec 21 10:00:00 AM - 2020 Jan 10 5:00:00 AM
#  --> ((y = start.year & m = start.month & d >= start.day) | (y = end.year & m = end.month & d <= end.day))
def _build_partition_filter(datetime_partition_columns, raw_data_time_limits):
    start_time, end_time = raw_data_time_limits.start, raw_data_time_limits.end
    time_range_seconds = raw_data_time_limits.total_seconds()

    # Filters relating to start_time and end_time
    start_filters = []
    end_filters = []
    # Common filter that applies to the entire range
    common_filters = []

    # sort partition columns by the number of seconds they represent from highest to lowest
    partitions_high_to_low = sorted(datetime_partition_columns, key=lambda c: c.minimum_seconds, reverse=True)
    for partition in partitions_high_to_low:
        partition_col = functions.col(partition.column_name)
        partition_value_at_start = _partition_value_for_time(partition, start_time)
        partition_value_at_end = _partition_value_for_time(partition, end_time)
        # If partition's datepart minimum length is >= time_range_seconds, we can be sure that 2 or fewer equality filters are enough to cover all possible times in time_limits
        if partition.minimum_seconds >= time_range_seconds:
            if partition_value_at_start == partition_value_at_end:
                common_filters.append(partition_col == partition_value_at_start)
            else:
                start_filters.append(partition_col == partition_value_at_start)
                end_filters.append(partition_col == partition_value_at_end)
        # Otherwise, we need to use a range filter
        else:
            start_range_filter = partition_col >= partition_value_at_start
            end_range_filter = partition_col <= partition_value_at_end
            # Case A: there are only common filters
            if len(start_filters) == 0:
                common_filters.append(start_range_filter)
                common_filters.append(end_range_filter)
                # we can't combine range filters on multiple columns, so break and ignore any smaller columns
                break
            # Case B
            else:
                start_filters.append(start_range_filter)
                end_filters.append(end_range_filter)
                # we can't combine range filters on multiple columns, so break and ignore any smaller columns
                break

    common_filter = _and_filters_in_list(common_filters)
    start_filter = _and_filters_in_list(start_filters)
    end_filter = _and_filters_in_list(end_filters)

    return common_filter & (start_filter | end_filter)


def _partition_value_for_time(partition, time):
    fmt = partition.format_string
    # On mac/linux strftime supports these formats, but
    # Windows python does not
    # Zero-padded formats are safe for a string comparison. Otherwise we need to compare ints
    # As long as the values returned here are ints, the column will be implicitly converted if needed.
    if fmt == "%-Y":
        return time.year
    elif fmt == "%-m":
        return time.month
    elif fmt == "%-d":
        return time.day
    elif fmt == "%-H":
        return time.hour
    return time.strftime(fmt)


def _and_filters_in_list(filter_list):
    if len(filter_list) == 0:
        return functions.lit(True)
    else:
        from functools import reduce

        return reduce(lambda x, y: x & y, filter_list)


def get_table_column_and_partition_names(spark: SparkSession, data_source: "HiveDSConfig") -> Tuple[Set[str], Set[str]]:  # type: ignore
    """Returns a tuple of (set of column names, set of partition names) for the given BatchDataSource."""
    _validate_data_source_proto(data_source)
    database = data_source.hive_table.database
    table = data_source.hive_table.table
    pandas_df = spark.sql(f"DESCRIBE TABLE {database}.{table}").toPandas()
    column_names = set(pandas_df[~pandas_df.col_name.str.startswith("#")].col_name)
    partition_index = pandas_df.index[pandas_df["col_name"] == "# Partition Information"]
    if partition_index.size > 0:
        partition_info = pandas_df[partition_index[0] :]
        partition_names = set(partition_info[~partition_info.col_name.str.startswith("#")].col_name)
    else:
        partition_names = set()

    return column_names, partition_names


def create_kinesis_stream_reader(
    spark: SparkSession,
    stream_name: str,
    region: str,
    initial_stream_position: Optional[str],
    options: List[StreamDataSource.Option],
) -> DataFrame:
    """
    Returns a DataFrame representing a Kinesis stream reader.
    """
    reader = spark.readStream.format("kinesis").option("streamName", stream_name)
    # kinesis has a 10 describeStream requests per second limit per region (that is unchangeable)
    # this allows us to read 300 kinesis streams per region
    if _is_running_on_emr():
        reader = (
            reader.option("endpointUrl", f"https://kinesis.{region}.amazonaws.com")
            .option("kinesis.client.describeShardInterval", "30s")
            .option("startingPosition", initial_stream_position)
        )
    else:
        reader = (
            reader.option("region", region)
            .option("shardFetchInterval", "30s")
            .option("initialPosition", initial_stream_position)
        )

    options_dict = {option.key.lower(): option.value for option in options}
    databricks_to_qubole_map = {
        "awsaccesskey": "awsAccessKeyId",
        "rolearn": "awsSTSRoleARN",
        "rolesessionname": "awsSTSSessionName",
    }

    for option in options:
        if option.key.lower() in databricks_to_qubole_map and _is_running_on_emr():
            if option.key.lower() == "rolearn" and "rolesessionname" not in options_dict:
                # this field must be supplied if we use roleArn for qubole kinesis reader
                reader = reader.option("awsSTSSessionName", "tecton-materialization")
            reader = reader.option(databricks_to_qubole_map[option.key.lower()], option.value)
        else:
            reader = reader.option(option.key, option.value)

    return reader.load()


def create_kafka_stream_reader(
    spark: SparkSession,
    kafka_bootstrap_servers: str,
    topics: str,
    user_options: List[StreamDataSource.Option],
    ssl_keystore_location: Optional[str] = None,
    ssl_keystore_password_secret_id: Optional[str] = None,
    ssl_truststore_location: Optional[str] = None,
    ssl_truststore_password_secret_id: Optional[str] = None,
    security_protocol: Optional[str] = None,
) -> DataFrame:
    """Returns a Kafka stream reader."""
    options = {o.key: o.value for o in user_options}
    options["kafka.bootstrap.servers"] = kafka_bootstrap_servers
    options["subscribe"] = topics
    options["startingOffsets"] = "earliest"
    reader = spark.readStream.format("kafka").options(**options)
    if ssl_keystore_location:
        local_keystore_loc, local_keystore_password = get_kafka_secrets(
            ssl_keystore_location, ssl_keystore_password_secret_id
        )
        reader = reader.option("kafka.ssl.keystore.location", local_keystore_loc)
        if local_keystore_password:
            reader = reader.option("kafka.ssl.keystore.password", local_keystore_password)
    if ssl_truststore_location:
        local_truststore_loc, local_truststore_password = get_kafka_secrets(
            ssl_truststore_location, ssl_truststore_password_secret_id
        )
        reader = reader.option("kafka.ssl.truststore.location", local_truststore_loc)
        if local_truststore_password:
            reader = reader.option("kafka.ssl.truststore.password", local_truststore_password)
    if security_protocol:
        reader = reader.option("kafka.security.protocol", security_protocol)

    return reader.load()


def get_raw_stream_dataframe(spark: SparkSession, stream_data_source: StreamDataSource) -> DataFrame:
    """Returns a DataFrame representing the raw stream data.

    :param spark: Spark session.
    :param stream_data_source: StreamDataSource proto.

    :return: The DataFrame for the raw stream data source.
    """
    if stream_data_source.HasField("kinesis_data_source"):
        kinesis_data_source = stream_data_source.kinesis_data_source
        initial_stream_position = _get_initial_stream_position(stream_data_source)
        df = create_kinesis_stream_reader(
            spark,
            kinesis_data_source.stream_name,
            kinesis_data_source.region,
            initial_stream_position,
            stream_data_source.options,
        )
    elif stream_data_source.HasField("kafka_data_source"):
        kafka_data_source = stream_data_source.kafka_data_source
        df = create_kafka_stream_reader(
            spark,
            kafka_data_source.bootstrap_servers,
            kafka_data_source.topics,
            stream_data_source.options,
            ssl_keystore_location=kafka_data_source.ssl_keystore_location,
            ssl_keystore_password_secret_id=kafka_data_source.ssl_keystore_password_secret_id,
            ssl_truststore_location=kafka_data_source.ssl_truststore_location,
            ssl_truststore_password_secret_id=kafka_data_source.ssl_truststore_password_secret_id,
            security_protocol=kafka_data_source.security_protocol,
        )
    else:
        raise ValueError("Unknown stream data source type")
    return df


def get_stream_dataframe(spark: SparkSession, stream_data_source: StreamDataSource) -> DataFrame:
    """Returns a DataFrame representing a stream data source *without* any options specified.
    Use get_stream_dataframe_with_options to get a DataFrame with stream-specific options.

    :param spark: Spark session.
    :param stream_data_source: StreamDataSource proto.

    :return: The DataFrame created from the data source.
    """

    df = get_raw_stream_dataframe(spark, stream_data_source)
    translator_fn = function_serialization.from_proto(stream_data_source.raw_stream_translator)
    return translator_fn(df)


def get_stream_dataframe_with_options(spark: SparkSession, stream_data_source: StreamDataSource) -> DataFrame:
    """Returns a DataFrame representing a stream data source with additional options:
        - watermark
        - drop duplicate column names
        - initial stream position

    :param spark: Spark session.
    :param stream_data_source: StreamDataSource proto.

    :return: The DataFrame created from the data source.
    """

    df = get_stream_dataframe(spark, stream_data_source)

    watermark = _get_watermark(stream_data_source)
    df = df.withWatermark(stream_data_source.time_column, watermark)

    dedup_columns = [column for column in stream_data_source.deduplication_column_names]
    if dedup_columns:
        df = df.dropDuplicates(dedup_columns)

    return df


def _get_watermark(stream_data_source: StreamDataSource) -> str:
    """Returns watermark as an "N seconds" string for the streaming data source.

    :param stream_data_source: StreamDataSource proto.

    :return: The watermark duration in seconds in string format.
    :rtype: String
    """
    return "{} seconds".format(stream_data_source.stream_config.watermark_delay_threshold.seconds)


def _get_initial_stream_position(stream_data_source: StreamDataSource) -> Optional[str]:
    """Returns initial stream position as a string (e.g. "latest") for the streaming data source.

    :param stream_data_source: StreamDataSource proto.

    :return: The initial stream position in string format.
    """
    return INITIAL_STREAM_POSITION_ENUM_TO_STR[stream_data_source.stream_config.initial_stream_position]


# should not be invoked directly by public SDK. Use TectonContext wrapper instead
def register_temp_views_for_feature_definition(
    spark: SparkSession,
    feature_definition: FeatureDefinition,
    data_sources: List[VirtualDataSource],
    register_stream: bool,
    raw_data_time_limits: Optional[pendulum.Period] = None,
):
    """Registers spark temp views per DataSource based on a FeatureView proto.

    :param spark: Spark session.
    :param feature_definition: FeatureDefinition interface implementing class.
    :param data_sources: Data source protos
    :param register_stream: If true, a stream DataFrame will be registered for streaming DSs instead of batch.
    :param raw_data_time_limits: The raw data time limits for the batch data source.
    """
    ds_by_id = {IdHelper.to_string(ds.virtual_data_source_id): ds for ds in data_sources}

    for ds_id in feature_definition.data_source_ids:
        register_temp_view_for_data_source(
            spark,
            ds_by_id[ds_id],
            register_stream,
            raw_data_time_limits=raw_data_time_limits,
        )


# should not be invoked directly by public SDK. Use TectonContext wrapper instead
def register_temp_view_for_data_source(
    spark: SparkSession,
    data_source: VirtualDataSource,
    register_stream: bool,
    raw_data_time_limits: Optional[pendulum.Period] = None,
    name: str = None,
    called_for_schema_computation: bool = False,
):
    """Registers a spark temp view for the data source.
    :param spark: Spark session.
    :param data_source: DataSource proto.
    :param register_stream: If true, a stream DataFrame will be registered for streaming DataSources instead of batch.
    :param raw_data_time_limits: If set, a data frame will filter on the time limits based on any partition columns that exist.
    :param name: If set, use this name for the temp view. Defaults to DS name.
    :param called_for_schema_computation: Indicates if method is being invoked to compute a schema.
    """
    df = get_ds_dataframe(
        spark,
        data_source,
        register_stream,
        raw_data_time_limits=raw_data_time_limits,
        called_for_schema_computation=called_for_schema_computation,
    )
    df.createOrReplaceTempView(data_source.fco_metadata.name if name is None else name)


def get_ds_dataframe(
    spark: SparkSession,
    data_source: VirtualDataSource,
    consume_streaming_data_source: bool,
    raw_data_time_limits: Optional[pendulum.Period] = None,
    called_for_schema_computation=False,
):
    assert (
        raw_data_time_limits is None or not consume_streaming_data_source
    ), "Can't specify time limits when conduming streaming data source"

    if consume_streaming_data_source:
        assert data_source.HasField(
            "stream_data_source"
        ), f"Can't consume streaming data source from the BatchDataSource: {data_source.fco_metadata.name}."
        df = get_stream_dataframe_with_options(spark, data_source.stream_data_source)
    else:
        df = get_table_dataframe(
            spark, data_source.batch_data_source, called_for_schema_computation=called_for_schema_computation
        )
        if data_source.HasField("stream_data_source"):
            schema = data_source.stream_data_source.spark_schema
            cols = [field.name for field in schema.fields]
            df = df.select(*cols)
        if raw_data_time_limits is not None:
            df = apply_partition_and_timestamp_filter(df, data_source.batch_data_source, raw_data_time_limits)

    return df


def convert_json_like_schema_to_glue_format(spark: SparkSession, df: DataFrame) -> DataFrame:
    """
    Converts a DataFrame schema to lowercase. This assumes JSON so
    MapTypes or Arrays of non-StructTypes are not allowed.

    :param spark: Spark session.
    :param df: DataFrame input.
    :return: DataFrame with lowercase schema.
    """

    def _get_lowercase_schema(datatype):
        if type(datatype) == ArrayType:
            return _get_lowercase_array_schema(datatype)
        elif type(datatype) == StructType:
            return _get_lowercase_structtype_schema(datatype)
        elif type(col.dataType) == MapType:
            raise TypeError("MapType not supported in JSON schema")
        return datatype

    def _get_lowercase_structtype_schema(s) -> StructType:
        assert type(s) == StructType, f"Invalid argument type {type(s)}, expected StructType"
        struct_fields = []
        for col in s:
            datatype = _get_lowercase_schema(col.dataType)
            struct_fields.append(StructField(col.name.lower(), datatype))
        return StructType(struct_fields)

    def _get_lowercase_array_schema(c) -> ArrayType:
        assert (
            type(c.elementType) == StructType
        ), f"Invalid ArrayType element type {type(c)}, expected StructType for valid JSON arrays."
        datatype = c.elementType
        struct_schema = _get_lowercase_structtype_schema(datatype)
        return ArrayType(struct_schema)

    # Simple columns (LongType, StringType, etc) can just be renamed without
    # casting schema.
    # Nested fields within complex columns (ArrayType, StructType) must also be recursively converted
    # to lowercase names, so they must be casted.
    # DateType columns should be converted to StringType to match Glue schemas.
    new_fields = []
    for col in df.schema:
        if type(col.dataType) in [ArrayType, StructType, MapType]:
            t = _get_lowercase_schema(col.dataType)
            new_fields.append(functions.col(col.name).cast(t).alias(col.name.lower()))
        elif type(col.dataType) is DateType:
            new_fields.append(functions.col(col.name).cast(StringType()).alias(col.name.lower()))
        else:
            new_fields.append(functions.col(col.name).alias(col.name.lower()))
    return df.select(new_fields)
