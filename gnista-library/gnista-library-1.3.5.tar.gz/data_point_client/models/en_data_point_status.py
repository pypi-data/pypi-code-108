from enum import Enum


class EnDataPointStatus(str, Enum):
    INCREATION = "InCreation"
    READY = "Ready"
    ERROR = "Error"

    def __str__(self) -> str:
        return str(self.value)
