from enum import Enum


class MbsCollateralType(str, Enum):
    NULL_COLLATERAL_TYPE = "NULL_COLLATERAL_TYPE"
    LOAN = "LOAN"
    POOL = "POOL"
    WHLN = "WHLN"

    def __str__(self) -> str:
        return str(self.value)
