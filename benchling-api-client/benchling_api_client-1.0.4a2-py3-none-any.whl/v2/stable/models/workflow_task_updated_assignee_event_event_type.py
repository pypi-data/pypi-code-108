from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class WorkflowTaskUpdatedAssigneeEventEventType(Enums.KnownString):
    V2_WORKFLOWTASKUPDATEDASSIGNEE = "v2.workflowTask.updated.assignee"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "WorkflowTaskUpdatedAssigneeEventEventType":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of WorkflowTaskUpdatedAssigneeEventEventType must be a string (encountered: {val})"
            )
        newcls = Enum("WorkflowTaskUpdatedAssigneeEventEventType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(WorkflowTaskUpdatedAssigneeEventEventType, getattr(newcls, "_UNKNOWN"))
