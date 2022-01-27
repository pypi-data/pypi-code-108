# -*- coding: utf-8 -*-
# Copyright 2007-2019 The Wazo Authors
# SPDX-License-Identifier: GPL-3.0-or-later
"""sonicprobe.libs.BackSQL.backsqlite3

Backend support for SQLite3 for anysql

Copyright (C) 2007-2010  Proformatique

"""

import sqlite3
import os.path

from sonicprobe.libs import anysql
from sonicprobe.libs.urisup import PATH, QUERY, uri_help_split, uri_help_unsplit

def __dict_from_query(query):
    if not query:
        return {}
    return dict(query)

def connect_by_uri(uri):
    puri = uri_help_split(uri)
    opts = __dict_from_query(puri[QUERY])

    con = None
    if 'timeout_ms' in opts:
        con = sqlite3.connect(puri[PATH], float(opts['timeout_ms']))
    else:
        con = sqlite3.connect(puri[PATH])

    return con

def c14n_uri(uri):
    puri = list(uri_help_split(uri))
    puri[PATH] = os.path.abspath(puri[PATH])
    return uri_help_unsplit(tuple(puri))

def escape(s):
    return '.'.join([('"%s"' % comp.replace('"', '""')) for comp in s.split('.')])

def is_connected(connection, link = None):
    _cursor = None
    ret     = True

    try:
        if link:
            if isinstance(link, anysql.cursor):
                _cursor = link._cursor__dbapi2_cursor
            else:
                _cursor = link
        else:
            _cursor = connection.cursor()
        _cursor.execute("SELECT 1")
    except sqlite3.ProgrammingError:
        ret = False
    finally:
        if not link and _cursor:
            _cursor.close()

    return ret

anysql.register_uri_backend('sqlite3', connect_by_uri, sqlite3, c14n_uri, escape, None, is_connected)
