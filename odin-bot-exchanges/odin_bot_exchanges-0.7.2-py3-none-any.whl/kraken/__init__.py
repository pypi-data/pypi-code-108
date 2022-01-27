import aiohttp
import time
import asyncio
import logging


from typing import List, Dict
from dataclasses import dataclass


from odin_bot_entities.trades import Transaction
from odin_bot_entities.balances import Wallet
from odin_bot_exchanges.exchange import ExchangeService
from odin_bot_exchanges.responses import AbstractResponseParser
import odin_bot_exchanges.kraken.currency as kraken_currency
from odin_bot_exchanges.kraken.client import KrakenClient

from odin_bot_exchanges.kraken.responses import KrakenLedgerTransactionResponseParser, KrakenWalletResponseParser, KrakenTransactionResponseParser, KrakenTickerResponseParser, KrakenTradeHistoryResponseParser


@dataclass
class KrakenExchange(ExchangeService):
    exchange: str = "kraken"

    def __init__(self, api_key: str, secret_key: str, api_url: str):
        self.client = KrakenClient(
            api_key=api_key, api_url=api_url, secret_key=secret_key)
        self.wallet_parser: AbstractResponseParser = KrakenWalletResponseParser()
        self.transaction_parser: AbstractResponseParser = (
            KrakenTransactionResponseParser()
        )
        self.ticker_parser: AbstractResponseParser = KrakenTickerResponseParser()
        self.trade_history_parser: AbstractResponseParser = (
            KrakenTradeHistoryResponseParser()
        )
        self.ledger_response_parser = KrakenLedgerTransactionResponseParser()

    async def get_transaction_response(self, trade_id: str, market_code: str) -> Transaction:
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "nonce": str(int(time.time() * 1000)),
                    "txid": trade_id,
                }

                response = await self.client.request(
                    "POST", "/0/private/QueryOrders", session, payload
                )

                transaction = self.transaction_parser.parse_response(trade_id=trade_id, market_code=market_code, response=response
                                                                     )
                return transaction
        except Exception as err:
            logging.debug(err)
            raise err

    async def get_wallet_response(self) -> List[Wallet]:
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "nonce": str(int(time.time() * 1000)),
                }

                response = await self.client.request(
                    "POST", "/0/private/Balance", session, payload
                )
                balance = self.wallet_parser.parse_response(response=response)
                return balance
        except Exception as err:
            logging.error(err)
            raise err

    async def get_trades_history_response(self, start: float, end: float, rename_market_map: Dict = kraken_currency.KRAKEN_RENAME_PAIRS) -> List[Transaction]:
        try:
            async with aiohttp.ClientSession() as session:
                offset = 0
                transactions = []

                while True:
                    print(offset)
                    await asyncio.sleep(2)
                    payload = {
                        "nonce": str(int(time.time() * 1000)),
                        "trades": True,
                        "start": str(int(start)),
                        "end": str(int(end)),
                        "ofs": offset,
                    }
                    response = await self.client.request(
                        "POST", "/0/private/TradesHistory", session, payload
                    )

                    if len(response["error"]) != 0:
                        print(response)
                        print("Rate Limit Reached- Sleeping")
                        await asyncio.sleep(30)
                    else:

                        count = response["result"]["count"]
                        logging.info(f"Number of Transactions: {count}")
                        transactions += self.trade_history_parser.parse_response(
                            response=response, rename_market_map=rename_market_map
                        )
                        if count == 0:
                            break
                        if offset <= count:
                            offset += 50
                        else:
                            break

                return transactions
        except Exception as err:
            logging.debug(err)
            raise err

    async def get_order_response(self):
        return await super().get_order_response()

    async def get_ledger_history_response(self, asset: str, type: str, start: float, end: float) -> List[Transaction]:
        try:
            async with aiohttp.ClientSession() as session:

                offset = 0
                transactions = []

                while True:
                    logging.info(offset)
                    await asyncio.sleep(3)
                    payload = {
                        "nonce": str(int(time.time() * 1000)),
                        "asset": asset,
                        "type": type,
                        "start": str(int(start)),
                        "end": str(int(end)),
                        "ofs": offset,
                    }
                    response = await self.client.request(
                        "POST", "/0/private/Ledgers", session, payload
                    )

                    if len(response["error"]) != 0:
                        logging.debug(response)
                        logging.info("Rate Limit Reached- Sleeping")
                        await asyncio.sleep(60)
                    else:

                        count = response["result"]["count"]
                        logging.info(f"Num Records: {count}")

                        ledgers = self.ledger_response_parser.parse_response(
                            response=response
                        )
                        print(ledgers)

                        transactions += ledgers
                        if count == 0:
                            break
                        if offset <= count:
                            offset += 50
                        else:
                            break

                return transactions
        except Exception as err:
            logging.debug(err)
            raise err
