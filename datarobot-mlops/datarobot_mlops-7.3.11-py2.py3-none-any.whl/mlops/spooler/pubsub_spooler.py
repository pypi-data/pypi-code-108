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

from google.api_core.exceptions import AlreadyExists
from google.cloud import pubsub_v1
import logging
import sys
import time

from datarobot.mlops.channel.record import Record
from datarobot.mlops.common import config
from datarobot.mlops.common.config import ConfigConstants
from datarobot.mlops.common.enums import SpoolerType
from datarobot.mlops.common.exception import DRSpoolerException
from datarobot.mlops.spooler.record_spooler import RecordSpooler

futures = dict()
published_messages = 0


class PubSubRecordSpooler(RecordSpooler):
    # PubSub has max 10MB message size limit
    # Note: the limit is 10,000,000 not 10 * 1024 * 1024
    PUBSUB_MESSAGE_SIZE_LIMIT_IN_BYTE = 1000 * 1000 * 10

    # Note that dequeue is only used by tests
    PUBSUB_MAX_RECORDS_TO_DEQUEUE = 10

    def __init__(self):
        super(PubSubRecordSpooler, self).__init__()
        self._logger = logging.getLogger(PubSubRecordSpooler.__name__)
        self.initialized = False

        self._project_id = None
        self._topic_name = None
        self._max_flush_time = None
        self._subscription_name = None

        self._full_topic_name = None
        self._publisher = None
        self._dequeue_enabled = False
        self._subscriber = None
        self._full_subscription_name = None

        self._last_connect_time = 0

        if sys.version_info < (3, 0):
            self._logger.error("PubSub only supports Python3.")
            raise Exception("PubSub only supports Python 3.")

    @staticmethod
    def get_type():
        return SpoolerType.PUBSUB

    def get_required_config(self):
        return [ConfigConstants.PUBSUB_PROJECT_ID, ConfigConstants.PUBSUB_TOPIC_NAME]

    def get_optional_config(self):
        return [ConfigConstants.PUBSUB_MAX_FLUSH_SECONDS, ConfigConstants.PUBSUB_SUBSCRIPTION_NAME]

    def set_config(self):
        missing = super(PubSubRecordSpooler, self).get_missing_config()
        if len(missing) > 0:
            raise DRSpoolerException("Configuration values missing: {}".format(missing))

        data_format_str = config.get_config_default(
            ConfigConstants.SPOOLER_DATA_FORMAT, self.JSON_DATA_FORMAT_STR
        )
        if data_format_str != self.JSON_DATA_FORMAT_STR:
            raise DRSpoolerException("Data Format: '{}' is not support for the PubSub Spooler"
                                     .format(data_format_str))

        self._project_id = config.get_config(ConfigConstants.PUBSUB_PROJECT_ID)
        self._topic_name = config.get_config(ConfigConstants.PUBSUB_TOPIC_NAME)
        self._max_flush_time = \
            config.get_config_default(ConfigConstants.PUBSUB_MAX_FLUSH_SECONDS, -1)

        # NOTE: subscription_name is only used for testing
        self._subscription_name = \
            config.get_config_default(ConfigConstants.PUBSUB_SUBSCRIPTION_NAME, None)

        self._full_topic_name = "projects/{project_id}/topics/{topic}".format(
            project_id=self._project_id, topic=self._topic_name)

        # dequeue/subscribe is only needed for testing
        if self._subscription_name is not None:
            self._dequeue_enabled = True

            self._full_subscription_name = "projects/{project_id}/subscriptions/{sub}".format(
                project_id=self._project_id, sub=self._subscription_name)
            self._logger.info("PubSub full subscription name is {}"
                              .format(self._full_subscription_name))
        else:
            self._logger.info("No subscription name provided. Dequeue will not be supported.")

    def open(self):
        self.set_config()

        # create publisher
        self._publisher = pubsub_v1.PublisherClient()

        if self._subscription_name is not None:
            self._subscriber = pubsub_v1.SubscriberClient()

        try:
            self._logger.info("Creating topic {}...".format(self._topic_name))
            self._publisher.create_topic(self._full_topic_name)
            self._logger.info("Created topic {}...".format(self._topic_name))

        except AlreadyExists:
            self._logger.info("Topic {} already exists.".format(self._topic_name))

        # dequeue/subscribe is only needed for testing
        if self._dequeue_enabled:
            self._subscriber = pubsub_v1.SubscriberClient()
            self._logger.info("Creating subscription {}...".format(self._full_subscription_name))
            try:
                self._subscriber.create_subscription(name=self._full_subscription_name,
                                                     topic=self._full_topic_name)
                self._logger.info("Subscription {} created".format(self._full_subscription_name))

            except AlreadyExists:
                self._logger.info("Subscription {} already exists."
                                  .format(self._full_subscription_name))

        self.initialized = True

    # used only for testing
    def delete_subscription(self):
        self._subscriber.delete_subscription(self._full_subscription_name)

    # used only for testing
    def delete_topic(self):
        self._publisher.delete_topic(self._full_topic_name)

    def close(self):
        flush_time_spent = 0
        wait_interval = 5
        while futures:
            self._logger.info("Waiting for {} unacked messages.".format(len(futures)))
            time.sleep(wait_interval)
            flush_time_spent += wait_interval
            if 0 < self._max_flush_time < wait_interval:
                break

    def get_message_byte_size_limit(self):
        return self.PUBSUB_MESSAGE_SIZE_LIMIT_IN_BYTE

    def publish_single_record(self, record):
        if not self.initialized:
            raise DRSpoolerException("Spooler must be opened before using.")

        if not isinstance(record, Record):
            raise DRSpoolerException("Argument of type {} is expected", type(Record))

        record_json = record.to_json()
        record_bytearray = record_json.encode("utf-8")
        record_size = len(record_bytearray)

        # Check size limit
        if record_size > self.get_message_byte_size_limit():
            self._logger.info("Cannot enqueue record of size: {}".format(record_size))
            raise DRSpoolerException(
                "Record size {} over maximum {}.".format(record_size,
                                                         self.get_message_byte_size_limit()))

        futures.update({record_json: None})
        f = self._publisher.publish(self._full_topic_name, record_bytearray)
        futures[record_json] = f
        f.add_done_callback(_get_callback(f, record_json))

    def enqueue(self, record_list):
        if not self.initialized:
            raise DRSpoolerException("Spooler must be opened before using.")

        self._logger.info("Publishing {} records".format(len(record_list)))
        status_list = []

        if len(record_list) < 1:
            return status_list

        for record in record_list:
            try:
                self.publish_single_record(record)
                status = True
            except Exception as e:
                self._logger.info("Exception {}".format(str(e)))
                status = False
            status_list.append(status)
        self._logger.info("Published {} messages, status {}".format(
            len(status_list), status_list
        ))
        return status_list

    # dequeue is only provided for testing
    def dequeue(self):
        if self._dequeue_enabled is False:
            raise DRSpoolerException(" You must provide a subscription name on spooler creation to \
            enable dequeue.")

        if not self.initialized:
            raise DRSpoolerException("Spooler must be opened before using.")

        record_list = []
        response = self._subscriber.pull(self._full_subscription_name,
                                         max_messages=self.PUBSUB_MAX_RECORDS_TO_DEQUEUE)

        for msg in response.received_messages:
            try:
                msg_bytes = msg.message.data
                message_json = msg_bytes.decode("utf-8")
                record = Record.from_json(message_json)
                self._logger.debug("Received message for deployment {}"
                                   .format(record.get_deployment_id()))
                record_list.append(Record.from_json(message_json))
            except Exception as e:
                self._logger.error("Unable to dequeue message: {}".format(e))

        ack_ids = [msg.ack_id for msg in response.received_messages]
        self._logger.debug("Received {} messages.".format(len(ack_ids)))
        if len(ack_ids) > 0:
            self._subscriber.acknowledge(self._full_subscription_name, ack_ids)
        return record_list

    def __dict__(self):
        return {
            ConfigConstants.SPOOLER_TYPE.name: SpoolerType.PUBSUB.name,
            ConfigConstants.PUBSUB_PROJECT_ID.name: self._project_id,
            ConfigConstants.PUBSUB_TOPIC_NAME.name: self._topic_name,
            ConfigConstants.PUBSUB_MAX_FLUSH_SECONDS.name: self._max_flush_time,
            ConfigConstants.PUBSUB_SUBSCRIPTION_NAME.name: self._subscription_name,
        }


def _get_callback(future, data):
    def callback(f):
        try:
            futures.pop(data)
        except Exception:
            print("Received exception {} for {}.".format(f.exception(), data))

    return callback
