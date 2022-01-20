from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ListBenchlingAppsSort(Enums.KnownString):
    MODIFIEDAT = "modifiedAt"
    NAME = "name"
    MODIFIEDATASC = "modifiedAt:asc"
    NAMEASC = "name:asc"
    MODIFIEDATDESC = "modifiedAt:desc"
    NAMEDESC = "name:desc"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "ListBenchlingAppsSort":
        if not isinstance(val, str):
            raise ValueError(f"Value of ListBenchlingAppsSort must be a string (encountered: {val})")
        newcls = Enum("ListBenchlingAppsSort", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ListBenchlingAppsSort, getattr(newcls, "_UNKNOWN"))
