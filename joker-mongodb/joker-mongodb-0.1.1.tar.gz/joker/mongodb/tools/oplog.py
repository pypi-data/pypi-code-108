#!/usr/bin/env python3
# coding: utf-8

import logging
import time
from collections import UserDict

import pymongo
from bson import Timestamp, json_util, ObjectId
from pymongo import MongoClient

_logger = logging.getLogger(__name__)


class OplogRecord(UserDict):
    @property
    def op(self) -> str:
        return self.data.get('op')

    @property
    def ns(self) -> str:
        return self.data.get('ns')

    @property
    def ts(self) -> Timestamp:
        return self.data.get('ts')

    def to_mongo_doc(self):
        doc = self.data.copy()
        doc['ns'] = self.ns
        if 'o' in doc:
            doc['o'] = json_util.dumps(doc['o'])
        return doc

    @classmethod
    def from_mongo_doc(cls, doc: dict):
        doc = dict(doc)
        if 'o' in doc:
            doc['o'] = json_util.loads(doc['o'])
        return cls(doc)

    @property
    def upstream_id(self) -> str:
        try:
            return str(self.data['o']['_id'])
        except (KeyError, TypeError):
            pass
        try:
            return str(self.data['o2']['_id'])
        except (KeyError, TypeError):
            pass

    @property
    def id_(self) -> ObjectId:
        if id_ := self.data.get('_id'):
            return ObjectId(id_)


# Caution: do NOT run multiple threads / processes of this!!
# TODO: consider thread safety
class OplogTailer(object):
    _ns_exclude = {}
    _db_exclude = {'config', 'local', 'admin'}
    record_cls = OplogRecord

    def __init__(
            self, upstream_client: MongoClient, ts: Timestamp,
            ns_pattern: str = None, ns_exclude: str = None):
        """
        Args:
            upstream_client:
            ts: starting timestamp (seconds since epoch), e.g. 1642477123
            ns_pattern: regex
            ns_exclude: regex
        """
        db = upstream_client.get_database('local')
        self.oplog_coll = db.get_collection('oplog.rs')
        self.ts = ts
        self.ns_pattern = ns_pattern
        self.ns_exclude = ns_exclude
        self._cursor = self._get_cursor()

    def _get_where_clause(self):
        tests = ['this.op != "n"']
        if self.ns_pattern is not None:
            tests.append('this.ns.match(/{}/)'.format(self.ns_pattern))
            # tests.append(f'this.ns.match(/{self.ns_pattern}/)')
        if self.ns_exclude is not None:
            tests.append('!this.ns.match(/{}/)'.format(self.ns_exclude))
            # tests.append(f'!this.ns.match(/{self.ns_exclude}/)')
        return '&&'.join(tests)

    def _get_cursor(self):
        filtr = {'ts': {'$gt': self.ts}}
        # https://pymongo.readthedocs.io/en/stable/examples/tailable.html
        # TODO: consider using $expr for mongo >= 3.6
        _logger.info('OplogTailer._get_cursor, filtr=%s', filtr)
        cursor = self.oplog_coll.find(
            filtr, oplog_replay=True,
            cursor_type=pymongo.CursorType.TAILABLE_AWAIT,
        )
        where_clause = self._get_where_clause()
        if where_clause:
            cursor = cursor.where(where_clause)
        return cursor

    def _reset_cursor(self):
        self._cursor.close()
        self._cursor = self._get_cursor()

    def _check_ns(self, doc: dict):
        ns = doc.get('ns')
        if not ns:
            return False
        if ns in self._ns_exclude:
            return False
        db_name = ns.split('.')[0]
        if db_name in self._db_exclude:
            return False
        return True

    def _fetch_next(self):
        try:
            return self._cursor.next()
        except (StopIteration, ConnectionResetError):
            self._reset_cursor()

    def __iter__(self):
        return self

    def __next__(self) -> 'record_cls':
        while True:
            doc = self._fetch_next()
            if doc is None:
                time.sleep(1)
                continue
            if not self._check_ns(doc):
                continue
            self.ts = doc.get('ts')
            return self.record_cls(doc)
