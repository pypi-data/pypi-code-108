import os

from dataUtils.DBClient import DBClient

db_client = DBClient.GetDBClient(os.getenv('APIKEY'))
db_name = os.environ['RIALTIC_REF_DB']
