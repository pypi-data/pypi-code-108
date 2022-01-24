#  Copyright (c) 2021 DataRobot, Inc. and its affiliates. All rights reserved.
#  Last updated 2021.
#
#  DataRobot, Inc. Confidential.
#  This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.
#  The copyright notice above does not evidence any actual or intended publication of
#  such source code.
#
#  This file and its contents are subject to DataRobot Tool and Utility Agreement.
#  For details, see
#  https://www.datarobot.com/wp-content/uploads/2021/07/DataRobot-Tool-and-Utility-Agreement.pdf.

import configparser
import logging
from os.path import expanduser
import time

from confluent_kafka.cimpl import Producer, Consumer, KafkaException, KafkaError, TopicPartition
from future.moves.urllib.parse import urlparse

from datarobot.mlops.channel.record import Record
from datarobot.mlops.common import config
from datarobot.mlops.common.config import ConfigConstants
from datarobot.mlops.common.enums import SpoolerType, MLOpsSpoolAction
from datarobot.mlops.common.exception import DRSpoolerException, DRCommonException
from datarobot.mlops.spooler.record_spooler import RecordSpooler

logger = logging.getLogger(__name__)


class KafkaRecordSpooler(RecordSpooler):
    # The largest record batch size allowed by Kafka.
    # See `message.max.bytes` https://kafka.apache.org/documentation/
    DEFAULT_KAFKA_MESSAGE_BYTE_SIZE_LIMIT = 1000000
    DEFAULT_KAFKA_CONSUMER_POLL_TIMEOUT_SECONDS = 3
    DEFAULT_KAFKA_CONSUMER_MAX_NUM_MESSAGES = 100

    KAFKA_CONFIG_GENERIC = "all"
    KAFKA_CONFIG_PYTHON_SPECIFIC = "python"

    KAFKA_CONFIG_BOOTSTRAP_SERVERS = "bootstrap.servers"
    KAFKA_CONFIG_GROUP_ID = "group.id"
    KAFKA_CONFIG_RESET_OFFSET = "auto.offset.reset"
    KAFKA_CONFIG_CA_LOCATION = "ssl.ca.location"
    KAFKA_CONFIG_SASL_MECH = "sasl.mechanism"
    KAFKA_CONFIG_SASL_OAUTH_CONF = "sasl.oauthbearer.config"

    KAFKA_PROPERTIES_DEFAULT_LOCATION = expanduser("~/.datarobot-mlops/kafka.conf")

    def __init__(self):
        super(KafkaRecordSpooler, self).__init__()
        self._initialized = False
        self._kafka_producer_config = None
        self._kafka_consumer_config = None
        self._topic_name = None
        self._bootstrap_servers = None
        self._kafka_properties_location = None
        self._consumer = None
        self._producer = None
        self._poll_timeout_seconds = None
        self._max_messages_to_consume = None
        self._dequeue_enabled = False
        self._max_flush_time = None
        self._desired_message_size = None

    def get_type(self):
        return SpoolerType.KAFKA

    def get_required_config(self):
        return [ConfigConstants.KAFKA_TOPIC_NAME, ConfigConstants.KAFKA_BOOTSTRAP_SERVERS]

    def get_optional_config(self):
        return [
            ConfigConstants.KAFKA_CONFIG_LOCATION,
            ConfigConstants.KAFKA_CONSUMER_GROUP_ID,
            ConfigConstants.KAFKA_CONSUMER_MAX_NUM_MESSAGES,
            ConfigConstants.KAFKA_CONSUMER_POLL_TIMEOUT_SECONDS,
            ConfigConstants.KAFKA_MAX_FLUSH_SECONDS,
            ConfigConstants.KAFKA_MESSAGE_BYTE_SIZE_LIMIT,
        ]

    def get_message_byte_size_limit(self):
        return config.get_config_default(ConfigConstants.KAFKA_MESSAGE_BYTE_SIZE_LIMIT,
                                         self.DEFAULT_KAFKA_MESSAGE_BYTE_SIZE_LIMIT)

    def set_config(self):
        self._topic_name = config.get_config(ConfigConstants.KAFKA_TOPIC_NAME)
        self._max_flush_time = \
            config.get_config_default(ConfigConstants.KAFKA_MAX_FLUSH_SECONDS, -1)

        self._desired_message_size = self.get_message_byte_size_limit()

        config_filepath = config.get_config_default(
            ConfigConstants.KAFKA_CONFIG_LOCATION,
            self.KAFKA_PROPERTIES_DEFAULT_LOCATION,
        )

        self._kafka_producer_config = self._read_kafka_client_config(config_filepath)
        # In the event the host OS isn't configured properly and the user didn't provide their own
        # CA bundle, use the certifi bundle.
        if self.KAFKA_CONFIG_CA_LOCATION not in self._kafka_producer_config:
            import certifi
            self._kafka_producer_config[self.KAFKA_CONFIG_CA_LOCATION] = certifi.where()

        bootstrap_servers = self._kafka_producer_config.get(self.KAFKA_CONFIG_BOOTSTRAP_SERVERS)
        if not bootstrap_servers:
            bootstrap_servers = config.get_config(
                ConfigConstants.KAFKA_BOOTSTRAP_SERVERS
            )
            self._kafka_producer_config[self.KAFKA_CONFIG_BOOTSTRAP_SERVERS] = bootstrap_servers

        sasl_mechanism = self._kafka_producer_config.get(self.KAFKA_CONFIG_SASL_MECH, "").upper()
        if sasl_mechanism == "OAUTHBEARER":
            oauth_conf_str = self._kafka_producer_config.get(self.KAFKA_CONFIG_SASL_OAUTH_CONF, "")
            oauth_handler = AzureActiveDirectoryOauthBearer.from_config_str(oauth_conf_str,
                                                                            bootstrap_servers)
            self._kafka_producer_config["oauth_cb"] = oauth_handler

        # NOTE: following consumer configuration is only used for testing
        consumer_group_id = config.get_config_default(ConfigConstants.KAFKA_CONSUMER_GROUP_ID, None)
        if consumer_group_id is not None:
            self._dequeue_enabled = True
            self._kafka_consumer_config = self._kafka_producer_config.copy()
            self._kafka_consumer_config[self.KAFKA_CONFIG_GROUP_ID] = consumer_group_id
            self._kafka_consumer_config[self.KAFKA_CONFIG_RESET_OFFSET] = "earliest"

    def open(self, action=MLOpsSpoolAction.ENQUEUE):
        self.set_config()
        self._poll_timeout_seconds = config.get_config_default(
            ConfigConstants.KAFKA_CONSUMER_POLL_TIMEOUT_SECONDS,
            self.DEFAULT_KAFKA_CONSUMER_POLL_TIMEOUT_SECONDS,
        )
        self._max_messages_to_consume = config.get_config_default(
            ConfigConstants.KAFKA_CONSUMER_MAX_NUM_MESSAGES,
            self.DEFAULT_KAFKA_CONSUMER_MAX_NUM_MESSAGES,
        )

        try:
            self._producer = Producer(self._kafka_producer_config)
            self._producer.poll(0)  # Make sure oauth callback triggered

            if self._dequeue_enabled:
                self._consumer = Consumer(self._kafka_consumer_config)
                # The subscribe method (an automatic partition assignment) flakes in tests
                # with the UNKNOWN_TOPIC_OR_PART. Manually assign partition to 0.
                self._consumer.assign([TopicPartition(self._topic_name, partition=0)])
                self._consumer.poll(0)  # make sure oauth is initialized

            self._initialized = True

        except Exception:
            logger.error("Failed to initialize Kafka client.", exc_info=True)
            raise DRCommonException

    def close(self):
        if self._producer:
            logger.info("Waiting for all buffered messages to flush...")
            self._producer.flush(self._max_flush_time)
            self._producer = None

        if self._consumer:
            self._consumer.close()
            self._consumer = None

    def enqueue(self, record_list):
        if not self._initialized:
            raise DRSpoolerException("Spooler must be opened before using.")

        logger.debug("Publishing %s records", len(record_list))
        status_list = []

        if len(record_list) < 1:
            return status_list

        for record in record_list:
            try:
                self._publish_single_record(record)

                # The 'status_list' here is used only to obey the RecordSpooler interface.
                # Send status may be obtained only via the blocking operation future.get(),
                # which we can't call on a consumer's thread.
                status_list.append(True)
            except (KafkaException, DRSpoolerException):
                logger.error("Failed to publish a message to Kafka", exc_info=True)
                status_list.append(False)

        logger.debug("Published %s messages", len(status_list))
        return status_list

    def _publish_single_record(self, record):
        record_json = record.to_json()
        record_bytearray = record_json.encode("utf-8")
        record_size = len(record_bytearray)

        if record_size > self._desired_message_size:
            logger.warning("Attempting to enqueue large record: %s bytes", record_size)

        # TODO: convert to generic channel back-pressure interface when available
        for i in range(30):
            try:
                self._producer.produce(
                    self._topic_name,
                    value=record_bytearray,
                    on_delivery=self._delivery_status_callback,
                )
                break  # no need to loop if no error
            except BufferError:
                if i == 0:
                    logger.warning("Local Kafka send buffer is full; backing off...")
                self._producer.poll(0.4)
        else:
            raise DRSpoolerException("Unable to publish record due to full buffer; consider tuning"
                                     " settings in kafka.conf (i.e. `buffer.memory`).")
        # used to trigger delivery report callbacks for previously delivered records
        self._producer.poll(0)

    def dequeue(self):
        if not self._initialized:
            raise DRSpoolerException("Spooler must be opened before using.")

        record_list = []
        try:
            messages = self._consumer.consume(
                num_messages=self._max_messages_to_consume, timeout=self._poll_timeout_seconds)

        except KafkaError:
            logger.error("Unable to dequeue messages.", exc_info=True)
            return record_list

        for msg in messages:
            record = self._read_single_message(msg)
            record_list.append(record)

        return record_list

    def _read_single_message(self, msg):

        if msg is None:
            logger.debug("Consumer assigned to topics: %s", self._consumer.assignment())
            return None

        logger.debug(
            "Received message from topic %s partition [%s] @ offset %s",
            msg.topic(), msg.partition(), msg.offset()
        )

        if msg.error():
            # skip broker messages about an empty queue
            if msg.error().code() != KafkaError._PARTITION_EOF:
                logger.error(msg.error())
            return None

        try:
            msg_bytes = msg.value()
            message_json = msg_bytes.decode("utf-8")
            record = Record.from_json(message_json)
        except UnicodeDecodeError:
            logger.error("Unable to deserialize message", exc_info=True)
            return None

        return record

    def _read_kafka_client_config(self, filepath):

        def get_config_section(config, section):
            try:
                return dict(config.items(section))
            except configparser.NoSectionError:
                return {}

        kafka_config = configparser.RawConfigParser()
        kafka_config.read(filepath)

        generic_config = get_config_section(kafka_config, self.KAFKA_CONFIG_GENERIC)
        python_specific_config = get_config_section(kafka_config, self.KAFKA_CONFIG_PYTHON_SPECIFIC)
        return {**generic_config, **python_specific_config}

    def _delivery_status_callback(self, err, msg):
        if err is not None:
            # TODO: other than this log message, this is more or less a silent error in that we
            #       don't bubble it up to the upstream code to try and deal with (i.e. retry)
            logger.error("Failed to deliver message: %s", err)
        else:
            logger.debug(
                "Produced record to topic %s partition [%s] @ offset %s",
                msg.topic(), msg.partition(), msg.offset()
            )

    def __dict__(self):
        return {
            ConfigConstants.SPOOLER_TYPE: SpoolerType.KAFKA,
            ConfigConstants.KAFKA_TOPIC_NAME: self._topic_name,
            ConfigConstants.KAFKA_BOOTSTRAP_SERVERS: self._bootstrap_servers,
            ConfigConstants.KAFKA_MAX_FLUSH_SECONDS: self._max_flush_time,
        }


