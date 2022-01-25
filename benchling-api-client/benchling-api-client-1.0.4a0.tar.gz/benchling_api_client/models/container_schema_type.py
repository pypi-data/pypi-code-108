from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ContainerSchemaType(Enums.KnownString):
    CONTAINER = "container"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "ContainerSchemaType":
        if not isinstance(val, str):
            raise ValueError(f"Value of ContainerSchemaType must be a string (encountered: {val})")
        newcls = Enum("ContainerSchemaType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ContainerSchemaType, getattr(newcls, "_UNKNOWN"))
