from enum import Enum

from vectice.entity._user_declared_version import UserDeclaredVersion


class ModelVersion(UserDeclaredVersion):
    @property
    def status(self) -> str:
        return str(self["status"])

    @property
    def algorithm_name(self) -> str:
        return str(self["algorithmName"])

    @property
    def model_id(self) -> int:
        return int(self["modelId"])

    @property
    def origin_id(self) -> int:
        return int(self["originId"])


class ModelVersionStatus(Enum):
    EXPERIMENTATION = "EXPERIMENTATION"
    PRODUCTION = "PRODUCTION"
    STAGING = "STAGING"
