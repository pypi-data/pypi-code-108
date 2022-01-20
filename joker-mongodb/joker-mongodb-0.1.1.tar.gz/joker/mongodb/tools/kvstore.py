#!/usr/bin/env python3
# coding: utf-8

from pymongo.collection import Collection


def kv_load(coll: Collection, key: str):
    doc = coll.find_one({'_id': key}, projection={'_id': False})
    if doc is None:
        return
    try:
        return doc['_']
    except KeyError:
        return doc


def kv_save(coll: Collection, key: str, val):
    filtr = {'_id': key}
    # explode dict if '_' and '_id' are not in it -- be less nested
    if isinstance(val, dict) and '_' not in val and '_id' not in val:
        replacement = val
    else:
        replacement = {'_': val}
    return coll.replace_one(filtr, replacement, upsert=True)
