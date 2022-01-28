import sqlite3
import json
from os.path import abspath
from py3db import log


class Sqlite:
    @classmethod
    def get_db_config(cls):
        sqlite_config_path = "%s/../../config/sqlite.json" % abspath(__file__)
        return json.load(fp=open(
            sqlite_config_path,
            "r",
            encoding="utf-8"
        ))

    @classmethod
    def set_db_config(cls, file_name=None, first=None):
        sqlite_config = cls.get_db_config()
        config_dict = {
            "file_name": file_name,
            "first": first
        }
        for key, value in config_dict.items():
            if value:
                sqlite_config[key] = value
        cls.save_sqlite_config(cls, sqlite_config)

    def __init__(self):
        self.sqlite_config = self.get_db_config()
        self.file_name = self.sqlite_config.get('file_name')
        self.log = log.Log("./book.log")
        self.conn = None
        if self.sqlite_config["first"]:
            self.create_table()
            self.sqlite_config["first"] = False
            self.save_sqlite_config(self.sqlite_config)

    def create_connect(self):
        conn = sqlite3.connect(self.file_name)
        return conn

    def query(self, sql, other_message=None):
        print(sql)
        self.conn = self.create_connect()
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            self.log.error("{} {}".format(
                e,
                other_message
            ))
        finally:
            cursor.close()
            self.conn.close()

    def create_table(self):
        book_sql_file = "%s/../../sql/sqlite/book.sql" % abspath(__file__)
        chapter_sql_file = "%s/../../sql/sqlite/chapter.sql" % abspath(__file__)
        with open(book_sql_file, "r", encoding="utf-8") as fp:
            book_sql_list = fp.read().split(";")
        with open(chapter_sql_file, "r", encoding="utf-8") as fk:
            chapter_sql_list = fk.read().split(";")
            try:
                for book_sql in book_sql_list:
                    self.query(book_sql)
                self.log.info("成功创建book表")
            except Exception as e:
                print(e)
                self.log.error(e)
            try:
                for chapter_sql in chapter_sql_list:
                    self.query(chapter_sql)
                self.log.info("成功创建chapter表")
            except Exception as e:
                self.log.error(e)

    def save_sqlite_config(self, sqlite_config):
        sqlite_config_path = "%s/../../config/sqlite.json" % abspath(__file__)
        with open(sqlite_config_path, "w", encoding="utf-8") as fp:
            print(sqlite_config)
            json.dump(sqlite_config, fp, indent=4)

    def get_datas(self, sql):
        self.conn = self.create_connect()
        cursor = self.conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        self.conn.close()
        return results


if __name__ == "__main__":
    sqlite = Sqlite()
