from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class WorkflowTaskArchiveReason(Enums.KnownString):
    MADE_IN_ERROR = "Made in error"
    RETIRED = "Retired"
    OTHER = "Other"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "WorkflowTaskArchiveReason":
        if not isinstance(val, str):
            raise ValueError(f"Value of WorkflowTaskArchiveReason must be a string (encountered: {val})")
        newcls = Enum("WorkflowTaskArchiveReason", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(WorkflowTaskArchiveReason, getattr(newcls, "_UNKNOWN"))
