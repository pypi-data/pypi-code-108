# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2021/12/1 9:43 上午
# Copyright (C) 2021 The lesscode Team

class ConditionWrapper:
    """
    查询SQL语句条件包装类，用于组装查询SQL语句
    """

    def __init__(self, table, column="*"):
        self.table = table
        self.column = column
        self.conditions: list = []
        self.groups = ""
        self.order: list = []

    @property
    def or_(self):
        self.conditions.append(("OR", None, None))
        return self

    @property
    def and_(self):
        self.conditions.append(("AND", None, None))
        return self

    def eq(self, column, value):
        """
        添加条件 =
        :param column: 列名
        :param value: 参考值
        :return:
        """
        self.conditions.append(("=", column, value))
        return self

    def eq_all(self, params: list):
        """
        添加多个条件 =
        :param params: 参数[("column","value")]
        :return:
        """
        [self.eq(*item) for item in params]
        return self

    def ne(self, column, value):
        """
        添加条件 <>
        :param column: 列名
        :param value: 参考值
        :return:
        """
        self.conditions.append(("<>", column, value))
        return self

    def gt(self, column, value):
        """
        添加条件 大于 >
        :param column: 列名
        :param value: 参考值
        :return:
        """
        self.conditions.append((">", column, value))
        return self

    def ge(self, column, value):
        """
        添加条件 大于等于 >=
        :param column: 列名
        :param value: 参考值
        :return:
        """
        self.conditions.append((">=", column, value))
        return self

    def lt(self, column, value):
        """
        添加条件 小于 <
        :param column: 列名
        :param value: 参考值
        :return:
        """
        self.conditions.append(("<", column, value))
        return self

    def le(self, column, value):
        """
        添加条件 小于等于 <=
        :param column: 列名
        :param value: 参考值
        :return:
        """
        self.conditions.append(("<=", column, value))
        return self

    def between(self, column, value1, value2):
        """
        添加条件 BETWEEN 值1 AND 值2
        :param column: 列名
        :param value1:
        :param value2:
        :return:
        """
        if value1 is None:
            self.ge(column, value1)
        elif value2 is None:
            self.lt(column, value2)
        else:
            self.conditions.append(("BETWEEN", column, [value1, value2]))
        return self

    def not_between(self, column, value1, value2):
        """
        添加条件 NOT BETWEEN 值1 AND 值2
        :param column: 列名
        :param value1:
        :param value2:
        :return:
        """
        if value1 is None:
            self.lt(column, value1)
        elif value2 is None:
            self.ge(column, value2)
        else:
            self.conditions.append(("NOT_BETWEEN", column, [value1, value2]))
        return self

    def like(self, column, value):
        """
        添加条件 LIKE '%值%'
        :param column: 列名
        :param value: 参考值
        :return:
        """
        self.conditions.append(("LIKE", column, value))
        return self

    def notLike(self, column, value):
        """
        添加条件 NOT LIKE '%值%'
        :param column: 列名
        :param value: 参考值
        :return:
        """
        self.conditions.append(("NOT_LIKE", column, value))
        return self

    def like_left(self, column, value):
        """
        添加条件 LIKE '%值'
        :param column: 列名
        :param value: 参考值
        :return:
        """
        self.conditions.append(("LIKE_LEFT", column, value))
        return self

    def like_right(self, column, value):
        """
        添加条件 LIKE '值%'
        :param column: 列名
        :param value: 参考值
        :return:
        """
        self.conditions.append(("LIKE_RIGHT", column, value))
        return self

    def is_null(self, column):
        """
        添加条件 字段 IS NULL
        :param column: 列名
        :return:
        """
        self.conditions.append(("IS_NULL", column, None))
        return self

    def is_not_null(self, column):
        """
        添加条件 字段 IS NOT NULL
        :param column: 列名
        :return:
        """
        self.conditions.append(("IS_NOT_NULL", column, None))
        return self

    def in_(self, column, value):
        """
        添加条件 字段 IN (v0, v1, ...)
        :param column: 列名
        :param value: 参考值
        :return:
        """
        self.conditions.append(("IN", column, value))
        return self

    def not_in(self, column, value):
        """
        添加条件 NOT IN (v0, v1, ...)
        :param column: 列名
        :param value: 参考值
        :return:
        """
        self.conditions.append(("NOT_IN", column, value))
        return self

    def group(self, column):
        """
        添加条件 分组：GROUP BY 字段
        :param column: 列名
        :return:
        """
        self.groups = column
        return self

    def order_asc(self, column):
        """
        添加条件 排序：ORDER BY 字段, ... ASC
        :param column: 列名
        :return:
        """
        self.order.append((column, "ASC"))
        return self

    def order_desc(self, column):
        """
        添加条件 排序：ORDER BY 字段, ... DESC
        :param column: 列名
        :return:
        """
        self.order.append((column, "DESC"))
        return self
