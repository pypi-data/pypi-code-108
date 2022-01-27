#   Copyright 2021-2021 Exactpro (Exactpro Systems Limited)
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

from abc import ABC, abstractmethod
from typing import Set

from th2_common.schema.metrics.metric import Metric
from th2_common.schema.metrics.metric_monitor import MetricMonitor


class AbstractMetric(Metric, ABC):

    __disabled_monitors: Set[MetricMonitor] = set()

    @property
    def enabled(self) -> bool:
        return not self.__disabled_monitors

    def create_monitor(self, name: str) -> MetricMonitor:
        return MetricMonitor(name, self)

    def is_enabled(self, monitor: MetricMonitor) -> bool:
        return monitor not in self.__disabled_monitors

    def enable(self, monitor: MetricMonitor):
        if not self.is_enabled(monitor):
            self.__disabled_monitors.remove(monitor)
            self.on_value_change(self.enabled)

    def disable(self, monitor: MetricMonitor):
        if self.is_enabled(monitor):
            self.__disabled_monitors.add(monitor)
            self.on_value_change(False)

    @abstractmethod
    def on_value_change(self, value: bool):
        pass
