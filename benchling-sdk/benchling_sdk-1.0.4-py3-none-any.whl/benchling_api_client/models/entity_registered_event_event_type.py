from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class EntityRegisteredEventEventType(Enums.KnownString):
    V2_ENTITYREGISTERED = "v2.entity.registered"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "EntityRegisteredEventEventType":
        if not isinstance(val, str):
            raise ValueError(f"Value of EntityRegisteredEventEventType must be a string (encountered: {val})")
        newcls = Enum("EntityRegisteredEventEventType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(EntityRegisteredEventEventType, getattr(newcls, "_UNKNOWN"))
