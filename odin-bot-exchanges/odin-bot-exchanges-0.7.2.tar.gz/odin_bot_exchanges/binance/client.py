import logging
import aiohttp

from datetime import datetime
from binance.spot import Spot
from dataclasses import dataclass


logging.basicConfig(level=logging.DEBUG,
                    format="%(levelname)s:%(asctime)s:%(message)s")


@dataclass
class BinanceClient:
    api_key: str
    secret_key: str

    def __post_init__(self):
        self.client = Spot(
            key=self.api_key, secret=self.secret_key
        )

    def get_order_response(
        self, order_id: str, market_code: str
    ):
        response = self.client.get_order(
            symbol=market_code, orderId=order_id
        )
        return response

    def get_transaction_response(self, order_id: str, market_code: str):
        try:
            symbol = market_code.replace("/", "")
            response = self.client.my_trades(
                symbol=symbol, orderId=int(order_id)
            )
            logging.info(response)
            return response
        except Exception as err:
            logging.debug(err)
            raise err

    def get_transaction_history_response(self, market_code: str, start_date: datetime, end_date: datetime):
        try:
            symbol = market_code.replace("/", "")
            start_time = int(start_date.timestamp()*1000)
            end_time = int(end_date.timestamp()*1000)
            response = self.client.my_trades(
                symbol=symbol, startTime=start_time, endTime=end_time)
            logging.info(response)
            return response
        except Exception as err:
            logging.debug(err)
            raise err

    def get_wallet_response(self):
        response = self.client.account()
        return response

    def exchange_info(self, symbol: str):
        response = self.client.exchange_info(symbol)
        return response

    def avg_price(self, symbol: str):
        response = self.client.avg_price(symbol)
        return response

    def new_position(self, params):
        # response = self.client.new_order(**params.dict())
        response = self.client.new_order(**params.dict())
        logging.info(response)
        entity_id = response.get("orderId", "test-id")
        logging.info(f"Order id: {entity_id}")
        return response
