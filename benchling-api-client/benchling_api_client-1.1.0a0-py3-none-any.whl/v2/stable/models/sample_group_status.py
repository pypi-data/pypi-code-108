from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class SampleGroupStatus(Enums.KnownString):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "SampleGroupStatus":
        if not isinstance(val, str):
            raise ValueError(f"Value of SampleGroupStatus must be a string (encountered: {val})")
        newcls = Enum("SampleGroupStatus", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(SampleGroupStatus, getattr(newcls, "_UNKNOWN"))
