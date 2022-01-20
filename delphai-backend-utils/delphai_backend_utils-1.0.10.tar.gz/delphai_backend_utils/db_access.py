"""
Connection to the database
"""

import pymongo
import socket

from delphai_backend_utils.config import get_config
from multiprocessing import current_process


DB_CONN_BY_PID_AND_DBNAME = {}  # (process id, db_name) -> DB_CONN

default_database_name = get_config('db')['name']

MAX_POOL_SIZE = 8
MAX_IDLE_TIMEOUT = 60

mongo_parameters = dict(
    host=get_config('db')['connection_string'],
    appname=socket.gethostname(),
    connect=False,
    maxPoolSize=MAX_POOL_SIZE,
    maxIdleTimeMS=MAX_IDLE_TIMEOUT * 1000,
)


def get_own_db_connection(db_name: str = None) -> pymongo.database.Database:
    """
    Creates neq connection to database.
    :param db_name: use this parameter only if DB name differs from `default_database_name`
    :return: database connection
    """
    pid = current_process().pid
    # db_config = get_config('db')
    req_db_name = default_database_name if db_name is None else db_name
    if (pid, req_db_name) in DB_CONN_BY_PID_AND_DBNAME:
        return DB_CONN_BY_PID_AND_DBNAME[(pid, req_db_name)]
    client = pymongo.MongoClient(**mongo_parameters)

    res = client[req_db_name]
    DB_CONN_BY_PID_AND_DBNAME[(pid, req_db_name)] = res
    return res


def chunks(iterable, chunk_size=100):
    """
    Splits iterable stream by chunks of size chunk_size. Very usefull when we need to split read
    or write operations to butches of reasonable size.
    :param iterable: something interable
    :param chunk_size: desirable size if chunks to be produced
    :yield: lists of elements extracted from iterable
    """
    curr_chunk = []
    for val in iterable:
        if len(curr_chunk) >= chunk_size:
            yield curr_chunk
            curr_chunk = []
        curr_chunk.append(val)
    if curr_chunk:
        yield curr_chunk
