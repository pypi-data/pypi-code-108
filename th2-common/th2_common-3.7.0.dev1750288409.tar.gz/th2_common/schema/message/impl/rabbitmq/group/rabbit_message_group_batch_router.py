#   Copyright 2020-2022 Exactpro (Exactpro Systems Limited)
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
from prometheus_client import Counter
from th2_grpc_common.common_pb2 import MessageGroupBatch

from th2_common.schema.message.configuration.message_configuration import QueueConfiguration
from th2_common.schema.message.impl.rabbitmq.abstract_rabbit_message_router import AbstractRabbitMessageRouter
from th2_common.schema.message.impl.rabbitmq.configuration.subscribe_target import SubscribeTarget
from th2_common.schema.message.impl.rabbitmq.connection.connection_manager import ConnectionManager
from th2_common.schema.message.impl.rabbitmq.group.rabbit_message_group_batch_sender import \
    RabbitMessageGroupBatchSender
from th2_common.schema.message.impl.rabbitmq.group.rabbit_message_group_batch_subscriber import \
    RabbitMessageGroupBatchSubscriber
from th2_common.schema.message.message_sender import MessageSender
from th2_common.schema.message.message_subscriber import MessageSubscriber
from th2_common.schema.message.queue_attribute import QueueAttribute
import th2_common.schema.metrics.common_metrics as common_metrics
from th2_common.schema.metrics.metric_utils import update_dropped_metrics as dropped_metrics_updater


class RabbitMessageGroupBatchRouter(AbstractRabbitMessageRouter):
    OUTGOING_MSG_DROPPED = Counter('th2_message_dropped_publish_total',
                                   'Quantity of messages dropped on sending',
                                   common_metrics.DEFAULT_LABELS + (common_metrics.DEFAULT_MESSAGE_TYPE_LABEL_NAME, ))
    OUTGOING_MSG_GROUP_DROPPED = Counter('th2_message_group_dropped_publish_total',
                                         'Quantity of message groups dropped on sending',
                                         common_metrics.DEFAULT_LABELS)

    def update_dropped_metrics(self, batch, pins):
        for pin in pins:
            dropped_metrics_updater(batch, pin, self.OUTGOING_MSG_DROPPED, self.OUTGOING_MSG_GROUP_DROPPED)

    @property
    def required_subscribe_attributes(self):
        return {QueueAttribute.SUBSCRIBE.value}

    @property
    def required_send_attributes(self):
        return {QueueAttribute.PUBLISH.value}

    def _get_messages(self, batch):
        return batch.groups

    def _create_batch(self):
        return MessageGroupBatch()

    def _add_message(self, batch: MessageGroupBatch, group):
        batch.groups.append(group)

    def create_sender(self, connection_manager: ConnectionManager,
                      queue_configuration: QueueConfiguration, th2_pin) -> MessageSender:
        return RabbitMessageGroupBatchSender(connection_manager, queue_configuration.exchange,
                                             queue_configuration.routing_key, th2_pin=th2_pin)

    def create_subscriber(self, connection_manager: ConnectionManager,
                          queue_configuration: QueueConfiguration, th2_pin) -> MessageSubscriber:
        subscribe_target = SubscribeTarget(queue_configuration.queue, queue_configuration.routing_key)
        return RabbitMessageGroupBatchSubscriber(connection_manager,
                                                 queue_configuration,
                                                 self.filter_strategy,
                                                 subscribe_target,
                                                 th2_pin=th2_pin)
