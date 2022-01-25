from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class WorkflowTaskGroupArchiveReason(Enums.KnownString):
    MADE_IN_ERROR = "Made in error"
    RETIRED = "Retired"
    OTHER = "Other"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "WorkflowTaskGroupArchiveReason":
        if not isinstance(val, str):
            raise ValueError(f"Value of WorkflowTaskGroupArchiveReason must be a string (encountered: {val})")
        newcls = Enum("WorkflowTaskGroupArchiveReason", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(WorkflowTaskGroupArchiveReason, getattr(newcls, "_UNKNOWN"))
