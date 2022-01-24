'''
:Author: ChenXiaolei
:Date: 2020-03-14 16:12:44
:LastEditTime: 2020-03-19 15:37:32
:LastEditors: ChenXiaolei
:Description: mysql helper
'''
# -*- coding: utf-8 -*-
import pymysql
from DBUtils.PooledDB import PooledDB
import traceback
from seven_framework import config, log, json


class MySQLHelper(object):
    # 对MySQLdb常用函数进行封装的类
    _conn = None
    _cur = None
    _log_sql = None

    def __init__(self, dbconfig):
        """
        :Description: mysql 操作类初始化
        :param dbconfig: 连接字符串
        :last_editors: ChenXiaolei
        """
        self.POOL = PooledDB(
            creator=pymysql,  # 使用链接数据库的模块
            maxconnections=0,  # 连接池允许的最大连接数，0和None表示不限制连接数
            mincached=0,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
            maxcached=0,  # 链接池中最多闲置的链接，0和None不限制
            maxshared=0,  # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，因为pymysql和MySQLdb等模块的 threadsafety都为1，所有值无论设置为多少，_maxcached永远为0，所以永远是所有链接都共享。
            blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
            maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
            setsession=[],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
            ping=0,
            # ping MySQL服务端，检查是否服务可用。# 如：0 = None = never, 1 = default = whenever it is requested, 2 = when a cursor is created, 4 = when a query is executed, 7 = always
            host=dbconfig['host'],
            port=dbconfig['port'],
            user=dbconfig['user'],
            passwd=dbconfig['passwd'],
            db=dbconfig['db'],
            charset=dbconfig['charset'])

        try:
            if not hasattr(self, "context") or not self.context:
                self._log_sql = log.Logger.get_logger_by_name("log_sql")
        except:
            pass

    def _add_sql_log(self, log):
        """
        :description: 添加日志
        :param log:日志内容
        :return action_mode: 执行模式
        :last_editors: ChenXiaolei
        """
        try:
            if type(log) == int:
                log = str(log)
            elif type(log) != str:
                log = json.JsonHelper.json_dumps(log)

            self.sql_log_dict["result"] = log
            log_msg = json.JsonHelper.json_dumps(self.sql_log_dict)
            # 如果有handler上下文,则使用链路日志记录
            if hasattr(self, "context") and self.context:
                self.context.logging_link_sql(log_msg)
            elif hasattr(self, "_log_sql") and self._log_sql:
                self._log_sql.info(log_msg)
        except:
            print(traceback.print_exc())
            pass

    def query(self, sql, params=None):
        """
        :Description: 执行 SELECT 语句
        :param sql: 查询语句
        :param params: 参数值
        :return: 查询结果
        :last_editors: ChenXiaolei
        """
        # 执行 SELECT 语句
        self._execute(sql, params)
        record_list = self._cur.fetchall()
        self.close()
        self._add_sql_log(record_list)
        return record_list

    def update(self, sql, params=None):
        """
        :Description: 执行 UPDATE 操作
        :param sql: 查询语句
        :param params: 参数值
        :return: 执行结果
        :last_editors: ChenXiaolei
        """
        self._execute(sql, params)
        self._conn.commit()
        row_count = self._cur.rowcount
        self.close()
        self._add_sql_log(row_count)
        return row_count

    def delete(self, sql, params=None):
        """
        :Description: 执行 Delete 操作
        :param sql: 查询语句
        :param params: 参数值
        :return: 执行结果
        :last_editors: ChenXiaolei
        """
        self._execute(sql, params)
        self._conn.commit()
        row_count = self._cur.rowcount
        self.close()
        self._add_sql_log(row_count)
        return row_count

    def insert(self, sql, params=None, return_increment_primary=True):
        """
        :Description: 执行 INSERT 语句
        :param sql: 数据insert语句
        :param return_increment_id: true=返回自增ID false=返回影响行数
        :return: 如主键为自增长int，则返回新生成的ID
        :last_editors: ChenXiaolei
        """
        # 执行 INSERT 语句。如主键为自增长int，则返回新生成的ID
        self._execute(sql, params)
        self._conn.commit()
        result = 0
        if return_increment_primary:
            result = self._cur._result.insert_id
        else:
            result = self._cur._result.affected_rows
        self.close()
        self._add_sql_log(result)
        return result

    def _execute(self, sql, params=None):
        try:
            sql_log_dict = {}
            sql_log_dict["sql"] = sql
            sql_log_dict["params"] = params if type(
                params) == str else json.JsonHelper.json_dumps(params)
            self.sql_log_dict = sql_log_dict
        except:
            print(traceback.print_exc())
            pass

        self.connection()

        if params != None and type(params) == int:
            params = [params]

        try:
            self._cur = self._conn.cursor(pymysql.cursors.DictCursor)
            if not params:
                self._cur.execute(sql)
            else:
                self._cur.execute(sql, params)
            return self._cur
        except Exception as e:
            print(traceback.print_exc())
            raise Exception("mysql execute error:" + str(e) + " sql:" +
                            str(sql) + " 参数:" + str(params))

    def transaction_execute(self, sql_list, return_detail_tuple=False):
        """
        :Description: 事务提交
        :param sql_list: sql字符串数组
        :param return_detail_tuple: 返回详细的元组信息
        :return: 执行成功返回 True   失败 False
        :last_editors: ChenXiaolei
        """
        try:
            self.connection()
            self._cur = self._conn.cursor(pymysql.cursors.DictCursor)

            for item in sql_list:
                if type(item) == str:
                    self._cur.execute(item)
                elif type(item) == dict:
                    sql = item["sql"]
                    params = item["params"]
                    self._cur.execute(sql, params)
        except Exception as e:
            print(e)
            self._conn.rollback  # 事务回滚
            # raise Exception("执行事务ERROR:" + str(e) + " SQL：" + str(sql))
            if return_detail_tuple:
                return (False, f"MYSQL事务执行失败并进行回滚,执行SQL:{sql},异常:{traceback.format_exc()}")
            return False
        else:
            self._conn.commit()  # 事务提交
            self._cur.close()
            self._conn.close()
        if return_detail_tuple:
            return (True, "")
        return True

    def fetch_all_rows(self, sql, params=None):
        """
        :Description: 返回结果列表
        :param sql: 查询语句
        :param params: 参数值
        :return: 结果列表
        :last_editors: ChenXiaolei
        """
        self._execute(sql, params)
        record_list = self._cur.fetchall()
        self.close()
        self._add_sql_log(record_list)
        return record_list

    def fetch_limit_rows(self, sql, params=None, current_page=1, list_rows=20):
        """
        :Description: 分页查询结果
        :param sql: 查询语句
        :param params: 参数值
        :return: 分页查询结果
        :last_editors: ChenXiaolei
        """
        count = self.get_row_count(sql, params)
        pages = count / list_rows
        pages = pages + 1 if not count % list_rows == 0 else pages
        if (pages == 0):
            pages = 1
        if (current_page < 1):
            current_page = 1
        if (current_page > pages):
            current_page = pages
        start = (current_page - 1) * list_rows
        end = list_rows
        previous_page = current_page - 1 if current_page > 1 else 1
        next_page = current_page + \
            1 if current_page < int(pages) else int(pages)
        limit_sql = sql + " limit " + str(int(start)) + "," + str(int(end))
        result = {}
        result["list"] = self.fetch_all_rows(limit_sql, params)
        result["page"] = {
            "prev": previous_page,
            "next": next_page,
            "current": current_page,
            "pages": int(pages),
            "total": count,
        }
        self._add_sql_log(result)
        return result

    def fetch_one_row(self, sql, params=None):
        """
        :Description: 返回一行结果，然后游标指向下一行。到达最后一行以后，返回None
        :param sql: 查询语句
        :param params: 参数值
        :return: 返回一行结果
        :last_editors: ChenXiaolei
        """
        self._execute(sql, params)
        record = self._cur.fetchone()
        self.close()
        self._add_sql_log(record)
        return record

    def get_row_count(self, sql, params=None):
        """
        :Description: 获取结果行数
        :param sql: 查询语句
        :param params: 参数值
        :return: 返回查询行数
        :last_editors: ChenXiaolei
        """
        self._execute(sql, params)
        row_count = self._cur.rowcount
        self.close()
        self._add_sql_log(row_count)
        return row_count

    def fetch_and_commit(self, sql, params=None):
        """
        :Description: 执行并commit提交
        :param sql: 查询语句
        :param params: 参数值
        :return: 返回第一行结果
        :last_editors: ChenXiaolei
        """
        self._execute(sql, params)
        record = self._cur.fetchone()
        self._conn.commit()
        self.close()
        self._add_sql_log(record)
        return record

    def commit(self):
        """
        :Description: 数据库commit操作
        :last_editors: ChenXiaolei
        """
        # 数据库commit操作
        self._conn.commit()

    def rollback(self):
        """
        :Description: 执行数据库回滚操作
        :last_editors: ChenXiaolei
        """
        # 数据库回滚操作'
        self._conn.rollback()

    def connection(self):
        self._conn = self.POOL.connection()

    def __del__(self):
        """
        :Description: 执行释放资源（系统GC自动调用）
        :last_editors: ChenXiaolei
        """
        # 释放资源（系统GC自动调用）
        try:
            self._cur.close()
            self._conn.close()
        except:
            pass

    def close(self):
        """
        :Description: 执行关闭数据库连接
        :last_editors: ChenXiaolei
        """
        # 关闭数据库连接
        self.__del__()


