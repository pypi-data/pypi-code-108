from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class TableNotePartType(Enums.KnownString):
    TABLE = "table"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "TableNotePartType":
        if not isinstance(val, str):
            raise ValueError(f"Value of TableNotePartType must be a string (encountered: {val})")
        newcls = Enum("TableNotePartType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(TableNotePartType, getattr(newcls, "_UNKNOWN"))
