# @Author: chunyang.xu
# @Email:  398745129@qq.com
# @Date:   2020-11-30 16:28:21
# @Last Modified time: 2021-12-30 19:45:56
# @github: https://github.com/longfengpili

# !/usr/bin/env python3
# -*- coding:utf-8 -*-


class ColumnModel(object):

    def __init__(self, newname, coltype='varchar', sqlexpr=None, func=None, order=0):
        self.newname = newname
        self.coltype = coltype
        self.sqlexpr = sqlexpr or newname
        self.func = self.__check_func(func)
        self.order = order

    def __repr__(self):
        return f"{self.newname}({self.coltype})"

    def __contains__(self, newname):
        return newname == self.newname

    def __check_func(self, func):
        if func and func not in ['min', 'max', 'sum', 'count']:
            raise ValueError(f"func:{func} not supported!")
        return func

    @property
    def final_sqlexpr(self):
        if self.func:
            final_sqlexpr = f"{self.func}({self.sqlexpr}) as {self.newname}"
        elif self.newname != self.sqlexpr:
            final_sqlexpr = f"{self.sqlexpr} as {self.newname}"
        else:
            final_sqlexpr = self.newname

        return final_sqlexpr

    @property
    def create_sqlexpr(self):
        create_sqlexpr = f"{self.newname} {self.coltype}"
        return create_sqlexpr


class ColumnsModel(object):

    def __init__(self, *columns):
        self.columns = columns

    def __repr__(self):
        return f"{[column for column in self.columns]}"

    def __getitem__(self, key):
        return self.columns[key]

    def index(self, key):
        return self.columns[key]

    def __contains__(self, name):
        col = self.get_column_by_name(name)
        isin = True if col else False
        return isin

    @property
    def func_cols(self):
        func_cols = [col for col in self.columns if col.func]
        return func_cols

    @property
    def nonfunc_cols(self):
        nonfunc_cols = [col for col in self.columns if not col.func]
        return nonfunc_cols

    @property
    def new_cols(self):
        all_cols = self.nonfunc_cols + self.func_cols
        new_cols = [col.newname for col in all_cols]
        new_cols = ', '.join(new_cols)
        return new_cols

    @property
    def create_cols(self):
        create_cols = [col.create_sqlexpr for col in self.columns]
        create_cols = '(' + ',\n'.join(create_cols) + ')'
        return create_cols

    @property
    def select_cols(self):
        all_cols = self.nonfunc_cols + self.func_cols
        all_cols = [col.final_sqlexpr for col in all_cols]
        select_cols = ',\n'.join(all_cols)
        return select_cols

    @property
    def group_cols(self):
        if self.func_cols:
            group_cols = [col.newname for col in self.nonfunc_cols]
            group_cols = ', '.join(group_cols)
            return group_cols

    @property
    def order_cols(self):
        all_cols = self.nonfunc_cols + self.func_cols
        order_cols = [(idx+1, col) for idx, col in enumerate(all_cols) if col.order > 0]
        order_cols_sorted = sorted(order_cols, key=lambda x: [x[1].order, x[1].newname])
        order_cols = [f"{col[0]}" for col in order_cols_sorted]
        order_cols = ', '.join(order_cols)
        return order_cols

    def get_column_by_name(self, name):
        for col in self.columns:
            if col.newname == name:
                return col
