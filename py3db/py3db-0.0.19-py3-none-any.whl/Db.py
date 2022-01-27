from abc import abstractmethod

from Connection import Connection
import json


class DB:
    _connection = None
    _config = dict()

    def __init__(self, config: dict = {}):
        with open("config/database.json", "r", encoding="utf-8") as fp:
            self._config = json.load(fp)
        if config:
            self._config = dict(self._config, **config)

    def connect(self, config: dict = {}):
        """
        :param config: dict
        :return: None
        """
        if not self._connection:
            config = dict(self._config, **config)
            self._connection = Connection.instance(config)

    def query(self, sql, bind: tuple = ()):
        return self._connection.query(sql, bind)

    def execute(self, sql, bind: tuple = ()):
        self._connection.execute(sql, bind)

    def __getattr__(self, name, *args):
        return getattr(self, "connect")

    def __str__(self):
        return "config:%s" % self._config


if __name__ == '__main__':
    db = DB()
    db.connect({
        "database": "sex"
    })
    db.execute("update book set type='垃圾' where book_id=1")

