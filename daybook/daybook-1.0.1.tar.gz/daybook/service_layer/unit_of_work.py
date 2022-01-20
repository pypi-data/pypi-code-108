import os
from mysql.connector import MySQLConnection
from abc import ABC
from abc import abstractmethod
import sqlite3

from daybook.adapters.repository import (
    AbstractReadingLogRepository,
    SqlRepository,
    SQLiteRepository,
)
from dotenv import load_dotenv


class AbstractUnitOfWork(ABC):
    session = None
    reading_logs: AbstractReadingLogRepository

    def __enter__(self):
        pass

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    def rollback(self):
        self._rollback()

    @abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abstractmethod
    def _rollback(self):
        raise NotImplementedError

    def collect_new_events(self):
        for reading_log in self.reading_logs.seen:
            while reading_log.events:
                yield reading_log.events.pop(0)


class MySqlUnitOfWork(AbstractUnitOfWork):
    def __init__(self) -> None:
        load_dotenv(".env.development")
        self.conn = MySQLConnection(
            user=os.environ.get("MYSQL_USER"),
            password=os.environ.get("MYSQL_PASSWORD"),
            host=os.environ.get("MYSQL_HOST"),
            port=3306,
            database=os.environ.get("MYSQL_DATABASE"),
        )
        self.reading_logs = None

    def __enter__(self):
        self.conn.connect()
        self.session = self.conn.cursor(buffered=True)
        self.reading_logs = SqlRepository(self.session)

    def __exit__(self, *args):
        self.session.close()
        self.conn.close()

    def _commit(self):
        self.conn.commit()

    def _rollback(self):
        self.conn.rollback()


class SQLiteUnitOfWork(AbstractUnitOfWork):
    def __init__(self) -> None:
        self.reading_logs = None

    def __enter__(self):
        self.conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "daybook.db"))
        self.session = self.conn.cursor()
        self.reading_logs = SQLiteRepository(self.session)

    def __exit__(self, *args):
        self.conn.close()

    def _commit(self):
        self.conn.commit()

    def _rollback(self):
        self.conn.rollback()
