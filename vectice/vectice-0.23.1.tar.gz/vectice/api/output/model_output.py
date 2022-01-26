from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from vectice.models import model


@dataclass
class __Output:
    createdDate: datetime
    updatedDate: datetime
    version: int
    id: int
    authorId: int
    workspaceId: int
    projectId: int
    repository: str
    deletedDate: Optional[datetime]


@dataclass
class ModelOutput(model.Model, __Output):
    pass
