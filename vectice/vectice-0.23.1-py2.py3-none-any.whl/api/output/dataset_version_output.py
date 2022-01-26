from dataclasses import dataclass, InitVar
from datetime import datetime
from typing import Optional

from vectice.models import dataset_version
from .dataset_output import DatasetOutput


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
    versionType: str
    dataSetId: int
    versionFolderId: int
    originId: Optional[int]
    isStarred: str
    dataSet: InitVar[dict]

    def __post_init__(self, dataSet: dict):
        self.dataSet = DatasetOutput(**dataSet)


@dataclass
class DatasetVersionOutput(dataset_version.DatasetVersion, __Output):
    pass
