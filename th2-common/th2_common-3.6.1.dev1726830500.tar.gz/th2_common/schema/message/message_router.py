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

from th2_common.schema.message.configuration.message_configuration import MessageRouterConfiguration, QueueConfiguration
from th2_common.schema.message.impl.rabbitmq.connection.connection_manager import ConnectionManager
from th2_common.schema.message.message_listener import MessageListener
from th2_common.schema.message.message_sender import MessageSender
from th2_common.schema.message.message_subscriber import MessageSubscriber
from th2_common.schema.message.subscriber_monitor import SubscriberMonitor


class MessageRouter(ABC):
    """
    Interface for send and receive RabbitMQ messages
    """

    def __init__(self, connection_manager: ConnectionManager,
                 configuration: MessageRouterConfiguration) -> None:
        self.configuration = configuration
        self.connection_manager = connection_manager
        self.subscriber_lock = Lock()
        self.sender_lock = Lock()

    @abstractmethod
    def subscribe(self, callback: MessageListener, *queue_attr) -> SubscriberMonitor:
        """
        RabbitMQ queue by intersection schemas queues attributes
        :param callback: listener
        :param queue_attr: queues attributes
        :return: SubscriberMonitor it start listening. Returns None is can not listen this queue
        """
        pass

    @abstractmethod
    def subscribe_all(self, callback: MessageListener, *queue_attr) -> SubscriberMonitor:
        """
        RabbitMQ queues
        :param callback: listener
        :param queue_attr: queues attributes
        :return: SubscriberMonitor it start listening. Returns None is can not listen this queue
        """

    @abstractmethod
    def unsubscribe_all(self):
        """
        Unsubscribe from all queues
        :return:
        """
        pass

    @abstractmethod
    def send(self, message, *queue_attr):
        pass

    @abstractmethod
    def send_all(self, message, *queue_attr):
        pass

    @abstractmethod
    def get_subscriber(self, queue_alias) -> MessageSubscriber:
        pass

    @abstractmethod
    def get_sender(self, queue_alias) -> MessageSender:
        pass

    @abstractmethod
    def close_connection(self, queue_alias):
        pass
