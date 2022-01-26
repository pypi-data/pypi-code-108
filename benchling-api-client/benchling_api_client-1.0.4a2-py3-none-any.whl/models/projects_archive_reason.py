from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ProjectsArchiveReason(Enums.KnownString):
    MADE_IN_ERROR = "Made in error"
    RETIRED = "Retired"
    OTHER = "Other"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "ProjectsArchiveReason":
        if not isinstance(val, str):
            raise ValueError(f"Value of ProjectsArchiveReason must be a string (encountered: {val})")
        newcls = Enum("ProjectsArchiveReason", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ProjectsArchiveReason, getattr(newcls, "_UNKNOWN"))
