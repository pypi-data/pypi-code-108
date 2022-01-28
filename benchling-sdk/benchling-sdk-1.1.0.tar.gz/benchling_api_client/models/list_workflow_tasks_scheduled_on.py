from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ListWorkflowTasksScheduledOn(Enums.KnownString):
    NULL = "null"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "ListWorkflowTasksScheduledOn":
        if not isinstance(val, str):
            raise ValueError(f"Value of ListWorkflowTasksScheduledOn must be a string (encountered: {val})")
        newcls = Enum("ListWorkflowTasksScheduledOn", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ListWorkflowTasksScheduledOn, getattr(newcls, "_UNKNOWN"))
