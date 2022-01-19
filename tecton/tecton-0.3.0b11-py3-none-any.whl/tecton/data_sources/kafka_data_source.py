from typing import Dict
from typing import Optional

from tecton.data_sources.base_data_source_config import BaseStreamDSConfig
from tecton_proto.args import data_source_pb2
from tecton_proto.args import virtual_data_source_pb2
from tecton_spark import function_serialization
from tecton_spark.time_utils import strict_pytimeparse


class KafkaDSConfig(BaseStreamDSConfig):
    """
    Configuration used to reference a Kafka stream.

    The KafkaDSConfig class is used to create a reference to a Kafka stream.

    This class used as an input to a :class:`StreamDataSource`'s parameter ``stream_ds_config``. This class is not
    a Tecton Object: it is a grouping of parameters. Declaring this class alone will not register a data source.
    Instead, declare as part of ``StreamDataSource`` that takes this configuration class instance as a parameter.

    """

    def __init__(
        self,
        kafka_bootstrap_servers: str,
        topics: str,
        raw_stream_translator,
        timestamp_key: str,
        default_watermark_delay_threshold: str = None,
        options: Optional[Dict[str, str]] = None,
        ssl_keystore_location: Optional[str] = None,
        ssl_keystore_password_secret_id: Optional[str] = None,
        ssl_truststore_location: Optional[str] = None,
        ssl_truststore_password_secret_id: Optional[str] = None,
        security_protocol: Optional[str] = None,
    ):
        """
        Instantiates a new KafkaDSConfig.

        :param kafka_bootstrap_servers: A comma-separated list of the Kafka bootstrap server addresses. Passed directly
                                        to the Spark ``kafka.bootstrap.servers`` option.
        :param topics: A comma-separated list of Kafka topics to subscribe to. Passed directly to the Spark ``subscribe``
                       option.
        :param raw_stream_translator: Python user defined function f(DataFrame) -> DataFrame that takes in raw
                                      Pyspark data source DataFrame and translates it to the DataFrame to be
                                      consumed by the Feature View. See an example of
                                      raw_stream_translator in the `User Guide`_.
        :param timestamp_key: Name of the column containing timestamp for watermarking.
        :param default_watermark_delay_threshold: (Optional) Watermark time interval, e.g: "24 hours", used by Spark Structured Streaming to account for late-arriving data. See: https://docs.tecton.ai/v2/overviews/framework/feature_views/stream_feature_view.html#productionizing-a-stream
        :param options: (Optional) A map of additional Spark readStream options
        :param ssl_keystore_location: An DBFS (Databricks only) or S3 URI that points to the keystore file that should be used for SSL brokers. Note for S3 URIs, this must be configured by your Tecton representative.
            Example: ``s3://tecton-${cluster_name}/kafka-credentials/kafka_client_keystore.jks``
            Example: ``dbfs:/kafka-credentials/kafka_client_keystore.jks``
        :param ssl_keystore_password_secret_id: The config key for the password for the Keystore.
            Should start with ``SECRET_``, example: ``SECRET_KAFKA_PRODUCTION``.
        :param ssl_truststore_location: An DBFS (Databricks only) or S3 URI that points to the truststore file that should be used for SSL brokers. Note for S3 URIs, this must be configured by your Tecton representative. If not provided, the default truststore for your compute provider will be used. Note that this is required for AWS-signed keystores on Databricks.
            Example: ``s3://tecton-${cluster_name}/kafka-credentials/kafka_client_truststore.jks``
            Example: ``dbfs:/kafka-credentials/kafka_client_truststore.jks``
        :param ssl_truststore_password_secret_id (Optional): The config key for the password for the Truststore.
            Should start with ``SECRET_``, example: ``SECRET_KAFKA_PRODUCTION``.
        :param security_protocol: (Optional) Security protocol passed to kafka.security.protocol. See Kafka documentation for valid values.

        :return: A KafkaDSConfig class instance.

        .. _User Guide: https://docs.tecton.ai/v2/overviews/framework/data_sources.html

        Example of a KafkaDSConfig declaration:

        .. code-block:: python

            import pyspark
            from tecton import KafkaDSConfig


            def raw_data_deserialization(df:pyspark.sql.DataFrame) -> pyspark.sql.DataFrame:
                from pyspark.sql.functions import from_json, col
                from pyspark.sql.types import StringType, TimestampType

                PAYLOAD_SCHEMA = (
                  StructType()
                        .add("accountId", StringType(), False)
                        .add("transaction_id", StringType(), False)
                )

                EVENT_ENVELOPE_SCHEMA = (
                  StructType()
                        .add("timestamp", TimestampType(), False)
                        .add("payload", PAYLOAD_SCHEMA, False)
                )

                value = col("value").cast("string")
                df = df.withColumn("event", from_json(value, EVENT_ENVELOPE_SCHEMA))
                df = df.withColumn("accountId", col("event.payload.accountId"))
                df = df.withColumn("transaction_id", col("event.payload.transaction_id"))
                df = df.withColumn("timestamp", col("event.timestamp"))

                return df

            # Declare Kafka DSConfig instance object that can be used as an argument in StreamDataSource
            click_stream_kafka_ds = KafkaDSConfig(default_watermark_delay_threshold="7 days",
                                        kafka_bootstrap_servers="127.0.0.1:12345",
                                        topics="click-events-json",
                                        timestamp_key="click_event_timestamp",
                                        raw_stream_translator=raw_data_deserialization)
        """
        self._args = args = data_source_pb2.KafkaDataSourceArgs()
        args.kafka_bootstrap_servers = kafka_bootstrap_servers
        args.topics = topics
        args.raw_stream_translator.CopyFrom(function_serialization.to_proto(raw_stream_translator))
        args.timestamp_key = timestamp_key
        if default_watermark_delay_threshold:
            args.default_watermark_delay_threshold.FromSeconds(strict_pytimeparse(default_watermark_delay_threshold))
        for key in sorted((options or {}).keys()):
            option = data_source_pb2.Option()
            option.key = key
            option.value = options[key]
            args.options.append(option)
        if ssl_keystore_location:
            args.ssl_keystore_location = ssl_keystore_location
        if ssl_keystore_password_secret_id:
            args.ssl_keystore_password_secret_id = ssl_keystore_password_secret_id
        if ssl_truststore_location:
            args.ssl_truststore_location = ssl_truststore_location
        if ssl_truststore_password_secret_id:
            args.ssl_truststore_password_secret_id = ssl_truststore_password_secret_id
        if security_protocol:
            args.security_protocol = security_protocol

    def _merge_stream_args(self, data_source_args: virtual_data_source_pb2.VirtualDataSourceArgs):
        data_source_args.kafka_ds_config.CopyFrom(self._args)
