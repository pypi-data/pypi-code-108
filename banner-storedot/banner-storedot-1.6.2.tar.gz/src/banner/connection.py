
from typing import Union, Dict, Iterable
from abc import ABC, abstractmethod
from enum import Enum
from sys import getsizeof
from json import loads
from itertools import chain

from MySQLdb import connect, MySQLError
from MySQLdb._exceptions import OperationalError
from MySQLdb.cursors import DictCursor
import redis
from pandas import DataFrame

class ConnectionType(Enum):
    mysql = 'mysql'
    redis = 'redis'

class ConnectionFactory(object):
    ''' Connection Factory'''
    def __new__(self, con_type: Union[ConnectionType, str] = ConnectionType.mysql, **kwargs):
        try:
            con_type = ConnectionType[con_type]

        except KeyError:
            pass
            
        if not isinstance(con_type, ConnectionType):
            raise TypeError('Unknown Connection Type')
        
        if con_type is ConnectionType.redis:
            return RedisConnection(**kwargs)
            
        return MySqlConnection(**kwargs)        

class Connection(ABC):
    HOST_KEY = 'host'
    NAME_KEY = 'name'
    DB_KEY = 'db'
    TTL_KEY = 'ttl'

    @abstractmethod
    def query(self, query: str):
        pass
    
    @abstractmethod
    def __str__(self):
        pass

class CacheConnection(Connection):
    @abstractmethod
    def cache(self, key, value):
        pass

class RedisConnection(CacheConnection):
    HOUR = 3600
    ENTRY_SIZE_LIMIT = 64000000
    DATAFRAME_ENTRY_LIMIT = 300000
    CHUNK_PREFIX = '#'

    def __init__(self, host, port=6379, passwd=None, db=0, ssl_key=None, ssl_cert=None, name=None, ttl=HOUR):
        self.data = dict(
            host=host,
            port=port,
            password=passwd,
            db=db,
            ssl_keyfile=ssl_key,
            ssl_certfile=ssl_cert,
            name=name,
            ttl=ttl
        )

        # Redis manages opening/closing by itself, it is safe to init it here
        self.instance = redis.Redis(
            **{k: v for k, v in self.data.items() if v and k not in [Connection.NAME_KEY, Connection.TTL_KEY]}, 
            decode_responses=True
        )

    def query(self, query: Union[Iterable, str] = '*', keys=False, resp_type=None):
        '''
            Retrieve Values/Keys from Connection
            Uses get for a single value, mget for multiple
            Returns value, list of values for multiple
        '''
        if keys:
            return self.__query_keys(query)
        
        # Look for values
        func = self.instance.get if isinstance(query, str) else self.instance.mget
        values = func(query)

        return self.__parse_result(values, resp_type)
    
    def __parse_result(self, result, _type=None):
        # Result could be a list or single value
        # Currently only handles DataFrame
        if _type == DataFrame:
            if isinstance(result, list):
                return DataFrame.from_dict(chain(*[loads(res) for res in result]), orient='columns')
        
            return DataFrame.from_dict(loads(result), orient='columns')

        return result

    def __query_keys(self, query: str):
        if not query:
            return []
        
        return self.instance.keys(pattern=f'*{str(query)}*')
        
    def cache(self, key, value, ttl=None, nx=False):
        ttl = ttl if isinstance(ttl, int) else self.data.get(Connection.TTL_KEY, RedisConnection.HOUR)
        
        # Case Pandas.DataFrame
        if isinstance(value, DataFrame):
            return self.__cache_df(key, value, ttl, nx)

        return self.instance.set(key, value, ex=ttl, nx=nx)

    def __cache_df(self, key, df, ttl, nx):
        if len(df) <= RedisConnection.DATAFRAME_ENTRY_LIMIT:
            return self.instance.set(key, df.to_json(orient='records'), ex=ttl, nx=nx)

        for index, chunck in enumerate(df.split(size=RedisConnection.DATAFRAME_ENTRY_LIMIT)): # Decorated function splitting df into list of dfs of size rows
            resp = self.instance.set(
                key + f'{RedisConnection.CHUNK_PREFIX}{index}' if index else key, 
                chunck.to_json(orient='records'), ex=ttl, nx=nx
            )
            
            if not resp:
                raise redis.ResponseError
        
        return True #All returned values are Truthy
        

    @property
    def db(self):
        return self.data.get(Connection.DB_KEY)

    @property
    def name(self):
        return self.data.get(Connection.NAME_KEY) or self.data.get(Connection.HOST_KEY)

    def __str__(self):
        return self.name
            
class MySqlConnection(Connection):
    def __init__(self, host, user, passwd=None, db=None, ssl_key=None, ssl_cert=None, charset='utf8', use_unicode=True, name=None):
        self.data = dict(
            host=host,
            user=user,
            passwd=passwd,
            db=db,
            ssl=dict(key=ssl_key, cert=ssl_cert),
            name=name,
            charset=charset,
            use_unicode=use_unicode,
            cursorclass=DictCursor
        )

    def query(self, query: str):
        try:
            self.__connect()
            
            cursor = self.instance.cursor()
            
            cursor.execute(query)

            records = cursor.fetchall()

            cursor.close()
        
            records = DataFrame(records)

        except MySQLError as e:
            raise e
        
        finally:
            self.__close()        

        return records

    def __connect(self):
        try:
            self.instance = connect(**{k: v for k, v in self.data.items() if v and k != Connection.NAME_KEY})

        except OperationalError:
            raise MySQLError(
                f'Connection to {self.data.get(Connection.NAME_KEY) if Connection.NAME_KEY in self.data else self.data.get(Connection.HOST_KEY)} Failed'
            )
      
    def __close(self):
        try:
            self.instance.close() 
            
        except AttributeError:
            pass
    
    @property
    def db(self):
        return self.data.get(Connection.DB_KEY)

    @property
    def name(self):
        return self.data.get(Connection.NAME_KEY) or self.data.get(Connection.HOST_KEY)

    def __str__(self):
        return self.name

def connections(conns: Dict[str, Connection] = {}):
    ''' 
        Dict of pre existing Connection Objects (name: connection)
        Setup new connections, returns all available
    '''
    try:
        connections.__CONNECTIONS.update(conns)

    except AttributeError:
        connections.__CONNECTIONS = {**conns}

    if not connections.__CONNECTIONS:
        return {None: None}

    return connections.__CONNECTIONS

def cache_connection(con: CacheConnection = None):
    ''' 
        Sets a CacheConnection as default Cache
    '''
    try:
        assert(cache_connection.__CACHE_CONNECTION)

    except (AssertionError, AttributeError):
        cache_connection.__CACHE_CONNECTION = None

    if isinstance(con, CacheConnection):
        cache_connection.__CACHE_CONNECTION = con
    
    return cache_connection.__CACHE_CONNECTION

def __get_known_connection(connection: Union[Connection, str]):
    # If no connection is provided, grab first available
    if not connection:
        connection = list(connections().keys())[0]

    # Provided connection is not a Connection, is it a key?
    if not isinstance(connection, Connection):
        connection = connections().get(str(connection), connection)
    
    # No connection could be found
    if not isinstance(connection, Connection):
        raise KeyError(f'Unknown Connection', connection)

    return connection

        