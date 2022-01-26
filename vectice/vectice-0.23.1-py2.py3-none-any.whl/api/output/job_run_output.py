from dataclasses import dataclass, InitVar
from datetime import datetime
from typing import Optional

from vectice.models import JobRun
from .job_output import JobOutput


@dataclass
class __Output:
    createdDate: datetime
    updatedDate: datetime
    version: int
    id: int
    description: Optional[str]
    authorId: int
    duration: int
    metadataSource: str
    systemName: Optional[str]
    jobId: int
    deletedDate: Optional[datetime]
    job: InitVar[dict]
    name: Optional[str]

    def __post_init__(self, job: dict):
        self.job = JobOutput(**job)


@dataclass
class JobRunOutput(JobRun, __Output):
    pass
