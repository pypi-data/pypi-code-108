#   Copyright 2020-2021 Exactpro (Exactpro Systems Limited)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import datetime
import functools
import logging
import threading
import time
from typing import Dict, Optional

import pika
from pika import SelectConnection
from pika.channel import Channel

from th2_common.schema.message.configuration.message_configuration import ConnectionManagerConfiguration
from th2_common.schema.message.impl.rabbitmq.configuration.rabbitmq_configuration import RabbitMQConfiguration

logger = logging.getLogger(__name__)


class Consumer:

    def __init__(self, parameters: pika.ConnectionParameters, prefetch_count,
                 consuming: Dict[str, bool], subscribers: Dict[str, tuple]):
        self.should_reconnect = False
        self.was_consuming = False

        self._parameters = parameters
        self._prefetch_count = prefetch_count
        self._consuming: Dict[str, bool] = consuming
        self._subscribers: Dict[str, tuple] = subscribers

        self._connection: Optional[SelectConnection] = None
        self._channel: Optional[Channel] = None
        self._closing = False

        self._subscribe_allowed = threading.Event()
        self.subscribers_lock = threading.Lock()

    def connect(self):
        logger.info('Connecting by ReconnectingConsumer')
        return pika.SelectConnection(
            parameters=self._parameters,
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed)

    def on_connection_open(self, _unused_connection):
        logger.info('Consumer\'s connection opened')
        self.open_channel()

    def close_connection(self):
        self._subscribe_allowed.clear()
        for consumer_tag in self._consuming.keys():
            self._consuming[consumer_tag] = False
        if self._connection.is_closing or self._connection.is_closed:
            logger.info('Consumer\'s connection is closing or already closed')
        else:
            logger.info('Closing Consumer\'s connection')
            self._connection.close()

    def on_connection_open_error(self, _unused_connection, err):
        self._subscribe_allowed.clear()
        logger.error('Consumer\'s connection open failed: %s', err)
        self.reconnect()

    def on_connection_closed(self, _unused_connection, reason):
        self._subscribe_allowed.clear()
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            logger.warning('Consumer\'s connection closed, reconnect necessary: %s', reason)
            self.reconnect()

    def reconnect(self):
        self.should_reconnect = True
        self.stop()

    def open_channel(self):
        logger.info('Creating the Consumer\'s channel')
        try:
            self._connection.channel(on_open_callback=self.on_channel_open)
        except Exception:
            logger.exception('An error occurred while creating the Consumer\'s channel ')

    def on_channel_open(self, channel):
        logger.info('Consumer\'s channel opened')
        self._channel = channel
        try:
            self._channel.add_on_close_callback(self.on_channel_closed)
        except Exception:
            logger.exception('An error occurred while adding a callback to close the Consumer\'s channel')
        self.set_qos()

    def on_channel_closed(self, channel, reason):
        self._subscribe_allowed.clear()
        logger.warning('Consumer\'s channel %i was closed: %s', channel, reason)
        self.close_connection()

    def set_qos(self):
        try:
            self._channel.basic_qos(prefetch_count=self._prefetch_count,
                                    callback=self.on_basic_qos_ok)
        except Exception:
            logger.exception('An error occurred when specifying prefetch_count for the Consumer\'s channel')

    def on_basic_qos_ok(self, _unused_frame):
        logger.info('QOS set to: %d', self._prefetch_count)
        try:
            self._channel.add_on_cancel_callback(self.on_consumer_cancelled)
            self._subscribe_allowed.set()
            with self.subscribers_lock:
                for consumer_tag in self._subscribers.keys():
                    self.start_consuming(consumer_tag)
        except Exception:
            logger.exception('An error occurred when executing basic_consume by %s for the Consumer\'s channel')

    def start_consuming(self, consumer_tag):
        if not self._subscribe_allowed.is_set():
            logger.warning('Waiting for the Consumer\'s channel to be ready to execute basic_consume')
        self._subscribe_allowed.wait()
        if not self._consuming[consumer_tag]:
            self._channel.basic_consume(queue=self._subscribers[consumer_tag][0],
                                        consumer_tag=consumer_tag,
                                        on_message_callback=self._subscribers[consumer_tag][1])
            self.was_consuming = True
            self._consuming[consumer_tag] = True

    def on_consumer_cancelled(self, method_frame):
        logger.info('Consumer was cancelled remotely, shutting down: %r', method_frame)
        if self._channel:
            self._channel.close()

    def stop_consuming(self, consumer_tag):
        if self._channel:
            logger.info('Sending a Basic.Cancel RPC command to RabbitMQ for tag: %s', consumer_tag)
            cb = functools.partial(self.on_cancel_ok, userdata=consumer_tag)
            self._channel.basic_cancel(consumer_tag, cb)

    def on_cancel_ok(self, _unused_frame, userdata):
        self._consuming[userdata] = False
        logger.info('RabbitMQ acknowledged the cancellation of the consumer: %s', userdata)
        for consumer_tag in self._consuming.keys():
            if self._consuming[consumer_tag] is True:
                return
        self.close_channel()

    def close_channel(self):
        logger.info('Closing the Consumer channel')
        self._channel.close()

    def run(self):
        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):
        if not self._closing:
            self._closing = True
            logger.info('Stopping ReconnectingConsumer')
            for consumer_tag in self._consuming.keys():
                if self._consuming:
                    self.stop_consuming(consumer_tag)
            else:
                self._connection.ioloop.stop()
            logger.info('Stopped ReconnectingConsumer')

    def add_callback_threadsafe(self, cb):
        self._connection.ioloop.add_callback_threadsafe(cb)


