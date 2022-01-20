from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ListFoldersSort(Enums.KnownString):
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
    def of_unknown(val: str) -> "ListFoldersSort":
        if not isinstance(val, str):
            raise ValueError(f"Value of ListFoldersSort must be a string (encountered: {val})")
        newcls = Enum("ListFoldersSort", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ListFoldersSort, getattr(newcls, "_UNKNOWN"))
