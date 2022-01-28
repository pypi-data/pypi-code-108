from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class WorkflowOutputArchiveReason(Enums.KnownString):
    MADE_IN_ERROR = "Made in error"
    RETIRED = "Retired"
    OTHER = "Other"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "WorkflowOutputArchiveReason":
        if not isinstance(val, str):
            raise ValueError(f"Value of WorkflowOutputArchiveReason must be a string (encountered: {val})")
        newcls = Enum("WorkflowOutputArchiveReason", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(WorkflowOutputArchiveReason, getattr(newcls, "_UNKNOWN"))
