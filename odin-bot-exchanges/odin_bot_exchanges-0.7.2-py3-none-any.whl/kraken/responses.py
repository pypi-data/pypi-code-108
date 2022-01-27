import time
import logging
import pydantic


from datetime import datetime
from typing import List

import odin_bot_exchanges.currency as balance_currency
import odin_bot_exchanges.kraken.currency as kraken_currency

from odin_bot_entities.trades import Transaction, LedgerTransaction
from odin_bot_entities.balances import Wallet
from odin_bot_exchanges.responses import AbstractResponseParser


class KrakenTransactionResponseParser(AbstractResponseParser):
    def parse_response(self, response: dict, trade_id: str, market_code: str, rename_coin_map: dict = kraken_currency.KRAKEN_RENAME_COINS) -> Transaction:
        if len(response["error"]) != 0:
            logging.error(response["error"])
            raise Exception("Kraken Parser: Response had errors")
        if response["result"] == {}:
            raise Exception("Kraken Parser: Response had no data")
        try:
            currency_name, pair_currency_name = market_code.split("/")
            currency_name = rename_coin_map.get(currency_name)
            pair_currency_name = rename_coin_map.get(pair_currency_name)
            transaction = Transaction.parse_obj(
                {
                    "id": trade_id,
                    "currency_name": currency_name,
                    "pair_currency_name": pair_currency_name,
                    "market": f"{currency_name}/{pair_currency_name}",
                    "time": response["result"][trade_id]["closetm"],
                    "exchange": "kraken",
                    "type": response["result"][trade_id]["descr"]["type"],
                    "fee": response["result"][trade_id]["fee"],
                    "currency_value": response["result"][trade_id]["vol"],
                    "pair_currency_value": response["result"][trade_id]["cost"],
                }
            )

            return transaction
        except Exception as err:
            logging.error(err)
            raise Exception("Kraken Parser: Could not parse Transaction.")


class KrakenTradeHistoryResponseParser(AbstractResponseParser):
    def parse_response(self, response: dict, rename_market_map: dict = kraken_currency.KRAKEN_RENAME_PAIRS):
        if len(response["error"]) != 0:
            logging.error(response["error"])
            raise Exception("Kraken Parser: Response had errors")
        try:
            logging.info(rename_market_map)
            transaction_data = []
            for _, tx in response["result"]["trades"].items():
                logging.info(tx["pair"])
                if tx["pair"] in rename_market_map.keys():
                    market = rename_market_map[tx["pair"]]
                    currency_name, pair_currency_name = market.split("/")
                    data = {
                        "id": tx["ordertxid"],
                        "time": tx["time"],
                        "exchange": "kraken",
                        "type": tx["type"],
                        "market": market,
                        "fee": float(tx["fee"]),
                        "currency_name": currency_name,
                        "pair_currency_name": pair_currency_name,
                        "currency_value": float(tx["vol"]),
                        "pair_currency_value": float(tx["cost"]),
                    }
                    transaction_data.append(data)
                else:
                    logging.error(f"Pair {tx['pair']} not in dict")
                    raise Exception
            transactions = pydantic.parse_obj_as(
                List[Transaction], transaction_data)
            return transactions

        except Exception as err:
            logging.debug(err)
            raise Exception("Kraken Parser: Could not parse Trade History")


class KrakenWalletResponseParser(AbstractResponseParser):
    def parse_response(self, response: dict, balance_coins: List[str] = balance_currency.BALANCE_COINS, rename_coin_map: dict = kraken_currency.KRAKEN_RENAME_COINS) -> List[Wallet]:
        if len(response["error"]) != 0:
            logging.error(response["error"])
            raise Exception("Kraken Parser: Response had errors")
        try:
            coin_data = {}

            for key, value in response["result"].items():

                if key in balance_coins:
                    currency_name = rename_coin_map.get(key)

                    if currency_name in balance_coins:
                        amount = round(float(value), 8)

                        coin = {"name": currency_name, "amount": amount}
                        coin_data[currency_name] = coin
                else:
                    logging.info(f"Currency: {key} is not in Balance Coins")

            wallet_data = {
                "exchange": "kraken",
                "coins": coin_data,
                "sign": 1,
                "time": time.time(),
                "date": datetime.utcnow(),
            }

            wallet = [Wallet.parse_obj(wallet_data)]
            return wallet
        except Exception as err:
            logging.debug(err)
            raise Exception("Kraken Parser: Could not parse Balance")


class KrakenTickerResponseParser(AbstractResponseParser):
    def parse_response(self, response: dict, market_code: str) -> float:
        if len(response["error"]) != 0:
            logging.error(response["error"])
            raise Exception("Kraken Parser: Response had errors.")
        try:
            market = market_code.replace("/", "")
            bid_price = float(response["result"][market]["b"][0])
            return bid_price
        except Exception as err:
            logging.debug(err)
            raise Exception("Kraken Parser: Could not parse bid price.")


class KrakenLedgerTransactionResponseParser(AbstractResponseParser):
    def parse_response(self, response: dict):
        if len(response["error"]) != 0:
            logging.error(response["error"])
            raise Exception("Kraken Parser: Response had errors")
        try:
            transaction_data = []
            for _, tx in response["result"]["ledger"].items():
                data = {
                    "id": tx["refid"],
                    "time": tx["time"],
                    "exchange": "kraken",
                    "type": tx["type"],
                    "fee": float(tx["fee"]),
                    "subtype": tx["subtype"],
                    "asset_class": tx["aclass"],
                    "asset": tx["asset"],
                    "amount": float(tx["amount"]),
                    "resulting_balance": float(tx["balance"]),
                }
                transaction_data.append(data)
            transactions = pydantic.parse_obj_as(
                List[LedgerTransaction], transaction_data)
            return transactions

        except Exception as err:
            logging.debug(err)
            raise Exception("Kraken Parser: Could not parse Trade History")
