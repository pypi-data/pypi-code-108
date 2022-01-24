from abc import ABCMeta, abstractmethod
from senkalib.caaj_journal import CaajJournal
from senkalib.chain.transaction import Transaction

class CaajPlugin(metaclass=ABCMeta):
  chain = None

  @abstractmethod
  def can_handle(cls, transaction:Transaction) -> bool:
    pass

  @abstractmethod
  def get_caajs(cls, transaction:Transaction) -> CaajJournal:
    pass