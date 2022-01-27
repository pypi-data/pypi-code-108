import os
from typing import Optional
from pymongo import MongoClient, database

__all__ = (
    'connect',
    'set_connection_env',
    'get_connection_env',
    '_DBConnection',
    '_get_connection',
)

DEFAULT_CONNECTION_NAME = 'default'
_connections: dict = {}
_connection_settings: dict = {}


def connect(
    connection_str: str,
    dbname: str,
    ssl: bool = False,
    max_pool_size: int = 100,
    ssl_cert_path: Optional[str] = None,
    server_selection_timeout_ms: int = 60000,
    connect_timeout_ms: int = 30000,
    socket_timeout_ms: int = 60000,
    env_name: Optional[str] = None,
) -> None:
    """init connection to mongodb

    Args:
        connection_str (str): full connection string
        dbname (str): mongo db name
        ssl (bool, optional): flag for ssl cert. Defaults to False.
        max_pool_size (int, optional): max connection pool. Defaults to 100.
        ssl_cert_path (Optional[str], optional): path to ssl cert. Defaults to None.
        server_selection_timeout_ms (int, optional): ServerSelectionTimeoutMS. Defaults to 60000.
        connect_timeout_ms (int, optional): ConnectionTimeoutMS. Defaults to 30000.
        socket_timeout_ms (int, optional): SocketTimeoutMS. Defaults to 60000.
        env_name (Optional[str], optional): connection env name. Defaults to None.
    """
    set_connection_env(env_name)
    connection_env = get_connection_env()
    _connection_settings[connection_env] = {
        'connection_str': connection_str,
        'dbname': dbname,
        'ssl': ssl,
        'pool_size': max_pool_size,
        'server_selection_timeout_ms': server_selection_timeout_ms,
        'connect_timeout_ms': connect_timeout_ms,
        'socket_timeout_ms': socket_timeout_ms,
        'ssl_cert_path': ssl_cert_path,
    }
    _get_connection(str(os.getpid()), env_name=connection_env)


def set_connection_env(name: Optional[str] = None):
    os.environ['MONGODANTIC_DB_ENV'] = name or DEFAULT_CONNECTION_NAME


def get_connection_env() -> str:
    return os.environ.get('MONGODANTIC_DB_ENV', DEFAULT_CONNECTION_NAME)


class _DBConnection(object):
    def __init__(
        self, alias: str = str(os.getpid()), env_name: str = get_connection_env()
    ):
        self._alias = alias
        if env_name not in _connection_settings:
            raise RuntimeError('not execute `connect` or empty connection settings')
        self.connection_string = _connection_settings[env_name]['connection_str']
        self.db_name = _connection_settings[env_name]['dbname']
        self.max_pool_size = _connection_settings[env_name]['pool_size']
        self.ssl = _connection_settings[env_name]['ssl']
        self.ssl_cert_path = _connection_settings[env_name]['ssl_cert_path']
        self.server_selection_timeout_ms = _connection_settings[env_name][
            'server_selection_timeout_ms'
        ]
        self.connect_timeout_ms = _connection_settings[env_name]['connect_timeout_ms']
        self.socket_timeout_ms = _connection_settings[env_name]['socket_timeout_ms']
        self._mongo_connection = self._init_mongo_connection()
        self._database: Optional[database.Database] = None

    def _init_mongo_connection(self, connect: bool = False) -> MongoClient:
        connection_params = dict(
            connect=connect,
            serverSelectionTimeoutMS=self.server_selection_timeout_ms,
            maxPoolSize=self.max_pool_size,
            connectTimeoutMS=self.connect_timeout_ms,
            socketTimeoutMS=self.socket_timeout_ms,
            retryWrites=False,
            retryReads=False,
        )
        if self.ssl:
            connection_params['tlsCAFile'] = self.ssl_cert_path
            connection_params['tlsAllowInvalidCertificates'] = self.ssl
        return MongoClient(self.connection_string, **connection_params)

    def _reconnect(self):
        self.close()
        return self.__init__(self._alias)

    def get_database(self) -> database.Database:
        if hasattr(self, '_database') and self._database is not None:
            return self._database
        self._database = self._mongo_connection.get_database(self.db_name)
        return self._database

    def close(self) -> None:
        if _connections:
            old_connection = _connections.pop(self._alias, None)
            if old_connection:
                old_connection._mongo_connection.close()
                del old_connection

    def __del__(self):
        self.close()


def _get_connection(alias: str, env_name: str = get_connection_env()) -> _DBConnection:
    connection = _connections.get(str(alias))
    if not connection:
        connection = _DBConnection(str(alias), env_name=env_name)
        _connections[alias] = connection
    return connection


# for old vervions
def init_db_connection_params(
    connection_str: str,
    dbname: str,
    ssl: bool = False,
    max_pool_size: int = 100,
    ssl_cert_path: Optional[str] = None,
    server_selection_timeout_ms: int = 60000,
    connect_timeout_ms: int = 30000,
    socket_timeout_ms: int = 60000,
    env_name: str = DEFAULT_CONNECTION_NAME,
):
    return connect(**locals())
