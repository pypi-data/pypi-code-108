from abc import ABCMeta, abstractmethod
from decimal import Decimal

class Transaction(metaclass=ABCMeta):
  def __init__(self, transaction_id:str):
    self.transaction_id = transaction_id

  def get_transaction_id(self) -> str:
    return self.transaction_id

  @abstractmethod
  def get_timestamp(self) -> str:
    pass

  @abstractmethod
  def get_transaction_fee(self) -> Decimal:
    pass