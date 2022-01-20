from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ListProjectsSort(Enums.KnownString):
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
    def of_unknown(val: str) -> "ListProjectsSort":
        if not isinstance(val, str):
            raise ValueError(f"Value of ListProjectsSort must be a string (encountered: {val})")
        newcls = Enum("ListProjectsSort", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ListProjectsSort, getattr(newcls, "_UNKNOWN"))
