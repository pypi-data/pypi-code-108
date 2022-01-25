from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class RegistrationTableNotePartType(Enums.KnownString):
    REGISTRATION_TABLE = "registration_table"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "RegistrationTableNotePartType":
        if not isinstance(val, str):
            raise ValueError(f"Value of RegistrationTableNotePartType must be a string (encountered: {val})")
        newcls = Enum("RegistrationTableNotePartType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(RegistrationTableNotePartType, getattr(newcls, "_UNKNOWN"))
