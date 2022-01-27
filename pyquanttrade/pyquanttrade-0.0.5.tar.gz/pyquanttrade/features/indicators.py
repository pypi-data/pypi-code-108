# -*- coding: utf-8 -*-
"""Functions from market data"""

__author__ = "Miguel Martin"
__version__ = "1"


def always_true():
    def return_function(when, ticket, trades, data):
        return True

    return return_function


def apply_all(criteria):
    def return_function(when, ticket, trades, data):
        return all([f(when, ticket, trades, data) for f in criteria])

    return return_function


def apply_any(criteria):
    def return_function(when, ticket, trades, data):
        return any([f(when, ticket, trades, data) for f in criteria])

    return return_function


def apply_not(criterium):
    def return_function(when, ticket, trades, data):
        return not criterium(when, ticket, trades, data)

    return return_function


def not_trade():
    def return_function(when, ticket, trades, data):
        return not trades.any_open_trade()

    return return_function


def eq(element, than):
    def return_function(when, ticket, trades, data):
        return element(when, ticket, trades, data) == than

    return return_function


def leq(element, than):
    def return_function(when, ticket, trades, data):
        return element(when, ticket, trades, data) <= than

    return return_function


def geq(element, than):
    def return_function(when, ticket, trades, data):
        return element(when, ticket, trades, data) >= than

    return return_function


def gt(element, than):
    def return_function(when, ticket, trades, data):
        return element(when, ticket, trades, data) > than

    return return_function


def lt(element, than):
    def return_function(when, ticket, trades, data):
        return element(when, ticket, trades, data) < than

    return return_function


def TF_indicator(func):
    def return_function(when, ticker, trades, data):
        data1 = func(data)
        column_name = data1.name
        return data[when, column_name]

    return return_function


def unit_indicator(func):
    def return_function(when, ticker, trades, data):
        data1 = func(data)
        column_name = f"unit_indicator_{data1.name}"
        if column_name not in data.columns:
            data[column_name] = data1 == 1
        return data[column_name][when]

    return return_function


def cross_of_values(func1, func2):
    def return_function(when, ticker, trades, data):
        data1 = func1(data)
        data2 = func2(data)
        column_name = f"diff_rows_{data1.name}_vs_{data2.name}"
        if column_name not in data.columns:
            data[column_name] = 0
            data.loc[data1 <= data2, [column_name]] = 1
            data[column_name] = data[column_name].diff()
            data[column_name].iloc[0] = 0
            data[column_name].loc[data[column_name] == 1] = True
            data[column_name].loc[data[column_name] != 1] = False
        return data[column_name][when]

    return return_function


def greater_than(func1, func2):
    def return_function(when, ticker, trades, data):
        data1 = func1(data)
        data2 = func2(data)
        column_name = f"{data1.name}_greater_than_{data2.name}"
        if column_name not in data.columns:
            data[column_name] = 0
            data.loc[data1 > data2, [column_name]] = 1
            data[column_name] = data[column_name].astype(bool)
        return data[column_name][when]

    return return_function


def lower_than(func1, func2):
    def return_function(when, ticker, trades, data):
        data1 = func1(data)
        data2 = func2(data)
        column_name = f"{data1.name}_lower_than_{data2.name}"
        if column_name not in data.columns:
            data[column_name] = 0
            data.loc[data1 < data2, [column_name]] = 1
            data[column_name] = data[column_name].astype(bool)
        return data[column_name][when]

    return return_function


def upwards_turn(func1):
    def return_function(when, ticker, trades, data):
        data1 = func1(data)
        column_name = f"upwards_turn_{data1.name}"
        if column_name not in data.columns:
            data[column_name] = 0
            data.loc[data1.diff(1) < 0, [column_name]] = -1
            data.loc[data1.diff(1) > 0, [column_name]] = 1
            data[column_name] = data[column_name].diff(1)
            data[column_name].iloc[0] = 0
            data.loc[data[column_name] > 0, [column_name]] = True
            data.loc[data[column_name] <= 0, [column_name]] = False
        return data[column_name][when]

    return return_function


def downwards_turn(func1):
    def return_function(when, ticker, trades, data):
        data1 = func1(data)
        column_name = f"downwards_turn_{data1.name}"
        if column_name not in data.columns:
            data[column_name] = 0
            data.loc[data1.diff(1) < 0, [column_name]] = -1
            data.loc[data1.diff(1) > 0, [column_name]] = 1
            data[column_name] = data[column_name].diff(1)
            data[column_name].iloc[0] = 0
            data.loc[data[column_name] >= 0, [column_name]] = False
            data.loc[data[column_name] < 0, [column_name]] = True
        return data[column_name][when]

    return return_function
