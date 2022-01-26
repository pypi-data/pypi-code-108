from vectice.entity._base_entity import BaseEntity


class Dataset(BaseEntity):
    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def job_artifact_type(self) -> str:
        return str(self["jobArtifactType"])

    @property
    def pattern(self) -> str:
        return str(self["pattern"])

    @property
    def is_pattern_base(self) -> bool:
        return bool(self["isPatternBase"])

    @property
    def connection_id(self) -> int:
        return int(self["connectionId"])

    @property
    def created_by_user_id(self) -> int:
        return int(self["createdByUserId"])

    @property
    def workspace_id(self) -> int:
        return int(self["workspaceId"])

    @property
    def project_id(self) -> int:
        return int(self["projectId"])

    @property
    def creation_date(self) -> str:
        return str(self["creationDate"])

    @property
    def update_date(self) -> str:
        return str(self["updateDate"])

    @property
    def delete_date(self) -> str:
        return str(self["deleteDate"])

    @property
    def is_deleted(self) -> bool:
        return bool(self["isDeleted"])
