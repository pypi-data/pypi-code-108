from dbpoolpy.utils import timesql
from dbpoolpy.dbhelper import DBHelper

class PostgresqlHelper(DBHelper):
    """Postgresql帮助类"""

    # 执行插入命令
    # @timesql
    # def execute_insert(self, sql, args=None, isdict=True):
    #     '''执行单个sql命令'''
    #     with self.connect_cur() as cur:
    #         lower_sql = str(sql).lower()
    #         if lower_sql.find('returning') == -1:
    #             sql = '%s returning *' % sql
    #         if args:
    #             if not isinstance(args, (dict, tuple, list)):
    #                 args = tuple([args])
    #             ret = cur.execute(sql, args)
    #         else:
    #             ret = cur.execute(sql)
    #         res = cur.fetchone()
    #         res = self.format_timestamp(res, cur)
    #         if res and isdict:
    #             xkeys = [i[0] for i in cur.description]
    #             return dict(zip(xkeys, res))
    #         else:
    #             return res

