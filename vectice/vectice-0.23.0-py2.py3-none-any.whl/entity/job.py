from enum import Enum

from vectice.entity._versioned_entity import VersionedEntity


class Job(VersionedEntity):
    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def type(self) -> str:
        return str(self["type"])

    @property
    def workspace_id(self) -> int:
        return int(self["workspaceId"])

    @property
    def project_id(self) -> int:
        return int(self["projectId"])

    @property
    def metadata_source(self) -> str:
        return str(self["metadataSource"])


class JobType(Enum):
    EXTRACTION = "EXTRACTION"
    PREPARATION = "PREPARATION"
    TRAINING = "TRAINING"
    INFERENCE = "INFERENCE"
    DEPLOYMENT = "DEPLOYMENT"
    OTHER = "OTHER"
