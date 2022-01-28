from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class EntityWorklistItemsListType(Enums.KnownString):
    BIOENTITY = "bioentity"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "EntityWorklistItemsListType":
        if not isinstance(val, str):
            raise ValueError(f"Value of EntityWorklistItemsListType must be a string (encountered: {val})")
        newcls = Enum("EntityWorklistItemsListType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(EntityWorklistItemsListType, getattr(newcls, "_UNKNOWN"))
