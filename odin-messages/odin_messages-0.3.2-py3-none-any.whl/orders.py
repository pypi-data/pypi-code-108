from typing import List
from odin_messages.base import BaseEventMessage


class UpdateLimitOrderMessage(BaseEventMessage):
    old_order_ids: List[str]
    exchange: str
    market_code: str
    new_limit_price: float
    new_quantity: float
    usd_price: float
    price_delta: float
    selling: bool


class NewLimitOrderMessage(BaseEventMessage):
    exchange: str
    market_code: str
    limit_price: float
    quantity: float
    usd_price: float
    price_delta: float
    selling: bool

class NewArbitrageSpotTradeMessage(BaseEventMessage):
    generator_order_id: str
    generator_order_status: str
    generator_order_type: str
    origin_exchange: str
    target_exchange: str
    origin_market: str
    target_market: str
    amount: float
    usd_observed: float



class NewSpotOrderMessage(BaseEventMessage):
    exchange: str
    order_id: str
    market_code: str
    quantity: float
    usd_price: float
    selling: bool


class UpdateOrderMessage(BaseEventMessage):
    order_id: str
    market_code: str
    exchange: str
    new_limit_price: float
    new_quantity: float

class CancelOrderByIdMessage(BaseEventMessage):
    order_id: str
    exchange: str
    market_code: str


class CancelAllOrdersMessage(BaseEventMessage):
    exchange: str

class CancelOrdersByMarketMessage(BaseEventMessage):
    exchange: str
    market_code: str
