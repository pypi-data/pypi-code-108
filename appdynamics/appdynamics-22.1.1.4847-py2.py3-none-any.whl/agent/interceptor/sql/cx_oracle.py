# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Intercept the AppDynamics appd_cx_oracle package.

Due to the way the cx_Oracle package is written entirely in C, users will
have to import our 'appd_cx_oracle' package, which then gets intercepted here.
"""

from __future__ import unicode_literals
import re

from .dbapi import DbAPIConnectionInterceptor, DbAPICursorInterceptor

# The format for the cx_Oracle connection string can take multiple forms:
#   cx_Oracle.connect('user/password@host:port/sid')
#   cx_Oracle.connect('user', 'password', 'host:port/sid')
#   cx_Oracle.connect('user', 'password', tns_dsn)
#   cx_Oracle.connect('user', 'password', config_from_tnsnames.ora)
#                                         ^ Uses Defaults in this case (no way to grab connection info)
#   cx_Oracle.connect(user='user', password='password', dsn=tns_dsn)
#
#   Example tns_dsn:
#     '(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=<host>)(PORT=<port>)))(CONNECT_DATA=(SID=<sid>)))'
#
#   Note:
#     - There may be leading slashes in front of the hostname (//host:port/sid)
#     - SERVICE_NAME will only appear if explicitly calling 'makedsn' with the 'service_name' kv.
#
# More Documentation:
#   https://cx-oracle.readthedocs.io/en/latest/module.html#cx_Oracle.connect
#   https://docs.oracle.com/cd/B28359_01/network.111/b28317/tnsnames.htm#i500390

USER_AND_PASSWORD_RE = re.compile('.+/.+@(.+)')
DSN_RE = re.compile(r'.*DESCRIPTION=.*ADDRESS=.*CONNECT_DATA.*')
URL_RE = re.compile(r'(.*//)?(.*?)(:([0-9]*))?/(.*)')
HOST_RE = re.compile(r'.*HOST=(//)?(.*?)\)')
PORT_RE = re.compile(r'.*PORT=(.*?)\)')
SID_SERVICE_RE = re.compile(r'.*(SID|SERVICE_NAME)=(.*?)\)')


def parse_cx_oracle_tns_dsn(dsn):
    host_match = HOST_RE.search(dsn)
    if host_match and len(host_match.group(2)):
        host = host_match.group(2)
    else:
        host = 'localhost'

    port_match = PORT_RE.search(dsn)
    if port_match and len(port_match.group(1)):
        port = port_match.group(1)
    else:
        port = '1521'

    dbname_match = SID_SERVICE_RE.search(dsn)
    if dbname_match and len(dbname_match.group(2)):
        dbname = dbname_match.group(2)
    else:
        dbname = 'XE'

    return host, port, dbname


def parse_cx_oracle_tns_url(conn):
    url_match = URL_RE.match(conn)

    if url_match:
        if url_match.group(2) and len(url_match.group(2)):
            host = url_match.group(2)
        else:
            host = 'localhost'

        if url_match.group(4) and len(url_match.group(4)):
            port = url_match.group(4)
        else:
            port = '1521'

        if url_match.group(5) and len(url_match.group(5)):
            dbname = url_match.group(5)
        else:
            dbname = 'XE'

        return host, port, dbname
    else:
        return 'localhost', '1521', 'XE'


def parse_oracle_args_dsn(*args):
    if len(*args) == 1:
        # If the credentials and connection were passed as a single string,
        # it'll look something like:
        #     (('user/password@host:port/sid',),)
        while type(args) is tuple:
            args = args[0]
        # Remove the username and password from the string
        args = USER_AND_PASSWORD_RE.match(args).group(1)
        return parse_cx_oracle_tns_url(args)
    else:
        # The Oracle tns would be the 3rd argument
        # ex: ('user', 'password', 'tns')
        tns = args[0][2]
        dsn_match = DSN_RE.match(tns)
        if dsn_match:
            return parse_cx_oracle_tns_dsn(tns)
        else:
            return parse_cx_oracle_tns_url(tns)


def parse_oracle_kwargs_dsn(**kwargs):
    dsn = kwargs.pop('dsn')
    return parse_cx_oracle_tns_dsn(dsn)


def parse_oracle_dsn(*args, **kwargs):
    if args:
        return parse_oracle_args_dsn(args)
    else:
        return parse_oracle_kwargs_dsn(**kwargs)


class CxOracleConnectionInterceptor(DbAPIConnectionInterceptor):
    def get_backend_properties(self, conn, *args, **kwargs):
        return parse_oracle_dsn(*args, **kwargs) + ('ORACLE',)


class CxOracleCursorInterceptor(DbAPICursorInterceptor):
    def get_connection(self, cursor):
        return cursor.connection


def intercept_cx_oracle_connection(agent, mod):
    # cx_Oracle is implemented purely in C, making interception via normal
    # methods impossible.  We redefine the classes we need to intercept here
    # and expose the relevate methods.
    class Cursor(mod.Cursor):
        def execute(self, *args, **kwargs):
            return super(Cursor, self).execute(*args, **kwargs)

        def executemany(self, *args, **kwargs):
            return super(Cursor, self).executemany(*args, **kwargs)

    class Connection(mod.Connection):
        def __init__(self, *args, **kwargs):
            super(Connection, self).__init__(*args, **kwargs)

        def cursor(self, *args, **kwargs):
            return Cursor(self, *args, **kwargs)

    mod.Cursor = Cursor
    mod.Connection = mod.connect = Connection

    CxOracleConnectionInterceptor(agent, mod.Connection, CxOracleCursorInterceptor).attach('__init__')
