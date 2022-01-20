# @Author: chunyang.xu
# @Email:  398745129@qq.com
# @Date:   2020-06-10 14:40:50
# @Last Modified time: 2021-12-30 19:36:17
# @github: https://github.com/longfengpili

# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import re
import threading
import pymysql

from pydbapi.db import DBCommon, DBFileExec
from pydbapi.sql import SqlCompile
from pydbapi.conf import AUTO_RULES


import logging
mysqllogger = logging.getLogger(__name__)


class SqlMysqlCompile(SqlCompile):
    '''[summary]

    [description]
        构造mysql sql
    Extends:
        SqlCompile
    '''

    def __init__(self, tablename):
        super(SqlMysqlCompile, self).__init__(tablename)

    def create_indexes(self, columns, indexes, index_part=128, ismultiple=True):
        if indexes and not isinstance(indexes, list):
            raise TypeError(f"indexes must be a list, but got {indexes} !")
        _indexes = []
        for index in indexes:
            column = columns.get_column_by_name(index)
            coltype = column.coltype
            varlength = re.search('varchar\((\d+)\)', coltype)
            varlength = int(varlength.group(1)) if varlength else 128
            index_part = varlength if varlength < index_part else index_part
            index = f"{index}({index_part})" if coltype.startswith('varchar') else index
            _indexes.append(index)

        if ismultiple:
            indexes = ', '.join(_indexes)
            indexes = f"index multiple_index({indexes})"
        else:
            indexes = [f"index {_index}_index({_index})" for _index in indexes]
            indexes = ',\n'.join(indexes)

        return indexes

    def create_partition(self, partition):
        coltype = partition.coltype
        if coltype != 'date':
            raise TypeError(f"{partition} only support date type !")
        partition = f"partition by hash (to_days({partition.newname}))"
        return partition

    def create(self, columns, indexes, index_part=128, ismultiple_index=True, 
               partition=None, distribution=None, isdoris=False):
        'mysql 暂不考虑索引'
        sql = self.create_nonindex(columns)

        if indexes and not isinstance(indexes, list):
            raise TypeError(f"indexes must be a list, but got {indexes} !")

        if indexes:
            indexes = self.create_indexes(columns, indexes, index_part=index_part, ismultiple=ismultiple_index)
            sql = sql.replace(');', f",\n{indexes});")

        if partition:
            partition = columns.get_column_by_name(partition)
            partition = self.create_partition(partition)
            sql = sql.replace(';', f'\n{partition};')

        if isdoris:
            distributed_col = distribution or columns.index(0).newname
            distributed = f"distributed by hash({distributed_col})"
            sql = sql.replace(';', f'\n{distributed};')

        return sql

    def dumpsql(self, columns, dumpfile, fromtable=None, condition=None):
        selectsql = self.select_base(columns, fromtable=fromtable, condition=condition)
        intosql = f'into outfile "{dumpfile}" fields terminated by ",";'
        dumpsql = selectsql.replace(";", intosql)
        return dumpsql

    def loadsql(self, columns, loadfile, intotable=None, fieldterminated=','):
        intotable = intotable or self.tablename
        loadsql = f'''load data infile "{loadfile}" into table {intotable}
                      fields terminated by "{fieldterminated}" ({columns.select_cols});'''
        return loadsql


class MysqlDB(DBCommon, DBFileExec):
    _instance_lock = threading.Lock()

    def __init__(self, host, user, password, database, port=3306, charset="utf8", safe_rule=True, isdoris=False):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.charset = charset
        self.isdoris = isdoris
        super(MysqlDB, self).__init__()
        self.auto_rules = AUTO_RULES if safe_rule else None

    def __new__(cls, *args, **kwargs):
        if not hasattr(MysqlDB, '_instance'):
            with MysqlDB._instance_lock:
                if not hasattr(MysqlDB, '_instance'):
                    MysqlDB._instance = super().__new__(cls)

        return MysqlDB._instance

    # @classmethod
    # def get_instance(cls, *args, **kwargs):
    #     mysqllogger.info(MysqlDB._instance_lock)
    #     if not hasattr(MysqlDB, '_instance'):
    #         mysqllogger.info(MysqlDB._instance_lock)
    #         with MysqlDB._instance_lock:
    #             if not hasattr(MysqlDB, '_instance'):
    #                 MysqlDB._instance = cls(*args, **kwargs)

    #     return MysqlDB._instance

    def get_conn(self):
        conn = pymysql.connect(database=self.database, user=self.user, password=self.password,
                               host=self.host, port=self.port, charset=self.charset)
        if not conn:
            self.get_conn()
        return conn

    def create(self, tablename, columns, indexes=None, index_part=128, ismultiple_index=True,
               partition=None, distribution=None, verbose=0):
        # tablename = f"{self.database}.{tablename}"
        sqlcompile = SqlMysqlCompile(tablename)
        sql_for_create = sqlcompile.create(columns, indexes, index_part=index_part,
                                           ismultiple_index=ismultiple_index, partition=partition,
                                           distribution=distribution, isdoris=self.isdoris)
        rows, action, result = self.execute(sql_for_create, verbose=verbose)
        return rows, action, result

    def dumpdata(self, tablename, columns, dumpfile, condition=None, verbose=0):
        sqlcompile = SqlMysqlCompile(tablename)
        sql_for_dump = sqlcompile.dumpsql(columns, dumpfile, condition=condition)
        rows, action, result = self.execute(sql_for_dump, verbose=verbose)
        mysqllogger.info(f"【{action}】{tablename} dumpdata {rows} rows succeed, outfile: {dumpfile} !")
        return rows, action, result

    def loaddata(self, tablename, columns, loadfile, fieldterminated=',', verbose=0):
        sqlcompile = SqlMysqlCompile(tablename)
        sql_for_load = sqlcompile.loadsql(columns, loadfile, fieldterminated=fieldterminated)
        rows, action, result = self.execute(sql_for_load, verbose=verbose)
        mysqllogger.info(f"【{action}】{tablename} loaddata {rows} rows succeed, loadfile: {loadfile} !")
        return rows, action, result
