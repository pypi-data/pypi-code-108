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


from th2_grpc_common.common_pb2 import MessageGroupBatch

from th2_common.schema.message.configuration.message_configuration import QueueConfiguration
from th2_common.schema.message.impl.rabbitmq.connection.connection_manager import ConnectionManager
from th2_common.schema.message.impl.rabbitmq.group.rabbit_message_group_batch_queue import RabbitMessageGroupBatchQueue
from th2_common.schema.message.impl.rabbitmq.router.abstract_rabbit_batch_message_router import \
    AbstractRabbitBatchMessageRouter
from th2_common.schema.message.message_queue import MessageQueue
from th2_common.schema.message.queue_attribute import QueueAttribute


class RabbitMessageGroupBatchRouter(AbstractRabbitBatchMessageRouter):

    def send(self, message, *queue_attr):
        for group in message.groups:
            for anymsg in group.messages:
                if anymsg.HasField('raw_message'):
                    msg = anymsg.raw_message
                elif anymsg.HasField('message'):
                    msg = anymsg.message
                book = msg.metadata.id.book_name
                if book == '':
                    if self.box_configuration is None or self.box_configuration.book_name is None:
                        raise Exception('Book name is undefined both explicitly in message IDs and implicitly in box configuration')
                    book = self.box_configuration.book_name
                    msg.metadata.id.book_name = book
        super().send(message, *queue_attr)

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

    def _create_queue(self, connection_manager: ConnectionManager,
                      queue_configuration: QueueConfiguration) -> MessageQueue:
        return RabbitMessageGroupBatchQueue(connection_manager, queue_configuration)
