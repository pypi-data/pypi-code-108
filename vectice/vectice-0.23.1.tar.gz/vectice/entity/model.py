from enum import Enum

from vectice.entity._versioned_entity import VersionedEntity


class Model(VersionedEntity):
    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def type(self) -> str:
        return str(self["type"])

    @property
    def repository(self) -> str:
        return str(self["repository"])

    @property
    def workspace_id(self) -> int:
        return int(self["workspaceId"])

    @property
    def project_id(self) -> int:
        return int(self["projectId"])


class ModelType(Enum):
    ANOMALY_DETECTION = "ANOMALY_DETECTION"
    CLASSIFICATION = "CLASSIFICATION"
    CLUSTERING = "CLUSTERING"
    OTHER = "OTHER"
    RECOMMENDATION_MODELS = "RECOMMENDATION_MODELS"
    REGRESSION = "REGRESSION"
    TIME_SERIES = "TIME_SERIES"
