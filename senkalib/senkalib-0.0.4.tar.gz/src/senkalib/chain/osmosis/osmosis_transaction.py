from senkalib.chain.transaction import Transaction 
from decimal import *
from datetime import datetime as dt

getcontext().prec = 50

class OsmosisTransaction(Transaction):
  chain = 'osmosis'

  def __init__(self, transaction:dict):
    super().__init__(transaction["data"]["txhash"])
    self.transaction = transaction

  def get_timestamp(self) -> str:
    return str(dt.strptime(self.transaction['header']['timestamp'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=None))

  def get_transaction_fee(self) -> Decimal:
    return Decimal(self.transaction['data']['tx']['auth_info']['fee']['amount'][0]['amount'])

  def get_transaction(self) -> dict:
    return self.transaction