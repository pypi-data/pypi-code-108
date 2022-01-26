from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class PlateWorklistItemsListType(Enums.KnownString):
    PLATE = "plate"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "PlateWorklistItemsListType":
        if not isinstance(val, str):
            raise ValueError(f"Value of PlateWorklistItemsListType must be a string (encountered: {val})")
        newcls = Enum("PlateWorklistItemsListType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(PlateWorklistItemsListType, getattr(newcls, "_UNKNOWN"))
