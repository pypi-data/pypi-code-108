from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class FloatFieldDefinitionType(Enums.KnownString):
    FLOAT = "float"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "FloatFieldDefinitionType":
        if not isinstance(val, str):
            raise ValueError(f"Value of FloatFieldDefinitionType must be a string (encountered: {val})")
        newcls = Enum("FloatFieldDefinitionType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(FloatFieldDefinitionType, getattr(newcls, "_UNKNOWN"))
