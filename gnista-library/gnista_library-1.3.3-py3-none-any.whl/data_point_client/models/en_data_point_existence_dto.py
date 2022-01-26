from enum import Enum


class EnDataPointExistenceDTO(str, Enum):
    FULL = "Full"
    LOW = "Low"
    HIDDEN = "Hidden"
    DELETED = "Deleted"

    def __str__(self) -> str:
        return str(self.value)
