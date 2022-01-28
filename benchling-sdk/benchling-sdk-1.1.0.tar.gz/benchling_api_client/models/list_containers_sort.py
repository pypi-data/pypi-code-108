from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ListContainersSort(Enums.KnownString):
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
    def of_unknown(val: str) -> "ListContainersSort":
        if not isinstance(val, str):
            raise ValueError(f"Value of ListContainersSort must be a string (encountered: {val})")
        newcls = Enum("ListContainersSort", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ListContainersSort, getattr(newcls, "_UNKNOWN"))
