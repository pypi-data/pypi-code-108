import re
from typing import Union, Dict
from threading import Thread
from functools import wraps
import json

import MySQLdb as mysql
from MySQLdb.cursors import DictCursor
from MySQLdb._exceptions import OperationalError, ProgrammingError
import pandas as pd
import numpy as np

from banner.utils.const import (
    FIRST_NEWARE_DATA_TABLE, SECOND_NEWARE_DATA_TABLE, FIRST_NEWARE_AUX_TABLE, SECOND_NEWARE_AUX_TABLE, 
    NW_TEMP, CACHE_CONNECTION_KWARG, TTL_KWARG, NW_DATA_SIGNIFICANT_COLUMNS, NW_AUX_SIGNIFICANT_COLUMNS
)
from banner.utils.neware import calculate_neware_columns, calculate_dqdv, merge_cache, query_cache
from banner.utils.web2py import parse_w2p_to_mysql_query, COLUMN_TO_LABEL, LABEL_TO_COLUMN
from banner.connection import Connection, CacheConnection, __get_known_connection, cache_connection as cache, connections

# Handles query caching
def __cache_query(func):
    @wraps(func)
    def inner(*args, **kwargs):
        cache_connection = kwargs.get(CACHE_CONNECTION_KWARG, None) or cache()
        ttl = kwargs.get(TTL_KWARG, None)
        
        key = f'{inner.__name__}-{"_".join(str(arg) for arg in args).strip()}'

        if kwargs:
            _kwargs = "_".join(
                [f'{key}:{str(value).strip()}' for key, value in kwargs.items() if type(value) not in (pd.DataFrame, )]
            )
            key += f'-{_kwargs}'
        
        response = __cached_query(key, cache_connection)
        
        if not response.empty:
            return response
        
        response = func(*args, **kwargs)
        
        # Cache TODO USE CELERY
        Thread(
            target=__cache_query, 
            kwargs=dict(
                query=key,
                value=response,
                cache_connection=cache_connection,
                ttl=ttl
            )
        ).start()

        return response

    return inner

@__cache_query
def simple_query(query: str, connection=None, cache_connection=None, ttl=None, w2p_parse=True) -> pd.DataFrame:
    '''
        Queries a given Connection/str of a known connection (or first known) return result as DataFrame
        Cache if cache_connection or first known with ttl or default ttl for cache_connection
        Raises KeyError and OperationalError
    '''
    return __query(
        query, 
        connection=connection, 
        cache_connection=cache_connection, 
        ttl=ttl, 
        w2p_parse=w2p_parse
    )

