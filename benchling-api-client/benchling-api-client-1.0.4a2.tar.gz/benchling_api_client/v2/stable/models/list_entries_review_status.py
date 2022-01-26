from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ListEntriesReviewStatus(Enums.KnownString):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    RETRACTED = "RETRACTED"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "ListEntriesReviewStatus":
        if not isinstance(val, str):
            raise ValueError(f"Value of ListEntriesReviewStatus must be a string (encountered: {val})")
        newcls = Enum("ListEntriesReviewStatus", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ListEntriesReviewStatus, getattr(newcls, "_UNKNOWN"))
