from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class IntegerFieldDefinitionType(Enums.KnownString):
    INTEGER = "integer"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "IntegerFieldDefinitionType":
        if not isinstance(val, str):
            raise ValueError(f"Value of IntegerFieldDefinitionType must be a string (encountered: {val})")
        newcls = Enum("IntegerFieldDefinitionType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(IntegerFieldDefinitionType, getattr(newcls, "_UNKNOWN"))
