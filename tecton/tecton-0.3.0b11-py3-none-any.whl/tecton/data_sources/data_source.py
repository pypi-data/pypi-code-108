from typing import Dict
from typing import Optional
from typing import Union

from typeguard import typechecked

from tecton._internals.fco import Fco
from tecton.basic_info import prepare_basic_info
from tecton.data_sources.base_data_source_config import BaseBatchDSConfig
from tecton.data_sources.base_data_source_config import BaseStreamDSConfig
from tecton.data_sources.file_data_source import FileDSConfig
from tecton.data_sources.hive_data_source import HiveDSConfig
from tecton.data_sources.kafka_data_source import KafkaDSConfig
from tecton.data_sources.kinesis_data_source import KinesisDSConfig
from tecton.data_sources.redshift_data_source import RedshiftDSConfig
from tecton.data_sources.snowflake_data_source import SnowflakeDSConfig
from tecton_proto.args import virtual_data_source_pb2
from tecton_proto.args.basic_info_pb2 import BasicInfo
from tecton_proto.args.repo_metadata_pb2 import SourceInfo
from tecton_proto.args.virtual_data_source_pb2 import DataSourceType
from tecton_proto.args.virtual_data_source_pb2 import VirtualDataSourceArgs
from tecton_proto.common.id_pb2 import Id
from tecton_spark.id_helper import IdHelper
from tecton_spark.logger import get_logger

logger = get_logger("DataSource")


class BaseDataSource(Fco):
    _args: VirtualDataSourceArgs
    _source_info: SourceInfo

    def _id(self) -> Id:
        return self._args.virtual_data_source_id

    @property
    def name(self) -> str:
        """
        The name of this DataSource.
        """
        return self._args.info.name

    @property
    def timestamp_key(self) -> str:
        """
        The name of the timestamp column or key of this DataSource.
        """
        if self._args.HasField("hive_ds_config"):
            return self._args.hive_ds_config.timestamp_column_name
        if self._args.HasField("redshift_ds_config"):
            return self._args.redshift_ds_config.timestamp_key
        if self._args.HasField("snowflake_ds_config"):
            return self._args.snowflake_ds_config.timestamp_key
        if self._args.HasField("file_ds_config"):
            return self._args.file_ds_config.timestamp_column_name
        else:
            raise Exception(f"Unknown Data Source Type: {self.name}")


class BatchDataSource(BaseDataSource):
    """
    Declare a ``BatchDataSource``, used to read batch data into Tecton.

    ``BatchFeatureViews`` and ``BatchWindowAggregateFeatureViews`` ingest data from a BatchDataSource.
    """

    _args: VirtualDataSourceArgs
    _source_info: SourceInfo

    @typechecked
    def __init__(
        self,
        *,
        name: str,
        description: str = "",
        family: str = "",
        tags: Dict[str, str] = None,
        owner: str = "",
        batch_ds_config: Union[FileDSConfig, HiveDSConfig, RedshiftDSConfig, SnowflakeDSConfig],
    ) -> None:
        """
        Creates a new BatchDataSource

        :param name: An unique name of the DataSource.
        :param description: (Optional) Description.
        :param family: (Optional) Family of this DataSource, used to group Tecton Objects.
        :param tags: (Optional) Tags associated with this Tecton Object (key-value pairs of arbitrary metadata).
        :param owner: Owner name (typically the email of the primary maintainer).
        :param batch_ds_config: BatchDSConfig object containing the configuration of the batch data source to be included
            in this DataSource.

        :return: A :class:`BatchDataSource` class instance.

        Example of a BatchDataSource declaration:

        .. code-block:: python

            from tecton import HiveDSConfig

            # Declare a BatchSource with HiveConfig instance as its batch_ds_config parameter
            # Refer to Configs API documentation other batch_ds_config types.
            credit_scores_batch = BatchDataSource(name='credit_scores_batch',
                                                  batch_ds_config=HiveDSConfig(
                                                        database='demo_fraud',
                                                        table='credit_scores',
                                                        timestamp_column_name='timestamp'),
                                                  family='fraud_detection',
                                                  owner='matt@tecton.ai',
                                                  tags={'release': 'staging',
                                                        'source: 'nexus'})
        """
        from tecton.cli.common import get_fco_source_info

        self._source_info = get_fco_source_info()

        basic_info = prepare_basic_info(name=name, description=description, owner=owner, family=family, tags=tags)
        args = prepare_ds_args(
            basic_info=basic_info, batch_ds_config=batch_ds_config, stream_ds_config=None, ds_type=DataSourceType.BATCH
        )

        self._args = args

        Fco._register(self)


