from fast_nosql_manager.abstractions._mongo import Mongo
from fast_nosql_manager.interfaces.db_config_interface import DBConfigInterface
import pymongo


class DataBaseConfig(DBConfigInterface):
  """ 
  Inicialização da classe de conexão
  ao banco
  """

  def __init__(self, db_str_connection: str, db_name: str = 'mongo'):
    self._db_connection = db_str_connection
    self.name = db_name


  def get_connection(self):
    mydb = pymongo.MongoClient(self._db_connection, serverSelectionTimeoutMS=5000)
    return mydb


class MongoRepository(Mongo):
  def __init__(self, db_str_connection: str, db_name: str):
    super().__init__(db_config=DataBaseConfig(db_str_connection), db_name=db_name)
