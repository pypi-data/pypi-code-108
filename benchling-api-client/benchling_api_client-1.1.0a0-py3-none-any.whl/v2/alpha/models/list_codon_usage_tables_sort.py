from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ListCodonUsageTablesSort(Enums.KnownString):
    NAME = "name"
    NAMEASC = "name:asc"
    NAMEDESC = "name:desc"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "ListCodonUsageTablesSort":
        if not isinstance(val, str):
            raise ValueError(f"Value of ListCodonUsageTablesSort must be a string (encountered: {val})")
        newcls = Enum("ListCodonUsageTablesSort", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ListCodonUsageTablesSort, getattr(newcls, "_UNKNOWN"))
