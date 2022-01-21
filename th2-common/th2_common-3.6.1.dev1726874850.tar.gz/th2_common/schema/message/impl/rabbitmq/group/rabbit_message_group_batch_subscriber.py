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

from google.protobuf.json_format import MessageToJson
from prometheus_client import Counter, Histogram, Gauge
from th2_grpc_common.common_pb2 import MessageGroupBatch

import th2_common.schema.metrics.common_metrics as common_metrics
from th2_common.schema.message.impl.rabbitmq.abstract_rabbit_batch_subscriber import AbstractRabbitBatchSubscriber, \
    Metadata
from th2_common.schema.util.util import get_debug_string_group, get_session_alias_and_direction_group, get_sequence
from th2_common.schema.metrics.metric_utils import update_dropped_metrics as util_dropped
from th2_common.schema.metrics.metric_utils import update_total_metrics as util_total


class RabbitMessageGroupBatchSubscriber(AbstractRabbitBatchSubscriber):

    INCOMING_MSG_QUANTITY = Counter('th2_message_subscribe_total',
                                    'Amount of received messages',
                                    common_metrics.DEFAULT_LABELS+(common_metrics.DEFAULT_MESSAGE_TYPE_LABEL_NAME, ))
    INCOMING_MSG_GROUP_QUANTITY = Counter('th2_message_group_subscribe_total',
                                          'Amount of received message groups',
                                          common_metrics.DEFAULT_LABELS)
    INCOMING_MSG_SEQUENCE = Gauge('th2_message_group_sequence_subscribe',
                                  'Last received sequence',
                                  common_metrics.DEFAULT_LABELS)
    INCOMING_MSG_DROPPED_QUANTITY = Counter('th2_message_dropped_subscribe_total',
                                            'Amount of messages dropped after filters',
                                            common_metrics.DEFAULT_LABELS+(common_metrics.DEFAULT_MESSAGE_TYPE_LABEL_NAME, ))
    INCOMING_MSG_GROUP_DROPPED_QUANTITY = Counter('th2_message_group_dropped_subscribe_total',
                                                  'Amount of message groups dropped after filters',
                                                  common_metrics.DEFAULT_LABELS)

    _th2_type = 'MESSAGE_GROUP'

    def update_dropped_metrics(self, batch):
        util_dropped(batch, self.th2_pin, self.INCOMING_MSG_DROPPED_QUANTITY, self.INCOMING_MSG_GROUP_DROPPED_QUANTITY)

    def get_messages(self, batch) -> list:
        return batch.groups

    def extract_metadata(self, message) -> Metadata:
        raise ValueError

    @staticmethod
    def value_from_bytes(body):
        message_group_batch = MessageGroupBatch()
        message_group_batch.ParseFromString(body)
        return message_group_batch

    def to_trace_string(self, value):
        return MessageToJson(value)

    def to_debug_string(self, value):
        return get_debug_string_group(value)

    def update_total_metrics(self, batch):
        util_total(batch, self.th2_pin, self.INCOMING_MSG_QUANTITY, self.INCOMING_MSG_GROUP_QUANTITY, self.INCOMING_MSG_SEQUENCE)