class DbTransaction(object):
    """
    :Description: 数据库事务执行类
    :last_editors: ChenXiaolei
    """

    def __init__(self, db_config_dict=None, db=None):
        self.transaction_list = []
        self.is_transaction = False

        if db:
            self.db = db
        elif db_config_dict and type(db_config_dict) == dict:
            self.db = MySQLHelper(db_config_dict)
        else:
            raise Exception("db not configured!")

    def begin_transaction(self):
        """
        :Description: 启动事务
        :return: 成功True  失败False
        :last_editors: ChenXiaolei
        """
        self.transaction_list = []
        self.is_transaction = True
        return True

    def commit_transaction(self, return_detail_tuple=False):
        """
        :Description: 提交事务
        :param return_detail_tuple: 返回详细的元组信息 True=tuple(Ture/False,str(异常信息,正常为空字符串))
        :return: 成功True  失败False
        :last_editors: ChenXiaolei
        """
        if not hasattr(self, "transaction_list"):
            return False

        sql_list = self.transaction_list

        self.is_transaction = False
        delattr(self, "transaction_list")

        return self.db.transaction_execute(sql_list, return_detail_tuple)

    def rollback_transaction(self):
        """
        :Description: 撤销事务
        :return: 成功True  失败False
        :last_editors: ChenXiaolei
        """
        self.is_transaction = False
        delattr(self, "transaction_list")

        return True

    def get_transaction_sql(self, rollback_transaction=True):
        """
        :Description: 获取事务需执行语句
        :param is_end: 是否结束事务
        :return: sql字符串
        :last_editors: ChenXiaolei
        """
        sql_list = self.transaction_list
        if not sql_list or len(sql_list) == 0:
            return ""
        sql_str = ''
        for sql in sql_list:
            if isinstance(sql['params'], list) or isinstance(
                    sql['params'], tuple):
                if isinstance(sql['params'], tuple):
                    sql['params'] = list(sql['params'])
                for params_num in range(len(sql['params'])):
                    if isinstance(sql['params'][params_num], str):
                        sql['params'][params_num] = '"' + \
                            sql['params'][params_num] + '"'
                sql_str += sql['sql'] % tuple(sql['params'])
            elif isinstance(sql['params'], str):
                sql['params'] = '"' + sql['params'] + '"'
                sql_str += sql['sql'] % sql['params']
            else:
                sql_str += sql['sql'] % sql['params']

        if rollback_transaction:
            self.rollback_transaction()
        return sql_str
