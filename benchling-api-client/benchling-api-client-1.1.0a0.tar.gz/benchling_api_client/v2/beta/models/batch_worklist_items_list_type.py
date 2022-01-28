from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class BatchWorklistItemsListType(Enums.KnownString):
    BATCH = "batch"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "BatchWorklistItemsListType":
        if not isinstance(val, str):
            raise ValueError(f"Value of BatchWorklistItemsListType must be a string (encountered: {val})")
        newcls = Enum("BatchWorklistItemsListType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(BatchWorklistItemsListType, getattr(newcls, "_UNKNOWN"))
