# 依赖包
import pymysql
from pyocs.pyocs_exception import *

#这里是公共的数据库接口，请勿添加业务逻辑
class pyocsDataBase:
    class sql_server:
        def __init__(self, host, port, user, passwd, db):
            self.host = host
            self.port = port
            self.user = user
            self.passwd = passwd
            self.db = db

    _instance = None
    # Singleton pattern
    def __new__(cls, _sql_server, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(pyocsDataBase, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, _sql_server, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mydb = pymysql.connect(
            host=_sql_server.host,
            port=_sql_server.port,
            user=_sql_server.user,
            passwd=_sql_server.passwd,
            database=_sql_server.db,
        )
        self.myCursor = self.mydb.cursor()

    def get_primary_key_info(self, table_name, primary_key_name, primary_key_value):
        '''返回值为 primary_key_name = primary_key_value 的一行数据的tuple，包含primary_key_name 列
        table_name 表名
        primary_key_name 列名
        primary_key_value 关键字
        '''
        sql = "SELECT * FROM " + table_name + " WHERE " + primary_key_name + "='" + primary_key_value + "'"
        self.myCursor.execute(sql)
        results = self.myCursor.fetchall()
        if len(results) == 0:
            raise IndexError("找不到指定项目")
        if len(results) > 1:
            raise DataNoUniqueError("此项不唯一")
        return results[0]

    def get_value_of_key(self, table_name, primary_key_name, primary_key_value):
        '''返回值为 primary_key_name = primary_key_value 的一行数据的tuple，不包含primary_key_name 列
        table_name 表名
        primary_key_name 列名
        primary_key_value 关键字
        '''
        result = self.get_primary_key_info(table_name, primary_key_name, primary_key_value)
        return result[1:]
