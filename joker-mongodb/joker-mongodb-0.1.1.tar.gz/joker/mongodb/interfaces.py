#!/usr/bin/env python3
# coding: utf-8

import os.path
from collections import defaultdict
from typing import Union

import pymongo.errors
from bson import ObjectId, json_util
from gridfs import GridFS
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.database import Database
from volkanic.utils import printerr

from joker.mongodb import utils
from joker.mongodb.tools import kvstore


class CollectionInterface:
    def __init__(self, coll: Collection, filtr=None, projection=None):
        self._coll = coll
        self.filtr = filtr or {}
        self.projection = projection

    def exist(self, filtr: Union[ObjectId, dict]):
        return self._coll.find_one(filtr, projection=[])

    def kv_load(self, key: str):
        return kvstore.kv_load(self._coll, key)

    def kv_save(self, key: str, val):
        return kvstore.kv_save(self._coll, key, val)

    def find_recent_by_count(self, count=50) -> Cursor:
        cursor = self._coll.find(self.filtr, projection=self.projection)
        return cursor.sort([('_id', -1)]).limit(count)

    def find_most_recent_one(self) -> dict:
        recs = list(self.find_recent_by_count(1))
        if recs:
            return recs[0]

    def _insert(self, records):
        if records:
            self._coll.insert_many(records, ordered=False)

    @staticmethod
    def _check_for_uniqueness(records, uk):
        vals = [r.get(uk) for r in records]
        uniq_vals = set(vals)
        if len(vals) != len(uniq_vals):
            raise ValueError('records contain duplicating keys')

    def make_fusion_record(self):
        fusion_record = {}
        contiguous_stale_count = -1
        for skip in range(1000):
            record = self._coll.find_one(sort=[('$natural', -1)], skip=skip)
            if not record:
                continue
            contiguous_stale_count += 1
            for key, val in record.items():
                if not record.get(key):
                    fusion_record[key] = val
                    contiguous_stale_count = -1
            if contiguous_stale_count > 10:
                return fusion_record
        return fusion_record

    def query_uniq_values(self, fields: list, limit=1000):
        latest = [('_id', -1)]
        records = self._coll.find(sort=latest, projection=fields, limit=limit)
        uniq = defaultdict(set)
        for key in fields:
            for rec in records:
                val = rec.get(key)
                uniq[key].add(val)
        return uniq


class MongoInterface:
    """A interface for multiple mongodb clusters."""

    def __init__(self, hosts: dict, default: str = None, aliases: dict = None):
        if default is None:
            self.default_host = 'localhost'
            self.default_db_name = 'test1'
        else:
            self.default_host, self.default_db_name = default.split('.')
        self.hosts = hosts
        self.aliases = aliases or {}
        self._clients = {}

    @classmethod
    def from_config(cls, options: dict):
        params = {
            'default': options.pop('_default', None),
            'aliases': options.pop('_aliases', None),
        }
        return cls(options, **params)

    def get_mongo(self, host: str = None) -> MongoClient:
        if host is None:
            host = self.default_host
        try:
            return self._clients[host]
        except KeyError:
            pass
        # host pass through as MongoClient argument
        params = self.hosts.get(host, host)
        if isinstance(params, str):
            params = {'host': params}
        return self._clients.setdefault(host, MongoClient(**params))

    @property
    def db(self) -> Database:
        return self.get_db(self.default_host, self.default_db_name)

    def _check_coll_triple(self, names: tuple) -> tuple:
        n = len(names)
        if n == 1:
            return self.default_host, self.default_db_name, names[0]
        elif n == 3:
            return names
        else:
            c = self.__class__.__name__
            msg = 'requires 1 or 3 arguments, got {}'.format(c, n)
            raise ValueError(msg)

    def __call__(self, *names) -> Collection:
        names = self._check_coll_triple(names)
        return self.get_coll(*names)

    def get_db(self, host: str, db_name: str) -> Database:
        mongo = self.get_mongo(host)
        db_name = self.aliases.get(db_name, db_name)
        return mongo.get_database(db_name)

    def get_coll(self, host: str, db_name: str, coll_name: str) \
            -> Collection:
        db = self.get_db(host, db_name)
        return db.get_collection(coll_name)

    def get_gridfs(self, host: str, db_name: str, coll_name: str = 'fs') \
            -> GridFS:
        db = self.get_db(host, db_name)
        return GridFS(db, collection=coll_name)


class MongoInterfaceExtended(MongoInterface):
    def _get_target(self, host: str, db_name: str = None):
        if db_name is None:
            return self.get_mongo(host)
        return self.get_db(host, db_name)

    def inspect_storage_sizes(self, host: str, db_name: str = None):
        target = self._get_target(host, db_name)
        return utils.inspect_mongo_storage_sizes(target)

    def print_storage_sizes(self, host: str, db_name: str = None):
        target = self._get_target(host, db_name)
        return utils.print_mongo_storage_sizes(target)

    def get_ci(self, *names, **kwargs) -> CollectionInterface:
        coll = self.__call__(*names)
        return CollectionInterface(coll, **kwargs)

    # TODO: support BSON
    def restore_a_file(self, lines, inner_path: str, empty_coll_only=True):
        host, db_name, coll_name = \
            utils.infer_coll_triple_from_filename(inner_path)
        if coll_name == 'system.indexes':
            return
        coll = self.get_coll(host, db_name, coll_name)
        if empty_coll_only and coll.find_one(projection=[]):
            printerr(inner_path, 'skipped')
            return
        for ix, line in enumerate(lines):
            doc = json_util.loads(line)
            id_ = doc.get('_id', '')
            printerr(inner_path, ix, id_, '...', end=' ')
            try:
                coll.insert_one(doc)
            except pymongo.errors.DuplicateKeyError:
                printerr('DuplicateKeyError')
            else:
                printerr('completed')
