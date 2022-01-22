#!/usr/bin/env python
# -*- coding: utf-8 -*-

from contextlib import contextmanager
from dbpoolpy.dbconnect import DBConnection
from dbpoolpy.dbhelper.sqlite3 import SQLite3Helper


class SQLite3Connection(DBConnection, SQLite3Helper):
    dbtype = "sqlite3"

