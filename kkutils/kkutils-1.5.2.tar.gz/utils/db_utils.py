#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: zhangkai
Email: zhangkai@cmcm.com
Last modified: 2018-01-05 11:24:17
'''
import asyncio
import os
import re
from urllib.parse import parse_qs, quote_plus, unquote_plus

import aiomysql
import aredis
import pymongo
import pymysql
import redis
from dbutils.pooled_db import PooledDB
from motor import core
from motor.docstrings import get_database_doc
from motor.frameworks import asyncio as asyncio_framework
from motor.metaprogramming import (AsyncCommand, AsyncRead, DelegateMethod,
                                   coroutine_annotation,
                                   create_class_with_framework,
                                   unwrap_args_session, unwrap_kwargs_session)

from .base_utils import Dict

__all__ = ['Mongo', 'MongoClient', 'Redis', 'AioRedis', 'Motor', 'MotorClient', 'Mysql', 'AioMysql', 'parse_uri']


def parse_uri(uri):
    pattern = re.compile(r'''
        (?P<schema>[\w\+]+)://
        (?:
            (?P<user>[^:/]*)
            (?::(?P<password>[^/]*))?
        @)?
        (?:
            (?P<host>[^/:]*)
            (?::(?P<port>[^/]*))?
        )?
        (?:/(?P<db>\w*))?
        (?:\?(?P<extra>.*))?
        ''', re.X)

    m = pattern.match(uri)
    assert m is not None, 'Could not parse rfc1738 URL'
    kwargs = Dict()
    for k, v in m.groupdict().items():
        if v is None:
            continue
        if k == 'extra':
            ret = parse_qs(v)
            ret = {_k: _v[0] if len(_v) == 1 else _v for _k, _v in ret.items()}
            kwargs.update(ret)
        elif k == 'port':
            kwargs[k] = int(v)
        else:
            kwargs[k] = unquote_plus(v)

    if kwargs.schema == 'redis' and kwargs.db:
        kwargs.db = int(kwargs.db)
    return kwargs


class Collection(pymongo.collection.Collection):

    def find(self, *args, **kwargs):
        kwargs.update({'no_cursor_timeout': True})
        return pymongo.cursor.Cursor(self, *args, **kwargs)

    @property
    def seq_id(self):
        ret = self.database.ids.find_one_and_update({'_id': self.name},
                                                    {'$inc': {'seq': 1}},
                                                    upsert=True,
                                                    projection={'seq': True, '_id': False},
                                                    return_document=True)
        return ret['seq']


class Database(pymongo.database.Database):

    def __getitem__(self, name):
        return Collection(self, name)


class MongoClient(pymongo.MongoClient):

    def __init__(self, **kwargs):
        env = 'MONGO_LOC' if kwargs.pop('loc', False) and os.environ.get('MONGO_LOC') else 'MONGO_URI'
        if any([key in kwargs for key in ['host', 'port', 'user', 'password']]):
            host = kwargs.pop('host', 'localhost')
            port = kwargs.pop('port', 27017)
            user = kwargs.pop('user', None)
            password = kwargs.pop('password', None)
            uri = f"mongodb://{quote_plus(user)}:{quote_plus(password)}@{host}:{port}" if user and password else f"mongodb://{host}:{port}"
        elif kwargs.get('uri'):
            uri = kwargs.pop('uri')
        elif os.environ.get(env):
            uri = os.environ[env]
        else:
            host = os.environ.get('MONGO_HOST', 'localhost')
            port = os.environ.get('MONGO_PORT', 27017)
            user = os.environ.get('MONGO_USER', None)
            password = os.environ.get('MONGO_PWD', None)
            uri = f"mongodb://{quote_plus(user)}:{quote_plus(password)}@{host}:{port}" if user and password else f"mongodb://{host}:{port}"

        if 'uri' in kwargs:
            kwargs.pop('uri')
        kwargs.setdefault('document_class', Dict)
        super(MongoClient, self).__init__(uri, **kwargs)

    def __getitem__(self, name):
        return Database(self, name)

    def __getattr__(self, name):
        return Database(self, name)


class Mongo(Database):

    def __init__(self, db='test', **kwargs):
        client = MongoClient(**kwargs)
        super(Mongo, self).__init__(client, db)


class AgnosticCursor(core.AgnosticCursor):
    count = AsyncRead()

    @coroutine_annotation
    def to_list(self, length=None):
        return super(core.AgnosticCursor, self).to_list(length)


class AgnosticCollection(core.AgnosticCollection):
    __delegate_class__ = Collection
    count = AsyncRead()

    def __init__(self, database, name, codec_options=None,
                 read_preference=None, write_concern=None, read_concern=None,
                 _delegate=None):
        db_class = create_class_with_framework(
            AgnosticDatabase, self._framework, self.__module__)

        if not isinstance(database, db_class):
            raise TypeError("First argument to MotorCollection must be "
                            "MotorDatabase, not %r" % database)

        delegate = _delegate or Collection(
            database.delegate, name, codec_options=codec_options,
            read_preference=read_preference, write_concern=write_concern,
            read_concern=read_concern)

        super(core.AgnosticBaseProperties, self).__init__(delegate)
        self.database = database

    def __getitem__(self, name):
        collection_class = create_class_with_framework(
            AgnosticCollection, self._framework, self.__module__)

        return collection_class(self.database, self.name + '.' + name,
                                _delegate=self.delegate[name])

    def find(self, *args, **kwargs):
        kwargs.update({'no_cursor_timeout': True})
        cursor = self.delegate.find(*unwrap_args_session(args),
                                    **unwrap_kwargs_session(kwargs))
        cursor_class = create_class_with_framework(
            AgnosticCursor, self._framework, self.__module__)

        return cursor_class(cursor, self)

    @property
    async def seq_id(self):
        ret = await self.database.ids.find_one_and_update({'_id': self.name},
                                                          {'$inc': {'seq': 1}},
                                                          upsert=True,
                                                          projection={'seq': True, '_id': False},
                                                          return_document=True)
        return ret['seq']


class AgnosticDatabase(core.AgnosticDatabase):
    __delegate_class__ = Database

    authenticate = AsyncCommand()
    logout = AsyncCommand()
    create_collection = AsyncCommand().wrap(Collection)
    get_collection = DelegateMethod().wrap(Collection)

    def __init__(self, client, name, **kwargs):
        self._client = client
        delegate = kwargs.get('_delegate') or Database(
            client.delegate, name, **kwargs)

        super(core.AgnosticBaseProperties, self).__init__(delegate)

    def __getitem__(self, name):
        collection_class = create_class_with_framework(
            AgnosticCollection, self._framework, self.__module__)

        return collection_class(self, name)


class AgnosticClient(core.AgnosticClient):
    __delegate_class__ = MongoClient
    get_database = DelegateMethod(doc=get_database_doc).wrap(Database)

    def __getitem__(self, name):
        db_class = create_class_with_framework(
            AgnosticDatabase, self._framework, self.__module__)
        return db_class(self, name)


def create_asyncio_class(cls):
    asyncio_framework.CLASS_PREFIX = ''
    return create_class_with_framework(cls, asyncio_framework, 'db_utils')


MotorClient = create_asyncio_class(AgnosticClient)
MotorDatabase = create_asyncio_class(AgnosticDatabase)
MotorCollection = create_asyncio_class(AgnosticCollection)


class Motor(MotorDatabase):

    def __init__(self, db='test', **kwargs):
        client = MotorClient(**kwargs)
        super(Motor, self).__init__(client, db)


class Redis(redis.StrictRedis):

    def __init__(self, **kwargs):
        if any([key in kwargs for key in ['host', 'port', 'password']]):
            host = kwargs.pop('host', 'localhost')
            port = kwargs.pop('port', 6379)
            password = kwargs.pop('password', None)
            db = kwargs.pop('db', 0)
            uri = f"redis://:{password}@{host}:{port}/{db}" if password else f"redis://{host}:{port}/{db}"
        elif kwargs.get('uri'):
            uri = kwargs.pop('uri')
        elif os.environ.get('REDIS_URI'):
            uri = os.environ['REDIS_URI']
        else:
            host = os.environ.get("REDIS_HOST", 'localhost')
            port = int(os.environ.get("REDIS_PORT", 6379))
            password = os.environ.get("REDIS_PWD", None)
            db = int(os.environ.get("REDIS_DB", 0))
            uri = f"redis://:{password}@{host}:{port}/{db}" if password else f"redis://{host}:{port}/{db}"

        if 'uri' in kwargs:
            kwargs.pop('uri')
        kwargs.setdefault('decode_responses', True)
        pool = redis.ConnectionPool.from_url(uri, **kwargs)
        super().__init__(connection_pool=pool)

    def clear(self, pattern='*'):
        if pattern == '*':
            self.flushdb()
        else:
            keys = [x for x in self.scan_iter(pattern)]
            if keys:
                self.delete(*keys)


class AioRedis(aredis.StrictRedis):

    def __init__(self, **kwargs):
        if any([key in kwargs for key in ['host', 'port', 'password']]):
            host = kwargs.pop('host', 'localhost')
            port = kwargs.pop('port', 6379)
            password = kwargs.pop('password', None)
            db = kwargs.pop('db', 0)
            uri = f"redis://:{password}@{host}:{port}/{db}" if password else f"redis://{host}:{port}/{db}"
        elif kwargs.get('uri'):
            uri = kwargs.pop('uri')
        elif os.environ.get('REDIS_URI'):
            uri = os.environ['REDIS_URI']
        else:
            host = os.environ.get("REDIS_HOST", 'localhost')
            port = int(os.environ.get("REDIS_PORT", 6379))
            password = os.environ.get("REDIS_PWD", None)
            db = int(os.environ.get("REDIS_DB", 0))
            uri = f"redis://:{password}@{host}:{port}/{db}" if password else f"redis://{host}:{port}/{db}"

        if 'uri' in kwargs:
            kwargs.pop('uri')
        kwargs.setdefault('decode_responses', True)
        pool = aredis.ConnectionPool.from_url(uri, **kwargs)
        super().__init__(connection_pool=pool)

    async def clear(self, pattern='*'):
        if pattern == '*':
            await self.flushdb()
        else:
            keys = [key async for key in self.scan_iter(pattern)]
            if keys:
                await self.delete(*keys)


class Mysql:

    def __init__(self, time_zone='+08:00', max_idle_time=3600, charset='utf8',
                 sql_mode='TRADITIONAL', autocommit=True, **kwargs):
        if any([key in kwargs for key in ['host', 'port', 'password']]):
            host = kwargs.pop('host', 'localhost')
            port = kwargs.pop('port', 3306)
            user = kwargs.pop('user', None)
            password = kwargs.pop('password', '')
            kwargs.update(dict(host=host, port=port, user=user, password=password))
        elif kwargs.get('uri'):
            uri = kwargs.pop('uri')
            kwargs.update(parse_uri(uri))
        elif os.environ.get('MYSQL_URI'):
            uri = os.environ['MYSQL_URI']
            kwargs.update(parse_uri(uri))

        kwargs.pop('schema', None)
        init_command = f'SET time_zone = "{time_zone}"'
        self._pool = None
        self._kwargs = Dict(charset=charset, init_command=init_command,
                            sql_mode=sql_mode, autocommit=autocommit, **kwargs)

    def __repr__(self):
        return f'Mysql(host={self._kwargs.host}, user={self._kwargs.user}, db={self._kwargs.db})'

    def cursor(self, cursorclass=pymysql.cursors.DictCursor):
        if self._pool is None:
            self._pool = PooledDB(pymysql, maxcached=10, **self._kwargs)
        return self._pool.connection().cursor(cursorclass)

    def __del__(self):
        self.close()

    def close(self):
        if self._pool is not None:
            self._pool.close()
            self._pool = None

    def iter(self, sql, *args):
        cursor = self.cursor(pymysql.cursors.SSDictCursor)
        try:
            cursor.execute(sql, args)
            for row in cursor.fetchall_unbuffered():
                yield Dict(row)
        finally:
            cursor.close()

    def query(self, sql, *args):
        cursor = self.cursor()
        try:
            cursor.execute(sql, args)
            rows = cursor.fetchall()
            return [Dict(row) for row in rows]
        finally:
            cursor.close()

    def get(self, sql, *args):
        cursor = self.cursor()
        try:
            cursor.execute(sql, args)
            row = cursor.fetchone()
            return Dict(row) if row else None
        finally:
            cursor.close()

    def execute(self, sql, *args):
        cursor = self.cursor()
        try:
            cursor.execute(sql, args)
            return cursor.lastrowid
        finally:
            cursor.close()

    def executemany(self, sql, args):
        cursor = self.cursor()
        try:
            return cursor.executemany(sql, args)
        finally:
            cursor.close()


class AioMysql(Mysql):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock = asyncio.Lock()

    async def _execute(self, cursor, sql, args):
        async with self._lock:
            await cursor.execute(sql, args)

    async def cursor(self, cursorclass=aiomysql.cursors.DictCursor):
        if self._pool is None:
            self._pool = await aiomysql.create_pool(minsize=0, maxsize=10, **self._kwargs)
            self._conn = await self._pool.acquire()
        return await self._conn.cursor(cursorclass)

    async def close(self):
        if self._pool is not None:
            self._pool.close()
            await self._pool.wait_closed()
            self._pool = None

    async def iter(self, sql, *args):
        cursor = await self.cursor(aiomysql.cursors.SSDictCursor)
        try:
            await self._execute(cursor, sql, args)
            async for row in cursor:
                yield Dict(row)
        finally:
            await cursor.close()

    async def query(self, sql, *args):
        cursor = await self.cursor()
        try:
            await self._execute(cursor, sql, args)
            rows = await cursor.fetchall()
            return [Dict(row) for row in rows]
        finally:
            await cursor.close()

    async def get(self, sql, *args):
        cursor = await self.cursor()
        try:
            await self._execute(cursor, sql, args)
            row = await cursor.fetchone()
            return Dict(row) if row else None
        finally:
            await cursor.close()

    async def execute(self, sql, *args):
        cursor = await self.cursor()
        try:
            await self._execute(cursor, sql, args)
            return cursor._lastrowid
        finally:
            await cursor.close()

    async def executemany(self, sql, args):
        cursor = await self.cursor()
        try:
            async with self._lock:
                return await cursor.executemany(sql, args)
        finally:
            await cursor.close()
