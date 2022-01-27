import math
import logging
from typing import List, NamedTuple


from odin_bot_entities.trades import Order, Transaction
from odin_bot_entities.balances import Wallet

from odin_bot_exchanges.binance.client import BinanceClient
from odin_bot_exchanges.binance.responses import BinanceWalletResponseParser, BinanceTransactionResponseParser, BinanceTransactionHistoryResponseParser
from odin_bot_exchanges.exchange import ExchangeService


class ExchangeInfo(NamedTuple):
    min_notional: float
    min_lot_size: float
    precision: float
    step_size: float

    def get_amount(self, quantity: float):
        step_precision = int(round(-math.log(self.step_size, 10), 0))
        new_quantity = float(round(quantity, step_precision))
        return new_quantity

    def filter_lot_size(self, quantity: float):
        return quantity >= self.min_lot_size

    def filter_min_notional(self, quantity: float, price: float):
        return quantity * price >= self.min_notional


class BinanceExchange(ExchangeService):
    exchange: str = "binance"

    def __init__(self, api_key: str, secret_key: str):
        self.client = BinanceClient(api_key=api_key, secret_key=secret_key)
        self.wallet_parser = BinanceWalletResponseParser()
        self.transaction_parser = BinanceTransactionResponseParser()
        self.transaction_history_parser = BinanceTransactionHistoryResponseParser()
        self.order_parser = None
    # async def get_order_response(self, order_id: str, market_code: str) -> Order:
    #     response = self.client.get_order_response(
    #         order_id=order_id, market_code=market_code)
    #     order: Order = self.order_parser.parse_response(response=response)
    #     return order

    async def get_transaction_response(self, order_id: str, market_code: str) -> Order:
        response = self.client.get_transaction_response(
            order_id=order_id, market_code=market_code)
        transaction: Transaction = self.transaction_parser.parse_response(order_id=order_id,
                                                                          market_code=market_code,
                                                                          response=response)
        return transaction

    async def get_transaction_history_response(self, **kwargs) -> List[Order]:
        response = self.client.get_transaction_history_response(**kwargs)
        transactions: List[Transaction] = self.transaction_history_parser.parse_response(
            response=response,
            **kwargs)
        return transactions

    async def get_wallet_response(self) -> List[Wallet]:
        response = self.client.get_wallet_response()
        wallets = self.wallet_parser.parse_response(response=response)
        return wallets

    async def new_position(self, params):
        # response = self.client.new_order(**params.dict())
        response = self.client.new_position(params)
        return response

    async def get_symbol_price(self, symbol: str):
        response = self.client.avg_price(symbol)
        price = float(response["price"])
        return price

    async def get_exchange_info(self, symbol: str):
        try:
            response = self.client.exchange_info(symbol)
            min_notional = 0
            lot_size = 0
            step_size = 0
            precision_digits = int(
                response["symbols"][0]["baseAssetPrecision"])
            for filter in response["symbols"][0]["filters"]:
                if filter["filterType"] == "LOT_SIZE":
                    lot_size = float(filter["minQty"])
                    step_size = float(filter["stepSize"])
                elif filter["filterType"] == "MIN_NOTIONAL":
                    min_notional = float(filter["minNotional"])

            info = ExchangeInfo(
                min_notional=min_notional,
                min_lot_size=lot_size,
                precision=precision_digits,
                step_size=step_size,
            )
            return info
        except Exception as err:
            logging.debug(err)
            logging.debug(
                f"Binance Exchange: Could not retrieve exchange info for {symbol}"
            )
