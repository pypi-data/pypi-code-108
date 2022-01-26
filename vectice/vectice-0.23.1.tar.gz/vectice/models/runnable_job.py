from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from .job import Job
from .job_run import JobRun


@dataclass
class RunnableJob:
    job: Job
    run: JobRun

    def with_property(self, key: str, value: str) -> RunnableJob:
        self.run.with_property(key, value)
        return self

    def with_properties(self, properties: List[Tuple[str, str]]) -> RunnableJob:
        self.run.with_properties(properties)
        return self

    def with_tag(self, key: str, value: str) -> RunnableJob:
        self.run.with_tag(key, value)
        return self