@__cache_query
def neware_query(
    device: int, unit: int, channel: int, test: int, connection: Union[Connection, str] = None, 
    cache_connection=None, ttl=None, raw=False, dqdv=False, condition: str = '1', 
    temperature: bool = True, cache_data: pd.DataFrame = pd.DataFrame()
) -> pd.DataFrame:
    '''
        Queries a given Connection(ip)/str of a known connection (or first known) return result as DataFrame
        Cache if cache_connection or first known with ttl or default ttl for cache_connection
        If dqdv -> neware.calc_dq_dv
        Raises KeyError and OperationalError
    '''
    connection = __get_known_connection(connection)
    
    # Look for the tables
    try:
        neware_data = __query(
            f'SELECT * FROM h_test WHERE dev_uid = {device} AND unit_id = {unit} AND chl_id = {channel} AND test_id = {test}',
            connection=connection
        ).iloc[0] # A single row is returned since we looked by primary key

    except IndexError:
        raise TypeError(f'{connection.name} has No data for device:{device}, unit:{unit}, channel:{channel}') 

    # Target Columns
    __data_columns = __aux_columns = '*'

    # Select only important columns
    if not raw:
        __data_columns, __aux_columns = ', '.join(NW_DATA_SIGNIFICANT_COLUMNS), ', '.join(NW_AUX_SIGNIFICANT_COLUMNS)
    
    # Parse W2P query
    condition = parse_w2p_to_mysql_query(condition)
    
    # Try to adjust query!
    if isinstance(cache_data, pd.DataFrame) and not cache_data.empty and condition != '1':
        condition = query_cache(
            cache_data, condition
        )
    
    # Main tables into a single df
    data = pd.concat([
        __query(
            f'SELECT {__data_columns} FROM {neware_data[FIRST_NEWARE_DATA_TABLE]} WHERE unit_id = {unit} AND chl_id = {channel} AND test_id = {test} AND {condition}', 
            connection=connection
        ) if neware_data[FIRST_NEWARE_DATA_TABLE] else pd.DataFrame(),
        __query(
            f'SELECT {__data_columns} FROM {neware_data[SECOND_NEWARE_DATA_TABLE]} WHERE unit_id = {unit} AND chl_id = {channel} AND test_id = {test} AND {condition}', 
            connection=connection
        ) if neware_data[SECOND_NEWARE_DATA_TABLE] else pd.DataFrame()
    ], ignore_index=True)
    
    # Aux tables into a single df
    aux_data = pd.DataFrame()
    
    if temperature:
        aux_data = pd.concat([
            __query(
                f'SELECT {__aux_columns} FROM {neware_data[FIRST_NEWARE_AUX_TABLE]} WHERE unit_id = {unit} AND chl_id = {channel} AND test_id = {test} AND {condition}', 
                connection=connection
            ) if neware_data[FIRST_NEWARE_AUX_TABLE] else pd.DataFrame(),
            __query(
                f'SELECT {__aux_columns} FROM {neware_data[SECOND_NEWARE_AUX_TABLE]} WHERE unit_id = {unit} AND chl_id = {channel} AND test_id = {test} AND {condition}', 
                connection=connection
            ) if neware_data[SECOND_NEWARE_AUX_TABLE] else pd.DataFrame()
        ], ignore_index=True)
        
        
    __data_columns, __aux_columns = list(data.columns), list(aux_data.columns) #Response columns
    
    try: # RAW
        __data_columns.remove(NW_TEMP) # NW_TEMP is still Redundant

        __aux_columns = set(np.setdiff1d(__aux_columns, __data_columns)) # data_flag, auxchl_id, test_tmp
        
    except ValueError:
        pass
    
    # Concat
    data = pd.concat(
        [
            data[__data_columns],
            aux_data[__aux_columns]
        ], 
        axis = 1
    )
    
    if not raw:
        # Calculate neware columns
        try:
            data = calculate_neware_columns(data, temperature=not aux_data.empty, cache_df=cache_data)
            
        except KeyError:
            pass
        
        # Merge provided cache data
        try:
            data = merge_cache(data, cache_data)

        except TypeError:
            pass
    
    # Calculate dqdv
    if dqdv:
        try:
            data['dqdv'] = calculate_dqdv(data, raw=raw)
        
        except KeyError:
            pass

    return data

@__cache_query
def neware_query_by_test(
    table: str, cell: int, test: int, connection: Union[Connection, str] = None, cache_connection=None, 
    ttl=None, raw=False, dqdv=False, condition: str = '1', temperature: bool = True
) -> pd.DataFrame:
    '''
        Queries a given Connection(ip)/str of a known connection (or first known) return result as DataFrame
        Queries the given connection for (device: int, unit: int, channel: int, test: int, connection: str) to feed neware_query
        ** Tries to merge neware_cache_query **
        Cache if cache_connection or first known with ttl or default ttl for cache_connection
        If dqdv -> neware.calc_dq_dv
        Raises OperationalError and KeyError(Failed to find a connection for given key) 
    '''
    connection = __get_known_connection(connection)
    
    # Look for the tables
    try:
        neware_keys = __query(
            f'SELECT device, unit, channel, test_id, ip FROM {table}_test WHERE {table}_id = {cell} AND test_id = {test}',
            connection=connection
        ).iloc[0] # A single row is returned since we looked by primary key
        
    except IndexError:
        raise TypeError(f'{connection.name} has No data for table:{table}, cell:{cell}, test:{test}') 
    
    try:
        cache_data = neware_cache_query(
            neware_keys['ip'], neware_keys['device'], neware_keys['unit'], neware_keys['channel'], neware_keys['test_id'],
            connection=connection
        )
        
    except (IndexError, OperationalError, ProgrammingError):
        cache_data = pd.DataFrame()
    
    data = neware_query(
        neware_keys['device'], neware_keys['unit'], neware_keys['channel'], neware_keys['test_id'],
        connection=neware_keys['ip'],
        raw=raw, 
        dqdv=dqdv, 
        condition=condition, 
        temperature=temperature, 
        cache_data=cache_data
    )
    
    return data

