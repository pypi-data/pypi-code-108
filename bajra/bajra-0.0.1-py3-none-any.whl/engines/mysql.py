from pymysql import connect as mysql_connect
from pymysql.cursors import DictCursor


from .base import EngineBase


class MySQLEngine(EngineBase):
    def __init__(self, user=None, password=None, db=None,
                 host="localhost", port=3306, **kwargs):
        self._params = {
            'user': user,
            'password': password,
            'db': db,
            'host': host,
            'port': port,
            'cursorclass': DictCursor,
            **kwargs
        }
        self._conn = self.connection()

    def connection(self):
        return mysql_connect(**self._params)

    def reset(self):
        self._conn = self.connection()

    def _fetch(self, query, params, operation):
        with self._conn.cursor() as cur:
            cur.execute(query, params)
            return getattr(cur, operation)()

    def execute(self, query, params):
        with self._conn.cursor() as cur:
            affected_rows = cur.execute(query, params)
            return {
                'lastrowid': None,
                'rowcount': None,
                'rownumber': affected_rows
            }

    def fetchone(self, query, params):
        return self._fetch(query, params, 'fetchone')

    def fetchall(self, query, params):
        return self._fetch(query, params, 'fetchall')

    def commit(self):
        self._conn.commit()

    def begin(self):
        self._conn.begin()

    def rollback(self):
        self._conn.rollback()

    def mogrify(self, query, params):
        with self._conn.cursor() as cur:
            return cur.mogrify(query, params)

    def close(self):
        self._conn.close()