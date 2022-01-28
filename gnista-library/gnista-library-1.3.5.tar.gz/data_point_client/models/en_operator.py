from enum import Enum


class EnOperator(str, Enum):
    LARGER = "Larger"
    SMALLER = "Smaller"
    EQUAL = "Equal"

    def __str__(self) -> str:
        return str(self.value)
