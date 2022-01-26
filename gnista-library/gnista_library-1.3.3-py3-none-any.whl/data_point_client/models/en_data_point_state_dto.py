from enum import Enum


class EnDataPointStateDTO(str, Enum):
    DRAFT = "Draft"
    INPROGRESS = "InProgress"
    READY = "Ready"
    ERROR = "Error"

    def __str__(self) -> str:
        return str(self.value)
