from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class OrgMembershipCollaboratorType(Enums.KnownString):
    ORGANIZATION_MEMBERSHIP = "ORGANIZATION_MEMBERSHIP"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "OrgMembershipCollaboratorType":
        if not isinstance(val, str):
            raise ValueError(f"Value of OrgMembershipCollaboratorType must be a string (encountered: {val})")
        newcls = Enum("OrgMembershipCollaboratorType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(OrgMembershipCollaboratorType, getattr(newcls, "_UNKNOWN"))
