import os
import pymysql
from RuirenyunLibrary.PublicLibrary import *


class MysqlDB(object):
    def __init__(self,config_path):
        self.model = load_yml(config_path)
        self.mysqldb = self.model["mysqldb"]
        # 打开数据库连接
        self.db = pymysql.connect(host=self.mysqldb["host"], user=self.mysqldb["username"], password=self.mysqldb["password"], database=self.mysqldb["database"],
                                  connect_timeout=30, read_timeout=30, write_timeout=30)
        # 使用cursor()方法获取操作游标
        self.cursor = self.db.cursor()

    def close(self):
        self.db.close()

    def execute(self, sql):
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 提交到数据库执行
            self.db.commit()
        except Exception as ee:
            logger.trace(ee)
            # 发生错误时回滚
            self.db.rollback()

    def fetchall(self):
        show = self.cursor.fetchall()
        debug(f"数据库命令回显:{show}")

    def fetchone(self):
        show = self.cursor.fetchone()
        debug(f"数据库命令回显:{show}")

    def fetchmany(self):
        show = self.cursor.fetchmany()
        debug(f"数据库命令回显:{show}")


if __name__ == '__main__':
    db = MysqlDB()
    sql = 'update z_user SET openid = "AnqCkQL0H7TzW8rf2FU9VudivJpx", WHERE phone = "18583285329";'
    db.execute(sql)
    db.close()
