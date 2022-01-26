from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class WorkflowTaskStatusStatusType(Enums.KnownString):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    INVALID = "INVALID"
    COMPLETED = "COMPLETED"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "WorkflowTaskStatusStatusType":
        if not isinstance(val, str):
            raise ValueError(f"Value of WorkflowTaskStatusStatusType must be a string (encountered: {val})")
        newcls = Enum("WorkflowTaskStatusStatusType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(WorkflowTaskStatusStatusType, getattr(newcls, "_UNKNOWN"))
