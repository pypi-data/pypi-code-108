from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class AssayRunUpdatedFieldsEventEventType(Enums.KnownString):
    V2_ASSAYRUNUPDATEDFIELDS = "v2.assayRun.updated.fields"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "AssayRunUpdatedFieldsEventEventType":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of AssayRunUpdatedFieldsEventEventType must be a string (encountered: {val})"
            )
        newcls = Enum("AssayRunUpdatedFieldsEventEventType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(AssayRunUpdatedFieldsEventEventType, getattr(newcls, "_UNKNOWN"))
