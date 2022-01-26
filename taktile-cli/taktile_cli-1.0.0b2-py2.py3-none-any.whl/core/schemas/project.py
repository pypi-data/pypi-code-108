from typing import List, Union

from pydantic import BaseModel

from tktl.core.t import ProjectAssetSourceT, ProjectAssetT


class ProjectContentsBase(BaseModel):
    type: str
    name: str
    path: str


class ProjectFile(ProjectContentsBase):
    type: str = "file"


class ProjectFileWithContent(ProjectContentsBase):
    type: str = "file"
    content: str


class ProjectDirectory(ProjectContentsBase):
    type: str = "dir"


class ProjectAsset(ProjectContentsBase):
    calculated_sha: str
    kind: ProjectAssetT
    source: ProjectAssetSourceT
    requires_download: bool


class TktlYamlConfigValidationError(BaseModel):
    loc: str
    msg: str


class ProjectValidationOutput(BaseModel):
    title: str
    summary: str
    text: str


ProjectContentSingleItemT = Union[ProjectFile, ProjectDirectory]
ProjectContentMultiItemT = List[ProjectContentSingleItemT]
ProjectContentT = Union[
    ProjectContentSingleItemT, ProjectContentMultiItemT, ProjectFileWithContent
]
