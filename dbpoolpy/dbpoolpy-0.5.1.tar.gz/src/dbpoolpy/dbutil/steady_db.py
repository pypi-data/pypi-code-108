"""SteadyDB - hardened DB-API 2 connections.
基于任意DB-API 2兼容的数据库接口模块实现与数据库的稳定连接。
当连接关闭或数据库连接丢失或连接的使用次数超过可选的使用限制时，连接将透明地重新打开。
当因为失去了连接而无法执行数据库操作时，数据库游标也会透明地重新打开。
只有在执行后连接丢失时，当已经从数据库中提取行时，才会给出一个错误，游标不会自动重新打开，
因为在这种情况下没有可靠的方法恢复游标的状态。通过begin()调用标记为处于事务中的连接也不会被静默替换。

数据库连接丢失的典型情况是由于维护原因关闭并重新启动数据库服务器或中间的防火墙。
在这种情况下，所有数据库连接都将变得不可用，即使数据库服务可能已经再次可用。

该模块提供的“steady”连接将使数据库连接立即可用。

这种方法会产生一个稳定的数据库连接，PooledDB或PersistentDB可以使用它在线程环
境(如“Webware for Python”的应用服务器)中创建到数据库的池连接或持久连接。

但是请注意，连接本身可能不是线程安全的(取决于所使用的DB-API模块)。

用法:
    import pgdb  # import used DB-API 2 module
    from dbutils.steady_db import connect
    db = connect(pgdb, 10000, ["set datestyle to german"],
        host=..., database=..., user=..., ...)
    ...
    cursor = db.cursor()
    ...
    cursor.execute('select ...')
    result = cursor.fetchall()
    ...
    cursor.close()
    ...
    db.close()

"""

import sys
from dbpoolpy.dbconnect.simple import SimpleConnection

baseint = int


class SteadyDBError(Exception):
    """General SteadyDB error."""


class InvalidCursor(SteadyDBError):
    """Database cursor is invalid."""


def connect(
        engine, maxusage=None, setsession=None,
        failures=None, ping=1, closeable=True, *args, **kwargs):
    """基于DB-API 2模块的稳定连接。
    engine: 可以是返回新的符合DB-API 2的连接对象的任意函数，也可以是符合DB-API 2的数据库模块
    maxusage: 底层DB-API 2连接的最大使用限制(数据库操作的数量，0或None意味着无限制的使用)
              callproc()、execute()和executemany()计数为一个操作。当达到限制时，连接将自动复位。
    setsession: 一个可选的SQL命令列表，可以用来准备会话，
                例如["set datestyle to german"， "set time zone mez"]
    failures: 如果默认值(OperationalError, InternalError)不够充分，
              则应应用故障转移机制的可选异常类或异常类的元组
    ping: 使用ping()确定何时应该检查连接
         (0 = None = never, 1 = default = when _ping_check()被调用，
         2 =每当创建游标时，4 =当执行查询时，
         7 = always，以及这些值的所有其他位组合)
    closeable: 如果将此设置为false，则关闭连接将被静默忽略，但默认情况下可以关闭连接
    args, kwargs: 应该传递给引擎函数或DB-API 2模块的连接构造函数的参数
    """
    return SteadyDBConnection(
        engine, maxusage, setsession,
        failures, ping, closeable, *args, **kwargs)


