# @Author: chunyang.xu
# @Email:  398745129@qq.com
# @Date:   2020-06-02 18:46:58
# @Last Modified time: 2022-01-20 10:00:10
# @github: https://github.com/longfengpili

# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import re
import pandas as pd
from tqdm import tqdm

from pydbapi.sql import SqlParse, SqlCompile
from pydbapi.conf import AUTO_RULES

import logging
dblogger = logging.getLogger(__name__)


class DBbase(object):

    def __init__(self, *args, **kwargs):
        pass

    def get_conn(self):
        pass

    def __execute_step(self, cursor, sql, ehandling='raise'):
        '''[summary]

        [description]
            在conn中执行单步sql
        Arguments:
            cursor {[cursor]} -- [游标]
            sql {[str]} -- [sql]

        Raises:
            ValueError -- [sql执行错误原因及SQL]
        '''
        sql = re.sub(r'\s{2,}', '\n', sql)
        try:
            cursor.execute(sql)
        except Exception as e:
            dblogger.error(f"【Error】{e}, 【error Sql】: {sql}")

            if ehandling == 'raise':
                raise ValueError(f"【Error】:{e}【Sql】:{sql}")

    def cur_results(self, cursor, count):
        results = cursor.fetchmany(count) if count else cursor.fetchall()
        results = list(results) if results else []
        return results

    def cur_columns(self, cursor):
        desc = cursor.description
        columns = tuple(map(lambda x: x[0].lower(), desc)) if desc else None  # 列名

        return desc, columns

    def execute(self, sql, count=None, ehandling='raise', verbose=0):
        '''[summary]

        [description]
            执行sql
        Arguments:
            sql {[str]} -- [sql]

        Keyword Arguments:
            count {[int]} -- [返回的结果数量] (default: {None})
            ehandling {[str]} -- [错误处理] （raise: 错误弹出异常）
            verbose {[int]} -- [打印进程状态] （0：不打印， 1：文字进度， 2：进度条）

        Returns:
            rows {[int]} -- [影响的行数]
            results {[list]} -- [返回的结果]
        '''
        # def cur_getresults(cur, count):
        #     results = cur.fetchmany(count) if count else cur.fetchall()
        #     results = list(results) if results else []
        #     columns = tuple(map(lambda x: x[0].lower(), cur.description)) if cur.description  # 列名
        #     return columns, results

        rows = 0
        idx = 0
        conn = self.get_conn()
        # dblogger.info(conn)
        cur = conn.cursor()
        sql = sql if sql.strip().endswith(';') else sql.strip() + ';'
        sqls = sql.split(";")[:-1]
        sqls = [sql.strip() for sql in sqls if sql]
        sqls_length = len(sqls)
        bar_format = '{l_bar}{bar:30}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}] {postfix[0]}'
        sqls = sqls if verbose <= 1 else tqdm(sqls, ncols=100, postfix=['START'], bar_format=bar_format)  # 如果verbose>=2则显示进度条
        for _sql in sqls:
            results = None
            idx += 1
            # dblogger.info(_sql)
            parser = SqlParse(_sql)
            comment, sql, action, tablename = parser.comment, parser.sql, parser.action, parser.tablename
            if not sql:
                # dblogger.info(f'【{idx:0>2d}_PROGRESS】 no run !!!\n{_sql}')
                continue

            step = f"【{idx:0>2d}_PROGRESS】({action}){tablename}::{comment}"
            if verbose == 1:
                dblogger.info(f"{step}")
            elif verbose >= 2:
                sqls.postfix[0] = f"{step}"
                sqls.update()
            else:
                pass

            self.__execute_step(cur, sql, ehandling=ehandling)

            if action == 'SELECT' and (verbose or idx == sqls_length):
                # columns, results = cur_getresults(cur, count)
                results = self.cur_results(cur, count)
                desc, columns = self.cur_columns(cur)
                if verbose and columns:
                    dblogger.info(f"\n{pd.DataFrame(results, columns=columns)}")
                elif not columns:
                    dblogger.warning(f"Not Columns, cursor description is {desc}")
                else:
                    pass

                if columns:
                    results.insert(0, columns)
        try:
            conn.commit()
        except Exception as e:
            dblogger.error(e)
            conn.rollback()
        rows = cur.rowcount
        conn.close()
        return rows, action, results


