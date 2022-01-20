
from typing import Dict
from odin_messages.base import BaseEventMessage

class OperatorLoansConfigMessage(BaseEventMessage):
    loans: Dict[str, float]

class OperatorMinimumToTradeMessage(BaseEventMessage):
    exchange: str
    minimumt_to_trade: Dict[str, float]


class OperatorCostConfigMessage(BaseEventMessage):
    exchange: str
    fee: float

class OperatorIsActiveMessage(BaseEventMessage):
    active: bool
