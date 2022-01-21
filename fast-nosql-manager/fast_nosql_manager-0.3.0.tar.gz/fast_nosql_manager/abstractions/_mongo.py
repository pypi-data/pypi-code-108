from fast_nosql_manager.interfaces.db_config_interface import DBConfigInterface
from pymongo import MongoClient, errors
from pymongo import errors

class Mongo(object):
  """ 
    Os IFs iniciáis são checagens de tipo
    para que não seja possível a quebra das
    funções
  """

  def __init__(self, db_config: DBConfigInterface, db_name: str = 'mongo'):
    self._conn: MongoClient = db_config.get_connection()
    self._db_name = db_name
    
  def update_document(self, collection_name, where, new_values):
    collection = self._conn[self._db_name][collection_name]
    update_values = { "$set": new_values }
    return collection.update_one(where, update_values, upsert=False)
    
  def delete_document(self, collection_name, where):
    collection = self._conn[self._db_name][collection_name]
    return collection.delete_one(where)
    
  def create_document(self, collection_name, documents):
    collection = self._conn[self._db_name][collection_name]
    
    if isinstance(documents, list):
      return collection.insert_many(documents)
  
    return collection.insert_one(documents)
    
  def delete_collection(self, collection_name):
    try:
      return self._conn[self._db_name].drop_collection(collection_name)
    except errors.CollectionInvalid:
      return
    
  def create_collection(self, collection_name: str):
    try:
      return self._conn[self._db_name].create_collection(collection_name)
    except errors.CollectionInvalid:
      return
      
  def select_all(self, collection_name, where={}):
    return_data=[]
    collection = self._conn[self._db_name][collection_name]
    for item in collection.find(where): return_data.append(item)
    return return_data