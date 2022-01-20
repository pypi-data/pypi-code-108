#
# 缓存实用工具
# @author Jochen.He
#
import asyncio
import base64
import logging
import warnings
import os
import pickle
import shutil
from _contextvars import copy_context
from datetime import timedelta
from functools import wraps, partial
from pathlib import Path
from typing import Union, Callable
from uuid import uuid4

from jcramda import (
    _, compose, join, replace, identity, hexdigest, pipe,
)
from jcramda.core.operator import default_to
from joblib import memory, dump

from .defines import CACHE_DEFAULT_DIR, Writable, DEFAULT_CACHE_TIME
from .core import async_run
from .core import to_json


_obj_encode: Callable = compose(
    base64.encodebytes,
    pickle.dumps
)

_obj_decode: Callable = compose(
    pickle.loads,
    base64.decodebytes
)

__all__ = [
    'mem_cache',
    'redis_cache',
    'persistence',
    'clear_mem',
]


def mem_cache(cache_dir: str = CACHE_DEFAULT_DIR):
    """

    Parameters
    ----------
    cache_dir: a cache temp dir path

    Returns
    -------
    a wrapper function that be cached result
    """
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)
    mem = memory.Memory(cache_dir, verbose=0)
    return mem.cache


def clear_mem(path: str = '', cache_dir: str = CACHE_DEFAULT_DIR):
    if '.' in path and '/' not in path:
        path = path.replace('.', os.path.sep)
    location = os.path.join(cache_dir, 'joblib', path)
    shutil.rmtree(location, ignore_errors=True)
    # warnings.warn(f'delete {location}')


try:
    from .drivers import redis
    def redis_cache(expires=DEFAULT_CACHE_TIME, prefix=None, redis_connector=None, result_assert=None):
        """
        cache function result in redis.
        result cache will be override by same process call

        Notes
        ----------
        this function is not thead safe
        ** function result must is a type can be json.dumps and json.loads **

        Parameters
        ----------
        prefix: cache key prefix, default is "fc"
        expires: Union[int, timedelta],
            seconds
        redis_connector: function,
            void -> redis.Client | redis.Pool
        result_assert: typing.Callable[[], bool]
            if this function is given, then use it check cache result, if return false then update cache

        """

        def decorator(f):
            f_name = f.__module__ + '.' + f.__name__
            c_key = join(':', [prefix, 'fc', f_name, '#pid'])
            key_gen = compose(
                replace('#pid', _, c_key),
                default_to(os.getpid()),
                hexdigest('md5'),
                to_json
            )

            @wraps(f)
            def redis_cache_f(*args, update_cache: bool = False, **kwargs):
                client = redis_connector() if redis_connector else redis.connect()
                cache_key = key_gen({'args': args, 'kwargs': kwargs})

                if not update_cache and client.exists(cache_key):
                    try:
                        r = _obj_decode(client.get(cache_key))
                        if not callable(result_assert) or result_assert(r):
                            return r
                    except (TypeError, ValueError, pickle.UnpicklingError) as err:
                        logging.error(err)

                r = f(*args, **kwargs)
                while asyncio.iscoroutine(r):
                    r = asyncio.run(r)
                if r is not None:
                    client.set(cache_key, _obj_encode(r))
                    client.expire(cache_key, int(expires.total_seconds()) if isinstance(timedelta, expires) else expires)
                return r

            if asyncio.iscoroutinefunction(f):
                async def async_cache_f(*args, update_cache: bool = False, **kwargs):
                    return await async_run(redis_cache_f, with_context=True, *args,
                                        update_cache=update_cache, **kwargs)
                return async_cache_f

            return redis_cache_f

        return decorator
except ModuleNotFoundError:
    warnings.warn('pyredis is not installed, [redis_cache] is not cached!!')
    def redis_cache(expires=DEFAULT_CACHE_TIME, prefix=None, redis_connector=None, result_assert=None):
        def decorator(f):
            return f
        return decorator


def _save_data(fs: Writable, tmp_file: Path, data):
    try:
        dump(data, tmp_file)
        with tmp_file.open('rb') as ft:
            fs.write(ft)
    except FileExistsError:
        pass
    finally:
        tmp_file.unlink()
        fs.close()


def persistence(fs: Union[Writable, Callable[[], Writable]], f):
    """
    非阻塞式持久化指定方法的执行结果
    :param fs:
    :param f:
    :return:
    :python_version: >= 3.8
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        r = f(*args, **kwargs)
        if r is not None:
            save_opts = (identity(fs), Path(os.path.join(CACHE_DEFAULT_DIR, uuid4().hex)), r)
            asyncio.get_event_loop().run_in_executor(None, copy_context().run, partial(_save_data, *save_opts))
        return r

    return wrapper

