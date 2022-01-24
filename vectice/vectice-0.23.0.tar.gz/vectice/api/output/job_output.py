from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from vectice.models import Job


@dataclass
class __Output:
    createdDate: datetime
    updatedDate: datetime
    version: int
    id: int
    workspaceId: int
    projectId: int
    authorId: int
    metadataSource: str
    deletedDate: Optional[datetime]


@dataclass
class JobOutput(Job, __Output):
    pass