class AzureActiveDirectoryOauthBearer(object):
    AUTHORITY_TEMPLATE = "https://login.microsoftonline.com/{}/"
    AAD_TENANT_ID = "aad.tenant.id"
    AAD_CLIENT_ID = "aad.client.id"
    AAD_CLIENT_SECRET = "aad.client.secret"

    def __init__(self, tenant_id, client_id, client_secret, scopes):
        # Delay import since the dep is optional as only Azure Event Hubs users will want to use
        # this auth method.
        try:
            import msal
        except ImportError:
            message = ("Azure Active Directory Authentication failed; missing package; "
                       "need to pip install msal>=0.6.1<2")
            raise RuntimeError(message)

        authority = self.AUTHORITY_TEMPLATE.format(tenant_id)
        self.app = msal.ConfidentialClientApplication(
            client_id,
            authority=authority,
            client_credential=client_secret,
        )
        self.scopes = scopes

    @classmethod
    def from_config_str(cls, config_string, bootstrap_servers):
        oauthbearer_config = dict(x.strip().split("=") for x in config_string.split(","))
        logger.debug("Parsed config str: %s", oauthbearer_config)

        _bootstrap_server = bootstrap_servers.split(",")[0].strip()
        logger.debug("Parsed bootstrap server: %s", _bootstrap_server)
        _uri = urlparse("https://" + _bootstrap_server)
        scope = "{}://{}/.default".format(_uri.scheme, _uri.hostname)
        logger.debug("Generated scope: %s", scope)
        return cls(tenant_id=oauthbearer_config[cls.AAD_TENANT_ID],
                   client_id=oauthbearer_config[cls.AAD_CLIENT_ID],
                   client_secret=oauthbearer_config[cls.AAD_CLIENT_SECRET],
                   scopes=[scope])

    def __call__(self, _config):
        """
        Note here value of _config comes from sasl.oauthbearer.config below.
        It is not used in this this case.
        """
        # Firstly, looks up a token from cache
        # Since we are looking for token for the current app, NOT for an end user,
        # notice we give account parameter as None.
        result = self.app.acquire_token_silent(self.scopes, account=None)
        if not result:
            logging.info("No suitable token exists in cache. Let's get a new one from AAD.")
            result = self.app.acquire_token_for_client(self.scopes)

        if "access_token" in result:
            logger.debug("Access token %s... (expires %s)",
                         result["access_token"][:10], result["expires_in"])
            return result["access_token"], time.time() + float(result["expires_in"])
        else:
            logging.debug(result)
            msg = "Failed to get Auth from Active Directory:\n{}".format(
                result["error_description"]
            )
            raise RuntimeError(msg)
