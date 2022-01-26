from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class EntitySchemaContainableType(Enums.KnownString):
    NONE = "NONE"
    ENTITY = "ENTITY"
    BATCH = "BATCH"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "EntitySchemaContainableType":
        if not isinstance(val, str):
            raise ValueError(f"Value of EntitySchemaContainableType must be a string (encountered: {val})")
        newcls = Enum("EntitySchemaContainableType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(EntitySchemaContainableType, getattr(newcls, "_UNKNOWN"))
