from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class UserCollaboratorType(Enums.KnownString):
    USER = "USER"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "UserCollaboratorType":
        if not isinstance(val, str):
            raise ValueError(f"Value of UserCollaboratorType must be a string (encountered: {val})")
        newcls = Enum("UserCollaboratorType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(UserCollaboratorType, getattr(newcls, "_UNKNOWN"))
