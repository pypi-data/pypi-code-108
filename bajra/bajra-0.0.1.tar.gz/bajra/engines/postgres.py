from psycopg2 import connect as psycopg2_connect
from psycopg2.extras import RealDictCursor

from .base import EngineBase


class PostgreSQLEngine(EngineBase):
    def __init__(self, dsn=None, host=None, port=5432,
                 user=None, password=None, database=None, **kwargs):
        self._params = {
            'cursor_factory': RealDictCursor,
            **kwargs
        }
        self._dsn = dsn
        if dsn is None:
             self._dsn = "postgresql://{}:{}@{}:{}/{}".format(
                user, password, host, port, database
            )

        self._conn = self.connection()

    def connection(self):
        return psycopg2_connect(self._dsn, **self._params)

    def reset(self):
        self._conn = self.connection()

    def _fetch(self, query, params, operation):
        with self._conn.cursor() as cur:
            cur.execute(query, params)
            return getattr(cur, operation)()

    def execute(self, query, params=None):
        with self._conn.cursor() as cur:
            cur.execute(query, params)
            return {
                'lastrowid': cur.lastrowid,
                'rowcount': cur.rowcount,
                'rownumber': cur.rownumber,
            }

    def fetchall(self, query, params):
        return self._fetch(query, params, 'fetchall')

    def fetchone(self, query, params):
        return self._fetch(query, params, 'fetchone')

    def commit(self):
        self._conn.commit()

    def begin(self):
        self.execute("BEGIN")

    def rollback(self):
        self._conn.rollback()

    def mogrify(self, query, params):
        with self._conn.cursor() as cur:
            return cur.mogrify(query, params).decode()

    def close(self):
        self._conn.close()