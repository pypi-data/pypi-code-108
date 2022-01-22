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


from th2_common.schema.filter.strategy.impl.default_filter_strategy import DefaultFilterStrategy
from th2_common.schema.message.configuration.message_configuration import QueueConfiguration
from th2_common.schema.message.impl.rabbitmq.abstract_rabbit_queue import AbstractRabbitQueue
from th2_common.schema.message.impl.rabbitmq.configuration.subscribe_target import SubscribeTarget
from th2_common.schema.message.impl.rabbitmq.connection.connection_manager import ConnectionManager
from th2_common.schema.message.impl.rabbitmq.group.rabbit_message_group_batch_sender import \
    RabbitMessageGroupBatchSender
from th2_common.schema.message.impl.rabbitmq.group.rabbit_message_group_batch_subscriber import \
    RabbitMessageGroupBatchSubscriber
from th2_common.schema.message.message_sender import MessageSender
from th2_common.schema.message.message_subscriber import MessageSubscriber


class RabbitMessageGroupBatchQueue(AbstractRabbitQueue):

    def create_sender(self, connection_manager: ConnectionManager,
                      queue_configuration: QueueConfiguration) -> MessageSender:
        return RabbitMessageGroupBatchSender(connection_manager, queue_configuration.exchange,
                                             queue_configuration.routing_key)

    def create_subscriber(self, connection_manager: ConnectionManager,
                          queue_configuration: QueueConfiguration) -> MessageSubscriber:
        subscribe_target = SubscribeTarget(queue_configuration.queue, queue_configuration.routing_key)
        return RabbitMessageGroupBatchSubscriber(connection_manager,
                                                 queue_configuration,
                                                 DefaultFilterStrategy(),
                                                 subscribe_target)
