#  Copyright (c) 2020. Sinri Edogawa
from typing import Iterable, Union

from nehushtan.mysql import constant
from nehushtan.mysql.MySQLKit import MySQLKit


class MySQLCondition:

    def __init__(self, field: str, operate: str, value: any, addition: any = None):
        self._field = field
        self._operate = operate
        self._value = value

        if self._operate == constant.MYSQL_CONDITION_OP_LIKE or self._operate == constant.MYSQL_CONDITION_OP_NOT_LIKE:
            self._value = MySQLKit.quote_offline(self._value)
            if addition == constant.MYSQL_CONDITION_LIKE_LEFT_WILDCARD:
                self._value = f"concat('%',{self._value})"
            elif addition == constant.MYSQL_CONDITION_LIKE_RIGHT_WILDCARD:
                self._value = f"concat({self._value},'%')"
            elif addition == constant.MYSQL_CONDITION_LIKE_BOTH_WILDCARD:
                self._value = f"concat('%',{self._value},'%')"
            # else treat as EQUAL of string

    @staticmethod
    def make_equal(field: str, value: any):
        return MySQLCondition(field, constant.MYSQL_CONDITION_OP_EQ, value)

    @staticmethod
    def make_equal_null_safe(field: str, value: any):
        return MySQLCondition(field, constant.MYSQL_CONDITION_OP_NULL_SAFE_EQUAL, value)

    @staticmethod
    def make_not_equal(field: str, value: any):
        return MySQLCondition(field, constant.MYSQL_CONDITION_OP_NEQ, value)

    @staticmethod
    def make_in_array(field: str, array: Union[tuple, list]):
        return MySQLCondition(field, constant.MYSQL_CONDITION_OP_IN, array)

    @staticmethod
    def make_not_in_array(field: str, array: Union[tuple, list]):
        return MySQLCondition(field, constant.MYSQL_CONDITION_OP_NOT_IN, array)

    @staticmethod
    def make_greater_than(field: str, value: any):
        return MySQLCondition(field, constant.MYSQL_CONDITION_OP_GT, value)

    @staticmethod
    def make_equal_or_greater_than(field: str, value: any):
        return MySQLCondition(field, constant.MYSQL_CONDITION_OP_EGT, value)

    @staticmethod
    def make_less_than(field: str, value: any):
        return MySQLCondition(field, constant.MYSQL_CONDITION_OP_LT, value)

    @staticmethod
    def make_equal_or_less_than(field: str, value: any):
        return MySQLCondition(field, constant.MYSQL_CONDITION_OP_ELT, value)

    @staticmethod
    def make_is_null(field: str):
        return MySQLCondition(field, constant.MYSQL_CONDITION_OP_IS, constant.MYSQL_CONDITION_CONST_NULL)

    @staticmethod
    def make_is_not_null(field: str):
        return MySQLCondition(field, constant.MYSQL_CONDITION_OP_IS_NOT, constant.MYSQL_CONDITION_CONST_NULL)

    @staticmethod
    def make_between(field: str, left, right):
        return MySQLCondition(field, constant.MYSQL_CONDITION_OP_BETWEEN, (left, right))

    @staticmethod
    def make_not_between(field: str, left, right):
        return MySQLCondition(field, constant.MYSQL_CONDITION_OP_NOT_BETWEEN, (left, right))

    @staticmethod
    def make_string_with_prefix(field: str, prefix: str):
        return MySQLCondition(field, constant.MYSQL_CONDITION_OP_LIKE, prefix,
                              constant.MYSQL_CONDITION_LIKE_RIGHT_WILDCARD)

    @staticmethod
    def make_string_with_suffix(field: str, suffix: str):
        return MySQLCondition(field, constant.MYSQL_CONDITION_OP_LIKE, suffix,
                              constant.MYSQL_CONDITION_LIKE_LEFT_WILDCARD)

    @staticmethod
    def make_string_contains(field: str, sub_string: str):
        return MySQLCondition(field, constant.MYSQL_CONDITION_OP_LIKE, sub_string,
                              constant.MYSQL_CONDITION_LIKE_BOTH_WILDCARD)

    @staticmethod
    def make_string_without_prefix(field: str, prefix: str):
        return MySQLCondition(field, constant.MYSQL_CONDITION_OP_NOT_LIKE, prefix,
                              constant.MYSQL_CONDITION_LIKE_RIGHT_WILDCARD)

    @staticmethod
    def make_string_without_suffix(field: str, suffix: str):
        return MySQLCondition(field, constant.MYSQL_CONDITION_OP_NOT_LIKE, suffix,
                              constant.MYSQL_CONDITION_LIKE_LEFT_WILDCARD)

    @staticmethod
    def make_string_contains_not(field: str, sub_string: str):
        return MySQLCondition(field, constant.MYSQL_CONDITION_OP_NOT_LIKE, sub_string,
                              constant.MYSQL_CONDITION_LIKE_BOTH_WILDCARD)

    @staticmethod
    def make_string_is_null_or_empty(field: str):
        return MySQLCondition(field, constant.MYSQL_CONDITION_MACRO_IS_NULL_OR_EMPTY_STRING, None)

    @staticmethod
    def make_string_is_not_null_nor_empty(field: str):
        return MySQLCondition(field, constant.MYSQL_CONDITION_MACRO_IS_NOT_NULL_NOR_EMPTY_STRING, None)

    @staticmethod
    def make_and(conditions: Iterable["MySQLCondition"]):
        return MySQLCondition.make_intersection_of_conditions(conditions)

    @staticmethod
    def make_intersection_of_conditions(conditions: Iterable["MySQLCondition"]):
        return MySQLCondition('', constant.MYSQL_CONDITION_OP_PARENTHESES_AND, conditions)

    @staticmethod
    def make_or(conditions: Iterable["MySQLCondition"]):
        return MySQLCondition.make_union_of_conditions(conditions)

    @staticmethod
    def make_union_of_conditions(conditions: Iterable["MySQLCondition"]):
        return MySQLCondition('', constant.MYSQL_CONDITION_OP_PARENTHESES_OR, conditions)

    @staticmethod
    def make_raw_expression(condition_sql: str):
        return MySQLCondition('', constant.MYSQL_CONDITION_MACRO_RAW_EXPRESSION, condition_sql)

    def __str__(self):
        return self.organize_to_sql()

    def organize_to_sql(self) -> str:
        """
        Since 0.1.4
        :return:
        """
        if (
                constant.MYSQL_CONDITION_OP_EQ,
                constant.MYSQL_CONDITION_OP_GT,
                constant.MYSQL_CONDITION_OP_EGT,
                constant.MYSQL_CONDITION_OP_LT,
                constant.MYSQL_CONDITION_OP_ELT,
                constant.MYSQL_CONDITION_OP_NEQ,
                constant.MYSQL_CONDITION_OP_NULL_SAFE_EQUAL,
        ).__contains__(self._operate):
            return f"`{self._field}` {self._operate} " + MySQLKit.quote_offline(self._value)

        elif (
                constant.MYSQL_CONDITION_OP_IS,
                constant.MYSQL_CONDITION_OP_IS_NOT,
        ).__contains__(self._operate):
            if (
                    constant.MYSQL_CONDITION_CONST_TRUE,
                    constant.MYSQL_CONDITION_CONST_FALSE,
                    constant.MYSQL_CONDITION_CONST_NULL,
            ).__contains__(self._value):
                return f"`{self._field}` {self._operate} {self._value}"
            else:
                raise Exception("YOU MUST USE CONSTANT FOR IS COMPARISON!")

        elif (
                constant.MYSQL_CONDITION_OP_IN,
                constant.MYSQL_CONDITION_OP_NOT_IN,
        ).__contains__(self._operate):
            if type(self._value) is list or type(self._value) is tuple:
                if len(self._value) <= 0:
                    raise Exception("ARRAY IS EMPTY!")
                x = []
                for item in self._value:
                    x.append(MySQLKit.quote_offline(item))
                return f"`{self._field}` {self._operate} ({','.join(x)})"
            else:
                raise Exception("YOU MUST USE AN ARRAY FOR IN!")

        elif (
                constant.MYSQL_CONDITION_OP_LIKE,
                constant.MYSQL_CONDITION_OP_NOT_LIKE,
        ).__contains__(self._operate):
            return f"`{self._field}` {self._operate} {self._value}"

        elif (
                constant.MYSQL_CONDITION_OP_BETWEEN,
                constant.MYSQL_CONDITION_OP_NOT_BETWEEN,
        ).__contains__(self._operate):
            if type(self._value) is list or type(self._value) is tuple:
                if len(self._value) < 2:
                    raise Exception("NOT ENOUGH VALUES TO TEST IN BETWEEN!")
                left = MySQLKit.quote_offline(self._value[0])
                right = MySQLKit.quote_offline(self._value[1])
                return f"`{self._field}` {self._operate} {left} AND {right}"
            else:
                raise Exception("YOU MUST USE AN ARRAY FOR BETWEEN!")

        elif (
                constant.MYSQL_CONDITION_OP_EXISTS,
                constant.MYSQL_CONDITION_OP_NOT_EXISTS,
        ).__contains__(self._operate):
            # only value is used, as raw sql
            return f"{self._operate} ({self._value})"

        elif (
                constant.MYSQL_CONDITION_OP_PARENTHESES_AND,
                constant.MYSQL_CONDITION_OP_PARENTHESES_OR,
        ).__contains__(self._operate):
            if isinstance(self._value, (tuple, list)):
                if len(self._value) <= 0:
                    raise Exception("CONDITION ARRAY EMPTY!")
                parts = []
                for sub_condition in self._value:
                    if isinstance(sub_condition, MySQLCondition):
                        parts.append(sub_condition.organize_to_sql())
                    else:
                        raise Exception("NOT A MySQLCondition INSTANCE!")
                if len(parts) <= 0:
                    raise Exception("EMPTY CONDITION ARRAY!")

                return "(" + (" " + self._operate + " ").join(parts) + ")"
            else:
                raise Exception("YOU MUST USE AN ARRAY FOR CONDITIONS!")

        elif self._operate == constant.MYSQL_CONDITION_MACRO_IS_NULL_OR_EMPTY_STRING:
            return f"(`{self._field}` IS NULL OR `{self._field}` = '')"

        elif self._operate == constant.MYSQL_CONDITION_MACRO_IS_NOT_NULL_NOR_EMPTY_STRING:
            return f"(`{self._field}` IS NOT NULL AND `{self._field}` <> '')"

        elif self._operate == constant.MYSQL_CONDITION_MACRO_RAW_EXPRESSION:
            return self._value

        else:
            raise NotImplementedError("CANNOT OPERATE UNKNOWN TYPE!")

    @staticmethod
    def build_sql_component(conditions: Iterable["MySQLCondition"]):
        parts = []
        # Fixed in 0.1.9: If conditions have type error... RAISE!
        # The fucking Python design and PyCharm cannot deal with such check.
        for condition in conditions:
            if not isinstance(condition, MySQLCondition):
                raise TypeError("You must give an instance of MySQLCondition here!")
            parts.append(condition.organize_to_sql())
        # if not follow the rule, just ignore
        if len(parts) <= 0:
            return "1=1"
        else:
            return " AND ".join(parts)
