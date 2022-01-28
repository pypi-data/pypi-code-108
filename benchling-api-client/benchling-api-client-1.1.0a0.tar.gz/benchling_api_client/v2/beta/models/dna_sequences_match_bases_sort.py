from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class DnaSequencesMatchBasesSort(Enums.KnownString):
    MODIFIEDATASC = "modifiedAt:asc"
    MODIFIEDATDESC = "modifiedAt:desc"
    NAMEASC = "name:asc"
    NAMEDESC = "name:desc"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "DnaSequencesMatchBasesSort":
        if not isinstance(val, str):
            raise ValueError(f"Value of DnaSequencesMatchBasesSort must be a string (encountered: {val})")
        newcls = Enum("DnaSequencesMatchBasesSort", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(DnaSequencesMatchBasesSort, getattr(newcls, "_UNKNOWN"))
