# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Intercept the psycopg2 package.

The interceptors in here are more complex than for other packages because the
classes are defined in C extension code.  We have to wrap the connection and
cursor classes with our own, which allows us to attach to the relevant methods.

"""

# pylint: disable=no-self-argument

from __future__ import unicode_literals
import re

from appdynamics.lang import parse_qs, str, urlparse
from ..base import BaseInterceptor
from .dbapi import DbAPIConnectionInterceptor, DbAPICursorInterceptor

# For format of PostgreSQL connection strings, see:
# http://www.postgresql.org/docs/current/static/libpq-connect.html#LIBPQ-CONNSTRING

KV_RE = re.compile(r'\s*(?P<key>[a-zA-Z_]+)\s*=\s*(?P<remainder>.+)')


def parse_postgresql_url_dsn(dsn):
    url = urlparse(dsn, allow_fragments=False)

    if '?' in url.path:
        parts = url.path.split('?', 1)
        path, params = parts[0], parse_qs(parts[1])
    else:
        path = url.path
        params = parse_qs(url.query) if url.query else {}

    if 'host' in params:
        host = params['host'][0]
    else:
        host = url.hostname or 'localhost'

    if 'port' in params:
        port = params['port'][0]
    elif url.port:
        port = str(url.port)
    else:
        port = '5432'

    path = path.strip('/')

    if 'dbname' in params:
        dbname = params['dbname'][0]
    elif path:
        dbname = path
    elif 'user' in params:
        dbname = params['user'][0]
    else:
        dbname = url.username or 'postgres'

    return host, port, dbname


def parse_quoted_value(remainder):
    length = len(remainder)
    idx = 1

    start_idx = idx
    val = []

    while idx < length and remainder[idx] != "'":
        if remainder[idx:idx + 2] in ("\\\\", "\\'"):
            # Valid escape sequence: collect the current run with the
            # escaped character, move past the escape sequence, and start a
            # new run.
            val.append(remainder[start_idx:idx] + remainder[idx + 1])
            idx += 2
            start_idx = idx
        else:
            idx += 1

    val.append(remainder[start_idx:idx])
    return ''.join(val), remainder[idx + 1:]


def parse_postgresql_kv_dsn(dsn):
    if "'" not in dsn:  # Fast path when there are no quoted strings.
        dsn = re.sub(r'(\s*=\s+|\s+=\s*)', '=', dsn).split()
        parts = dict(pair.split('=', 1) for pair in dsn)
    else:
        parts = {}
        m = KV_RE.match(dsn)

        while m:
            key, remainder = m.group('key'), m.group('remainder')

            if remainder[0] == "'":
                value, remainder = parse_quoted_value(remainder)
            else:
                split = remainder.split(None, 1)
                if len(split) == 1:
                    value, remainder = split[0], ''
                elif split:
                    value, remainder = split
                else:
                    break

            parts[key] = value
            m = KV_RE.match(remainder)

    return parse_postgresql_keyword_args(parts)


def parse_postgresql_keyword_args(parts):
    host = parts.get('host', 'localhost')
    port = parts.get('port', '5432')
    dbname = parts.get('dbname', parts.get('user', 'postgres'))
    return host, port, dbname


def parse_postgresql_dsn(dsn=None, *args, **kwargs):
    if kwargs and len(kwargs):
        return parse_postgresql_keyword_args(kwargs)
    elif dsn.startswith('postgresql://'):
        return parse_postgresql_url_dsn(dsn)
    else:
        return parse_postgresql_kv_dsn(dsn)


class Psycopg2ConnectionInterceptor(DbAPIConnectionInterceptor):
    def get_backend_properties(self, conn, *args, **kwargs):
        return parse_postgresql_dsn(*args, **kwargs) + ('POSTGRESQL',)


class Psycopg2CursorInterceptor(DbAPICursorInterceptor):
    def get_connection(self, cursor):
        return cursor.connection


class Psycopg2Interceptor(BaseInterceptor):
    cursor_classes = {}

    def _connect(self, connect, dsn=None, connection_factory=None, cursor_factory=None, *args, **kwargs):
        connection_factory = connection_factory or kwargs.pop('connection_factory', None) or \
            self.cls.extensions.connection

        class Connection(connection_factory):
            def __init__(conn, *args, **kwargs):
                super(Connection, conn).__init__(*args, **kwargs)

            def cursor(conn, *args, **kwargs):
                cursor_factory = kwargs.pop('cursor_factory', None) or conn.cursor_factory or self.cls.extensions.cursor
                try:
                    # we store these wrapper classes to avoid 're-instrumenting' each time
                    cursor_class = self.cursor_classes[cursor_factory]
                except KeyError:
                    class Cursor(cursor_factory):
                        def execute(curs, *args, **kwargs):
                            return super(Cursor, curs).execute(*args, **kwargs)

                        def executemany(curs, *args, **kwargs):
                            return super(Cursor, curs).executemany(*args, **kwargs)
                    self.cursor_classes[cursor_factory] = Cursor
                    cursor_class = Cursor
                return super(Connection, conn).cursor(cursor_factory=cursor_class, *args, **kwargs)

        Psycopg2ConnectionInterceptor(
            self.agent, Connection, Psycopg2CursorInterceptor).attach('__init__')

        return connect(dsn, connection_factory=Connection, cursor_factory=cursor_factory, *args, **kwargs)


def intercept_psycopg2_connection(agent, mod):
    Psycopg2Interceptor(agent, mod).attach('connect')
