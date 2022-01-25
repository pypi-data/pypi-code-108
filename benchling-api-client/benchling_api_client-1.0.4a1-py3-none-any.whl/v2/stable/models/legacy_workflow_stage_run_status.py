from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class LegacyWorkflowStageRunStatus(Enums.KnownString):
    COMPLETED = "COMPLETED"
    DISCARDED = "DISCARDED"
    INITIALIZED = "INITIALIZED"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "LegacyWorkflowStageRunStatus":
        if not isinstance(val, str):
            raise ValueError(f"Value of LegacyWorkflowStageRunStatus must be a string (encountered: {val})")
        newcls = Enum("LegacyWorkflowStageRunStatus", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(LegacyWorkflowStageRunStatus, getattr(newcls, "_UNKNOWN"))
