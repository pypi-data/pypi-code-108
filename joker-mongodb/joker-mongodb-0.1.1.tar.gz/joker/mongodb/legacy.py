#!/usr/bin/env python3
# coding: utf-8

"""
This module is DEPRECATED.
"""

from gridfs import GridFS
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from joker.mongodb import utils
from joker.mongodb.interfaces import CollectionInterface


class DatabaseInterface:
    def __init__(self, db: Database):
        self._db = db

    def inspect_storage_sizes(self):
        return utils.inspect_mongo_storage_sizes(self._db)

    def print_storage_sizes(self):
        return utils.print_mongo_storage_sizes(self._db)


class MongoClientExtended(MongoClient):
    """An extended client-side representation of a mongodb cluster."""

    def __repr__(self):
        cn = self.__class__.__name__
        return "{}({})".format(cn, self._repr_helper())

    def inspect_storage_sizes(self):
        return utils.inspect_mongo_storage_sizes(self)

    def print_storage_sizes(self):
        return utils.print_mongo_storage_sizes(self)

    def get_db(self, db_name: str) -> Database:
        return self.get_database(db_name)

    def get_dbi(self, db_name: str) -> DatabaseInterface:
        return DatabaseInterface(self.get_database(db_name))

    def get_coll(self, db_name: str, coll_name: str) -> Collection:
        db = self.get_database(db_name)
        return db.get_collection(coll_name)

    def get_ci(self, db_name: str, coll_name: str) -> CollectionInterface:
        coll = self.get_coll(db_name, coll_name)
        return CollectionInterface(coll)

    def get_gridfs(self, db_name: str, coll_name: str = 'fs') \
            -> GridFS:
        # avoid names like "images.files.files"
        if coll_name.endswith('.files') or coll_name.endswith('.chunks'):
            coll_name = coll_name.rsplit('.', 1)[0]
        db = self.get_database(db_name)
        return GridFS(db, collection=coll_name)