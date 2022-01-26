from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class StageEntryUpdatedReviewRecordEventEventType(Enums.KnownString):
    V2_ALPHASTAGEENTRYUPDATEDREVIEWRECORD = "v2-alpha.stageEntry.updated.reviewRecord"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "StageEntryUpdatedReviewRecordEventEventType":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of StageEntryUpdatedReviewRecordEventEventType must be a string (encountered: {val})"
            )
        newcls = Enum("StageEntryUpdatedReviewRecordEventEventType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(StageEntryUpdatedReviewRecordEventEventType, getattr(newcls, "_UNKNOWN"))
