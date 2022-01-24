from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from .job_run_status import JobRunStatus
from .with_properties import WithProperties
from .with_tags import WithTags


@dataclass
class JobRun(WithTags, WithProperties):
    startDate: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    """"""
    status: str = JobRunStatus.STARTED
    """"""
    endDate: Optional[datetime] = None
    """"""
    name: Optional[str] = None
    """"""
