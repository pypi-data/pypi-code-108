from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class BlobUploadStatus(Enums.KnownString):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    ABORTED = "ABORTED"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "BlobUploadStatus":
        if not isinstance(val, str):
            raise ValueError(f"Value of BlobUploadStatus must be a string (encountered: {val})")
        newcls = Enum("BlobUploadStatus", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(BlobUploadStatus, getattr(newcls, "_UNKNOWN"))
