from abc import ABC, abstractmethod


class DBConfigInterface(ABC):
  
  name: str

  @abstractmethod
  def get_connection(self):
    pass