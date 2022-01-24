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

from typing import Tuple

from th2_common.schema.metrics.aggregating_metric import AggregatingMetric
from th2_common.schema.metrics.file_metric import FileMetric
from th2_common.schema.metrics.prometheus_metric import PrometheusMetric

DEFAULT_BUCKETS = [0.000_25, 0.000_5, 0.001, 0.005, 0.010, 0.015, 0.025, 0.050, 0.100, 0.250, 0.500, 1.0]

DEFAULT_SESSION_ALIAS_LABEL_NAME: str = "session_alias"
DEFAULT_DIRECTION_LABEL_NAME: str = "direction"
DEFAULT_LABELS: Tuple[str, str] = (DEFAULT_SESSION_ALIAS_LABEL_NAME, DEFAULT_DIRECTION_LABEL_NAME)
EMPTY_LABELS: Tuple[str, str] = ('', '')
UNKNOWN_LABELS: Tuple[str, str] = ('unknown', 'unknown')

LIVENESS_ARBITER = AggregatingMetric([PrometheusMetric("th2_liveness", "Service liveness"), FileMetric('healthy')])
READINESS_ARBITER = AggregatingMetric([PrometheusMetric("th2_readiness", "Service readiness"), FileMetric('ready')])


def register_liveness(name: str):
    return LIVENESS_ARBITER.create_monitor(name)


def register_readiness(name: str):
    return READINESS_ARBITER.create_monitor(name)


LIVENESS_MONITOR = register_liveness('user_liveness')
READINESS_MONITOR = register_readiness('user_readiness')


class HealthMetrics:

    def __init__(self, obj: object) -> None:
        self.liveness_monitor = register_liveness(f'{obj.__class__.__name__}_liveness_{hash(obj)}')
        self.readiness_monitor = register_readiness(f'{obj.__class__.__name__}_readiness_{hash(obj)}')

    def enable(self):
        self.liveness_monitor.enable()
        self.readiness_monitor.enable()

    def disable(self):
        self.liveness_monitor.disable()
        self.readiness_monitor.disable()
