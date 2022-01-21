from .implementations.mongo import MongoRepository

mongo = MongoRepository(
  db_str_connection='mongodb://localhost:27017/',
  db_name='local'
) 

mongo_pagarme = MongoRepository(
  db_str_connection='mongodb://localhost:27017/',
  db_name='pagarme'
) 

def test_update_document():
  mongo_pagarme.update_document(
    collection_name='accounts', 
    where={'document': '12345678904'}, 
    new_values={'user_name': 'Blabla'}
  )
  
def test_create_collection():
  mongo.create_collection('teste')

def test_create_document():
  mongo.create_document('teste', [{'name': 'Oscar'}, {'name': 'Oscar'}])
  
def test_select_all():
  response = mongo.select_all(collection_name='teste')
  assert len(response) == 2
  
def test_delete_document():
  mongo.delete_document('teste', {'name': 'Oscar'})
  response = mongo.select_all(collection_name='teste')
  assert len(response) == 1

def test_delete_collection():
  mongo.delete_collection('teste')