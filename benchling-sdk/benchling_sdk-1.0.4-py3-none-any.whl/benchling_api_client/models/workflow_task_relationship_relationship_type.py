from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class WorkflowTaskRelationshipRelationshipType(Enums.KnownString):
    BASE_OF = "BASE_OF"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "WorkflowTaskRelationshipRelationshipType":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of WorkflowTaskRelationshipRelationshipType must be a string (encountered: {val})"
            )
        newcls = Enum("WorkflowTaskRelationshipRelationshipType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(WorkflowTaskRelationshipRelationshipType, getattr(newcls, "_UNKNOWN"))
