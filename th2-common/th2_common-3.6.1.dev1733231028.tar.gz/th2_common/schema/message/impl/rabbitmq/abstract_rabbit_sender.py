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

import logging
from abc import ABC, abstractmethod

from prometheus_client import Counter

from th2_common.schema.message.impl.rabbitmq.connection.connection_manager import ConnectionManager
from th2_common.schema.message.impl.rabbitmq.connection.reconnecting_publisher import ReconnectingPublisher
from th2_common.schema.message.message_sender import MessageSender

logger = logging.getLogger(__name__)


class AbstractRabbitSender(MessageSender, ABC):

    def __init__(self, connection_manager: ConnectionManager, exchange_name: str, send_queue: str) -> None:
        self.__publisher: ReconnectingPublisher = connection_manager.publisher
        self.__exchange_name: str = exchange_name
        self.__send_queue: str = send_queue
        self.__closed = True

    def start(self):
        if self.__send_queue is None or self.__exchange_name is None:
            raise Exception('Sender can not start. Sender did not init')
        self.__closed = False

    def is_close(self) -> bool:
        return self.__closed

    def close(self):
        self.__closed = True

    def send(self, message):
        if message is None:
            raise ValueError('Value for send can not be null')
        try:
            self.__publisher.publish_message(exchange_name=self.__exchange_name,
                                             routing_key=self.__send_queue,
                                             message=self.value_to_bytes(message))

            if logger.isEnabledFor(logging.TRACE):
                logger.trace(f'Sending to exchange_name = "{self.__exchange_name}", '
                             f'routing_key = "{self.__send_queue}", '
                             f'message = {self.to_trace_string(message)}')
            elif logger.isEnabledFor(logging.DEBUG):
                logger.debug(f'Sending to exchange_name = "{self.__exchange_name}", '
                             f'routing_key = "{self.__send_queue}", '
                             f'message = {self.to_debug_string(message)}')

            counter = self.get_delivery_counter()
            counter.inc()
            content_counter = self.get_content_counter()
            content_counter.inc(self.extract_count_from(message))

        except Exception:
            logger.exception('Can not send')

    @staticmethod
    @abstractmethod
    def value_to_bytes(value):
        pass

    @abstractmethod
    def get_delivery_counter(self) -> Counter:
        pass

    @abstractmethod
    def get_content_counter(self) -> Counter:
        pass

    @abstractmethod
    def extract_count_from(self, batch):
        pass

    @abstractmethod
    def to_trace_string(self, value):
        pass

    @abstractmethod
    def to_debug_string(self, value):
        pass
