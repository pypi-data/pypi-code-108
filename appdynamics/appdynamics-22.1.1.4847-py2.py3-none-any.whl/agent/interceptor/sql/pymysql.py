# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Intercept the pymysql package.

"""

from __future__ import unicode_literals

from .dbapi import DbAPIConnectionInterceptor, DbAPICursorInterceptor


class PymysqlConnectionInterceptor(DbAPIConnectionInterceptor):
    def get_backend_properties(self, conn, *args, **kwargs):
        return conn.host, conn.port, conn.db, 'MYSQL'


class PymysqlCursorInterceptor(DbAPICursorInterceptor):
    def get_connection(self, cursor):
        return cursor.connection


def intercept_pymysql_connections(agent, mod):
    PymysqlConnectionInterceptor(agent, mod.Connection, PymysqlCursorInterceptor).attach('connect')
