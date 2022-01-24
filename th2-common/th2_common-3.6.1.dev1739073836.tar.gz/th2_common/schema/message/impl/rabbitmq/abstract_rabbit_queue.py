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

from abc import ABC, abstractmethod

from th2_common.schema.exception.router_error import RouterError
from th2_common.schema.message.configuration.message_configuration import QueueConfiguration
from th2_common.schema.message.impl.rabbitmq.connection.connection_manager import ConnectionManager
from th2_common.schema.message.message_queue import MessageQueue
from th2_common.schema.message.message_sender import MessageSender
from th2_common.schema.message.message_subscriber import MessageSubscriber


class AbstractRabbitQueue(MessageQueue, ABC):

    def __init__(self, connection_manager: ConnectionManager, queue_configuration: QueueConfiguration) -> None:
        super().__init__(connection_manager, queue_configuration)
        self.subscriber = None
        self.sender = None

    def get_subscriber(self) -> MessageSubscriber:
        if self.connection_manager is None or self.queue_configuration is None:
            raise RouterError('Queue not yet init')
        if not self.queue_configuration.can_read:
            raise RouterError('Queue can not read')
        with self.subscriber_lock:
            if self.subscriber is None or self.subscriber.is_close():
                self.subscriber = self.create_subscriber(self.connection_manager, self.queue_configuration)
            return self.subscriber

    def get_sender(self) -> MessageSender:
        if self.connection_manager is None or self.queue_configuration is None:
            raise RouterError('Queue not yet init')
        if not self.queue_configuration.can_write:
            raise RouterError('Queue can not write')
        with self.sender_lock:
            if self.sender is None or self.sender.is_close():
                self.sender = self.create_sender(self.connection_manager, self.queue_configuration)
            return self.sender

    def close(self):
        with self.subscriber_lock:
            if self.subscriber is not None and not self.subscriber.is_close():
                self.subscriber.close()
        with self.sender_lock:
            if self.sender is not None and not self.sender.is_close():
                self.sender.close()

    @abstractmethod
    def create_sender(self, connection_manager: ConnectionManager,
                      queue_configuration: QueueConfiguration) -> MessageSender:
        pass

    @abstractmethod
    def create_subscriber(self, connection_manager: ConnectionManager,
                          queue_configuration: QueueConfiguration) -> MessageSubscriber:
        pass
