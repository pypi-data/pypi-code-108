from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class SimpleNotePartType(Enums.KnownString):
    TEXT = "text"
    CODE = "code"
    LIST_BULLET = "list_bullet"
    LIST_NUMBER = "list_number"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "SimpleNotePartType":
        if not isinstance(val, str):
            raise ValueError(f"Value of SimpleNotePartType must be a string (encountered: {val})")
        newcls = Enum("SimpleNotePartType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(SimpleNotePartType, getattr(newcls, "_UNKNOWN"))
