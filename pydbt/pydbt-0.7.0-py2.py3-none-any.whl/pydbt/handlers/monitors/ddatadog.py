from ...types import Message
from ...config import ENV
from .base import BaseMonitor, Tags

from datadog import statsd, initialize
from datadog.dogstatsd.context import TimedContextManagerDecorator


class DatadogMonitor(BaseMonitor):
    def __init__(self, host: str, port: str, **kwargs):
        super(DatadogMonitor, self).__init__()

        self.host = host
        self.port = port
        self.use_ms = False
        self.common_tags = {**kwargs.get('common_tags', {}), **{'env': ENV}}

    def initialize(self):
        return initialize(statsd_host=self.host, statsd_port=self.port, hostname_from_config=False)

    def increment(self, name: str, value: int = 1, tags: Tags = None, sample_rate: float = 1):
        return statsd.increment(name, value, tags=self._merge_tags(tags), sample_rate=sample_rate)

    def decrement(self, name: str, value: int = 1, tags: Tags = None, sample_rate: float = 1):
        return statsd.decrement(name, value, tags=self._merge_tags(tags), sample_rate=sample_rate)

    def timed(self, name: str, tags: Tags = None, sample_rate: float = 1, use_ms: bool = None):
        return TimedContextManagerDecorator(
            self, name, tags=self._merge_tags(tags), sample_rate=sample_rate, use_ms=use_ms)

    def timing(self, name: str, value: int, tags: Tags = None, sample_rate: float = 1):
        return statsd.timing(name, value, tags=self._merge_tags(tags), sample_rate=sample_rate)

    def report(self, msg: Message):
        if msg.reporting and msg.reporting.timing:
            self.report_detailed_timing(msg.reporting.timing, tags=msg.context)

        if msg.reporting and msg.reporting.execution_time:
            self.report_execution_time(msg.reporting.execution_time, tags=msg.context)

        if msg.reporting and msg.reporting.freshness:
            self.report_freshness_age(msg.reporting.freshness.age, tags=msg.context)

        if msg.reporting and msg.reporting.rows:
            self.report_rows_moved(msg.reporting.rows, tags=msg.context)

        return
