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
from prometheus_client import Counter
from th2_grpc_common.common_pb2 import EventBatch

from th2_common.schema.message.impl.rabbitmq.abstract_rabbit_sender import AbstractRabbitSender
import th2_common.schema.metrics.common_metrics as common_metrics
from th2_common.schema.metrics.metric_utils import update_total_metrics
from th2_common.schema.util.util import get_debug_string_event


class EventBatchSender(AbstractRabbitSender):
    OUTGOING_EVENT_QUANTITY = Counter('th2_event_publish_total',
                                      'Quantity of outgoing events',
                                      (common_metrics.DEFAULT_TH2_PIN_LABEL_NAME, ))

    _TH2_TYPE = 'EVENT'

    def send(self, message):
        self.OUTGOING_EVENT_QUANTITY.labels(self.th2_pin).inc(len(message.events))
        super().send(message)

    def get_events(self, batch: EventBatch) -> list:
        return batch.events

    @staticmethod
    def value_to_bytes(value: EventBatch):
        return value.SerializeToString()

    def to_trace_string(self, value):
        return MessageToJson(value)

    def to_debug_string(self, value):
        return get_debug_string_event(value)
