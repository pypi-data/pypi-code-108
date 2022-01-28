from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class DnaSequencesSearchBasesSort(Enums.KnownString):
    MODIFIEDATASC = "modifiedAt:asc"
    MODIFIEDATDESC = "modifiedAt:desc"
    NAMEASC = "name:asc"
    NAMEDESC = "name:desc"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "DnaSequencesSearchBasesSort":
        if not isinstance(val, str):
            raise ValueError(f"Value of DnaSequencesSearchBasesSort must be a string (encountered: {val})")
        newcls = Enum("DnaSequencesSearchBasesSort", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(DnaSequencesSearchBasesSort, getattr(newcls, "_UNKNOWN"))
