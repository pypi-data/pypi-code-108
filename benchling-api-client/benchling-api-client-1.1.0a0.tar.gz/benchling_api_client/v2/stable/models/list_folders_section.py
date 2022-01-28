from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ListFoldersSection(Enums.KnownString):
    INVENTORY = "INVENTORY"
    NOTEBOOK = "NOTEBOOK"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "ListFoldersSection":
        if not isinstance(val, str):
            raise ValueError(f"Value of ListFoldersSection must be a string (encountered: {val})")
        newcls = Enum("ListFoldersSection", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ListFoldersSection, getattr(newcls, "_UNKNOWN"))
