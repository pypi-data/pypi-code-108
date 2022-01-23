#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Author:        digua
Created at:    2021-10-30 17:03:31
Last modified: 2021-11-01 15:26:05
'''

import asyncio
import collections
import datetime
import decimal
import inspect
import json
import math
import os
import queue
import socket
import sys
import threading
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import partial, reduce
from pathlib import Path
from socket import inet_aton, inet_ntoa
from struct import pack, unpack

import requests
import yaml
from orderedset import OrderedSet
from pymongo.cursor import Cursor
from rich.console import Console
from rich.table import Table
from tqdm import tqdm


def _include_yaml(loader, node):
    root = Path(loader.name).parent
    if isinstance(node, yaml.SequenceNode):
        return [yaml.load(open(root / x.value), Loader=yaml.FullLoader) for x in node.value]
    else:
        return yaml.load(open(root / node.value), Loader=yaml.FullLoader)


def yaml_load(stream, **kwargs):
    loader = yaml.FullLoader(stream)
    try:
        return DictWrapper(loader.get_single_data())
    finally:
        loader.dispose()


def yaml_dump(data, stream=None, default_flow_style=False, allow_unicode=True, **kwargs):
    return yaml.dump_all([DictUnwrapper(data)], stream,
                         Dumper=yaml.Dumper,
                         default_flow_style=default_flow_style,
                         allow_unicode=allow_unicode,
                         **kwargs)


yaml.add_constructor('!include', _include_yaml)
yaml.load = yaml_load
yaml.dump = yaml_dump


class tqdm(tqdm):

    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], Cursor):
            kwargs.setdefault('total', args[0].count())
        kwargs.setdefault('disable', not sys.stdout.isatty())
        super().__init__(*args, **kwargs)

    def update(self, n=None, total=None, incr=None):
        if total is not None:
            self.total = total
        if n is not None:
            super().update(max(0, n - self.n))
        elif incr is not None:
            super().update(incr)


class Queue(queue.Queue):

    def _init(self, maxsize):
        self.queue = OrderedSet()

    def _put(self, item):
        self.queue.add(item)

    def _get(self):
        return self.queue.pop(last=False)

    def __contains__(self, item):
        with self.mutex:
            return item in self.queue


class AioQueue(asyncio.Queue):

    def _init(self, maxsize):
        self._queue = OrderedSet()

    def _put(self, item):
        self._queue.add(item)

    def _get(self):
        return self._queue.pop(last=False)

    def __contains__(self, item):
        return item in self.queue


class JSONEncoder(json.encoder.JSONEncoder):
    '''针对某些不能序列化的类型如datetime，使用json.dumps(data, cls=JSONEncoder)
    '''

    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, Path):
            return str(obj)
        elif hasattr(obj, 'tolist') and callable(obj.tolist):
            return obj.tolist()
        try:
            return super().default(obj)
        except Exception:
            return str(obj)


class Singleton(type):
    _instance_lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with Singleton._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class Storage:

    def __init__(self):
        self.mutex = threading.Lock()
        self.data = {}

    def get(self, key):
        item = self.data.get(key)
        if item is not None:
            value, ttl = item
            if ttl is None:
                return value
            if ttl >= int(time.time()):
                return value

    def set(self, key, value, ttl=None):
        self.mutex.acquire()
        ttl = int(time.time()) + ttl if ttl is not None else None
        self.data[key] = value, ttl
        self.mutex.release()

    def delete(self, key):
        self.mutex.acquire()
        self.data.pop(key, None)
        self.mutex.release()

    def ttl(self, key, ttl):
        self.mutex.acquire()
        item = self.data[key]
        if item is not None:
            self.data[key] = item[0], int(time.time()) + ttl
        self.mutex.release()


class Dict(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in self.items():
            self.__setitem__(key, value)

    def dict(self):
        return DictUnwrapper(self)

    def __delattr__(self, key):
        try:
            del self[key]
        except Exception:
            pass

    def __getattr__(self, key):
        try:
            return self[key]
        except Exception:
            pass

    def __setitem__(self, key, value):
        super().__setitem__(key, DictWrapper(value))

    __setattr__ = __setitem__

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __or__(self, other):
        if not isinstance(other, (Dict, dict)):
            return NotImplemented
        new = Dict(self)
        new.update(other)
        return new

    def __ror__(self, other):
        if not isinstance(other, (Dict, dict)):
            return NotImplemented
        new = Dict(other)
        new.update(self)
        return new

    def __ior__(self, other):
        self.update(other)
        return self

    # def __repr__(self):
    #     return 'Dict<%s>' % dict.__repr__(self)

    # def __str__(self):
    #     return json.dumps(self, cls=JSONEncoder, ensure_ascii=False)


class DefaultDict(collections.defaultdict):

    def __delattr__(self, key):
        try:
            del self[key]
            return True
        except Exception:
            return False

    def __getattr__(self, key):
        return self[key]


def DictWrapper(*args, **kwargs):
    if args and len(args) == 1:
        if isinstance(args[0], collections.defaultdict):
            return DefaultDict(args[0].default_factory, args[0])
        elif isinstance(args[0], dict):
            return Dict(args[0])
        elif isinstance(args[0], (tuple, list)):
            return type(args[0])(map(DictWrapper, args[0]))
        else:
            return args[0]
    elif args:
        return type(args)(map(DictWrapper, args))
    else:
        return Dict(**kwargs)


def DictUnwrapper(doc):
    if isinstance(doc, DefaultDict):
        return collections.defaultdict(doc.default_factory, doc)
    if isinstance(doc, Dict):
        return dict(map(lambda x: (x[0], DictUnwrapper(x[1])), doc.items()))
    if isinstance(doc, (tuple, list)):
        return type(doc)(map(DictUnwrapper, doc))
    return doc


async def awaitable(ret):
    return await ret if inspect.isawaitable(ret) else ret


def multi_apply(func, *args, **kwargs):
    workers = kwargs.pop('workers', os.cpu_workers())
    pool = kwargs.pop('pool', False)
    pfunc = partial(func, **kwargs) if kwargs else func
    size = math.ceil(len(args[0]) / workers)
    pargs = [[arg[i * size:(i + 1) * size] for i in range(workers)] for arg in args]
    if pool:
        with ThreadPoolExecutor(workers) as executor:
            results = executor.map(pfunc, *pargs)
    else:
        with ProcessPoolExecutor(workers) as executor:
            results = executor.map(pfunc, *pargs)
    results = list(results)
    if len(results) > 0:
        if isinstance(results[0], list):
            return reduce(lambda x, y: x + y, results)
        elif results[0] is not None:
            return results


def floor(number, ndigits=0):
    '''当ndigits大于等于number的小数点位数时，直接返回
    '''
    if ndigits == 0:
        return math.floor(number)
    else:
        if float(f'{number:.{ndigits}f}') == number:
            return number
        else:
            return float(decimal.Decimal(number).quantize(decimal.Decimal(f'{0:.{ndigits}f}'), rounding=decimal.ROUND_DOWN))


def ceil(number, ndigits=0):
    if ndigits == 0:
        return math.ceil(number)
    else:
        if float(f'{number:.{ndigits}f}') == number:
            return number
        else:
            return float(decimal.Decimal(number).quantize(decimal.Decimal(f'{0:.{ndigits}f}'), rounding=decimal.ROUND_UP))


def to_str(*args):
    result = tuple(map(lambda x: x.decode() if isinstance(x, bytes) else x if isinstance(x, str) else str(x), args))
    return result[0] if len(args) == 1 else result


def to_bytes(*args):
    result = tuple(map(lambda x: x.encode() if isinstance(x, str) else x if isinstance(x, bytes) else str(x).encode(), args))
    return result[0] if len(args) == 1 else result


def get_ip(local=True):
    if local:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]
        except Exception:
            return '127.0.0.1'
        finally:
            s.close()
    else:
        try:
            resp = requests.get('http://api.imgdb.cn/ip', timeout=1)
            return resp.text.split()[-1]
        except Exception:
            return get_ip()


def connect(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        return True
    except Exception:
        return False
    finally:
        s.close()


def ip2int(ip):
    return unpack("!I", inet_aton(ip))[0]


def int2ip(i):
    return inet_ntoa(pack("!I", i))


def str2int(str_time):
    return int(time.mktime(time.strptime(str_time, "%Y-%m-%d %H:%M:%S")))


def int2str(int_time):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int_time))


def pprint(docs, header=None, auto=False):
    console = Console()
    if auto:
        stack = inspect.stack()
        if not [x for x in stack if x.function == 'Fire']:
            return

    if not docs:
        return console.print(docs)

    if isinstance(docs, (list, tuple)):
        table = Table(show_header=True, header_style="bold magenta")
        if header is not None:
            for key in header:
                table.add_column(key)
        if isinstance(docs[0], dict):
            if header is None:
                header = sorted(set(reduce(lambda x, y: x + y, [list(x.keys()) for x in docs])))
                for key in header:
                    table.add_column(key)
            for doc in docs:
                table.add_row(*[str(doc.get(x, '')) for x in header])
            console.print(table)
        elif isinstance(docs[0], (list, tuple)):
            for doc in docs:
                table.add_row(*[str(x) for x in doc])
            console.print(table)
        else:
            console.print(docs)
    else:
        console.print(docs)
