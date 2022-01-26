from vectice.entity._versioned_entity import VersionedEntity


class UserDeclaredVersion(VersionedEntity):
    @property
    def name(self) -> str:
        return str(self["name"])

    @property
    def version_number(self) -> int:
        return int(self["versionNumber"])

    @property
    def user_version(self) -> int:
        return int(self["userVersion"])

    @property
    def uri(self) -> int:
        return int(self["uri"])

    @property
    def is_favorite(self) -> bool:
        return bool(self["isFavourite"])
