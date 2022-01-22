#!/usr/bin/env python
# -*- coding: utf-8 -*-

from contextlib import contextmanager
from dbpoolpy.dbconnect import DBConnection
from dbpoolpy.dbhelper.mysql import MysqlHelper


class MySQLConnection(DBConnection, MysqlHelper):
    dbtype = "mysql"


    def connect(self):
        #  ssl = None
        #  key_path = os.path.join(MYSQL_SSLKEY_PATH, '{host}_{port}'.format(**{
        #      'host': self._param['host'], 'port': self._param['port']}))
        #  if os.path.exists(key_path):
        #      print('IP:%s|PORT:%s|SSL=True|ssl_path:%s',
        #                  self._param['host'], self._param['port'], key_path)
        #      ssl = {
        #          'ssl': {
        #              'ca': os.path.join(key_path, 'ssl-ca'),
        #              'key': os.path.join(key_path, 'ssl-key'),
        #              'cert': os.path.join(key_path, 'ssl-cert'),
        #          }
        #      }
        self._conn = self._engine.connect(*self._args, **self._kwargs)
        self._conn.autocommit(1)
        self._transaction = False

        cur = self._conn.cursor()
        cur.execute("show variables like 'server_id'")
        row = cur.fetchone()
        self._server_id = int(row[1])
        cur.close()

        cur = self._conn.cursor()
        cur.execute("select connection_id()")
        row = cur.fetchone()
        self._conn_id = row[0]
        cur.close()

        print('server=%s|func=connect|id=%d|name=%s|user=%s|role=%s|addr=%s:%d|db=%s' % (
                 self.dbtype,
                 self._conn_id % 10000,
                 self._name,
                 self._kwargs.get('user', ''),
                 self._role,
                 self._kwargs.get('host', ''),
                 self._kwargs.get('port', 0),
                 self._kwargs.get('database', '')))


    def begin(self, *args, **kwargs):
        self._transaction = True
        begin = self._conn.begin
        begin(*args, **kwargs)


    def cancel(self):
        cancel = self._conn.cancel
        cancel()

    def ping(self, *args, **kwargs):
        return self._conn.ping(*args, **kwargs)

    def escape(self, s):
        return self._conn.escape_string(s)

    def alive(self):
        pass

