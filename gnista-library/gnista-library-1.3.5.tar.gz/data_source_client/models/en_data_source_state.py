from enum import Enum


class EnDataSourceState(str, Enum):
    NEW = "New"
    FAILED = "Failed"
    READY = "Ready"

    def __str__(self) -> str:
        return str(self.value)
