#!/usr/bin/env python3
# coding: utf-8

import datetime

from pymongo.collection import Collection, ReturnDocument
from pymongo.errors import DuplicateKeyError


class SerialNumber:
    __slots__ = ['prefix', 'number', 'length']

    @staticmethod
    def _get_collection() -> Collection:
        raise NotImplementedError

    def __init__(self, prefix='ID', length=6):
        coll = self._get_collection()
        doc = coll.find_one_and_update(
            {'_id': prefix}, {'$inc': {'i': 1}},
            upsert=True, return_document=ReturnDocument.AFTER,
        )
        self.prefix = prefix
        self.number = doc['i']
        self.length = length

    def __str__(self):
        return self.prefix + str(self.number).zfill(self.length)


class NamedLock(object):
    @staticmethod
    def _get_collection() -> Collection:
        raise NotImplementedError

    def __init__(self, name: str, ttl=12):
        self.name = name
        self.coll = self._get_collection()
        self.ttl = ttl

    def acquire(self):
        now = datetime.datetime.now()
        expire_at = now + datetime.timedelta(seconds=self.ttl)
        self.coll.delete_many({'expire_at': {'$lt': now}})
        record = {'_id': self.name, 'expire_at': expire_at}
        try:
            self.coll.insert_one(record)
        except DuplicateKeyError:
            return False
        return True

    def release(self):
        self.coll.delete_one({'_id': self.name})
