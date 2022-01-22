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
from threading import Lock

from th2_common.schema.message.configuration.message_configuration import QueueConfiguration
from th2_common.schema.message.impl.rabbitmq.connection.connection_manager import ConnectionManager
from th2_common.schema.message.message_sender import MessageSender
from th2_common.schema.message.message_subscriber import MessageSubscriber


class MessageQueue(ABC):

    def __init__(self, connection_manager: ConnectionManager, queue_configuration: QueueConfiguration) -> None:
        self.connection_manager = connection_manager
        self.queue_configuration = queue_configuration
        self.subscriber_lock = Lock()
        self.sender_lock = Lock()

    @abstractmethod
    def get_subscriber(self) -> MessageSubscriber:
        pass

    @abstractmethod
    def get_sender(self) -> MessageSender:
        pass

    @abstractmethod
    def close(self):
        pass
