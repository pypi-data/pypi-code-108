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

from google.protobuf.json_format import MessageToJson
from prometheus_client import Counter, Histogram
from th2_grpc_common.common_pb2 import MessageBatch, MessageGroupBatch

import th2_common.schema.metrics.common_metrics as common_metrics
from th2_common.schema.message.impl.rabbitmq.abstract_rabbit_batch_subscriber import AbstractRabbitBatchSubscriber, \
    Metadata
from th2_common.schema.util.util import get_debug_string, get_session_alias_and_direction


class RabbitParsedBatchSubscriber(AbstractRabbitBatchSubscriber):
    INCOMING_PARSED_MSG_BATCH_QUANTITY = Counter('th2_mq_incoming_parsed_msg_batch_quantity',
                                                 'Quantity of incoming parsed message batches',
                                                 common_metrics.DEFAULT_LABELS)
    INCOMING_PARSED_MSG_QUANTITY = Counter('th2_mq_incoming_parsed_msg_quantity',
                                           'Quantity of incoming parsed messages',
                                           common_metrics.DEFAULT_LABELS)
    PARSED_MSG_PROCESSING_TIME = Histogram('th2_mq_parsed_msg_processing_time',
                                           'Time of processing parsed messages',
                                           buckets=common_metrics.DEFAULT_BUCKETS)

    def get_delivery_counter(self) -> Counter:
        return self.INCOMING_PARSED_MSG_BATCH_QUANTITY

    def get_content_counter(self) -> Counter:
        return self.INCOMING_PARSED_MSG_QUANTITY

    def get_processing_timer(self) -> Histogram:
        return self.PARSED_MSG_PROCESSING_TIME

    def extract_count_from(self, batch: MessageBatch):
        return len(self.get_messages(batch))

    def get_messages(self, batch: MessageBatch) -> list:
        return batch.messages

    def extract_metadata(self, message) -> Metadata:
        metadata = message.metadata
        return Metadata(message_type=metadata.message_type,
                        direction=metadata.id.direction,
                        sequence=metadata.id.sequence,
                        session_alias=metadata.id.connection_id.session_alias)

    @staticmethod
    def value_from_bytes(body):
        message_group_batch = MessageGroupBatch()
        message_group_batch.ParseFromString(body)

        message_batches = []
        for message_group in message_group_batch.groups:
            messages = []
            for any_message in message_group.messages:
                any_message.HasField('message')
                messages.append(any_message.message)
            message_batches.append(MessageBatch(messages=messages))

        return message_batches

    def extract_labels(self, batch):
        return get_session_alias_and_direction(self.get_messages(batch)[0].metadata.id)

    def to_trace_string(self, value):
        return MessageToJson(value)

    def to_debug_string(self, value):
        return get_debug_string(self.__class__.__name__, [message.metadata.id for message in self.get_messages(value)])
