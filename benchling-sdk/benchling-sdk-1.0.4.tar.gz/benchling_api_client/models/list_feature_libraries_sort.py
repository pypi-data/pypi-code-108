from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ListFeatureLibrariesSort(Enums.KnownString):
    MODIFIEDAT = "modifiedAt"
    MODIFIEDATASC = "modifiedAt:asc"
    MODIFIEDATDESC = "modifiedAt:desc"
    NAME = "name"
    NAMEASC = "name:asc"
    NAMEDESC = "name:desc"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "ListFeatureLibrariesSort":
        if not isinstance(val, str):
            raise ValueError(f"Value of ListFeatureLibrariesSort must be a string (encountered: {val})")
        newcls = Enum("ListFeatureLibrariesSort", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ListFeatureLibrariesSort, getattr(newcls, "_UNKNOWN"))
