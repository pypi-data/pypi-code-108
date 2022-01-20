# Redis driver
# please install python-redis
#
import time
import asyncio
from functools import wraps
from datetime import timedelta
from uuid import uuid4
from typing import Union
from jcramda import loc


__clients = {}


def new_client(uri: str, tag: str = None):
    if tag is None:
        tag = uuid4()
    if uri.startswith('cluster'):
        from rediscluster import RedisCluster
        seeds = [{'host': ss[0], 'port': ss[1]}
                 for entry in uri.lstrip('cluster://').split(',') if (ss := entry.strip().split(':'))]
        __clients[tag] = RedisCluster(
            startup_nodes=seeds, decode_responses=True)
    else:
        from pyredis import get_by_url
        __clients[tag] = get_by_url(uri)


def connect(tag: Union[str, int] = 0):
    pool = loc(tag, __clients)
    if pool:
        return pool
    raise RuntimeWarning(f'Not found redis client with name: {tag}')


def load(conf: dict):
    if conf and len(conf) > 0:
        for key in conf:
            new_client(conf[key], key)
            # print(f'redis: {key} connected')


conn = connect


class Lock:
    def __init__(self, tag, lock_flg):
        self._client = connect(tag)
        self._flg = lock_flg
        self._owner = False

    async def acquire(self, blocking=True, timeout=None):
        if not blocking and timeout is not None:
            raise ValueError("can't specify timeout for non-blocking acquire")
        start_time = int(time.time())
        while self._client.exists(self._flg):
            if not blocking:
                break
            await asyncio.sleep(0.5)
            curr_time = int(time.time())
            if isinstance(timeout, int) and curr_time - start_time > timeout:
                return False
        r = self._client.setnx(self._flg, int(time.time()))
        if r:
            self._owner = True
            return True
        return False

    def release(self):
        if self._owner:
            self._client.delete(self._flg)
            self._owner = False

    @property
    def locked(self):
        return self._owner


class IntervalLimitError(RuntimeError):
    pass


def interval_lock(flg, name, timeout=timedelta(seconds=3)):
    def limit_ann(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            client = connect(flg)
            time_limit = int(timeout.total_seconds())
            if client.exists(name):
                raise IntervalLimitError(
                    f'time interval limit in {time_limit}s')
            client.setnx(name, time.time())
            client.expire(name, time_limit)
            return fn(*args, **kwargs)
        return wrapped
    return limit_ann
