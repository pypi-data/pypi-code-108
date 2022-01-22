from dbpoolpy.utils import timesql
from dbpoolpy.dbhelper import DBHelper

class MysqlHelper(DBHelper):
    """Mysql帮助类"""

    # 执行插入命令
    # @timesql
    # def execute_insert(self, sql, args=None, isdict=True):
    #     '''执行单个sql命令'''
    #     with self.connect_cur() as cur:
    #         if args:
    #             if not isinstance(args, (dict, tuple, list)):
    #                 args = tuple([args])
    #             ret = cur.execute(sql, args)
    #         else:
    #             ret = cur.execute(sql)
    #         if cur.lastrowid:
    #             return cur.lastrowid
    #         return ret
