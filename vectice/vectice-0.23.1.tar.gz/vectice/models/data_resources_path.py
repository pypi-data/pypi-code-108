from dataclasses import dataclass
from typing import Optional


@dataclass
class DataResourcePath:
    id: Optional[str]
    parentId: Optional[str]
    path: str
    uri: Optional[str]
    uniqueId: Optional[str]
    type: Optional[str]
    isFolder: Optional[bool]
