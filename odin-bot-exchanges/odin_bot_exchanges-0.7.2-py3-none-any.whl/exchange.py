from abc import ABC, abstractmethod
from .responses import AbstractResponseParser

from dataclasses import dataclass, field


@dataclass
class ExchangeService(ABC):
    exchange: str
    wallet_parser: AbstractResponseParser = field(init=False)
    transaction_parser: AbstractResponseParser = field(init=False)

    # @abstractmethod
    # async def get_transaction_response(self):
    #     pass

    # @abstractmethod
    # async def get_order_response(self):
    #     pass

    # @abstractmethod
    # async def get_wallet_response(self):
    #     pass

    # @abstractmethod
    # async def get_ticker_price_response(self):
    #     pass
