import pydantic
import logging
import time

from datetime import datetime
from typing import List


from orionx_python_client.currency import CEROS as ORIONX_CEROS

from odin_bot_entities.trades import Order, Transaction
from odin_bot_entities.balances import Wallet

from odin_bot_exchanges.responses import AbstractResponseParser


class OrionXOrderResponseParser(AbstractResponseParser):
    def parse_response(self, response: dict, order_id: str, market_code: str, currency_ceros: dict = ORIONX_CEROS) -> Order:
        if response["data"]["order"] == None:
            raise Exception("OrionX Parser: No Order data received.")
        if "errors" in response:
            logging.error(response["errors"])
            raise Exception("OrionX Parser: Found errors in response")

        try:
            transaction_data = [
                {
                    "id": data["id"],
                    "currency_name": data["currency"]["code"],
                    "pair_currency_name": data["pairCurrency"]["code"],
                    "market": f"{data['currency']['code']}/{data['pairCurrency']['code']}",
                    "exchange": "orionX",
                    "time": data["date"] / 1000,
                    "type": data["type"],
                    "fee": data["commission"]
                    / 10 ** currency_ceros[data["currency"]["code"]],
                    "currency_value": data["cost"]
                    / 10 ** currency_ceros[data["pairCurrency"]["code"]],
                    "pair_currency_value": data["amount"]
                    / 10 ** currency_ceros[data["currency"]["code"]],
                }
                for data in response["data"]["order"]["transactions"]
                if data["type"] == "trade-in"
            ]

            transactions = pydantic.parse_obj_as(
                List[Transaction], transaction_data)

            order_data = {
                "id": order_id,
                "amount": response["data"]["order"]["amount"],
                "exchange": "orionX",
                "type": response["data"]["order"]["type"],
                "market": market_code,
                "status": response["data"]["order"]["amount"],
                "transactions": transactions,
            }
            order = Order.parse_obj(order_data)
            return order
        except Exception as err:
            logging.error(err)
            logging.debug(response)
            raise Exception("OrionX Parser: Could not parse Order.")


class OrionXTransactionFromOrderResponseParser(AbstractResponseParser):
    def parse_response(self, response: dict, currency_ceros: dict = ORIONX_CEROS) -> Order:
        logging.info(response)
        if response["data"]["order"] == None:
            raise Exception("OrionX Parser: No Order data received.")
        if "errors" in response:
            logging.error(response["errors"])
            raise Exception("OrionX Parser: Found errors in response")

        try:
            transaction_data = [
                {
                    "id": data["id"],
                    "currency_name": data["currency"]["code"],
                    "pair_currency_name": data["pairCurrency"]["code"],
                    "market": f"{data['currency']['code']}/{data['pairCurrency']['code']}",
                    "exchange": "orionX",
                    "time": data["date"] / 1000,
                    "type": data["type"],
                    "fee": data["commission"]
                    / 10 ** currency_ceros[data["currency"]["code"]],
                    "currency_value": data["cost"]
                    / 10 ** currency_ceros[data["pairCurrency"]["code"]],
                    "pair_currency_value": data["amount"]
                    / 10 ** currency_ceros[data["currency"]["code"]],
                }
                for data in response["data"]["order"]["transactions"]
                if data["type"] == "trade-in" or data["type"] == "trade-out"
            ]

            transactions = pydantic.parse_obj_as(
                List[Transaction], transaction_data)
            return transactions
        except Exception as err:
            logging.debug(err)
            raise Exception(
                "OrionX Parser: Could not parse Transactions From Order Response."
            )


class OrionXWalletResponseParser(AbstractResponseParser):
    def parse_response(self, response: dict, currency_ceros: dict = ORIONX_CEROS) -> List[Wallet]:
        print(currency_ceros)
        if response["data"]["me"] == None:
            raise Exception("OrionX Parser: No Order data received.")
        if "errors" in response:
            logging.error(response["errors"])
            raise Exception("OrionX Parser: Found errors in response")

        try:
            coins = {}
            available = {}
            loans = {}
            for wallet_data in response["data"]["me"]["wallets"]:
                currency = wallet_data["currency"]["code"]
                available_balance = round(
                    wallet_data["availableBalance"] /
                    10 ** currency_ceros[currency],
                    currency_ceros[currency],
                )
                balance = round(
                    wallet_data["balance"] / 10 ** currency_ceros[currency],
                    currency_ceros[currency],
                )
                if wallet_data["loanUsedAmount"]:
                    loan = round(
                        wallet_data["loanUsedAmount"]
                        / 10 ** currency_ceros[currency],
                        currency_ceros[currency],
                    )
                else:
                    loan = 0
                coins[currency] = {"name": currency, "amount": balance}
                available[currency] = {
                    "name": currency, "amount": available_balance}

                loans[currency] = {"name": currency, "amount": loan}

            wallets = pydantic.parse_obj_as(
                List[Wallet],
                [
                    {
                        "exchange": "orionX",
                        "coins": coins,
                        "sign": 1,
                        "time": time.time(),
                        "date": datetime.utcnow(),
                    },
                    {
                        "exchange": "orionX-available",
                        "coins": available,
                        "sign": 0,
                        "time": time.time(),
                        "date": datetime.utcnow(),
                    },
                    {
                        "exchange": "Loans",
                        "coins": loans,
                        "sign": -1,
                        "time": time.time(),
                        "date": datetime.utcnow(),
                    },
                ],
            )

            return wallets
        except Exception as err:
            logging.debug(err)
            raise Exception("OrionX Parser: Could not parse Balances")


class OrionXTradeHistoryResponseParser(AbstractResponseParser):
    def parse_response(self, response: dict, currency_ceros: dict = ORIONX_CEROS) -> List[Transaction]:
        if response["data"]["orders"] == None:
            raise Exception(
                "OrionX Parser: No Trade History data received.")
        if "errors" in response:
            logging.error(response["errors"])
            raise Exception("OrionX Parser: Found errors in response")

        try:

            for order_data in response["data"]["orders"]["items"]:

                transaction_data = order_data["transactions"]
                transaction_obj = [
                    {
                        "id": tx["_id"],
                        "currency_name": tx["currency"]["code"],
                        "pair_currency_name": tx["pairCurrency"]["code"],
                        "market": f"{tx['currency']['code']}/{tx['pairCurrency']['code']}",
                        "time": tx["date"] / 1000,
                        "exchange": "orionX",
                        "type": tx["type"],
                        "fee": tx["commission"]
                        / 10 ** currency_ceros[tx["currency"]["code"]],
                        "currency_value": tx["cost"]
                        / 10 ** currency_ceros[tx["pairCurrency"]["code"]],
                        "pair_currency_value": tx["amount"]
                        / 10 ** currency_ceros[tx["currency"]["code"]],
                        "taker": tx["adds"],
                        "order_id": tx["orderId"],
                    }
                    for tx in transaction_data
                ]

            transactions = pydantic.parse_obj_as(
                List[Transaction], transaction_obj)

            return transactions
        except Exception as err:
            logging.error(err)
            logging.debug(response)
            raise Exception("OrionX Parser: Could not parse Trade History.")
