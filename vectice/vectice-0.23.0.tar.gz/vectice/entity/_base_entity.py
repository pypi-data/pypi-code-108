class BaseEntity(dict):
    @property
    def id(self) -> int:
        return int(self["id"])

    @property
    def description(self) -> str:
        return str(self["description"])
