import typing as T
from ...types import Message
from abc import ABC, abstractmethod
from dbt.contracts.results import TimingInfo

Tags = T.Optional[T.Union[T.List, T.Dict]]


class BaseMonitor(ABC):
    common_tags = []

    @abstractmethod
    def initialize(self):
        raise NotImplementedError()

    def increment(self, name: str, value: int = 1, tags: Tags = None, sample_rate: float = 1):
        raise NotImplementedError()

    def decrement(self, name: str, value: int = 1, tags: Tags = None, sample_rate: float = 1):
        pass

    def timed(self, name: str, tags: Tags = None, sample_rate: float = 1, use_ms: bool = None):
        pass

    def timing(self, name: str, value: float, tags: Tags = None, sample_rate: float = 1):
        pass

    def _format_tags(self, tags: Tags):
        # For safety
        if isinstance(tags, dict):
            dd_tags = []
            for key in tags.keys():
                # Only keep top level keys
                if isinstance(tags[key], (dict, list)):
                    continue
                dd_tags.append(f'{key}:{tags[key]}')

            return dd_tags

        if isinstance(tags, list):
            return tags

        if isinstance(tags, str):
            return [tags]

        return []

    def _merge_tags(self, tags: Tags):
        formatted_tags = self._format_tags(tags)
        common_tags = self._format_tags(self.common_tags)
        if common_tags and formatted_tags:
            return list(set(common_tags + formatted_tags))

        if common_tags:
            return common_tags

        if formatted_tags:
            return formatted_tags

        return None

    def report_detailed_timing(self, timing: T.List[TimingInfo], tags: Tags = None):
        if len(timing) < 1:
            return

        for timer in timing:
            execution_time = (timer.completed_at - timer.started_at).total_seconds()
            self.timing(f'dbt.{timer.name}.time',
                        execution_time, tags=self._merge_tags(tags))

    def report_execution_time(self, execution_time: float, tags: Tags = None):
        return self.timing('dbt.run.time', execution_time, tags=self._merge_tags(tags))

    def report_freshness_age(self, age: float, tags: Tags = None):
        return self.timing('dbt.freshness.age', age, tags=self._merge_tags(tags))

    def report_rows_moved(self, rows: int, tags: Tags = None):
        metric_name = 'dbt.rows.moved'
        return self.increment(metric_name, rows, tags=self._merge_tags(tags))

    def report(self, msg: Message):
        raise NotImplementedError()