class ReconnectingConsumer(object):
    def __init__(self, configuration: RabbitMQConfiguration,
                 connection_manager_configuration: ConnectionManagerConfiguration,
                 connection_parameters: pika.ConnectionParameters):
        self._configuration: RabbitMQConfiguration = configuration
        self._connection_manager_configuration: ConnectionManagerConfiguration = connection_manager_configuration
        self._connection_parameters: pika.ConnectionParameters = connection_parameters
        self._consuming: Dict[str, bool] = dict()
        self._subscribers: Dict[str, tuple] = dict()
        self._reconnect_delay = 0

        self._subscriber_name = self._connection_manager_configuration.subscriber_name

        self._consumer = Consumer(self._connection_parameters, self._connection_manager_configuration.prefetch_count,
                                  self._consuming, self._subscribers)
        self._is_running = True
        self.__next_id_val = -1
        self.__next_id_lock = threading.Lock()

    def next_id(self):
        with self.__next_id_lock:
            self.__next_id_val += 1
            return self.__next_id_val

    def run(self):
        while self._is_running:
            try:
                self._consumer.run()
            finally:
                self._maybe_reconnect()

    def stop(self):
        self._is_running = False
        self._consumer.should_reconnect = False
        self._consumer.stop()

    def add_subscriber(self, queue, on_message_callback):
        with self._consumer.subscribers_lock:
            if self._subscriber_name is None:
                self._subscriber_name = 'rabbit_mq_subscriber'
                logger.info(f"Using default subscriber name: '{self._subscriber_name}'")
            consumer_tag = f'{self._subscriber_name}.{self.next_id()}.{datetime.datetime.now()}'
            self._subscribers[consumer_tag] = (queue, on_message_callback)
            self._consuming[consumer_tag] = False
            self._consumer.start_consuming(consumer_tag)
            return consumer_tag

    def remove_subscriber(self, consumer_tag):
        with self._consumer.subscribers_lock:
            self._consumer.stop_consuming(consumer_tag)
            self._subscribers.pop(consumer_tag)
            self._consuming.pop(consumer_tag)

    def add_callback_threadsafe(self, cb):
        self._consumer.add_callback_threadsafe(cb)

    def _maybe_reconnect(self):
        if self._consumer.should_reconnect:
            self._consumer.stop()
            reconnect_delay = self._get_reconnect_delay()
            logger.info('Reconnecting consumer after %d seconds', reconnect_delay)
            time.sleep(reconnect_delay)
            self._consumer = Consumer(self._connection_parameters, self._connection_manager_configuration.prefetch_count,
                                      self._consuming, self._subscribers)

    def _get_reconnect_delay(self):
        if self._consumer.was_consuming:
            self._reconnect_delay = 0
        else:
            self._reconnect_delay += 1
        if self._reconnect_delay > 30:
            self._reconnect_delay = 30
        return self._reconnect_delay
