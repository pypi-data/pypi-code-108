from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class BatchJobStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    PENDING = "PENDING"
    RUNNABLE = "RUNNABLE"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class BatchJobsIn(BaseModel):
    job_status: List[BatchJobStatus] = Field(..., title="Batch job statuses", min_items=1)
