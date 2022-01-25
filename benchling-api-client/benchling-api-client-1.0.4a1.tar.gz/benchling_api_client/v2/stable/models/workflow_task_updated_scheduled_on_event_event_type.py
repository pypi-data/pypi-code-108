from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class WorkflowTaskUpdatedScheduledOnEventEventType(Enums.KnownString):
    V2_WORKFLOWTASKUPDATEDSCHEDULEDON = "v2.workflowTask.updated.scheduledOn"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "WorkflowTaskUpdatedScheduledOnEventEventType":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of WorkflowTaskUpdatedScheduledOnEventEventType must be a string (encountered: {val})"
            )
        newcls = Enum("WorkflowTaskUpdatedScheduledOnEventEventType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(WorkflowTaskUpdatedScheduledOnEventEventType, getattr(newcls, "_UNKNOWN"))
