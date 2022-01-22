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

from th2_grpc_common.common_pb2 import RawMessageBatch, RawMessage

from th2_common.schema.message.configuration.message_configuration import QueueConfiguration
from th2_common.schema.message.impl.rabbitmq.connection.connection_manager import ConnectionManager
from th2_common.schema.message.impl.rabbitmq.raw.rabbit_raw_batch_queue import RabbitRawBatchQueue
from th2_common.schema.message.impl.rabbitmq.router.abstract_rabbit_batch_message_router import \
    AbstractRabbitBatchMessageRouter
from th2_common.schema.message.message_queue import MessageQueue
from th2_common.schema.message.queue_attribute import QueueAttribute


class RabbitRawBatchRouter(AbstractRabbitBatchMessageRouter):

    @property
    def required_subscribe_attributes(self):
        return {QueueAttribute.SUBSCRIBE.value, QueueAttribute.RAW.value}

    @property
    def required_send_attributes(self):
        return {QueueAttribute.PUBLISH.value, QueueAttribute.RAW.value}

    def _get_messages(self, batch: RawMessageBatch) -> list:
        return batch.messages

    def _create_batch(self):
        return RawMessageBatch()

    def _add_message(self, batch: RawMessageBatch, message: RawMessage):
        batch.messages.append(message)

    def _create_queue(self, connection_manager: ConnectionManager,
                      queue_configuration: QueueConfiguration) -> MessageQueue:
        return RabbitRawBatchQueue(connection_manager, queue_configuration)
