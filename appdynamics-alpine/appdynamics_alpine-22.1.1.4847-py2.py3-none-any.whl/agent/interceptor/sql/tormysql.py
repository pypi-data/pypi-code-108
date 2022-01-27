from __future__ import unicode_literals

from .dbapi import DbAPIConnectionInterceptor, DbAPICursorInterceptor
from ..base import ExitCallInterceptor


class TormysqlInterceptor(ExitCallInterceptor):
    def end_exit_call(self, exit_call, future=None, exc_info=None):
        if exc_info or not future:
            super(TormysqlInterceptor, self).end_exit_call(exit_call, exc_info=exc_info)
            return

        from appdynamics.agent.interceptor.utils.tornado_exit_call_utils import get_exc_info, add_callback

        def end_exit_call(exit_call, completed_future):
            # In tornado>=5, future.exc_info() method is not present. tornado>=5 uses asyncio.Future instead of
            # tornado.concurrent.Future whenever asyncio is present.
            # get_exc_info method checks for presence of exc_info(), if absent creates and return exc_info tuple
            super(TormysqlInterceptor, self).end_exit_call(exit_call, exc_info=get_exc_info(completed_future))

        if future.done():
            end_exit_call(exit_call, future)
        else:
            # In tornado>=6 future._callbacks returns None. Using add_done_callback for callback addition as
            # the callback argument is removed.
            # tornado.stack_context has been replaced with context_vars for interception for tornado >= 6
            with self.log_exceptions():
                add_callback(future, end_exit_call, exit_call)


class TormysqlConnectionInterceptor(TormysqlInterceptor, DbAPIConnectionInterceptor):
    def get_backend_properties(self, client, *args, **kwargs):
        host = client._kwargs.get('host', 'localhost')
        port = client._kwargs.get('port', '3306')
        db = client._kwargs.get('database', client._kwargs.get('db', ''))
        return host, port, db, 'TORMYSQL'


class TormysqlCursorInterceptor(TormysqlInterceptor, DbAPICursorInterceptor):
    def get_connection(self, cursor):
        # Since in the `connect` interceptor we are actually setting attributes
        # on the client, not the connection, we need to return it here.
        # Getting the client instance from the bound callback is horrible, but
        # it's the only way I could manage to get at it.
        return cursor.connection._close_callback.__self__

    # cursor._cursor in tormysql contains the pymysql cursor. This object is set in tormysql and fetched
    # in pymysql to avoid formation of extra exit call
    def get_underlying_cursor(self, cursor):
        return cursor._cursor


def intercept_tormysql_client(agent, mod):
    TormysqlConnectionInterceptor(agent, mod.Client, TormysqlCursorInterceptor).attach('connect')
