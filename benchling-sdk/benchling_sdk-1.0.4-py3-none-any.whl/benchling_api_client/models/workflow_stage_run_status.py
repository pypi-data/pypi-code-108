from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class WorkflowStageRunStatus(Enums.KnownString):
    COMPLETED = "COMPLETED"
    DISCARDED = "DISCARDED"
    INITIALIZED = "INITIALIZED"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "WorkflowStageRunStatus":
        if not isinstance(val, str):
            raise ValueError(f"Value of WorkflowStageRunStatus must be a string (encountered: {val})")
        newcls = Enum("WorkflowStageRunStatus", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(WorkflowStageRunStatus, getattr(newcls, "_UNKNOWN"))
