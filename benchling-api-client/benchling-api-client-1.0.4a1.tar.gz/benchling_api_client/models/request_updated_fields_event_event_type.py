from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class RequestUpdatedFieldsEventEventType(Enums.KnownString):
    V2_REQUESTUPDATEDFIELDS = "v2.request.updated.fields"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "RequestUpdatedFieldsEventEventType":
        if not isinstance(val, str):
            raise ValueError(
                f"Value of RequestUpdatedFieldsEventEventType must be a string (encountered: {val})"
            )
        newcls = Enum("RequestUpdatedFieldsEventEventType", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(RequestUpdatedFieldsEventEventType, getattr(newcls, "_UNKNOWN"))
