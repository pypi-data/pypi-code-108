from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, TypeVar

from .job_type import JobType

JobAndChildTypes = TypeVar("JobAndChildTypes", bound="Job")


@dataclass
class Job:
    name: str
    """"""
    type: Optional[str] = JobType.OTHER
    """
    see possible values in py:class:: JobType
    """
    description: Optional[str] = None
    """"""

    def with_description(self: JobAndChildTypes, description: str) -> JobAndChildTypes:
        """"""
        self.description = description
        return self

    def with_type(self: JobAndChildTypes, job_type: str) -> JobAndChildTypes:
        """"""
        self.type = job_type
        return self
