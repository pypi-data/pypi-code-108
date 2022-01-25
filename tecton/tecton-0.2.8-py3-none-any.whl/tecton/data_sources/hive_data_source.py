from typing import Callable
from typing import List
from typing import Optional

from tecton.data_sources.base_data_source import BaseBatchDataSource
from tecton.data_sources.datetime_partition_column import DatetimePartitionColumn
from tecton_proto.args import data_source_pb2
from tecton_proto.args import virtual_data_source_pb2
from tecton_spark import function_serialization


class HiveDSConfig(BaseBatchDataSource):
    """
    Configuration used to reference a Hive table.

    The HiveDSConfig class is used to create a reference to a Hive Table.

    This class used as an input to a :class:`BatchDataSource`'s parameter ``batch_ds_config``. This class is not
    a Tecton Object: it is a grouping of parameters. Declaring this class alone will not register a data source.
    Instead, declare as part of ``BatchDataSource`` that takes this configuration class instance as a parameter.
    """

    def __init__(
        self,
        table: str,
        database: str,
        date_partition_column: str = None,
        timestamp_column_name: str = None,
        timestamp_format: str = None,
        skip_validation=False,
        datetime_partition_columns: List[DatetimePartitionColumn] = None,
        raw_batch_translator=None,
    ):
        """
        Instantiates a new HiveDSConfig.

        :param table: A table registered in Hive MetaStore.
        :param database: A database registered in Hive MetaStore.
        :param date_partition_column: (Optional) Partition column name in case the raw data is partitioned by date, otherwise None.
        :param datetime_partition_columns: (Optional) List of DatetimePartitionColumn the raw data is partitioned by, otherwise None.
        :param timestamp_column_name: Name of timestamp column.
        :param timestamp_format: (Optional) Format of string-encoded timestamp column (e.g. "yyyy-MM-dd'T'hh:mm:ss.SSS'Z'")
        :param raw_batch_translator: Python user defined function f(DataFrame) -> DataFrame that takes in raw
                                     PySpark data source DataFrame and translates it to the DataFrame to be
                                     consumed by the Feature View. See an example of
                                     raw_batch_translator in the `User Guide`_.

        :return: A HiveDSConfig class instance.

        .. _User Guide: https://docs.tecton.ai/v2/overviews/framework/data_sources.html

        Example of a HiveDSConfig declaration:

        .. code-block:: python

            from tecton import HiveDSConfig
            import pyspark

            def convert_temperature(df: pyspark.sql.DataFrame) -> pyspark.sql.DataFrame:
                from pyspark.sql.functions import udf,col
                from pyspark.sql.types import DoubleType

                # Convert the incoming PySpark DataFrame temperature Celsius to Fahrenheit
                udf_convert = udf(lambda x: x * 1.8 + 32.0, DoubleType())
                converted_df = df.withColumn("Fahrenheit", udf_convert(col("Temperature"))).drop("Temperature")
                return converted_df

            # declare a HiveDSConfig instance, which can be used as a parameter to a BatchDataSource
            batch_ds_config=HiveDSConfig(database='global_temperatures',
                                        table='us_cities',
                                        timestamp_column_name='timestamp',
                                        raw_batch_translator=convert_temperature)

        """
        self._args = prepare_hive_ds_args(
            table=table,
            database=database,
            date_partition_column=date_partition_column,
            timestamp_column_name=timestamp_column_name,
            timestamp_format=timestamp_format,
            skip_validation=skip_validation,
            datetime_partition_columns=datetime_partition_columns,
            raw_batch_translator=raw_batch_translator,
        )

    def _merge_batch_args(self, data_source_args: virtual_data_source_pb2.VirtualDataSourceArgs):
        data_source_args.hive_ds_config.CopyFrom(self._args)


def prepare_hive_ds_args(
    *,
    table: str,
    database: str,
    date_partition_column: Optional[str],
    timestamp_column_name: Optional[str],
    timestamp_format: Optional[str],
    skip_validation: bool,
    datetime_partition_columns: Optional[List[DatetimePartitionColumn]],
    raw_batch_translator: Optional[Callable],
):
    args = data_source_pb2.HiveDataSourceArgs()
    args.table = table
    args.database = database
    if date_partition_column:
        args.date_partition_column = date_partition_column
    if timestamp_column_name:
        args.timestamp_column_name = timestamp_column_name
    if timestamp_format:
        args.timestamp_format = timestamp_format
    args.skip_validation = skip_validation

    if datetime_partition_columns:
        for column in datetime_partition_columns:
            column_args = data_source_pb2.DatetimePartitionColumnArgs()
            column_args.column_name = column.column_name
            column_args.datepart = column.datepart
            column_args.zero_padded = column.zero_padded
            args.datetime_partition_columns.append(column_args)
    if raw_batch_translator is not None:
        args.raw_batch_translator.CopyFrom(function_serialization.to_proto(raw_batch_translator))

    return args
