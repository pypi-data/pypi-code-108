from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class TeamMembershipCollaboratorRole(Enums.KnownString):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "TeamMembershipCollaboratorRole":
        if not isinstance(val, str):
            raise ValueError(f"Value of TeamMembershipCollaboratorRole must be a string (encountered: {val})")
        newcls = Enum("TeamMembershipCollaboratorRole", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(TeamMembershipCollaboratorRole, getattr(newcls, "_UNKNOWN"))
