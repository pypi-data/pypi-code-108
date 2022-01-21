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

import asyncio
import functools
import logging
import queue
import threading
import time
from typing import Optional

import pika
from pika.adapters.asyncio_connection import AsyncioConnection
from pika.channel import Channel

logger = logging.getLogger(__name__)


class ReconnectingPublisher(object):
    TIMEOUT_WAIT_CONFIRM_DELIVERY_BY_CLOSE = 10
    TIMEOUT_STOPPING = 5

    def __init__(self, connection_parameters: pika.ConnectionParameters):
        self._connection_parameters = connection_parameters

        self._connection: Optional[AsyncioConnection] = None
        self._channel: Optional[Channel] = None
        self._loop = asyncio.new_event_loop()
        self._not_executed_tasks = queue.Queue(maxsize=1000)

        self._deliveries = []
        self._acked = None
        self._nacked = None
        self._message_number = None

        self._message_lock = threading.Lock()
        self._publishing_allowed = threading.Event()

        self._stopping = False

    def on_connection_open(self, _unused_connection):
        logger.info('Publisher\'s connection has been opened')
        self.open_channel()

    def on_connection_open_error(self, _unused_connection, err):
        self._publishing_allowed.clear()
        logger.error('An error occurred while opening a publisher\'s connection,'
                     ' reopening as soon as possible: %s', err)
        if not self._stopping and not self._connection.is_closed and not self._connection.is_closing:
            self._connection.close()

    def on_connection_closed(self, _unused_connection, reason):
        self._publishing_allowed.clear()
        logger.info('Publisher\'s connection has been closed: %s', reason)
        self._loop.call_soon_threadsafe(self._connection.ioloop.stop)

    def open_channel(self):
        logger.info('Creating a channel for Publisher')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        logger.info('Publisher\'s channel has been opened')
        self._channel = channel
        self._channel.confirm_delivery(self.on_delivery_confirmation)
        self._channel.add_on_close_callback(self.on_channel_closed)
        self._publishing_allowed.set()

    def on_channel_closed(self, channel, reason):
        self._publishing_allowed.clear()
        logger.info('Publisher\'s channel %i has been closed: %s', channel, reason)
        if not self._stopping and not self._connection.is_closed and not self._connection.is_closing:
            self._connection.close()

    def on_delivery_confirmation(self, method_frame):
        with self._message_lock:
            confirmation_type = method_frame.method.NAME.split('.')[1].lower()
            logger.debug('Received %s for delivery tag: %i multi: %s', confirmation_type,
                         method_frame.method.delivery_tag, method_frame.method.multiple)
            cnt = 0
            if method_frame.method.multiple:
                idx = len(self._deliveries) - 1
                while self._deliveries[idx] != method_frame.method.delivery_tag:
                    idx -= 1
                while idx >= 0:
                    self._deliveries.pop(0)
                    cnt += 1
                    idx -= 1
            else:
                cnt += 1
                self._deliveries.remove(method_frame.method.delivery_tag)
            if confirmation_type == 'ack':
                self._acked += cnt
            elif confirmation_type == 'nack':
                self._nacked += cnt

            logger.debug(
                'Published %i messages, %i have yet to be confirmed, '
                '%i were acked and %i were nacked', self._message_number,
                len(self._deliveries), self._acked, self._nacked)

    def publish_message(self, exchange_name, routing_key, message):
        self._publishing_allowed.wait()
        cb = functools.partial(self._basic_publish, exchange_name, routing_key, message)
        while not self._not_executed_tasks.empty():
            self._connection.ioloop.call_soon_threadsafe(self._not_executed_tasks.get())
        while self._stopping:
            # It may be worth throwing an exception here that the connection is closed manually.
            time.sleep(1)
        self._connection.ioloop.call_soon_threadsafe(cb)

    def _basic_publish(self, exchange_name, routing_key, message):
        with self._message_lock:
            if not self._publishing_allowed.is_set():
                cb = functools.partial(self._basic_publish, exchange_name, routing_key, message)
                self._not_executed_tasks.put(cb)
            else:
                self._channel.basic_publish(exchange=exchange_name,
                                            routing_key=routing_key,
                                            body=message)

                self._message_number += 1
                self._deliveries.append(self._message_number)
                logger.debug('Published message # %i', self._message_number)

    def connect(self):
        self._connection = AsyncioConnection(
            self._connection_parameters,
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed,
            custom_ioloop=self._loop)

    def run(self):
        while not self._stopping:
            self._connection = None
            with self._message_lock:
                self._acked = 0
                self._nacked = 0
                self._message_number = 0

            try:
                self.connect()
                logger.info('Publisher\'s Event loop running')
                self._connection.ioloop.run_forever()
                logger.info('Publisher\'s Event loop has been stopped')
            except Exception:
                logger.exception("Error while running Publisher")

    def stop(self):
        logger.info('Publisher stopping')
        self._stopping = True
        logger.info(f'Waiting for the remaining messages to be published for'
                    f' {ReconnectingPublisher.TIMEOUT_STOPPING} sec.')
        # Pull from queue tasks
        time.sleep(ReconnectingPublisher.TIMEOUT_STOPPING)
        deliveries_size = len(self._deliveries)
        wait_counter = 0
        while deliveries_size > 0 and wait_counter <= ReconnectingPublisher.TIMEOUT_WAIT_CONFIRM_DELIVERY_BY_CLOSE:
            logger.info(f'Deliveries size != 0, size={deliveries_size}. Wait confirm delivery '
                        f'{ReconnectingPublisher.TIMEOUT_WAIT_CONFIRM_DELIVERY_BY_CLOSE - wait_counter} sec.')
            time.sleep(1)
            wait_counter += 1
            deliveries_size = len(self._deliveries)
        self.close_channel()
        self.close_connection()

    def close_channel(self):
        if self._channel is not None and not self._channel.is_closing and not self._channel.is_closed:
            logger.info('Closing Publisher\'s channel')
            self._channel.close()

    def close_connection(self):
        if self._connection is not None and not self._connection.is_closing and not self._connection.is_closed:
            logger.info('Closing Publisher\'s connection')
            self._connection.close()
