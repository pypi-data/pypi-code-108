from dataclasses import dataclass, InitVar
from datetime import datetime
from typing import Optional

from vectice.models import model_version
from .model_output import ModelOutput


@dataclass
class __Output:
    createdDate: datetime
    updatedDate: datetime
    id: int
    versionNumber: int
    name: str
    description: Optional[str]
    uri: Optional[str]
    authorId: int
    deletedDate: Optional[datetime]
    modelId: int
    isStarred: str
    originId: Optional[int]
    model: InitVar[dict]

    def __post_init__(self, model: dict):
        self.model = ModelOutput(**model)


@dataclass
class ModelVersionOutput(model_version.ModelVersion, __Output):
    pass