class SteadyDBConnection(SimpleConnection):
    """基于DB-API 2模块的稳定连接。"""

    def __init__(
            self, engine, maxusage=None, setsession=None,
            failures=None, ping=1, closeable=True, *args, **kwargs):
        # 连接存储位置
        self._conn = None
        self._closed = True
        # 适当的初始化连接器
        try:
            self._engine = engine.connect
            self._dbapi = engine
        except AttributeError:
            # try finding the DB-API 2 module via the connection engine
            self._engine = engine
            try:
                self._dbapi = engine.dbapi
            except AttributeError:
                try:
                    self._dbapi = sys.modules[engine.__module__]
                    if self._dbapi.connect != engine:
                        raise AttributeError
                except (AttributeError, KeyError):
                    self._dbapi = None
        try:
            self._threadsafety = engine.threadsafety
        except AttributeError:
            try:
                self._threadsafety = self._dbapi.threadsafety
            except AttributeError:
                self._threadsafety = None
        if not callable(self._engine):
            raise TypeError("%r is not a connection provider." % (engine,))
        if maxusage is None:
            maxusage = 0
        if not isinstance(maxusage, baseint):
            raise TypeError("'maxusage' must be an integer value.")
        self._maxusage = maxusage
        self._setsession_sql = setsession
        if failures is not None and not isinstance(
                failures, tuple) and not issubclass(failures, Exception):
            raise TypeError("'failures' must be a tuple of exceptions.")
        self._failures = failures
        self._ping = ping if isinstance(ping, int) else 0
        self._closeable = closeable
        self._args, self._kwargs = args, kwargs
        self._store(self._create())
        self.conn_info()

    def __enter__(self):
        """Enter the runtime context for the connection object."""
        return self

    def __exit__(self, *exc):
        """Exit the runtime context for the connection object.

        This does not close the connection, but it ends a transaction.
        """
        if exc[0] is None and exc[1] is None and exc[2] is None:
            self.commit()
        else:
            self.rollback()

    def _create(self):
        """Create a new connection using the engine function."""
        conn = self._engine(*self._args, **self._kwargs)
        try:
            try:
                if self._dbapi.connect != self._engine:
                    raise AttributeError
            except AttributeError:
                # try finding the DB-API 2 module via the connection itself
                try:
                    mod = conn.__module__
                except AttributeError:
                    mod = None
                while mod:
                    try:
                        self._dbapi = sys.modules[mod]
                        if not callable(self._dbapi.connect):
                            raise AttributeError
                    except (AttributeError, KeyError):
                        pass
                    else:
                        break
                    i = mod.rfind('.')
                    if i < 0:
                        mod = None
                    else:
                        mod = mod[:i]
                else:
                    try:
                        mod = conn.OperationalError.__module__
                    except AttributeError:
                        mod = None
                    while mod:
                        try:
                            self._dbapi = sys.modules[mod]
                            if not callable(self._dbapi.connect):
                                raise AttributeError
                        except (AttributeError, KeyError):
                            pass
                        else:
                            break
                        i = mod.rfind('.')
                        if i < 0:
                            mod = None
                        else:
                            mod = mod[:i]
                    else:
                        self._dbapi = None
            if self._threadsafety is None:
                try:
                    self._threadsafety = self._dbapi.threadsafety
                except AttributeError:
                    try:
                        self._threadsafety = conn.threadsafety
                    except AttributeError:
                        pass
            if self._failures is None:
                try:
                    self._failures = (
                        self._dbapi.OperationalError,
                        self._dbapi.InternalError)
                except AttributeError:
                    try:
                        self._failures = (
                            self._engine.OperationalError,
                            self._engine.InternalError)
                    except AttributeError:
                        try:
                            self._failures = (
                                conn.OperationalError, conn.InternalError)
                        except AttributeError:
                            raise AttributeError(
                                "Could not determine failure exceptions"
                                " (please set failures or engine.dbapi).")
            if isinstance(self._failures, tuple):
                self._failure = self._failures[0]
            else:
                self._failure = self._failures
            self._setsession(conn)
        except Exception as error:
            # the database module could not be determined
            # or the session could not be prepared
            try:  # close the connection first
                conn.close()
            except Exception:
                pass
            raise error  # re-raise the original error again
        return conn

    def reconnect(self):
        '''重新连接'''
        self._close()
        self._store(self._create())
        self.conn_info()

    def _setsession(self, conn=None):
        """Execute the SQL commands for session preparation."""
        if conn is None:
            conn = self._conn
        if self._setsession_sql:
            cursor = conn.cursor()
            for sql in self._setsession_sql:
                cursor.execute(sql)
            cursor.close()

    def _store(self, conn):
        """Store a database connection for subsequent use."""
        self._conn = conn
        self._transaction = False
        self._closed = False
        self._usage = 0

    def _close(self):
        """Close the tough connection.

        You can always close a tough connection with this method
        and it will not complain if you close it more than once.
        """
        if not self._closed:
            try:
                self._conn.close()
            except Exception:
                pass
            self._transaction = False
            self._closed = True

    def _reset(self, force=False):
        """Reset a tough connection.

        Rollback if forced or the connection was in a transaction.
        """
        if not self._closed and (force or self._transaction):
            try:
                self.rollback()
            except Exception:
                pass

    def _ping_check(self, ping=1, reconnect=True):
        """使用ping()检查连接是否仍然活跃。
        如果底层连接不活跃，则将重新创建连接, 除非连接正处在事务中。
        """
        if ping & self._ping:
            try:  # if possible, ping the connection
                try:  # pass a reconnect=False flag if this is supported
                    alive = self._conn.ping(False)
                except TypeError:  # the reconnect flag is not supported
                    alive = self._conn.ping()
            except (AttributeError, IndexError, TypeError, ValueError):
                self._ping = 0  # ping() is not available
                alive = None
                reconnect = False
            except Exception:
                alive = False
            else:
                if alive is None:
                    alive = True
                if alive:
                    reconnect = False
            if reconnect and not self._transaction:
                try:  # try to reopen the connection
                    conn = self._create()
                except Exception:
                    pass
                else:
                    self._close()
                    self._store(conn)
                    alive = True
            return alive

    def dbapi(self):
        """Return the underlying DB-API 2 module of the connection."""
        if self._dbapi is None:
            raise AttributeError(
                "Could not determine DB-API 2 module"
                " (please set engine.dbapi).")
        return self._dbapi

    def threadsafety(self):
        """Return the thread safety level of the connection."""
        if self._threadsafety is None:
            if self._dbapi is None:
                raise AttributeError(
                    "Could not determine threadsafety"
                    " (please set engine.dbapi or engine.threadsafety).")
            return 0
        return self._threadsafety

    def close(self):
        """Close the tough connection.

        You are allowed to close a tough connection by default
        and it will not complain if you close it more than once.

        You can disallow closing connections by setting
        the closeable parameter to something false.  In this case,
        closing tough connections will be silently ignored.
        """
        if self._closeable:
            self._close()
        elif self._transaction:
            self._reset()

    def begin(self, *args, **kwargs):
        """Indicate the beginning of a transaction.

        During a transaction, connections won't be transparently
        replaced, and all errors will be raised to the application.

        If the underlying driver supports this method, it will be called
        with the given parameters (e.g. for distributed transactions).
        """
        self._transaction = True
        try:
            begin = self._conn.begin
        except AttributeError:
            pass
        else:
            begin(*args, **kwargs)

    def commit(self):
        """Commit any pending transaction."""
        self._transaction = False
        try:
            self._conn.commit()
        except self._failures as error:  # cannot commit
            try:  # try to reopen the connection
                conn = self._create()
            except Exception:
                pass
            else:
                self._close()
                self._store(conn)
            raise error  # re-raise the original error

    def rollback(self):
        """Rollback pending transaction."""
        self._transaction = False
        try:
            self._conn.rollback()
        except self._failures as error:  # cannot rollback
            try:  # try to reopen the connection
                conn = self._create()
            except Exception:
                pass
            else:
                self._close()
                self._store(conn)
            raise error  # re-raise the original error

    def cancel(self):
        """Cancel a long-running transaction.

        If the underlying driver supports this method, it will be called.
        """
        self._transaction = False
        try:
            cancel = self._conn.cancel
        except AttributeError:
            pass
        else:
            cancel()

    def ping(self, *args, **kwargs):
        """Ping connection."""
        return self._conn.ping(*args, **kwargs)

    def _cursor(self, *args, **kwargs):
        """A "tough" version of the method cursor()."""
        # The args and kwargs are not part of the standard,
        # but some database modules seem to use these.
        transaction = self._transaction
        if not transaction:
            self._ping_check(2)
        try:
            # check whether the connection has been used too often
            if (self._maxusage and self._usage >= self._maxusage and
                    not transaction):
                raise self._failure
            cursor = self._conn.cursor(*args, **kwargs)  # try to get a cursor
        except self._failures as error:  # error in getting cursor
            try:  # try to reopen the connection
                conn = self._create()
            except Exception:
                pass
            else:
                try:  # and try one more time to get a cursor
                    cursor = conn.cursor(*args, **kwargs)
                except Exception:
                    pass
                else:
                    self._close()
                    self._store(conn)
                    if transaction:
                        raise error  # re-raise the original error again
                    return cursor
                try:
                    conn.close()
                except Exception:
                    pass
            if transaction:
                self._transaction = False
            raise error  # re-raise the original error again
        return cursor

    def cursor(self, *args, **kwargs):
        """Return a new Cursor Object using the connection."""
        return SteadyDBCursor(self, *args, **kwargs)

    def __del__(self):
        """Delete the steady connection."""
        try:
            self._close()  # make sure the connection is closed
        except:  # builtin Exceptions might not exist any more
            pass


