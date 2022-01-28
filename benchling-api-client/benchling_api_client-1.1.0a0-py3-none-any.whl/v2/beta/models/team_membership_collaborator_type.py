from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class TeamMembershipCollaboratorType(Enums.KnownString):
    TEAM_MEMBERSHIP = "TEAM_MEMBERSHIP"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "TeamMembershipCollaboratorType":
        if not isinstance(val, str):
            raise ValueError(f"Value of TeamMembershipCollaboratorType must be a string (encountered: {val})")
        newcls = Enum("TeamMembershipCollaboratorType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(TeamMembershipCollaboratorType, getattr(newcls, "_UNKNOWN"))
