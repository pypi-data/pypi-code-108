from enum import Enum


class JsonDataType(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"

    def __str__(self) -> str:
        return str(self.value)
