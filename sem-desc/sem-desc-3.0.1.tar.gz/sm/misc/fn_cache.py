import functools
import os
from pathlib import Path

import orjson
from typing import Callable, Tuple, Any, Dict, Optional, Union

from sm.misc.big_dict.rocksdb import PickleRocksDBStore
from sm.misc.big_dict.redis import PickleRedisStore

CACHE = {}


def cache_func(
    dbfile: str = "/tmp/cache_func.db",
    namespace: str = "",
    get_key: Callable[[str, str, Tuple[Any, ...], Dict[str, Any]], str] = None,
    instance_method: bool = False,
    cache: Optional[dict] = None,
    read_only: bool = False,
):
    """Cache a function

    Args:
        dbfile: can be redis (e.g., "redis://localhost:6379") or rocksdb (local file)
        namespace:
        get_key:
        instance_method:
        cache:

    Returns:

    """
    global CACHE
    if cache is None:
        cache = CACHE

    if dbfile not in cache:
        if dbfile.startswith("redis://"):
            db = PickleRedisStore(dbfile)
        else:
            db = PickleRocksDBStore(dbfile, read_only=read_only)
        cache[dbfile] = db
    db = cache[dbfile]

    if get_key is None:
        get_key = default_get_key

    if instance_method:

        def wrapper_instance_fn(func):
            fn_name = func.__name__

            @functools.wraps(func)
            def fn(*args, **kwargs):
                key = get_key(namespace, fn_name, args[1:], kwargs)
                if key not in db:
                    db[key] = func(*args, **kwargs)
                return db[key]

            return fn

        return wrapper_instance_fn

    def wrapper_fn(func):
        fn_name = func.__name__

        @functools.wraps(func)
        def fn(*args, **kwargs):
            key = get_key(namespace, fn_name, args, kwargs)
            if key not in db:
                db[key] = func(*args, **kwargs)
            return db[key]

        return fn

    return wrapper_fn


def default_get_key(namespace, func_name, args, kwargs):
    return orjson.dumps(
        {"ns": namespace, "fn": func_name, "a": args, "kw": kwargs}
    ).decode()


def skip_if_file_exist(filepath: Union[Path, str]):
    """Skip running a function if a file exist"""

    def wrapper_fn(func):
        @functools.wraps(func)
        def fn(*args, **kwargs):
            if os.path.exists(filepath):
                return
            func(*args, **kwargs)

        return fn

    return wrapper_fn


def exec_or_skip_if_file_exist(filepath: Union[Path, str], skip: bool = False):
    """Skip running a function if a file exist. Otherwise, run it"""

    def wrapper_fn(func):
        @functools.wraps(func)
        def fn():
            if os.path.exists(filepath):
                return
            func()

        if not skip:
            fn()

    return wrapper_fn
