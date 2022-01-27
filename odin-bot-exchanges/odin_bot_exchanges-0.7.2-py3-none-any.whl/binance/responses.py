import pydantic
import logging
import time


from datetime import datetime
from typing import List

import odin_bot_exchanges.currency as balance_currency

from odin_bot_entities.trades import Transaction
from odin_bot_entities.balances import Wallet

from odin_bot_exchanges.responses import AbstractResponseParser


class BinanceTransactionResponseParser(AbstractResponseParser):
    def parse_response(
        self, order_id: str, market_code: str, response: dict
    ) -> List[Transaction]:
        try:
            currency_name, pair_currency_name = market_code.split("/")

            transaction_data = []

            for currency in response:
                if currency["isBuyer"] == True:
                    order_type = "buyer"
                elif currency["isBuyer"] == False:
                    order_type = "seller"

                data = {
                    "id": currency["id"],
                    "currency_name": currency_name,
                    "pair_currency_name": pair_currency_name,
                    "market": market_code,
                    "time": currency["time"]/1000,
                    "exchange": "binance",
                    "type": order_type,
                    "fee": currency["commission"],
                    "currency_value": currency["qty"],
                    "pair_currency_value": float(currency["price"]),
                    "order_id": order_id
                }

                transaction_data.append(data)

            transactions = pydantic.parse_obj_as(
                List[Transaction], transaction_data)

            return transactions
        except Exception as err:
            logging.debug(err)
            raise Exception("Binance Parser: Could not parse Transaction")


class BinanceWalletResponseParser(AbstractResponseParser):
    def parse_response(self, response: dict, balance_coins: List[str] = balance_currency.BALANCE_COINS) -> List[Wallet]:
        try:
            wallet_data = {
                "exchange": "binance",
                "coins": {
                    currency["asset"]: {
                        "name": currency["asset"],
                        "amount": currency["free"],
                    }
                    for currency in response["balances"]
                    if currency["asset"] in balance_coins
                },
                "sign": -1.0,
                "time": time.time(),
                "date": datetime.utcnow(),
            }

            wallet = [Wallet.parse_obj(wallet_data)]
            return wallet
        except Exception as err:
            logging.debug(err)
            raise Exception("Binance Parser: Could not parse Wallet")


class BinanceTransactionHistoryResponseParser(AbstractResponseParser):
    def parse_response(self, response: dict, market_code: str, **kwargs):

        try:

            currency_name, pair_currency_name = market_code.split("/")

            transaction_data = []

            for currency in response:
                if currency["isBuyer"] == True:
                    order_type = "buyer"
                elif currency["isBuyer"] == False:
                    order_type = "seller"

                data = {
                    "id": currency["id"],
                    "currency_name": currency_name,
                    "pair_currency_name": pair_currency_name,
                    "market": market_code,
                    "time": currency["time"]/1000,
                    "exchange": "binance",
                    "type": order_type,
                    "fee": currency["commission"],
                    "currency_value": currency["qty"],
                    "pair_currency_value": float(currency["price"]),
                }

                transaction_data.append(data)
            transactions = pydantic.parse_obj_as(
                List[Transaction], transaction_data)
            return transactions
        except Exception as err:
            logging.debug(err)
            raise err
