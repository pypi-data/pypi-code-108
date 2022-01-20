#!/usr/bin/env python3
# coding: utf-8

import csv
import datetime
import functools
import logging
import sys
import traceback
from collections import defaultdict
from typing import Union

import pymongo.errors
from bson import ObjectId
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.database import Database
from volkanic.utils import printerr

from joker.mongodb import utils

_logger = logging.getLogger(__name__)


# too smart ..., deprecate?
def projection_(*keys, value=True, smart=True):
    if smart and len(keys) == 1:
        keys = keys[0].split()
    return {k: bool(value) for k in keys}


def _show_call_stack(func):
    @functools.wraps(func)
    def ret_func(*args, **kwargs):
        print(func, file=sys.stderr)
        rv = func(*args, **kwargs)
        traceback.print_stack()
        return rv

    return ret_func


def patch_mongo_for_debug(wrapper_func=None):
    if wrapper_func is None:
        wrapper_func = _show_call_stack
    Collection.find = wrapper_func(Collection.find)
    Collection.find_one = wrapper_func(Collection.find_one)
    Collection.update = wrapper_func(Collection.update)  # noqa
    Collection.update_one = wrapper_func(Collection.update_one)
    Collection.update_many = wrapper_func(Collection.update_many)


def gridfs_copy(source_fs, target_fs, _id):
    if isinstance(_id, str):
        _id = ObjectId(_id)
    print('copying gridfs file:', _id)
    source_file = source_fs.find_one({'_id': _id})
    if not source_file:
        raise ValueError('not found: _id = {}'.format(_id))
    target_file = target_fs.new_file(_id=_id)
    target_file.write(source_file)
    target_file.close()


def export_records_to_csv(records, outpath):
    fields = set()
    for rec in records:
        fields.update(rec)
    header = list(fields)
    header.sort()
    with open(outpath, 'w') as fout:
        writer = csv.writer(fout)
        writer.writerow(header)
        for rec in records:
            row = [rec.get(k, '') for k in header]
            writer.writerow(row)


def _insert(target_coll: Collection, record: dict, identifier=None):
    identifier = identifier or str(record.get('_id'))
    try:
        target_coll.insert_one(record)
    except pymongo.errors.DuplicateKeyError:
        printerr('Dup:', target_coll, identifier)
    else:
        printerr('OK:', target_coll, identifier)
    return record


def copy_one(source_coll, target_coll, filtr: dict, updates: dict = None, **kwargs):
    record = source_coll.find_one(filtr, **kwargs)
    if not record:
        printerr('NotFound:', source_coll, filtr)
        return
    if updates:
        record.update(updates)
    return _insert(target_coll, record, identifier=filtr)


def copy_many(source_coll, target_coll, filtr: dict, updates: dict = None, **kwargs):
    for record in source_coll.find(filtr, **kwargs):
        if updates:
            record.update(updates)
        _insert(target_coll, record)


def find_field_names(coll: Collection, retry: int = 10):
    keys = set()
    name_count = 0
    for i in range(50):
        doc = coll.find_one(skip=i, sort=[('_id', -1)])
        keys.update(doc)
        if len(keys) == name_count:
            retry -= 1
        else:
            name_count = len(keys)
    return keys


class DatabaseWrapper:
    def __init__(self, db: Database):
        self.db = db

    def inspect_storage_sizes(self):
        return utils.inspect_mongo_storage_sizes(self.db)

    def print_storage_sizes(self):
        return utils.print_mongo_storage_sizes(self.db)


