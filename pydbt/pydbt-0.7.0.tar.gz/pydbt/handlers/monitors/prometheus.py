from ...config import ENV
from ...types import Message
from .base import BaseMonitor, Tags
from prometheus_client import (
    CollectorRegistry,
    Histogram,
    Counter,
    Summary,
    push_to_gateway,
)


class PrometheusMonitor(BaseMonitor):
    labels = [
        "database",
        "schema",
        "name",
        "resource_type",
        "command",
        "version",
        "env",
    ]

    def __init__(self, host: str, port: str, **kwargs):
        self.host = host
        self.port = port
        self.common_tags = {**kwargs.get("common_tags", {}), **{"env": ENV}}

    def _merge_tags(self, tags: Tags):
        if tags:
            return {**tags, **self.common_tags}

        return self.common_tags

    def initialize(self):
        self.registry = CollectorRegistry()

        self.row_counter = Counter(
            "dbt_rows_moved",
            "Records the number of rows moved",
            self.labels,
            registry=self.registry,
        )

        self.run_time = Summary(
            "dbt_run_time_seconds",
            "Records the time it takes to complete a full dbt run",
            labelnames=self.labels,
            registry=self.registry,
        )
        self.exec_time = Histogram(
            "dbt_execution_time_seconds",
            "Records the time it takes to execute a dbt job",
            labelnames=self.labels,
            registry=self.registry,
        )
        self.freshness = Histogram(
            "dbt_freshness_seconds",
            "Records how fresh a source is",
            labelnames=self.labels,
            registry=self.registry,
        )

    def _get_labels(self, tags: Tags):
        result = []
        if isinstance(tags, dict):
            tags = self._merge_tags(tags)
            for lbl in self.labels:
                result.append(tags.get(lbl, "unknown"))
        return result

    def timed(
        self, name: str, tags: Tags = {}, sample_rate: float = 1, use_ms: bool = None
    ):
        labels = self._get_labels(tags)
        return self.run_time.labels(*labels).time()

    def report_execution_time(self, execution_time: float, tags: Tags):
        labels = self._get_labels(tags)
        return self.exec_time.labels(*labels).observe(execution_time)

    def report_freshness_age(self, age: float, tags: Tags):
        labels = self._get_labels(tags)
        return self.freshness.labels(*labels).observe(age)

    def report_rows_moved(self, rows: int, tags: Tags):
        labels = self._get_labels(tags)
        return self.row_counter.labels(*labels).inc(rows)

    def report(self, msg: Message):
        if msg.reporting and msg.reporting.timing:
            self.report_detailed_timing(msg.reporting.timing, tags=msg.context)

        if msg.reporting and msg.reporting.execution_time:
            self.report_execution_time(msg.reporting.execution_time, tags=msg.context)

        if msg.reporting and msg.reporting.freshness:
            self.report_freshness_age(msg.reporting.freshness.age, tags=msg.context)

        if msg.reporting and msg.reporting.rows:
            self.report_rows_moved(msg.reporting.rows, tags=msg.context)

        return push_to_gateway(f"{self.host}:{self.port}", "dbt", self.registry)
