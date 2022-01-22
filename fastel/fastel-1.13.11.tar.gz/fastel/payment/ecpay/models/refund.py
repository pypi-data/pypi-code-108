from typing import Literal, Optional

from pydantic import BaseModel


class RefundModel(BaseModel):
    MerchantTradeNo: str
    TradeNo: str
    Action: Literal["C", "R", "E", "N"] = "R"
    TotalAmount: int
    PlatformID: Optional[str]
