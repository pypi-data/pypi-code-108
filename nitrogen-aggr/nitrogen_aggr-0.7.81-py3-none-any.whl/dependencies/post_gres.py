"""
    This is the Postgres database helpers with connections and other sql related functions
    like insert.
"""

import psycopg2
from dependencies.logger import logger


class CadmiumPostGres:
    _cursor = None

    def __init__(self, host, dbname, user, password, port, auto_commit=False):
        self.create_connection(_host=host, _dbname=dbname, _user=user, _password=password, _port=port,
                               _auto_commit=auto_commit)
        self._log = logger()

    @classmethod
    def create_connection(cls, _host, _dbname, _user, _password, _port, _auto_commit):
        conn = psycopg2.connect(host=_host, dbname=_dbname, user=_user, password=_password, port=_port)
        conn.autocommit = _auto_commit
        cls._cursor = conn.cursor()

    def query_table(self, _query):
        try:
            self._cursor.execute(_query)
            result = self._cursor.fetchone()
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            self._log.error(f"post_gres.py: Query Error : {error}, query: {_query}")

    def query_table_fetchall(self, _query):
        try:
            self._cursor.execute(_query)
            result = self._cursor.fetchall()
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            self._log.error(f"post_gres.py: Query Error : {error}, query: {_query}")

    def execute_table(self, _query):
        try:
            self._cursor.execute(_query)
        except (Exception, psycopg2.DatabaseError) as error:
            self._log.error(f"post_gres.py: Execute Error : {error}, query: {_query}")

    def insert_into_table(self, table_name, columns_tuples, placeholders_tuple, values_tuple):
        query = f"INSERT INTO {table_name} {columns_tuples} VALUES {placeholders_tuple}"
        try:
            self._cursor.execute(query, values_tuple)
        except (Exception, psycopg2.DatabaseError) as error:
            self._log.error(f"post_gres.py: Insert Error : {error}, query: {query}")

    def close(self):
        self._cursor.close()

    @property
    def log(self):
        return self._log
