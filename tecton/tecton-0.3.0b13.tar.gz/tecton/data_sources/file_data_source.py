from collections.abc import Callable
from typing import Optional

from pyspark.sql.types import StructType

from tecton.data_sources.base_data_source_config import BaseBatchDSConfig
from tecton_proto.args.data_source_pb2 import FileDataSourceArgs
from tecton_proto.args.virtual_data_source_pb2 import VirtualDataSourceArgs
from tecton_spark import function_serialization
from tecton_spark.spark_schema_wrapper import SparkSchemaWrapper


class FileDSConfig(BaseBatchDSConfig):
    """
    Configuration used to reference a file or directory (S3, etc.)

    The FileDSConfig class is used to create a reference to a file or directory of files in S3,
    HDFS, or DBFS.

    The schema of the data source is inferred from the underlying file(s). It can also be modified using the
    ``raw_batch_translator`` parameter.

    This class is used as an input to a :class:`BatchDataSource`'s parameter ``batch_ds_config``. This class is not
    a Tecton Object: it is a grouping of parameters. Declaring this class alone will not register a data source.
    Instead, declare a part of ``BatchDataSource`` that takes this configuration class instance as a parameter.
    """

    def __init__(
        self,
        uri: str,
        file_format: str,
        convert_to_glue_format=False,
        timestamp_column_name: Optional[str] = None,
        timestamp_format: Optional[str] = None,
        raw_batch_translator: Optional[Callable] = None,
        schema_uri: Optional[str] = None,
        schema_override: Optional[StructType] = None,
    ):
        """
        Instantiates a new FileDSConfig.

        :param uri: S3 or HDFS path to file(s).
        :param file_format: File format. "json", "parquet", or "csv"
        :param convert_to_glue_format: Converts all schema column names to lowercase.
        :param timestamp_column_name: Name of timestamp column.
        :param timestamp_format: (Optional) Format of string-encoded timestamp column (e.g. "yyyy-MM-dd'T'hh:mm:ss.SSS'Z'").
                                 If the timestamp string cannot be parsed with this format, Tecton will fallback and attempt to
                                 use the default timestamp parser.
        :param raw_batch_translator: Python user defined function f(DataFrame) -> DataFrame that takes in raw
                                     Pyspark data source DataFrame and translates it to the DataFrame to be
                                     consumed by the Feature View. See an example of
                                     raw_batch_translator in the `User Guide`_.
        :param schema_uri: (Optional) A file or subpath of "uri" that can be used for fast schema inference.
                           This is useful for speeding up plan computation for highly partitioned data sources containing many files.
        :param schema_override: (Optional) a pyspark.sql.types.StructType object that will be used as the schema when
                                reading from the file. If omitted, the schema will be inferred automatically.

        :return: A FileDSConfig class instance.

        .. _User Guide: https://docs.tecton.ai/v2/overviews/framework/data_sources.html

        Example of a FileDSConfig declaration:

        .. code-block:: python

            from tecton import FileDSConfig, BatchDataSource

            def convert_temperature(df):
                from pyspark.sql.functions import udf,col
                from pyspark.sql.types import DoubleType

                # Convert the incoming PySpark DataFrame temperature Celsius to Fahrenheit
                udf_convert = udf(lambda x: x * 1.8 + 32.0, DoubleType())
                converted_df = df.withColumn("Fahrenheit", udf_convert(col("Temperature"))).drop("Temperature")
                return converted_df

            # declare a FileDSConfig, which can be used as a parameter to a `BatchDataSource`
            ad_impressions_file_ds = FileDSConfig(uri="s3://tecton.ai.public/data/ad_impressions_sample.parquet",
                                                file_format="parquet",
                                                timestamp_column_name="timestamp",
                                                raw_batch_translator=convert_temperature)

            # This FileDSConfig can then be included as an parameter a BatchDataSource declaration.
            # For example,
            ad_impressions_batch = BatchDataSource(name="ad_impressions_batch",
                                                   batch_ds_config=ad_impressions_file_ds)

        """
        self._args = prepare_file_ds_args(
            uri=uri,
            file_format=file_format,
            convert_to_glue_format=convert_to_glue_format,
            timestamp_column_name=timestamp_column_name,
            timestamp_format=timestamp_format,
            raw_batch_translator=raw_batch_translator,
            schema_uri=schema_uri,
            schema_override=schema_override,
        )

    def _merge_batch_args(self, data_source_args: VirtualDataSourceArgs):
        data_source_args.file_ds_config.CopyFrom(self._args)


def prepare_file_ds_args(
    *,
    uri: str,
    file_format: str,
    convert_to_glue_format: bool,
    timestamp_column_name: Optional[str],
    timestamp_format: Optional[str],
    raw_batch_translator: Optional[Callable],
    schema_uri: Optional[str],
    schema_override: Optional[StructType],
) -> FileDataSourceArgs:
    args = FileDataSourceArgs()
    args.uri = uri
    args.file_format = file_format
    args.convert_to_glue_format = convert_to_glue_format
    if schema_uri is not None:
        args.schema_uri = schema_uri
    if raw_batch_translator is not None:
        args.raw_batch_translator.CopyFrom(function_serialization.to_proto(raw_batch_translator))
    if timestamp_column_name:
        args.timestamp_column_name = timestamp_column_name
    if timestamp_format:
        args.timestamp_format = timestamp_format
    if schema_override:
        args.schema_override.CopyFrom(SparkSchemaWrapper(schema_override).to_proto())

    return args
