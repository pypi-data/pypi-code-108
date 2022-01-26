from enum import Enum

from vectice.entity._user_declared_version import UserDeclaredVersion


class DatasetVersion(UserDeclaredVersion):
    @property
    def version_type(self) -> str:
        return str(self["versionType"])

    @property
    def dataset_id(self) -> int:
        return int(self["dataSetId"])

    @property
    def version_folder_id(self) -> str:
        return str(self["versionFolderId"])

    @property
    def origin_id(self) -> int:
        return int(self["originId"])


class DatasetVersionType(Enum):
    UNKNOWN = "UNKNOWN"
    USER_DECLARED = "USER_DECLARED"
    AUTO_VERSION = "AUTO_VERSION"
