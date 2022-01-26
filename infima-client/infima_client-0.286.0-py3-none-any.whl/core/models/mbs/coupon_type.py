from enum import Enum


class MbsCouponType(str, Enum):
    NULL_COUPON_TYPE = "NULL_COUPON_TYPE"
    FIX = "FIX"
    ARM = "ARM"
    VAR = "VAR"

    def __str__(self) -> str:
        return str(self.value)
