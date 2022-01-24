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
from th2_grpc_common.common_pb2 import MessageGroupBatch

import th2_common.schema.metrics.common_metrics as common_metrics
from th2_common.schema.message.impl.rabbitmq.abstract_rabbit_batch_subscriber import AbstractRabbitBatchSubscriber, \
    Metadata
from th2_common.schema.util.util import get_debug_string_group, get_session_alias_and_direction_group


class RabbitMessageGroupBatchSubscriber(AbstractRabbitBatchSubscriber):
    INCOMING_MSG_GROUP_BATCH_QUANTITY = Counter('th2_mq_incoming_msg_group_batch_quantity',
                                                'Quantity of incoming message group batches',
                                                common_metrics.DEFAULT_LABELS)
    INCOMING_MSG_GROUP_QUANTITY = Counter('th2_mq_incoming_msg_group_quantity',
                                          'Quantity of incoming message groups',
                                          common_metrics.DEFAULT_LABELS)
    MSG_GROUP_PROCESSING_TIME = Histogram('th2_mq_msg_group_processing_time',
                                          'Time of processing message groups',
                                          buckets=common_metrics.DEFAULT_BUCKETS)

    def get_delivery_counter(self) -> Counter:
        return self.INCOMING_MSG_GROUP_BATCH_QUANTITY

    def get_content_counter(self) -> Counter:
        return self.INCOMING_MSG_GROUP_QUANTITY

    def get_processing_timer(self) -> Histogram:
        return self.MSG_GROUP_PROCESSING_TIME

    def extract_count_from(self, batch: MessageGroupBatch):
        return len(batch.groups)

    def get_messages(self, batch) -> list:
        return batch.groups

    def extract_metadata(self, message) -> Metadata:
        raise ValueError

    @staticmethod
    def value_from_bytes(body):
        message_group_batch = MessageGroupBatch()
        message_group_batch.ParseFromString(body)
        return [message_group_batch]

    def extract_labels(self, batch):
        return get_session_alias_and_direction_group(self.get_messages(batch)[0].messages[0])

    def to_trace_string(self, value):
        return MessageToJson(value)

    def to_debug_string(self, value):
        return get_debug_string_group(value)
