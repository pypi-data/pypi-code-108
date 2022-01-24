from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from vectice.models import dataset


@dataclass
class __Output:
    id: int
    pattern: str
    isPatternBase: str
    createdDate: datetime
    updatedDate: datetime
    deletedDate: Optional[datetime]
    connectionId: int
    createdByUserId: int
    projectId: int
    workspaceId: int
    version: str


@dataclass
class DatasetOutput(dataset.Dataset, __Output):
    pass
