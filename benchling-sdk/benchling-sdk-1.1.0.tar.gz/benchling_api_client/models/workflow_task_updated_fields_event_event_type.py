from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class WorkflowTaskUpdatedFieldsEventEventType(Enums.KnownString):
    V2_WORKFLOWTASKUPDATEDFIELDS = "v2.workflowTask.updated.fields"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "WorkflowTaskUpdatedFieldsEventEventType":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of WorkflowTaskUpdatedFieldsEventEventType must be a string (encountered: {val})"
            )
        newcls = Enum("WorkflowTaskUpdatedFieldsEventEventType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(WorkflowTaskUpdatedFieldsEventEventType, getattr(newcls, "_UNKNOWN"))
