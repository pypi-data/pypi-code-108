from contextlib import contextmanager
from dbpoolpy.dbhelper import DBHelper


class TestPool():
    def __init__(self):
        self._idle_cache = []
        self._idle_using = []
        self._maxconnections = 10

class SimpleConnection(DBHelper):

    type='simple_mysql'

    def __init__(self, engine, *args, **kwargs):
        self._conn = None
        self._name = 'simple'
        self.pool = TestPool()
        self._args, self._kwargs = args, kwargs
        try:
            self._engine = engine.connect
        except Exception as e:
            raise Exception('数据库连接器不可用')
        self._conn = self._engine(*self._args, **self._kwargs)
        # 记录连接的数据库信息
        self._server_id = None
        self._conn_id = 0
        self.conn_info()
        self._transaction = 0

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

    def conn_info(self):
        """获取数据库连接信息，便于问题追踪"""
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


    def cursor(self, *args, **kwargs):
        return self._conn.cursor(*args, **kwargs)

    def close(self):
        self._conn.close()

    def begin(self, *args, **kwargs):
        begin = self._conn.begin
        begin(*args, **kwargs)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def cancel(self):
        cancel = self._conn.cancel
        cancel()

    def ping(self, *args, **kwargs):
        return self._conn.ping(*args, **kwargs)

    def escape(self, s):
        return self._conn.escape_string(s)

    @contextmanager
    def connect_cur(self):
        cur = None
        try:
            cur = self.cursor()
            yield cur
            self.commit()
        except Exception as e:
            self.rollback()
            raise e
        finally:
            if cur is not None:
                cur.close()
