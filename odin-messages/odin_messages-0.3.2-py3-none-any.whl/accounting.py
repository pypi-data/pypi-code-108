from typing import List, Dict
from pydantic import BaseModel
from  odin_messages.base import BaseEventMessage


class GeneratorOrder(BaseModel):
    id: str
    exchange: str
    amount: float
    status: str
    side: str
    type: str



class AccountingMessage(BaseEventMessage):
    trade_id: str
    exchange: str
    generator_info: List[GeneratorOrder]
    origin_market: str
    target_market: str
    order_type: str
    usd_observed: float
    amount: float

class OperatorBalanceMessage(BaseEventMessage):
    balances: Dict[str, float]

class OperatorManagedAmounts(BaseEventMessage):
    managed_amounts: Dict[str, float]

class OperatorMinimumToTrade(BaseEventMessage):
    exchange: str
    minimum_to_trade: Dict[str, float]
