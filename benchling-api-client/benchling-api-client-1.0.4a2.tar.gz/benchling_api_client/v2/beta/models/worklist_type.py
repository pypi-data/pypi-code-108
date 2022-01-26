from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class WorklistType(Enums.KnownString):
    BATCH = "batch"
    BIOENTITY = "bioentity"
    CONTAINER = "container"
    PLATE = "plate"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "WorklistType":
        if not isinstance(val, str):
            raise ValueError(f"Value of WorklistType must be a string (encountered: {val})")
        newcls = Enum("WorklistType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(WorklistType, getattr(newcls, "_UNKNOWN"))
