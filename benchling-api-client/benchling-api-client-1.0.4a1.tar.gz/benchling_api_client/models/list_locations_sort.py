from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ListLocationsSort(Enums.KnownString):
    BARCODE = "barcode"
    MODIFIEDAT = "modifiedAt"
    NAME = "name"
    BARCODEASC = "barcode:asc"
    MODIFIEDATASC = "modifiedAt:asc"
    NAMEASC = "name:asc"
    BARCODEDESC = "barcode:desc"
    MODIFIEDATDESC = "modifiedAt:desc"
    NAMEDESC = "name:desc"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "ListLocationsSort":
        if not isinstance(val, str):
            raise ValueError(f"Value of ListLocationsSort must be a string (encountered: {val})")
        newcls = Enum("ListLocationsSort", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ListLocationsSort, getattr(newcls, "_UNKNOWN"))
