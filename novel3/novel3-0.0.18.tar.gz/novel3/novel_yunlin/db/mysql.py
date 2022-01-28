from py3db import mysql, log
import json
from os.path import abspath


class Mysql:
    def __init__(self) -> None:
        self.mysql_config = self.get_db_config()
        self.ip = self.mysql_config["ip"]
        self.user = self.mysql_config["user_name"]
        self.password = self.mysql_config["password"]
        self.database = self.mysql_config["database"]
        self.mysql_config_path = None
        self.mysql = mysql.MySql(
            self.ip, self.user, self.password, self.database)
        self.log = log.Log("./book.log")
        if self.mysql_config["first"]:
            self.create_database()
            self.create_table()
            self.mysql_config["first"] = False
            self.save_mysql_config(self.mysql_config)

    @classmethod
    def get_db_config(cls):
        mysql_config_path = "%s/../../config/mysql.json" % abspath(__file__)
        return json.load(fp=open(
            mysql_config_path,
            "r",
            encoding="utf-8"
        ))

    @classmethod
    def set_db_config(cls, ip=None, user_name=None, password=None, database=None, first=None):
        mysql_config = cls.get_db_config()
        config_dict = {
            "ip": ip,
            "user_name": user_name,
            "password": password,
            "database": database,
            "first": first
        }
        for key, value in config_dict.items():
            mysql_config[key] = value if value else mysql_config[key]
        cls.save_mysql_config(cls, mysql_config)

    def create_database(self):
        database_sql = "create sex"
        self.mysql.operation_database(database_sql)

    def create_table(self):
        book_sql_file = "%s/../../sql/mysql/book.sql" % abspath(__file__)
        chapter_sql_file = "%s/../../sql/mysql/chapter.sql" % abspath(__file__)
        with open(book_sql_file, "r", encoding="utf-8") as fp:
            book_sql_list = fp.read().split(";")
        with open(chapter_sql_file, "r", encoding="utf-8") as fk:
            chapter_sql_list = fk.read().split(";")
            try:
                for book_sql in book_sql_list:
                    self.mysql.operation_database(book_sql)
                self.log.info("成功创建book表")
            except Exception as e:
                self.log.error(e)
            try:
                for chapter_sql in chapter_sql_list:
                    self.mysql.operation_database(chapter_sql)
                self.log.info("成功创建chapter表")
            except Exception as e:
                self.log.error(e)

    def save_mysql_config(self, mysql_config):
        mysql_config_path = "%s/../../config/mysql.json" % abspath(__file__)
        with open(mysql_config_path, "w", encoding="utf-8") as fp:
            json.dump(mysql_config, fp, indent=4)

    def query(self, sql, other_message=None):
        self.mysql.create_connect()
        self.mysql.operation_database(sql, other_message)
        self.mysql.close_connect()

    def get_datas(self, sql):
        self.mysql.create_connect()
        cursor = self.mysql.db.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        self.mysql.close_connect()
        return results
