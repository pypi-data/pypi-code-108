from vectice.entity._base_entity import BaseEntity


class VersionedEntity(BaseEntity):
    @property
    def author_id(self) -> int:
        return int(self["authorId"])

    @property
    def version(self) -> int:
        return int(self["version"])

    @property
    def created_date(self) -> str:
        return str(self["createdDate"])

    @property
    def updated_date(self) -> str:
        return str(self["updatedDate"])

    @property
    def deleted_date(self) -> str:
        return str(self["deletedDate"])
