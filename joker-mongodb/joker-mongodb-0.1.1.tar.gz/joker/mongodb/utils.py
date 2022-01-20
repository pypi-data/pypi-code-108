#!/usr/bin/env python3
# coding: utf-8

import logging
import os.path
from typing import Union

import bson.json_util
import volkanic.utils
from joker.cast.numeric import human_filesize
from joker.textmanip.tabular import tabular_format
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.monitoring import (
    CommandListener, CommandStartedEvent,
    CommandFailedEvent, CommandSucceededEvent,
)


def is_in_replset(mongo: MongoClient) -> bool:
    db = mongo.get_database('admin')
    return 'replication' in db.command('getCmdLineOpts')['parsed']


def inspect_mongo_storage_sizes(target: Union[MongoClient, Database]):
    if isinstance(target, MongoClient):
        return {r['name']: r['sizeOnDisk'] for r in target.list_databases()}
    size_of_collections = {}
    for coll_name in target.list_collection_names():
        info = target.command('collStats', coll_name)
        size_of_collections[info['ns']] = info['storageSize']
    return size_of_collections


def print_mongo_storage_sizes(target: Union[MongoClient, Database]):
    s_rows = list(inspect_mongo_storage_sizes(target).items())
    s_rows.sort(key=lambda r: r[1], reverse=True)
    rows = []
    for k, v in s_rows:
        num, unit = human_filesize(v)
        rows.append([round(num), unit, k])
    for row in tabular_format(rows):
        print(*row)


def indented_json_dumps(obj, **kwargs):
    kwargs.setdefault('dumps', bson.json_util.dumps)
    return volkanic.utils.indented_json_dumps(obj, **kwargs)


def indented_json_print(obj, **kwargs):
    kwargs.setdefault('dumps', indented_json_dumps)
    return volkanic.utils.indented_json_print(obj, **kwargs)


def infer_coll_triple_from_filename(path: str):
    """
    >>> p = "somedir/local.retail.customers.6789.json"
    >>> infer_coll_triple_from_filename(p)
    ['local', 'retail', 'customers']
    """
    filename = os.path.split(path)[1]
    coll_fullname = filename.rsplit('.', 2)[0]
    return coll_fullname.split('.', 2)


class MongoCommandLogger(CommandListener):
    _registered = False
    _logger = logging.getLogger('_mongodb')
    _level = logging.DEBUG

    @staticmethod
    def _fmt_opid(event):
        if event.request_id == event.operation_id:
            return event.request_id
        return '{}.{}'.format(event.request_id, event.operation_id)

    @staticmethod
    def _fmt_url(event):
        addr = ':'.join(str(s) for s in event.connection_id)
        return '{}/{}'.format(addr, event.database_name)

    def started(self, event: CommandStartedEvent):
        if not self._logger.isEnabledFor(self._level):
            return
        parts = [
            self._fmt_opid(event),
            'started',
            self._fmt_url(event),
            event.command,
        ]
        msg = " ".join(str(s) for s in parts)
        self._logger.debug(msg)

    def succeeded(self, event: CommandSucceededEvent):
        if not self._logger.isEnabledFor(self._level):
            return
        parts = [
            self._fmt_opid(event),
            'succeeded',
            int(event.duration_micros / 1000),
        ]
        msg = " ".join(str(s) for s in parts)
        self._logger.debug(msg)

    def failed(self, event: CommandFailedEvent):
        if not self._logger.isEnabledFor(self._level):
            return
        parts = [
            self._fmt_opid(event),
            'failed',
            event.duration_micros,
        ]
        msg = " ".join(str(s) for s in parts)
        self._logger.debug(msg)
