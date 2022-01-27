from enum import Enum


class TradingColumnMeaning(str, Enum):
    PRICE = "price"
    RETURNS = "returns"

    def __str__(self) -> str:
        return str(self.value)
