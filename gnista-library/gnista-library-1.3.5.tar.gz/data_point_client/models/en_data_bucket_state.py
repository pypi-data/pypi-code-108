from enum import Enum


class EnDataBucketState(str, Enum):
    INPROGRESS = "InProgress"
    READY = "Ready"
    ERROR = "Error"

    def __str__(self) -> str:
        return str(self.value)
