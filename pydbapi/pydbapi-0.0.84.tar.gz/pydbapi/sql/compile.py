# @Author: chunyang.xu
# @Email:  398745129@qq.com
# @Date:   2020-06-03 14:04:33
# @Last Modified time: 2021-08-25 16:46:12
# @github: https://github.com/longfengpili

# !/usr/bin/env python3
# -*- coding:utf-8 -*-


from pydbapi.col import ColumnsModel


class SqlCompile(object):

    def __init__(self, tablename):
        self.tablename = tablename

    def select_base(self, columns, fromtable=None, condition=None):
        '''[summary]

        [description]
            生成select sql (未考虑join，所以暂时用base)
        Arguments:
            columns {[ColumnsModel]} -- [列信息需要按照排列顺序处理]

        Keyword Arguments:
            condition {[条件]} -- [where中的条件] (default: {None})

        Returns:
            [str] -- [返回sql]

        Raises:
            TypeError -- [检查columns的情况]
        '''
        tablename = fromtable or self.tablename
        if not isinstance(columns, ColumnsModel):
            raise TypeError("colums must be a ColumnsModel !")

        sql = f'select {columns.select_cols}\nfrom {tablename}'
        condition = f"where {condition}" if condition else ''
        group = f'group by {columns.group_cols}' if columns.group_cols else ''
        order = f'order by {columns.order_cols}' if columns.order_cols else ''

        if condition:
            sql = sql + '\n' + condition
        if group:
            sql = sql + '\n' + group
        if order:
            sql = sql + '\n' + order
        sql = sql + '\n;'
        return sql

    def create_nonindex(self, columns):
        '''[summary]

        [description]
            create sql
        Arguments:
            self.tablename {[str]} -- [表名]
            columns {[ColumnsModel]} -- [列信息]

        Returns:
            [str] -- [sql]

        Raises:
            TypeError -- [类别错误]
        '''

        if not isinstance(columns, ColumnsModel):
            raise TypeError("colums must be a ColumnsModel !")

        sql = f'create table if not exists {self.tablename}\n{columns.create_cols};'
        return sql

    def drop(self):
        sql = f'drop table if exists {self.tablename};'
        return sql

    def _insert_value(self, columns, values):
        '''[summary]

        [description]
            插入数据
        Arguments:
            self.tablename {[str]} -- [表名]
            columns {[ColumnsModel]} -- [列信息]
            values {[list]} -- [插入的数据]
        '''
        def deal_values(values):
            j_values = []
            if not values:
                raise ValueError(f"{values} is empty !!!")
            if not isinstance(values, list):
                raise TypeError('values must be a list !')
            j_values = [str(tuple(value)) for value in values]
            j_values = ',\n'.join(j_values)
            # j_values = j_values.replace('\'\'', 'null').replace('None', 'null')  # 空值替换为null
            return j_values

        values = deal_values(values)

        if not isinstance(columns, ColumnsModel):
            raise TypeError("colums must be a ColumnsModel !")

        sql = f'insert into {self.tablename}\n({columns.new_cols})\nvalues\n{values};'
        sql = sql.replace('\'\'', 'Null').replace('None', 'Null')  # 空值替换为null
        return sql

    def _insert_by_value(self, columns, values, chunksize=1000):
        sql = []
        vlength = len(values)
        step = 0
        for i in range(0, vlength, chunksize):
            step += 1
            maxi = i+chunksize
            maxi = maxi if maxi < vlength else vlength
            chvalues = values[i: maxi]
            _sql = self._insert_value(columns, chvalues)
            _sql = f"--[NO.{step}]insert {maxi-i} rows, From [{i+1}] to [{maxi}]\n{_sql}"
            sql.append(_sql)

        sql = ''.join(sql)
        # print(sql)
        return sql

    def _insert_by_select(self, fromtable, columns, condition=None):
        selectsql = self.select_base(columns, fromtable, condition=condition)

        sql = f'''insert into {self.tablename}\n({columns.new_cols})\n{selectsql}'''
        return sql

    def insert(self, columns, inserttype='value', values=None, chunksize=1000, fromtable=None, condition=None):
        if inserttype == 'value':
            if not values:
                raise Exception(f"InsertType is {inserttype}, values must be not None")
            sql = self._insert_by_value(columns, values, chunksize=chunksize)
            # print(sql)
        elif inserttype == 'select':
            if not fromtable:
                raise Exception(f"InsertType is {inserttype}, fromtable must be not None")
            sql = self._insert_by_select(fromtable, columns, condition=condition)
        else:
            raise Exception(f"Not supported {inserttype}, insertType must be value or select")
        return sql

    def delete(self, condition):
        sql = f'''delete from {self.tablename} where {condition};'''
        return sql

    def add_column(self, colname, coltype):
        coltype = f"{coltype}(32)" if coltype == 'varchar' else coltype
        sql = f'alter table {self.tablename} add column {colname} {coltype};'
        return sql
