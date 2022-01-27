
import logging
from typing import List

from orionx_python_client import OrionXClient
from odin_bot_entities.trades import Order
from odin_bot_exchanges.exchange import ExchangeService
from orionx_python_client.currency import CEROS as ORIONX_CEROS
from .responses import OrionXOrderResponseParser, OrionXTradeHistoryResponseParser, OrionXWalletResponseParser, OrionXTransactionFromOrderResponseParser


class OrionXExchange(ExchangeService):
    exchange: str = "orionX"

    def __init__(self, api_url: str, api_key: str, secret_key: str):
        self.client = OrionXClient(
            api_key=api_key, api_url=api_url, secret_key=secret_key)
        self.wallet_parser = OrionXWalletResponseParser()
        self.order_parser = OrionXOrderResponseParser()
        self.trade_history_parser = OrionXTradeHistoryResponseParser()
        self.transaction_from_order_parser = OrionXTransactionFromOrderResponseParser()

    def get_order_response(
        self, order_id: str, market_code: str
    ):
        try:

            response = self.client.get_order(
                order_id=order_id)
            order = self.order_parser.parse_response(
                order_id=order_id,
                market_code=market_code,
                response=response)
            return order
        except Exception as err:
            logging.error(err)
            return None

    def get_transaction_from_order_response(self, order_id: str) -> Order:
        try:

            response = self.client.get_order(
                order_id=order_id)
            order = self.transaction_from_order_parser.parse_response(
                response=response)
            return order
        except Exception as err:
            logging.debug(err)
            raise err

    def get_wallet_response(self, currency_ceros: dict = ORIONX_CEROS):
        try:

            response = self.client.get_balance()
            wallet = self.wallet_parser.parse_response(
                response=response, currency_ceros=currency_ceros)
            return wallet
        except Exception as err:
            logging.error(err)
            return None

    def get_open_orders(self):
        try:

            response = self.client.get_open_orders()
            logging.info(response)
            return response
        except Exception as err:
            logging.debug(err)
            raise err

    def get_open_orders_by_market(self, market: str, selling: str):
        try:

            response = self.client.get_open_orders_by_market(
                market=market, selling=selling)
            logging.info(response)
            return response
        except Exception as err:
            logging.debug(err)
            raise err

    def close_orders(self, order_ids: List[str]):
        try:

            response = self.client.close_orders(
                order_ids=order_ids)
            logging.info(response)
            return response
        except Exception as err:
            logging.debug(err)
            raise err

    def close_orders_by_market(self, market: str, selling: str):
        try:

            response = self.client.close_orders_by_market(
                market=market, selling=selling)
            logging.info(response)
            return response
        except Exception as err:
            logging.debug(err)
            raise err

    def get_order_status(self, order_id: str):
        try:

            response = self.client.get_order_status(
                order_id=order_id)
            logging.info(response)
            return response
        except Exception as err:
            logging.debug(err)
            raise Exception("Could not get Order Status")

    def close_order_by_id(self, order_id: str):
        try:

            response = self.client.close_order_by_id(order_id=order_id)
            logging.info(response)

            return response

        except Exception as err:
            logging.debug(err)
            raise Exception(f"Could not get Cancel Order {order_id}")

    def new_position(
        self,
        market_code: str,
        amount: float,
        limit_price: float,
        selling: str,
    ):
        try:

            response = self.client.new_position(
                market_code=market_code, amount=amount, limit_price=limit_price, selling=selling)
            logging.info(response)
            return response
        except Exception as err:
            logging.error(err)
            raise False
