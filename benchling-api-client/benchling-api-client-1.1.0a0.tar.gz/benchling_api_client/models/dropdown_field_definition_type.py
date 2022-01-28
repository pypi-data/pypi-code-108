from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class DropdownFieldDefinitionType(Enums.KnownString):
    DROPDOWN = "dropdown"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "DropdownFieldDefinitionType":
        if not isinstance(val, str):
            raise ValueError(f"Value of DropdownFieldDefinitionType must be a string (encountered: {val})")
        newcls = Enum("DropdownFieldDefinitionType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(DropdownFieldDefinitionType, getattr(newcls, "_UNKNOWN"))
