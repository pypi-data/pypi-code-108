from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class NamingStrategy(Enums.KnownString):
    NEW_IDS = "NEW_IDS"
    IDS_FROM_NAMES = "IDS_FROM_NAMES"
    DELETE_NAMES = "DELETE_NAMES"
    SET_FROM_NAME_PARTS = "SET_FROM_NAME_PARTS"
    REPLACE_NAMES_FROM_PARTS = "REPLACE_NAMES_FROM_PARTS"
    KEEP_NAMES = "KEEP_NAMES"
    REPLACE_ID_AND_NAME_FROM_PARTS = "REPLACE_ID_AND_NAME_FROM_PARTS"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "NamingStrategy":
        if not isinstance(val, str):
            raise ValueError(f"Value of NamingStrategy must be a string (encountered: {val})")
        newcls = Enum("NamingStrategy", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(NamingStrategy, getattr(newcls, "_UNKNOWN"))
