from enum import Enum


class TradingAlgoParamType(str, Enum):
    STR = "str_"
    INT = "int_"
    FLOAT = "float_"
    BOOL = "bool_"

    def __str__(self) -> str:
        return str(self.value)
