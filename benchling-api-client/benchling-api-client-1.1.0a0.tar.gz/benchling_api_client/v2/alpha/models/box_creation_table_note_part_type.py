from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class BoxCreationTableNotePartType(Enums.KnownString):
    BOX_CREATION_TABLE = "box_creation_table"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "BoxCreationTableNotePartType":
        if not isinstance(val, str):
            raise ValueError(f"Value of BoxCreationTableNotePartType must be a string (encountered: {val})")
        newcls = Enum("BoxCreationTableNotePartType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(BoxCreationTableNotePartType, getattr(newcls, "_UNKNOWN"))
