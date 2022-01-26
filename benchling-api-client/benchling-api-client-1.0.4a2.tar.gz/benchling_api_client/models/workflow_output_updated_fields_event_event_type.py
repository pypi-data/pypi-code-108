from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class WorkflowOutputUpdatedFieldsEventEventType(Enums.KnownString):
    V2_WORKFLOWOUTPUTUPDATEDFIELDS = "v2.workflowOutput.updated.fields"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "WorkflowOutputUpdatedFieldsEventEventType":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of WorkflowOutputUpdatedFieldsEventEventType must be a string (encountered: {val})"
            )
        newcls = Enum("WorkflowOutputUpdatedFieldsEventEventType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(WorkflowOutputUpdatedFieldsEventEventType, getattr(newcls, "_UNKNOWN"))
