# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Interceptors for dealing with DB-API 2.0 compatible libraries.

"""

from __future__ import unicode_literals
import abc

from appdynamics.lib import MissingConfigException
from appdynamics.lang import str
from appdynamics.agent.models.exitcalls import EXIT_DB, EXIT_SUBTYPE_DB
from .. import HOST_PROPERTY_MAX_LEN, DB_NAME_PROPERTY_MAX_LEN, VENDOR_PROPERTY_MAX_LEN
from ..base import ExitCallInterceptor


def get_db_backend(agent, host, port, dbname, vendor):
    if agent.backend_registry is None:
        raise MissingConfigException

    naming_format_string = '{HOST}:{PORT} - {DATABASE} - {VENDOR} - {VERSION}'
    host = host[:HOST_PROPERTY_MAX_LEN]
    dbname = dbname[:DB_NAME_PROPERTY_MAX_LEN]
    vendor = vendor[:VENDOR_PROPERTY_MAX_LEN]

    backend_properties = {
        'VENDOR': vendor,
        'HOST': host,
        'PORT': str(port),
        'DATABASE': dbname,
        'VERSION': 'unknown',
    }

    return agent.backend_registry.get_backend(EXIT_DB, EXIT_SUBTYPE_DB, backend_properties, naming_format_string)


class DbAPICursorInterceptor(ExitCallInterceptor):
    def end_exit_call(self, exit_call, execute_result=None, exc_info=None):
        # execute_result is intentionally not used here.  Its purpose is to
        # allow subclasses to override this method and use the value.
        super(DbAPICursorInterceptor, self).end_exit_call(exit_call, exc_info=exc_info)

    # tormysql is formed above pymysql, during interception of tormysql bt info is passed from tormysql to pymysql
    # interceptor, calling _execute twice for a single db call which can lead to extra exit call formation
    # for tornado<=5, stack_context is unable to propagate bt info from tormysql to pymysql interceptor so, no extra
    # exit_call was formed
    # for tornado>=6, using context_var bt info is propagated to pymysql interceptor. To avoid formation of exit call,
    # this function is overridden in TormysqlCursorInterceptor for setting _appd_exit_call in cursor._cursor
    # which is a shared object between tormysql and pymysql
    def get_underlying_cursor(self, cursor):
        return cursor

    def _execute(self, execute, cursor, operation, *args, **kwargs):
        with self.log_exceptions():
            backend = None
            exit_call = None

            bt = self.bt
            if bt and not hasattr(self.get_underlying_cursor(cursor), '_appd_exit_call'):
                connection = self.get_connection(cursor)
                try:
                    backend = connection._appd_backend
                except AttributeError:
                    # If we weren't able to create a backend when the
                    # connection object was created, we can try again now.
                    try:
                        backend = get_db_backend(self.agent, *connection._appd_backend_properties)
                        connection._appd_backend = backend
                    except MissingConfigException:
                        # Still no config; try again next time!
                        pass
                if backend:
                    exit_call = self.start_exit_call(bt, backend, operation=operation)
                    self.get_underlying_cursor(cursor)._appd_exit_call = exit_call

        result = execute(cursor, operation, appd_exit_call=exit_call, *args, **kwargs)

        # Normally it's fine to just try to end the exit call even if we
        # aren't sure it actually started.  However for cases where we have
        # several `execute` calls nested inside an `executemany` call, we do
        # not want to end the exit call until the outer call is over.
        if exit_call:
            self.end_exit_call(exit_call, result)
            try:
                delattr(self.get_underlying_cursor(cursor), '_appd_exit_call')
            except AttributeError:
                pass
        return result

    @abc.abstractmethod
    def get_connection(self, cursor):
        """Return the `Connection` object used to create this `Cursor`.

        """
        pass


class DbAPIConnectionInterceptor(ExitCallInterceptor):
    def __init__(self, agent, cls, cursor_interceptor):
        super(DbAPIConnectionInterceptor, self).__init__(agent, cls)
        self.cursor_interceptor = cursor_interceptor

    def attach(self, connect_func):
        super(DbAPIConnectionInterceptor, self).attach(connect_func, patched_method_name='_connect')
        super(DbAPIConnectionInterceptor, self).attach('cursor')

    def end_exit_call(self, exit_call, maybe_connection=None, exc_info=None):
        # maybe_connection is intentionally not used here.  Its purpose is to
        # allow subclasses to override this method and use the value.
        super(DbAPIConnectionInterceptor, self).end_exit_call(exit_call=exit_call, exc_info=exc_info)

    def _connect(self, connect, connection, *args, **kwargs):
        with self.log_exceptions():
            backend = None
            exit_call = None

            backend_properties = self.get_backend_properties(connection, *args, **kwargs)
            try:
                backend = get_db_backend(self.agent, *backend_properties)
                connection._appd_backend = backend
            except MissingConfigException:
                # If the agent has just started and doesn't have config yet,
                # we cannot create and store a backend on the connection object.
                # We store the backend properties instead so that the cursor
                # interceptor can try again later.
                connection._appd_backend_properties = backend_properties

            bt = self.bt
            if bt and backend:
                exit_call = self.start_exit_call(bt, backend, operation='connect')

        # The reason this is called `maybe_connection` is that different
        # interceptors will return different values here.  `connect` could
        # be an __init__ method on a class, returning None, it could be a
        # function which returns an initialized connection object, or even a
        # method returning an async future object.  The only reason we capture
        # this value and pass it to `end_exit_call` is to allow subclasses to
        # override the behaviour of `end_exit_call` (for example in the async
        # case, to only end the exit call when the future is completed).
        maybe_connection = connect(connection, appd_exit_call=exit_call, *args, **kwargs)
        self.end_exit_call(exit_call, maybe_connection)
        return maybe_connection

    def _cursor(self, cursor, connection, *args, **kwargs):
        cursor_instance = cursor(connection, appd_exit_call=None, *args, **kwargs)
        with self.log_exceptions():
            self.cursor_interceptor(self.agent, type(cursor_instance)).attach(['execute', 'executemany'],
                                                                              patched_method_name='_execute')
        return cursor_instance

    @abc.abstractmethod
    def get_backend_properties(self, connection, *args, **kwargs):
        """Return a tuple of (host, port, database, vendor) for this connection.

        The parameters passed to this function are the same as those passed to
        the intercepted `connect` function.

        WARNING: `connection` may not have been initialized when this
        function is called; be careful.

        """
        pass
