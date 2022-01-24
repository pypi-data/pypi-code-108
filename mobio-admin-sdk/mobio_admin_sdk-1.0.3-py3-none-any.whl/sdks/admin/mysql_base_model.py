from mobio.libs.Singleton import Singleton
import threading
from peewee import Metadata, MySQLDatabase, Model
from playhouse.shortcuts import ReconnectMixin

class ReconnectMySQLDatabase(ReconnectMixin, MySQLDatabase):
    pass

class ThreadSafeDatabaseMetadata(Metadata):
    def __init__(self, *args, **kwargs):
        # database attribute is stored in a thread-local.
        self._local = threading.local()
        super(ThreadSafeDatabaseMetadata, self).__init__(*args, **kwargs)

    def _get_db(self):
        return getattr(self._local, 'database', self._database)
    def _set_db(self, db):
        self._local.database = self._database = db
    database = property(_get_db, _set_db)


@Singleton
class MySQLClientInit(object):
    def __init__(self):
        self.db_conn = dict()

    def get_connection_from_server(self, server_id, db_uri):
        db_name, db_host, db_port, db_user, db_pwd = MySQLClientInit.get_param_from_uri(db_uri)
        if not self.db_conn or not self.db_conn.get(server_id):
            db = ReconnectMySQLDatabase(db_name, host=db_host, port=int(db_port), user=db_user, passwd=db_pwd)
            db.connect()
            self.db_conn[server_id] = db
        return self.db_conn.get(server_id)

    def get_connection_from_merchant(self, merchant_id, key_module):
        from .utils import get_server_uri_from_merchant
        server_id, db_uri = get_server_uri_from_merchant(merchant_id, key_module)
        return self.get_connection_from_server(server_id, db_uri)

    def get_connection_from_default(self, key_module):
        from .utils import get_server_uri_default_from_module
        server_id, db_uri = get_server_uri_default_from_module(key_module)
        return self.get_connection_from_server(server_id, db_uri)

    @staticmethod
    def get_param_from_uri(db_uri):
        db_name, db_host, db_port, db_user, db_pwd = None, None, None, None, None
        try:
            l = db_uri.split("@")
            l1 = l[0].split("//")[1].split(":")
            db_user = l1[0]
            db_pwd = l1[1]
            l2 = l[1].split("/")
            db_name = l2[1]
            l3 = l2[0].split(":")
            db_host = l3[0]
            db_port = l3[1]
        except Exception as er:
            err_msg = "admin_sdk::get_param_from_uri ERR: {}".format(er)
            print(err_msg)
        return db_name, db_host, db_port, db_user, db_pwd

class BaseModel(Model):
    class Meta:
        # Instruct peewee to use our thread-safe metadata implementation.
        model_metadata_class = ThreadSafeDatabaseMetadata

