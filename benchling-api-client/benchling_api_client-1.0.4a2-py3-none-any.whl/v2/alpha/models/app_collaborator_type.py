from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class AppCollaboratorType(Enums.KnownString):
    APP = "APP"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "AppCollaboratorType":
        if not isinstance(val, str):
            raise ValueError(f"Value of AppCollaboratorType must be a string (encountered: {val})")
        newcls = Enum("AppCollaboratorType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(AppCollaboratorType, getattr(newcls, "_UNKNOWN"))
