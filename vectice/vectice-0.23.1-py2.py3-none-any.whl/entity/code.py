from vectice.entity._versioned_entity import VersionedEntity


class Code(VersionedEntity):
    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def uri(self) -> str:
        return str(self["type"])

    @property
    def workspace_id(self) -> int:
        return int(self["workspaceId"])

    @property
    def project_id(self) -> int:
        return int(self["projectId"])
