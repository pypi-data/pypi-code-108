from odin_messages.base import BaseEventMessage


class DownFallOrderBookMessage(BaseEventMessage):
    market_code: str
    reference_price: float
    downfall_amount: float
