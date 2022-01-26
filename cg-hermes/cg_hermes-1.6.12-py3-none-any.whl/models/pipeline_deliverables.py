from typing import FrozenSet, List, Optional

from pydantic import BaseModel, validator

from .tags import CGTag

# Classes to represent file entries in the deliverables files


class FileBase(BaseModel):
    """Definition for elements in deliverables file"""

    path: str
    tag: Optional[str]
    id: str


class MipFile(FileBase):
    """Definition for elements in MIP deliverables"""

    format: str
    path_index: Optional[str]
    step: str


class MicrosaltFile(FileBase):
    """Definition for elements in Microsalt deliverables"""

    format: str
    step: str


class MutantFile(FileBase):
    """Definition for elements in Mutant deliverables"""

    format: str
    step: str


class BalsamicFile(FileBase):
    """Definition of elements in balsamic deliverables"""

    format: Optional[str]
    tag: List[str]

    @validator("tag", pre=True)
    def split_str(cls, v):
        if isinstance(v, str):
            return v.split(",")
        return v


# Classes to represent deliverable files


class PipelineDeliverables(BaseModel):
    """Specification for a general deliverables file"""

    files: List[FileBase]


class MipDeliverables(PipelineDeliverables):
    """Specification for a MIP specific deliverables file"""

    files: List[MipFile]


class MicrosaltDeliverables(PipelineDeliverables):
    """Specification for a MIP specific deliverables file"""

    files: List[MicrosaltFile]


class BalsamicDeliverables(PipelineDeliverables):
    """Specification for a BALSAMIC specific deliverables file"""

    files: List[BalsamicFile]


class FluffyDeliverables(PipelineDeliverables):
    """Specification for a FLUFFY specific deliverables file"""

    files: List[FileBase]


class MutantDeliverables(PipelineDeliverables):
    """Specification for a MUTANT specific deliverables file"""

    files: List[MutantFile]


class CGDeliverables(PipelineDeliverables):
    """Class that specifies the output to CG"""

    pipeline: str
    bundle_id: str
    files: List[CGTag]


class TagBase(BaseModel):
    """Internal mapping of deliverable file content"""

    tags: FrozenSet[str]
    subject_id: str
    path: str
    path_index: Optional[str]
