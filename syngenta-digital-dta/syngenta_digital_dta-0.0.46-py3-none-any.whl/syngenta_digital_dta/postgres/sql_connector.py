from functools import lru_cache

import psycopg2
from psycopg2.extras import RealDictCursor


class SQLConnector:
    def __init__(self, cls):
        self.endpoint = cls.endpoint
        self.database = cls.database
        self.table = cls.table
        self.user = cls.user
        self.password = cls.password
        self.port = cls.port
        self.autocommit = cls.autocommit
        self.connection = None

    @lru_cache(maxsize=128)
    def connect(self):
        try:
            if not self.connection:
                self.connection = psycopg2.connect(
                    dbname=self.database,
                    host=self.endpoint,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                )
            if self.autocommit:
                self.connection.set_session(autocommit=self.autocommit)
            return self.connection
        except Exception as error:
            print(error)
            raise error

    @lru_cache(maxsize=128)
    def cursor(self):
        return self.connection.cursor(cursor_factory=RealDictCursor)
