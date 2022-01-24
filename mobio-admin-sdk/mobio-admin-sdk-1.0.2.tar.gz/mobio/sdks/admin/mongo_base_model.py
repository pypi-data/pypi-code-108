from pymongo import MongoClient, ReadPreference
import re
from mobio.libs.Singleton import Singleton


@Singleton
class MongoClientInit(object):
    def __init__(self):
        self.db_conn = dict()

    def mongodb_init(self, server_id, db_uri):
        db_name = str(re.search(
            r"^mongodb://[^@]+@[^/]+/([^?$]+).*$", db_uri
        ).group(1))
        if not self.db_conn or not self.db_conn.get(server_id):
            self.db_conn[server_id] = MongoClient(db_uri)
        #     print("MongoClientInit server_info: {}".format(global_dict_mongodb_client.get(merchant_id).server_info()))
        # else:
        #     print("MongoClientInit not none")
        return self.db_conn.get(server_id).get_database(db_name)


class BaseMongoDB(object):
    def __init__(self):
        self.db = None
        self.collection = None
        self.conn_primary = None
        self.conn_secondary = None

    def get_connection_from_merchant(self, merchant_id, key_module):
        try:
            from .utils import get_server_uri_from_merchant
            server_id, db_uri = get_server_uri_from_merchant(merchant_id, key_module)
            self.db = MongoClientInit().mongodb_init(server_id, db_uri)
            self.conn_primary = self.db.get_collection(self.collection)
            self.conn_secondary = self.db.get_collection(
                self.collection, read_preference=ReadPreference.SECONDARY_PREFERRED
            )
        except Exception as er:
            err_msg = "admin_sdk::get_connection_from_merchant ERR: {}".format(er)
            print(err_msg)

    def get_connection_from_server(self, server_id, db_uri):
        try:
            self.db = MongoClientInit().mongodb_init(server_id, db_uri)
            self.conn_primary = self.db.get_collection(self.collection)
            self.conn_secondary = self.db.get_collection(
                self.collection, read_preference=ReadPreference.SECONDARY_PREFERRED
            )
        except Exception as er:
            err_msg = "admin_sdk::get_connection_from_server ERR: {}".format(er)
            print(err_msg)

    def get_connection_from_default(self, key_module):
        try:
            from .utils import get_server_uri_default_from_module
            server_id, db_uri = get_server_uri_default_from_module(key_module)
            self.db = MongoClientInit().mongodb_init(server_id, db_uri)
            self.conn_primary = self.db.get_collection(self.collection)
            self.conn_secondary = self.db.get_collection(
                self.collection, read_preference=ReadPreference.SECONDARY_PREFERRED
            )
        except Exception as er:
            err_msg = "admin_sdk::get_connection_from_default ERR: {}".format(er)
            print(err_msg)


# class BaseCollectionMongoDB(BaseMongoDB):
#     def __init__(self):
#         super(BaseCollectionMongoDB, self).__init__()
#
#     @abstractmethod
#     def validate_bson(self, bson_data):
#         """Schema Validation"""
#         pass
#
#     @abstractmethod
#     def sync_table(self):
#         """Manager index of collection"""
#         pass
