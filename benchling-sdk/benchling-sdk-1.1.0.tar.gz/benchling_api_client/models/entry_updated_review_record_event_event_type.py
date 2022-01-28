from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class EntryUpdatedReviewRecordEventEventType(Enums.KnownString):
    V2_ENTRYUPDATEDREVIEWRECORD = "v2.entry.updated.reviewRecord"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "EntryUpdatedReviewRecordEventEventType":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of EntryUpdatedReviewRecordEventEventType must be a string (encountered: {val})"
            )
        newcls = Enum("EntryUpdatedReviewRecordEventEventType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(EntryUpdatedReviewRecordEventEventType, getattr(newcls, "_UNKNOWN"))
