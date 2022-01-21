#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/1/6 10:04 下午
# @Author  : lance.txl
# @Site    : 
# @File    : db_utils.py
# @Software: PyCharm
import pymysql

class DBDao(object):
    def __init__(self):
        object.__init__(self)
    def set_params(self,host,user,password,database,charset='utf8'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.charset = charset
    def execute_select_sql(self, sql):
        print(sql)
        db = self.init_db()
        cursor = db.cursor()
        try:
            cursor.execute(sql)
            l = cursor.fetchall()
        except Exception as e:
            print(e)
            l = []
            cursor.close()
            db.close()
        else:
            cursor.close()
            db.close()
        return l

    def execute_insert_sql(self, sql):
        print(sql)
        db = self.init_db()
        cursor = db.cursor()
        try:
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            print("error")
            print(e)
            db.rollback()
            cursor.close()
            db.close()
        else:
            print("done")
            cursor.close()
            db.close()

    def init_db(self):
        db = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database, charset=self.charset)
        return db