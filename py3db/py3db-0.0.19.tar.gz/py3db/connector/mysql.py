# @Time : 2021/4/23 10:04 
# @File : mysql.py.py 
# @Email: 1727949032@qq.com
# @Software: PyCharm
__author__ = "GanJanWen"

# -*- coding:utf-8 -*-

from py3db.Connection import Connection
from pymysql import connect


class Mysql(Connection):

    def __init__(self, config: dict = {}):
        self.config = config
        self.db = connect(
            host=self.config["host"],
            user=self.config['username'],
            password=self.config['password'],
            database=self.config["database"]
        )

    def query(self, sql, bind: tuple = ()) -> tuple:
        if bind:
            sql = sql % bind
        cursor = self.db.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        return results

    def execute(self, sql: str, bind: list = []):
        if bind:
            sql = sql % bind
        cursor = self.db.cursor()
        try:
            cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print(str(e))
            self.db.rollback()


if __name__ == '__main__':
    mysql = Mysql()
    mysql.connect()
