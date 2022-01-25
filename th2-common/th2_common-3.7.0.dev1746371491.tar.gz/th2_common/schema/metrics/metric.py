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

from abc import ABC

import th2_common.schema.metrics.metric_monitor as metric_monitor


class Metric(ABC):

    enabled: bool = None

    def create_monitor(self, name: str) -> 'metric_monitor.MetricMonitor':
        """
        Creates new monitor for the metric

        :param name: monitor name
        :return: MetricMonitor which can change metrics value
        """
        pass

    def is_enabled(self, monitor: 'metric_monitor.MetricMonitor') -> bool:
        """
        Checks if status of a monitor is `enabled`

        :param monitor: MetricMonitor
        :return: Status (bool) of MetricMonitor
        """
        pass

    def enable(self, monitor: 'metric_monitor.MetricMonitor'):
        """
        Changes status of a monitor to `enabled`

        :param monitor: MetricMonitor
        """
        pass

    def disable(self, monitor: 'metric_monitor.MetricMonitor'):
        """
        Changes status of a monitor to `disabled`

        :param monitor: MetricMonitor
        """
        pass
