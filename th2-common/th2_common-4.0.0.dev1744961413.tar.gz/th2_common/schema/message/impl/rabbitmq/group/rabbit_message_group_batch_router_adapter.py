#   Copyright 2021-2022 Exactpro (Exactpro Systems Limited)
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

from th2_common.schema.message.impl.rabbitmq.group.rabbit_message_group_batch_router import \
    RabbitMessageGroupBatchRouter
from abc import ABC, abstractmethod

from th2_common.schema.message.message_listener import MessageListener
from th2_common.schema.message.subscriber_monitor import SubscriberMonitor


class RabbitMessageGroupBatchRouterAdapter(RabbitMessageGroupBatchRouter, ABC):

    def send(self, message, *queue_attr):
        super().send(self.to_group_batch(message), *queue_attr)

    def send_all(self, message, *queue_attr):
        super().send_all(self.to_group_batch(message), *queue_attr)

    def subscribe(self, callback: MessageListener, *queue_attr) -> SubscriberMonitor:
        return super().subscribe(self.get_converter(callback), *queue_attr)

    def subscribe_all(self, callback: MessageListener, *queue_attr) -> SubscriberMonitor:
        return super().subscribe_all(self.get_converter(callback), *queue_attr)

    @staticmethod
    @abstractmethod
    def to_group_batch(message):
        pass

    @staticmethod
    @abstractmethod
    def from_group_batch(message):
        pass

    def get_converter(self, callback: MessageListener):
        return type('MessageListenerConverter', (callback.__class__, ), {'handler': lambda attributes, message: callback.handler(attributes, self.from_group_batch(message))})
