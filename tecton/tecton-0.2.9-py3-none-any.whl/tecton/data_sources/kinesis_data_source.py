from typing import Dict
from typing import List
from typing import Optional

from tecton.data_sources.base_data_source import BaseStreamDataSource
from tecton_proto.args import data_source_pb2
from tecton_proto.args import virtual_data_source_pb2
from tecton_spark import data_source_helper
from tecton_spark import function_serialization
from tecton_spark.time_utils import strict_pytimeparse


class KinesisDSConfig(BaseStreamDataSource):
    """
    Configuration used to reference a Kinesis stream.

    The KinesisDSConfig class is used to create a reference to an AWS Kinesis stream.

    This class used as an input to a :class:`StreamDataSource`'s parameter ``stream_ds_config``. This class is not
    a Tecton Object: it is a grouping of parameters. Declaring this class alone will not register a data source.
    Instead, declare as part of ``StreamDataSource`` that takes this configuration class instance as a parameter.
    """

    def __init__(
        self,
        stream_name: str,
        region: str,
        raw_stream_translator,
        timestamp_key: str,
        default_initial_stream_position: str,
        default_watermark_delay_threshold: str,
        deduplication_columns: List[str] = None,
        options=None,
    ):
        """
        Instantiates a new KinesisDSConfig.

        :param stream_name: Name of the Kinesis stream.
        :param region: AWS region of the stream, e.g: "us-west-2".
        :param raw_stream_translator: Python user defined function f(DataFrame) -> DataFrame that takes in raw
                                      Pyspark data source DataFrame and translates it to the DataFrame to be
                                      consumed by the Feature View. See an example of
                                      raw_stream_translator in the `User Guide`_.
        :param timestamp_key: Name of the column containing timestamp for watermarking.
        :param default_initial_stream_position: Initial position in stream, e.g: "latest" or "trim_horizon".
                                                More information available in `Spark Kinesis Documentation`_.
        :param default_watermark_delay_threshold: Watermark time interval, e.g: "24 hours", used by Spark Structured Streaming to account for late-arriving data. See: https://docs.tecton.ai/v2/overviews/framework/feature_views/stream_feature_view.html#productionizing-a-stream
        :param deduplication_columns: (Optional) Columns in the stream data that uniquely identify data records.
                                        Used for de-duplicating.
        :param options: (Optional) A map of additional Spark readStream options

        :return: A KinesisDSConfig class instance.

        .. _User Guide: https://docs.tecton.ai/v2/overviews/framework/data_sources.html
        .. _Spark Kinesis Documentation: https://spark.apache.org/docs/latest/streaming-kinesis-integration.html

        Example of a KinesisDSConfig declaration:

        .. code-block:: python

            import pyspark
            from tecton import KinesisDSConfig


            # Define our deserialization raw stream translator
            def raw_data_deserialization(df:pyspark.sql.DataFrame) -> pyspark.sql.DataFrame:
                from pyspark.sql.functions import col, from_json, from_utc_timestamp
                from pyspark.sql.types import StructType, StringType

                payload_schema = (
                  StructType()
                        .add('amount', StringType(), False)
                        .add('isFraud', StringType(), False)
                        .add('timestamp', StringType(), False)
                )

                return (
                    df.selectExpr('cast (data as STRING) jsonData')
                    .select(from_json('jsonData', payload_schema).alias('payload'))
                    .select(
                        col('payload.amount').cast('long').alias('amount'),
                        col('payload.isFraud').cast('long').alias('isFraud'),
                        from_utc_timestamp('payload.timestamp', 'UTC').alias('timestamp')
                    )
                )
            # Declare KinesisDSConfig instance object that can be used as argument in `StreamDataSource`
            stream_ds_config = KinesisDSConfig(
                                    stream_name='transaction_events',
                                    region='us-west-2',
                                    default_initial_stream_position='latest',
                                    default_watermark_delay_threshold='30 minutes',
                                    timestamp_key='timestamp',
                                    raw_stream_translator=raw_data_deserialization,
                                    options={'roleArn': 'arn:aws:iam::472542229217:role/demo-cross-account-kinesis-ro'}
            )
        """

        self._args = prepare_kinesis_ds_args(
            stream_name=stream_name,
            region=region,
            raw_stream_translator=raw_stream_translator,
            timestamp_key=timestamp_key,
            default_initial_stream_position=default_initial_stream_position,
            default_watermark_delay_threshold=default_watermark_delay_threshold,
            deduplication_columns=deduplication_columns,
            options=options,
        )

    def _merge_stream_args(self, data_source_args: virtual_data_source_pb2.VirtualDataSourceArgs):
        data_source_args.kinesis_ds_config.CopyFrom(self._args)


def prepare_kinesis_ds_args(
    *,
    stream_name: str,
    region: str,
    raw_stream_translator,
    timestamp_key: str,
    default_initial_stream_position: Optional[str],
    default_watermark_delay_threshold: Optional[str],
    deduplication_columns: Optional[List[str]],
    options: Optional[Dict[str, str]],
):
    args = data_source_pb2.KinesisDataSourceArgs()
    args.stream_name = stream_name
    args.region = region
    args.raw_stream_translator.CopyFrom(function_serialization.to_proto(raw_stream_translator))
    args.timestamp_key = timestamp_key
    if default_initial_stream_position:
        args.default_initial_stream_position = data_source_helper.INITIAL_STREAM_POSITION_STR_TO_ENUM[
            default_initial_stream_position
        ]
    if default_watermark_delay_threshold:
        args.default_watermark_delay_threshold.FromSeconds(strict_pytimeparse(default_watermark_delay_threshold))
    if deduplication_columns:
        for column_name in deduplication_columns:
            args.deduplication_columns.append(column_name)
    options_ = options or {}
    for key in sorted(options_.keys()):
        option = data_source_pb2.Option()
        option.key = key
        option.value = options_[key]
        args.options.append(option)

    return args
