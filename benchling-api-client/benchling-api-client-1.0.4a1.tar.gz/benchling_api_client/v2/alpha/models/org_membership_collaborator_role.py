from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class OrgMembershipCollaboratorRole(Enums.KnownString):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "OrgMembershipCollaboratorRole":
        if not isinstance(val, str):
            raise ValueError(f"Value of OrgMembershipCollaboratorRole must be a string (encountered: {val})")
        newcls = Enum("OrgMembershipCollaboratorRole", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(OrgMembershipCollaboratorRole, getattr(newcls, "_UNKNOWN"))