class DBCommon(DBbase):

    def __init__(self):
        self.auto_rules = AUTO_RULES
        super(DBCommon, self).__init__()

    def __check_isauto(self, tablename):
        '''[summary]

        [description]
            通过tablename控制是否可以通过python代码处理
        Arguments:
            tablename {[str]} -- [表名]
        '''
        if not self.auto_rules:
            return True
        for rule in self.auto_rules:
            if rule in tablename:
                return True
        else:
            raise Exception(f"【drop】 please drop [{tablename}] on workbench! Or add rule into auto_rules !")
        return False

    def drop(self, tablename, verbose=0):
        if self.__check_isauto(tablename):
            sqlcompile = SqlCompile(tablename)
            sql_for_drop = sqlcompile.drop()
            rows, action, result = self.execute(sql_for_drop, verbose=verbose)
            dblogger.info(f'【{action}】{tablename} drop succeed !')
            return rows, action, result

    def delete(self, tablename, condition, verbose=0):
        if self.__check_isauto(tablename):
            sqlcompile = SqlCompile(tablename)
            sql_for_delete = sqlcompile.delete(condition)
            rows, action, result = self.execute(sql_for_delete, verbose=verbose)
            dblogger.info(f'【{action}】{tablename} delete {rows} rows succeed !')
            return rows, action, result

    def insert(self, tablename, columns, inserttype='value', values=None, chunksize=1000, 
               fromtable=None, condition=None, verbose=0):
        if values:
            vlength = len(values)

        if self.__check_isauto(tablename):
            sqlcompile = SqlCompile(tablename)
            sql_for_insert = sqlcompile.insert(columns, inserttype=inserttype, values=values,
                                               chunksize=chunksize, fromtable=fromtable, condition=condition)
            rows, action, result = self.execute(sql_for_insert, verbose=verbose)

            if values and rows != vlength % chunksize:
                raise Exception(f'Insert Error !!!')

            rows = vlength if values else rows
            dblogger.info(f'【{action}】{tablename} insert {rows} rows succeed !')
            return rows, action, result

    def get_columns(self, tablename, verbose=0):
        sql = f"select * from {tablename} limit 1;"
        rows, action, result = self.execute(sql, verbose=verbose)
        columns = result[0]
        columns = [c.lower() for c in columns]
        return columns

    def select(self, tablename, columns, condition=None, verbose=0):
        '''[summary]

        [description]
            执行select 
        Arguments:
            tablename {[str]} -- [表名]
            columns {[dict]} -- [列的信息]

        Keyword Arguments:
            condition {[str]} -- [where中的表达式] (default: {None})

        Returns:
            rows[int] -- [影响的数量]
            action[str] -- [sql表达式DML]
            result[list] -- [结果, 第一个元素是列名]
        '''
        sqlcompile = SqlCompile(tablename)
        sql_for_select = sqlcompile.select_base(columns, condition=condition)
        rows, action, result = self.execute(sql_for_select, verbose=verbose)
        return rows, action, result

    def add_columns(self, tablename, columns, verbose=0):
        old_columns = self.get_columns(tablename)
        old_columns = set(old_columns)
        new_columns = columns.new_cols
        new_columns = set([col.strip() for col in new_columns.split(',')])
        # dblogger.info(f'{old_columns}, {new_columns}')

        if old_columns == new_columns:
            dblogger.info(f'【{tablename}】columns not changed !')
        if old_columns - new_columns:
            raise Exception(f"【{tablename}】columns【{old_columns - new_columns}】 not set, should exists !")
        if new_columns - old_columns:
            sqlcompile = SqlCompile(tablename)
            add_columns = new_columns - old_columns
            for col_name in add_columns:
                column = columns.get_column_by_name(col_name)
                sql = sqlcompile.add_column(column.newname, column.coltype)
                self.execute(sql, verbose=0)
            dblogger.info(f'【{tablename}】add columns succeeded !【{new_columns - old_columns}】')