class CollectionWrapper:
    def __init__(self, coll: Collection, filtr=None, projection=None):
        self.coll = coll
        self.filtr = filtr or {}
        self.projection = projection

    def exist(self, filtr: Union[ObjectId, dict]):
        return self.coll.find_one(filtr, projection=[])

    def find_by_oid_range(
            self, start: Union[ObjectId, None],
            end: Union[ObjectId, None]) -> Cursor:
        _id_conf = {}
        if start:
            _id_conf['$gt'] = start
        if end:
            _id_conf['$lt'] = end
        filtr = self.filtr.copy()
        filtr['_id'] = _id_conf
        return self.coll.find(filtr, projection=self.projection)

    def find_by_oid_time_range(
            self, start: Union[datetime.datetime, None],
            end: Union[datetime.datetime, None]) -> Cursor:
        _id_conf = {}
        if start:
            _id_conf['$gt'] = ObjectId.from_datetime(start)
        if end:
            _id_conf['$lt'] = ObjectId.from_datetime(end)
        filtr = self.filtr.copy()
        if _id_conf:
            filtr['_id'] = _id_conf
        _logger.debug(filtr)
        return self.coll.find(filtr, projection=self.projection)

    def find_recent_by_time(self, days=30, seconds=0) -> Cursor:
        delta = datetime.timedelta(days=days, seconds=seconds)
        start = datetime.datetime.now() - delta
        return self.find_by_oid_time_range(start, None)

    def find_recent_by_count(self, count=50) -> Cursor:
        cursor = self.coll.find(self.filtr, projection=self.projection)
        return cursor.sort([('_id', -1)]).limit(count)

    def find_most_recent_one(self) -> dict:
        recs = list(self.find_recent_by_count(1))
        if recs:
            return recs[0]

    def _replace(self, records, uk='_id'):
        """
        :param records: a list of dicts
        :param uk: unique key
        """
        for rec in records:
            uk_val = rec.get(uk)
            self.coll.replace_one({uk: uk_val}, rec)

    def _update(self, records, uk='_id'):
        """
        :param records: a list of dicts
        :param uk: unique key
        """
        for rec in records:
            uk_val = rec.get(uk)
            self.coll.update_one({uk: uk_val}, {'$set': rec})

    def _insert(self, records):
        if records:
            self.coll.insert_many(records, ordered=False)

    @staticmethod
    def _check_for_uniqueness(records, uk):
        vals = [r.get(uk) for r in records]
        uniq_vals = set(vals)
        if len(vals) != len(uniq_vals):
            raise ValueError('records contain duplicating keys')

    def upsert_with_index(self, records, uk='_id', replace=False):
        """Batch insert or update
        requires single-field unique index on `uk`
        Similar to `INESRT ... ON DUPLICATE KEY UPDATE ...` in MySQL
        Caution:
        - repeats in records lead to unpredictable results
        - not atomic
        :param records: a list of dicts
        :type records: list
        :param uk: unique key
        :type uk: str
        :param replace: use coll.replace instead of collection.update
        :type replace: bool
        """
        if not records:
            return
        dup_records = []
        try:
            self._insert(records)
        except pymongo.errors.BulkWriteError as exc:
            other_errors = []
            for err in exc.details['writeErrors']:
                if err['code'] == 11000:
                    dup_records.append(err['op'])
                else:
                    other_errors.append(err)
            if other_errors or exc.details['writeConcernErrors']:
                exc.details['writeErrors'] = other_errors
                raise exc
        if replace:
            self._replace(records, uk=uk)
        else:
            self._update(records, uk=uk)

    def upsert_without_index(self, records, uk='_id', replace=False):
        """Batch insert or update
        single-field unique index on `uk` is not required
        Caution:
        - repeats in records lead to unpredictable results
        - not atomic
        :param records: a list of dicts
        :type records: list
        :param uk: unique key
        :type uk: str
        :param replace: use coll.replace instead of collection.update
        :type replace: bool
        """
        if not records:
            return
        self._check_for_uniqueness(records, uk)
        insert_records = []
        update_records = []
        existing_vals = {r.get(uk) for r in self.coll.find({}, ['uk'])}
        for rec in records:
            uk_val = rec.get(uk)
            if uk_val in existing_vals:
                update_records.append(rec)
            else:
                insert_records.append(rec)
        self._insert(insert_records)
        if replace:
            self._replace(update_records, uk=uk)
        else:
            self._update(update_records, uk=uk)

    def make_fusion_record(self):
        fusion_record = {}
        contiguous_stale_count = -1
        for skip in range(1000):
            record = self.coll.find_one(sort=[('$natural', -1)], skip=skip)
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
        records = self.coll.find(sort=latest, projection=fields, limit=limit)
        uniq = defaultdict(set)
        for key in fields:
            for rec in records:
                val = rec.get(key)
                uniq[key].add(val)
        return uniq

    def batch_update_a_field_with_log(self, field_name, old_value, new_value, log=None):
        upd = {'$set': {field_name: new_value}}
        if log:
            upd['$push'] = {'log': log}
        ur = self.coll.update_many({field_name: old_value}, upd)
        s = f'{field_name}={old_value}'
        print(s, ur.matched_count, ur.modified_count)