@__cache_query
def neware_cache_query(ip: int, device: int, unit: int, channel: int, test: int, connection: Union[Connection, str] = None, cache_connection=None, ttl=None) -> pd.DataFrame:
    '''
        Queries a given Connection(ip)/str of a known connection (or first known) return result as DataFrame
        Cache if cache_connection or first known with ttl or default ttl for cache_connection
        Raises KeyError and OperationalError
    '''
    connection = __get_known_connection(connection)
    
    for cache_table in ('neware_cache', 'neware_pulses_cache', 'neware_cache_anode'):
        __data = __query(
            f'SELECT * FROM {cache_table} WHERE ip = {ip} AND dev_uid = {device} AND unit_id = {unit} AND chl_id = {channel} AND test_id = {test}',
            connection=connection
        )
        
        if isinstance(__data, pd.DataFrame) and not __data.empty:
            return __data
    
    return pd.DataFrame()

def describe_table(table, connection: Union[Connection, str] = None) -> pd.DataFrame:
    '''
        Describes a table in connection
        Raises OperationalError and KeyError(Failed to find a connection for given key) 
    '''
    connection = __get_known_connection(connection)
    
    data = __query(f'DESCRIBE {table}', connection)

    data['Label'] = data['Field'].map(COLUMN_TO_LABEL)

    return data

def describe(connection: Union[Connection, str] = None) -> pd.DataFrame:
    '''
        Describe Table names in connection
        Raises OperationalError and KeyError(Failed to find a connection for given key) 
    '''
    connection = __get_known_connection(connection)
    
    return __query(
        f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{connection.db}'",
        connection
    )

@__cache_query
def table_query(table: str, columns: Union[list, str] = '*', condition: str = '1', connection=None, cache_connection=None, ttl=None, raw=False) -> pd.DataFrame:
    '''
        Queries a given connection for 'SELECT {columns} FROM {table} WHERE {condition}'
        Accepts both column values and labels
        raw=True - column names as in db
        Queries a given Connection(ip)/str of a known connection (or first known) return result as DataFrame
        Cache if cache_connection or first known with ttl or default ttl for cache_connection
        Raises OperationalError and KeyError(Failed to find a connection for given key) 
    '''
    if isinstance(columns, str):
        columns = list(
            map(
                str.strip,
                filter(
                    None, 
                    re.split(
                        ',|, | ,',
                        columns
                    )
                )
            )
        )
    
    _columns = [LABEL_TO_COLUMN.get(column, column) for column in columns]
    
    data = __query(
        f"SELECT {', '.join(_columns)} FROM {table} WHERE {condition}",
        connection=connection,
        cache_connection=cache_connection,
        ttl=ttl
    )
    
    if not raw:
        try:
            #Columns as requested!
            data.columns = columns 

        except ValueError:
            # Case columns contain *
            data.columns = [COLUMN_TO_LABEL.get(column, column) for column in data.columns]
            pass
        

    return data

def __cache_query(query, value, cache_connection: CacheConnection, ttl=None):
    try:
        assert(isinstance(cache_connection, CacheConnection))
        
        return cache_connection.cache(
            query, 
            value, 
            ttl=ttl, 
            nx=True
        )

    except Exception as e:
        print(f'Failed Caching {query} into {cache_connection}', e)
    
def __cached_query(query, cache_connection: CacheConnection):
    try:
        assert(isinstance(cache_connection, CacheConnection))
        
        cached_keys = cache_connection.query(query, keys=True)
        
        assert(cached_keys)
        
        cached = cache_connection.query(
            sorted(cached_keys), resp_type=pd.DataFrame
        )
        
        assert(isinstance(cached, pd.DataFrame))

        return cached

    except AssertionError:
        return pd.DataFrame()

def __query(query: str, connection=None, cache_connection=None, ttl=None, w2p_parse=True, promise=False) -> pd.DataFrame:
    if not isinstance(query, str):
        return pd.DataFrame()

    connection = __get_known_connection(connection)
    
    if w2p_parse:
        query = parse_w2p_to_mysql_query(query)

    return connection.query(query)

    




