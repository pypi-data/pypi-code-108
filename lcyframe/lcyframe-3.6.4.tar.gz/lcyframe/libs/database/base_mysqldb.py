# #!/usr/bin/env python
# #encoding=utf-8
# try:
#     import MySQLdb
# except:
#     MySQLdb = None
#
# import time
#
#
# class MysqlDb(object):
#     """
#        eg:
#         db = dbpool.db
#         sql = "insert into user(userid, user, password) values(%d,%s,%s)";
#         try:
#             #这里可以执行几个sql
#             db.execute(sql,[1,'lcj','123'])
#             db.commit()
#         except:
#             print('error!')
#
#     """
#     max_idle_time = 3600 * 7
#     conf = {
#         "host": "127.0.0.1",
#         "port": 3306,
#         "user": "root",
#         "charset": "utf8"
#     }
#     def __init__(self, **kwargs):
#         self.conf.update(kwargs)
#         self.__reconnect()
#
#     def __del__(self):
#         self.close()
#
#     def insert(self, sql, args=None, commit=False):
#         """
#         commit=True 插入成功后马上提交，其他连接会看到最新的数据,已提交后不可用回滚
#         :param sql:
#         :param args:
#         :return:
#         """
#         return self.execute(sql, args, commit=commit)
#
#     def find_one(self, sql, args=None):
#         """
#         返回一行数据
#         :param sql:
#         :param args:
#         :return:
#         """
#         return self.execute(sql, args, exec_type="one")
#
#     def find(self, sql, args=None):
#         """
#         查询多条
#         :param sql:
#         :param args:
#         :return:
#         """
#         return self.execute(sql, args, exec_type="many")
#
#     def remove(self, sql, args=None, commit=False):
#         """
#
#         :param sql:
#         :param args:
#         :return:
#         """
#         return self.execute(sql, args, commit=commit)
#
#     def delete(self, sql, args=None, commit=False):
#         """
#
#         :param sql:
#         :param args:
#         :return:
#         """
#         return self.execute(sql, args, commit=commit)
#
#     def update(self, sql, args=None, commit=False):
#         """
#
#         :param sql:
#         :param args:
#         :return:
#         """
#         return self.execute(sql, args, commit=commit)
#
#     def cursor(self):
#         """
#
#         :return:
#         """
#         return self.__cursor()
#
#     def execute(self, sql, args=None, exec_type="", commit=False):
#         """
#         commit=True 插入成功后马上提交，其他连接会看到最新的数据,已提交后不可用回滚
#
#         :param sql:
#         :param args:
#         :return:
#         """
#         rows = None
#         cursor = self.__cursor()
#         try:
#             cursor.execute(sql, args)
#             if exec_type == "one":
#                 rows = cursor.fetchone()
#             elif exec_type == "many":
#                 rows = cursor.fetchall()
#             else:
#                 pass
#         except MySQLdb.OperationalError:
#             self.rollback()
#             self.close()
#             cursor.close()
#             raise
#         finally:
#             if commit == True:
#                 self.commit()
#             cursor.close()
#             return self.__return_string(rows)
#
#     def executemany(self, sql, args=None, commit=False):
#         cursor = self.__cursor()
#         try:
#             cursor.executemany(sql, args)
#         except MySQLdb.OperationalError:
#             self.rollback()
#             self.close()
#             cursor.close()
#             raise
#         else:
#             cursor.close()
#             rows = cursor.fetchall()
#             if commit == True:
#                 self.commit()
#             return self.__return_string(rows)
#
#     def rollback(self):
#         """
#         回滚当前所有操作且没有被提交的数据，提交之后无法在回滚
#         :return:
#         """
#         self.conn.rollback()
#
#     def close(self):
#         if getattr(self, "conn", None) is not None:
#             self.conn.close()
#             self.conn = None
#
#     def commit(self):
#         """
#         提交前，当前游标链接的事务内可见，提交后替他链接的事务开可见，已提交后的数据没办法回滚
#         :return:
#         """
#         self.conn.commit()
#
#     def __reconnect(self):
#         self.last_use_time = time.time()
#         self.close()
#         self.conn = MySQLdb.connect(host=self.conf["host"],
#                                     user=self.conf["user"],
#                                     passwd=self.conf["passwd"],
#                                     db=self.conf["database"],
#                                     charset=self.conf["charset"])
#         self.conn.autocommit(False)
#
#     def __ensure_connected(self):
#         if self.conn is None or (time.time() - self.last_use_time > self.max_idle_time):
#             self.__reconnect()
#         self.last_use_time = time.time()
#
#     def __cursor(self):
#         """每次生成cursor 先确保连接"""
#         self.__ensure_connected()
#         return self.conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
#
#     def __return_string(self, rows):
#         docs = []
#         if type(rows) is dict:
#             t = dict
#             rows = [rows]
#         else:
#             t = list
#
#         if not rows:
#             return docs
#
#         for row in rows:
#             for k, v in row.items():
#                 if type(v) in [unicode]:
#                     v = v.encode("utf-8")
#                 row[k] = v
#             docs.append(row)
#
#         return docs[0] if t == dict else docs
