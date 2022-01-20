from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class CheckboxNotePartType(Enums.KnownString):
    LIST_CHECKBOX = "list_checkbox"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "CheckboxNotePartType":
        if not isinstance(val, str):
            raise ValueError(f"Value of CheckboxNotePartType must be a string (encountered: {val})")
        newcls = Enum("CheckboxNotePartType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(CheckboxNotePartType, getattr(newcls, "_UNKNOWN"))
