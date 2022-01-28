from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class BoxSchemaType(Enums.KnownString):
    BOX = "box"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "BoxSchemaType":
        if not isinstance(val, str):
            raise ValueError(f"Value of BoxSchemaType must be a string (encountered: {val})")
        newcls = Enum("BoxSchemaType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(BoxSchemaType, getattr(newcls, "_UNKNOWN"))