class SteadyDBCursor:
    """A "tough" version of DB-API 2 cursors."""

    def __init__(self, conn, *args, **kwargs):
        """Create a "tough" DB-API 2 cursor."""
        # basic initialization to make finalizer work
        self._cursor = None
        self._closed = True
        # proper initialization of the cursor
        self._conn = conn
        self._args, self._kwargs = args, kwargs
        self._clearsizes()
        try:
            self._cursor = conn._cursor(*args, **kwargs)
        except AttributeError:
            raise TypeError("%r is not a SteadyDBConnection." % (conn,))
        self._closed = False

    def __enter__(self):
        """Enter the runtime context for the cursor object."""
        return self

    def __exit__(self, *exc):
        """Exit the runtime context for the cursor object."""
        self.close()

    def setinputsizes(self, sizes):
        """Store input sizes in case cursor needs to be reopened."""
        self._inputsizes = sizes

    def setoutputsize(self, size, column=None):
        """Store output sizes in case cursor needs to be reopened."""
        self._outputsizes[column] = size

    def _clearsizes(self):
        """Clear stored input and output sizes."""
        self._inputsizes = []
        self._outputsizes = {}

    def _setsizes(self, cursor=None):
        """Set stored input and output sizes for cursor execution."""
        if cursor is None:
            cursor = self._cursor
        if self._inputsizes:
            cursor.setinputsizes(self._inputsizes)
        for column, size in self._outputsizes.items():
            if column is None:
                cursor.setoutputsize(size)
            else:
                cursor.setoutputsize(size, column)

    def close(self):
        """Close the tough cursor.

        It will not complain if you close it more than once.
        """
        if not self._closed:
            try:
                self._cursor.close()
            except Exception:
                pass
            self._closed = True

    def _get_tough_method(self, name):
        """Return a "tough" version of the given cursor method."""
        def tough_method(*args, **kwargs):
            execute = name.startswith('execute')
            conn = self._conn
            transaction = conn._transaction
            if not transaction:
                conn._ping_check(4)
            try:
                # check whether the connection has been used too often
                if (conn._maxusage and conn._usage >= conn._maxusage and
                        not transaction):
                    raise conn._failure
                if execute:
                    self._setsizes()
                method = getattr(self._cursor, name)
                result = method(*args, **kwargs)  # try to execute
                if execute:
                    self._clearsizes()
            except conn._failures as error:  # execution error
                if not transaction:
                    try:
                        cursor2 = conn._cursor(
                            *self._args, **self._kwargs)  # open new cursor
                    except Exception:
                        pass
                    else:
                        try:  # and try one more time to execute
                            if execute:
                                self._setsizes(cursor2)
                            method = getattr(cursor2, name)
                            result = method(*args, **kwargs)
                            if execute:
                                self._clearsizes()
                        except Exception:
                            pass
                        else:
                            self.close()
                            self._cursor = cursor2
                            conn._usage += 1
                            return result
                        try:
                            cursor2.close()
                        except Exception:
                            pass
                try:  # try to reopen the connection
                    conn2 = conn._create()
                except Exception:
                    pass
                else:
                    try:
                        cursor2 = conn2.cursor(
                            *self._args, **self._kwargs)  # open new cursor
                    except Exception:
                        pass
                    else:
                        if transaction:
                            self.close()
                            conn._close()
                            conn._store(conn2)
                            self._cursor = cursor2
                            raise error  # raise the original error again
                        error2 = None
                        try:  # try one more time to execute
                            if execute:
                                self._setsizes(cursor2)
                            method2 = getattr(cursor2, name)
                            result = method2(*args, **kwargs)
                            if execute:
                                self._clearsizes()
                        except error.__class__:  # same execution error
                            use2 = False
                            error2 = error
                        except Exception as error:  # other execution errors
                            use2 = True
                            error2 = error
                        else:
                            use2 = True
                        if use2:
                            self.close()
                            conn._close()
                            conn._store(conn2)
                            self._cursor = cursor2
                            conn._usage += 1
                            if error2:
                                raise error2  # raise the other error
                            return result
                        try:
                            cursor2.close()
                        except Exception:
                            pass
                    try:
                        conn2.close()
                    except Exception:
                        pass
                if transaction:
                    self._transaction = False
                raise error  # re-raise the original error again
            else:
                conn._usage += 1
                return result
        return tough_method

    def __getattr__(self, name):
        """Inherit methods and attributes of underlying cursor."""
        if self._cursor:
            if name.startswith(('execute', 'call')):
                # make execution methods "tough"
                return self._get_tough_method(name)
            else:
                return getattr(self._cursor, name)
        else:
            raise InvalidCursor

    def __del__(self):
        """Delete the steady cursor."""
        try:
            self.close()  # make sure the cursor is closed
        except:  # builtin Exceptions might not exist any more
            pass
