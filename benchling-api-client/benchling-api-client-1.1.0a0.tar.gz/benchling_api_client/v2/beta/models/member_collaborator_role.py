from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class MemberCollaboratorRole(Enums.KnownString):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "MemberCollaboratorRole":
        if not isinstance(val, str):
            raise ValueError(f"Value of MemberCollaboratorRole must be a string (encountered: {val})")
        newcls = Enum("MemberCollaboratorRole", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(MemberCollaboratorRole, getattr(newcls, "_UNKNOWN"))
