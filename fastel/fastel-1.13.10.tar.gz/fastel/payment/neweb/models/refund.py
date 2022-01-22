from typing import Literal, Optional

from pydantic import BaseModel


class RefundModel(BaseModel):
    Amt: int
    MerchantOrderNo: str
    IndexType: Literal[1, 2] = 1
    TradeNo: str
    CloseType: Literal[1, 2] = 2
    Cancel: Optional[Literal[1]]