class StreamDataSource(BaseDataSource):
    """
    Declare a ``StreamDataSource``, used to read streaming data into Tecton.

    ``StreamFeatureViews`` and ``StreamWindowAggregateFeatureViews`` ingest data from StreamDataSources.
    A StreamDataSource contains both a batch and a stream data source configs.
    """

    _args: VirtualDataSourceArgs
    _source_info: SourceInfo

    @typechecked
    def __init__(
        self,
        *,
        name: str,
        description: str = "",
        family: str = "",
        tags: Dict[str, str] = None,
        owner: str = "",
        batch_ds_config: Union[FileDSConfig, HiveDSConfig, RedshiftDSConfig, SnowflakeDSConfig],
        stream_ds_config: Union[KinesisDSConfig, KafkaDSConfig],
    ) -> None:
        """
        Creates a new StreamDataSource.

        :param name: An unique name of the DataSource.
        :param description: (Optional) Description.
        :param family: (Optional) Family of this DataSource, used to group Tecton Objects.
        :param tags: (Optional) Tags associated with this Tecton Object (key-value pairs of arbitrary metadata).
        :param owner: Owner name (typically the email of the primary maintainer).
        :param batch_ds_config: BatchDSConfig object containing the configuration of the batch data source that is to be included
            in this DataSource.
        :param stream_ds_config: StreamDSConfig object containing the configuration of the
            stream data source that is to be included in this DataSource.

        :return: A :class:`StreamDataSource` class instance.

        Example of a StreamDataSource declaration:

        .. code-block:: python

         import pyspark
            from tecton import KinesisDSConfig, HiveDSConfig


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

            # Declare a StreamDataSource with both a batch_ds_config and a stream_ds_config as parameters
            # See the API documentation for both BatchDSConfig and StreamDSConfig
            transactions_stream = StreamDataSource(
                                    name='transactions_stream',
                                    stream_ds_config=KinesisDSConfig(
                                        stream_name='transaction_events',
                                        region='us-west-2',
                                        default_initial_stream_position='latest',
                                        default_watermark_delay_threshold='30 minutes',
                                        timestamp_key='timestamp',
                                        raw_stream_translator=raw_data_deserialization,
                                        options={'roleArn': 'arn:aws:iam::472542229217:role/demo-cross-account-kinesis-ro'}
                                    ),
                                    batch_ds_config=HiveDSConfig(
                                        database='demo_fraud',
                                        table='transactions',
                                        timestamp_column_name='timestamp',
                                    ),
                                    family='fraud',
                                    owner='jules@tecton.ai',
                                    tags={'release': 'staging',
                                          'source: 'mobile'})
        """
        from tecton.cli.common import get_fco_source_info

        self._source_info = get_fco_source_info()

        basic_info = prepare_basic_info(name=name, description=description, owner=owner, family=family, tags=tags)
        args = prepare_ds_args(
            basic_info=basic_info,
            batch_ds_config=batch_ds_config,
            stream_ds_config=stream_ds_config,
            ds_type=DataSourceType.STREAM_WITH_BATCH,
        )

        self._args = args

        Fco._register(self)


def prepare_ds_args(
    *,
    basic_info: BasicInfo,
    batch_ds_config: BaseBatchDSConfig,
    stream_ds_config: Optional[BaseStreamDSConfig],
    ds_type: Optional["DataSourceType"],
):
    args = virtual_data_source_pb2.VirtualDataSourceArgs()
    args.virtual_data_source_id.CopyFrom(IdHelper.from_string(IdHelper.generate_string_id()))
    args.info.CopyFrom(basic_info)
    batch_ds_config._merge_batch_args(args)
    if stream_ds_config is not None:
        stream_ds_config._merge_stream_args(args)
    if ds_type:
        args.type = ds_type
    return args
