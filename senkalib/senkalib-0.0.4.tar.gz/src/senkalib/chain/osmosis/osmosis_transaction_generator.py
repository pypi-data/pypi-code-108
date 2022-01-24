from senkalib.chain.transaction import Transaction
from senkalib.chain.transaction_generator import TransactionGenerator
from senkalib.senka_setting import SenkaSetting
from senkalib.chain.osmosis.osmosis_transaction import OsmosisTransaction
from typing import List
import requests

class OsmosisTransactionGenerator(TransactionGenerator):
  chain = 'osmosis'

  @classmethod
  def get_transactions(cls, settings:SenkaSetting, address:str, timerange:dict = None, blockrange:dict = None) -> List[Transaction]:
    osmosis_transactions = []
    num_transactions = 50
    startblock = int(blockrange['startblock']) if blockrange is not None and 'startblock' in blockrange and type(blockrange['startblock']) is int else 0
    endblock = int(blockrange['endblock']) if blockrange is not None and 'endblock' in blockrange and type(blockrange['endblock']) is int else None

    while num_transactions >= 50:
      transactions = OsmosisTransactionGenerator.get_txs(address, startblock)
      num_transactions = len(transactions)
      for transaction in transactions:
        startblock = transaction['header']['id']
        if endblock is not None and startblock <= endblock:
          return osmosis_transactions
        osmosis_transactions.append(OsmosisTransaction(transaction))


    return osmosis_transactions

  @classmethod
  def get_txs(cls, address, startblock):
    response = requests.get(
        'https://api-osmosis.cosmostation.io/v1/account/new_txs/%s' % address,
        params={'from': startblock, 'limit': 50})
    transactions = response.json()
    return transactions