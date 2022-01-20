from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class StageEntryUpdatedFieldsEventEventType(Enums.KnownString):
    V2_ALPHASTAGEENTRYUPDATEDFIELDS = "v2-alpha.stageEntry.updated.fields"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "StageEntryUpdatedFieldsEventEventType":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of StageEntryUpdatedFieldsEventEventType must be a string (encountered: {val})"
            )
        newcls = Enum("StageEntryUpdatedFieldsEventEventType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(StageEntryUpdatedFieldsEventEventType, getattr(newcls, "_UNKNOWN"))
