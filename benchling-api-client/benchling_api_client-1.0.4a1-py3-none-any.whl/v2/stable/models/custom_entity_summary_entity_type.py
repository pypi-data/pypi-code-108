from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class CustomEntitySummaryEntityType(Enums.KnownString):
    CUSTOM_ENTITY = "custom_entity"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "CustomEntitySummaryEntityType":
        if not isinstance(val, str):
            raise ValueError(f"Value of CustomEntitySummaryEntityType must be a string (encountered: {val})")
        newcls = Enum("CustomEntitySummaryEntityType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(CustomEntitySummaryEntityType, getattr(newcls, "_UNKNOWN"))
