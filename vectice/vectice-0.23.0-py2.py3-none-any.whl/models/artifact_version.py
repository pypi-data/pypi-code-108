from dataclasses import dataclass
from typing import Optional


@dataclass
class ArtifactVersion:
    versionNumber: Optional[int]
    """"""
    versionName: Optional[str]
    """"""
    id: Optional[int]
    """"""
