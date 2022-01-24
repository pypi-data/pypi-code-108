#  Copyright (c) 2020 DataRobot, Inc. and its affiliates. All rights reserved.
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

import logging
import pika
from pika.exceptions import AMQPConnectionError
import ssl
import sys
from time import sleep, time

from datarobot.mlops.channel.record import Record
from datarobot.mlops.common import config
from datarobot.mlops.common.config import ConfigConstants
from datarobot.mlops.common.enums import SpoolerType
from datarobot.mlops.common.exception import DRSpoolerException
from datarobot.mlops.spooler.record_spooler import RecordSpooler


class RabbitMQRecordSpooler(RecordSpooler):

    RABBITMQ_MAX_RECORDS_TO_DEQUEUE = 10
    RABBITMQ_MESSAGE_SIZE_LIMIT_IN_BYTE = 1024 * 1024 * 50
    DEFAULT_PUBLISH_ATTEMPTS = 5
    DEFAULT_PUBLISH_INTERVAL = 0.2  # in seconds

    def __init__(self):
        super(RabbitMQRecordSpooler, self).__init__()
        self._logger = logging.getLogger(RabbitMQRecordSpooler.__name__)
        self.publish_attempts = self.DEFAULT_PUBLISH_ATTEMPTS
        self.publish_interval = self.DEFAULT_PUBLISH_INTERVAL
        self.refresh_conn_time = float("inf")
        self._last_connect_time = 0
        self.initialized = False

        self._queue_url = None
        self._queue_name = None
        self._ssl_ca_certificate_path = None
        self._ssl_certificate_path = None
        self._ssl_key_path = None
        self._tls_version = None
        self._enable_ssl = False

        self.rabbitmq_params = None
        self._connection = None
        self._channel = None

    @staticmethod
    def get_type():
        return SpoolerType.RABBITMQ

    def get_required_config(self):
        return [ConfigConstants.RABBITMQ_QUEUE_URL, ConfigConstants.RABBITMQ_QUEUE_NAME]

    def get_optional_config(self):
        return []

    def set_config(self):
        missing = super(RabbitMQRecordSpooler, self).get_missing_config()
        if len(missing) > 0:
            raise DRSpoolerException("Configuration values missing: {}".format(missing))

        data_format_str = config.get_config_default(
            ConfigConstants.SPOOLER_DATA_FORMAT, self.JSON_DATA_FORMAT_STR
        )
        if data_format_str != self.JSON_DATA_FORMAT_STR:
            raise DRSpoolerException("Data Format: '{}' is not support for the RabbitMQ Spooler"
                                     .format(data_format_str))
        self._queue_url = config.get_config(ConfigConstants.RABBITMQ_QUEUE_URL)
        self._queue_name = config.get_config(ConfigConstants.RABBITMQ_QUEUE_NAME)

        self._ssl_ca_certificate_path = config.get_config_default(
            ConfigConstants.RABBITMQ_SSL_CA_CERTIFICATE_PATH, None
        )
        self._ssl_certificate_path = config.get_config_default(
            ConfigConstants.RABBITMQ_SSL_CERTIFICATE_PATH, None
        )
        self._ssl_key_path = config.get_config_default(
            ConfigConstants.RABBITMQ_SSL_KEYFILE_PATH, None
        )
        tls_version_str = config.get_config_default(
            ConfigConstants.RABBITMQ_SSL_TLS_VERSION, "TLSv1.2"
        )
        self._tls_version = self._convert_tls_version(tls_version_str)

        self._enable_ssl = (
                self._ssl_ca_certificate_path and
                self._ssl_certificate_path and
                self._ssl_key_path
        )

        self._validate_url(self._queue_url)
        self.rabbitmq_params = pika.URLParameters(self._queue_url)

        if self._enable_ssl:
            self.rabbitmq_params.ssl_options = {
                "ca_certs": self._ssl_ca_certificate_path,
                "certfile": self._ssl_certificate_path,
                "keyfile": self._ssl_key_path,
            }
            if self._tls_version:
                self.rabbitmq_params.ssl_options["ssl_version"] = self._tls_version

    def open(self):
        self.set_config()
        try:
            self._connection = pika.BlockingConnection(self.rabbitmq_params)
            self._channel = self._connection.channel()
            self._channel.confirm_delivery()
            self._channel.queue_declare(queue=self._queue_name, durable=True)
            self._logger.debug("Successfully connected to {}, using queue: {}".format(
                self._queue_url, self._queue_name
            ))
            self.initialized = True
        except AMQPConnectionError as ex:
            msg = "Fail to establish connection to RabbitMQ: {}".format(ex)
            self._logger.error(msg)
            raise DRSpoolerException(msg)

    def close(self):
        if self._channel and not self._channel.is_closed:
            self._channel.close()

        if self._connection and not self._connection.is_closed:
            self._connection.close()

    def reconnect(self):
        self.close()
        self.open()

    @staticmethod
    def _validate_url(url):
        if not url:
            raise DRSpoolerException("Invalid URL - " + url)

    @staticmethod
    def _convert_tls_version(tls_version_str):
        if tls_version_str == "TLSv1.1":
            return ssl.PROTOCOL_TLSv1_1
        elif tls_version_str == "TLSv1.2":
            return ssl.PROTOCOL_TLSv1_2
        return None

    def get_message_byte_size_limit(self):
        return self.RABBITMQ_MESSAGE_SIZE_LIMIT_IN_BYTE

    def publish_single_message(self, message):
        if not self.initialized:
            raise DRSpoolerException("Spooler must be opened before using.")

        will_reconnect = self._channel is None or (
                time() - self._last_connect_time >= self.refresh_conn_time
        )

        for attempt in range(self.publish_attempts):
            # Sleep before second attempt; Increase sleep time exponentially
            if attempt > 0:
                sleep(attempt * self.publish_interval)

            if will_reconnect:
                try:
                    self.reconnect()
                except pika.exceptions.ProbableAccessDeniedError:
                    # If credentials are invalid, there is no sense to sleep and reconnect
                    self._logger.error(
                        "Access denied error when publishing a message to RabbitMQ"
                    )
                    reason = "access denied"
                    break
                except Exception as ex:
                    self._logger.warning(
                        "Reconnection error when publishing a message to RabbitMQ - {}".format(ex)
                    )
                    reason = "reconnection error"
                    continue

            try:
                if self._channel.basic_publish(
                        exchange="",
                        routing_key=self._queue_name,
                        body=message,
                        properties=pika.BasicProperties(
                            delivery_mode=2,
                        )):
                    return True
                else:
                    self._logger.warning("Delivery confirmation not received")
                    return False
            except pika.exceptions.AMQPConnectionError:
                self._logger.debug("Connection error when publishing a message to RabbitMQ")
                reason = "connection error"
            except pika.exceptions.ChannelClosed:
                self._logger.info("Channel closed when publishing a message to RabbitMQ")
                reason = "channel close"
            except Exception as ex:
                self._logger.warning(
                    "Unexpected exception when publishing a message to RabbitMQ - {}".format(ex)
                )
                reason = "unexpected exception"
                break

            will_reconnect = True

        self._logger.error("Failed to publish a message to RabbitMQ, reason: {}".format(reason))
        return False

    def enqueue(self, record_list):
        self._logger.debug("About to publish {} messages".format(len(record_list)))
        status_list = []

        for record in record_list:
            record_json = record.to_json()

            # Check size limit
            record_size = sys.getsizeof(record_json)
            if record_size > self.get_message_byte_size_limit():
                self._logger.warning("Cannot enqueue record size: {}".format(record_size))
                status_list.append(False)
                continue
            status = self.publish_single_message(record_json)
            status_list.append(status)
        self._logger.debug("Published {} messages, status {}".format(
            len(status_list), status_list
        ))
        return status_list

    def dequeue(self):
        if not self.initialized:
            raise DRSpoolerException("Spooler must be opened before using.")

        record_list = []
        try:
            for _ in range(self.RABBITMQ_MAX_RECORDS_TO_DEQUEUE):
                _, _, body = self._channel.basic_get(self._queue_name, no_ack=True)
                if body is None:
                    break

                record_list.append(Record.from_json(body))
        except Exception as e:
            self._logger.error("Failed to dequeue message from RabbitMQ[{}],"
                               "with error: {}".format(self._queue_url, str(e)))

        return record_list

    def __dict__(self):
        return {
            ConfigConstants.SPOOLER_TYPE.name: SpoolerType.RABBITMQ.name,
            ConfigConstants.RABBITMQ_QUEUE_NAME.name: self._queue_name,
            ConfigConstants.RABBITMQ_QUEUE_URL.name: self._queue_url,
        }
