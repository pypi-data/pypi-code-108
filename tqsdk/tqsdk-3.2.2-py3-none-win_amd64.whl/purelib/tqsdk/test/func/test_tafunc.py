#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'limin'

import unittest

import pandas

from tqsdk.tafunc import get_dividend_df, get_dividend_factor


class TestGetDividendCoeff(unittest.TestCase):
    """
    增加对边界状况的测试
    """

    def test_get_dividend_df(self):
        df = get_dividend_df(['20190729,0.300000', '20201203,0.200000'],
                                ['20180806,0.010000', '20181217,0.010000', '20190729,0.020000', '20200622,0.030000',
                                 '20201203,0.020000'])
        dt = pandas.Series([1.533485e+18, 1.544976e+18, 1.564330e+18, 1.592755e+18, 1.606925e+18])
        stock_dividend = pandas.Series([0.0, 0.0, 0.3, 0.0, 0.2])
        cash_dividend = pandas.Series([0.01, 0.01, 0.02, 0.03, 0.02])
        pandas.testing.assert_series_equal(dt, df["datetime"], check_names=False)
        pandas.testing.assert_series_equal(stock_dividend, df["stock_dividend"], check_names=False)
        pandas.testing.assert_series_equal(cash_dividend, df["cash_dividend"], check_names=False)

        df = get_dividend_df(['20200609,1.000000'],
                             ['20180503,0.800000', '20190524,0.800000', '20200609,1.000000'])
        print(df.to_string())
        dt = pandas.Series([1.525277e+18, 1.558627e+18, 1.591632e+18])
        stock_dividend = pandas.Series([0.0, 0.0, 1.0])
        cash_dividend = pandas.Series([0.8, 0.8, 1.0])
        pandas.testing.assert_series_equal(dt, df["datetime"], check_names=False)
        pandas.testing.assert_series_equal(stock_dividend, df["stock_dividend"], check_names=False)
        pandas.testing.assert_series_equal(cash_dividend, df["cash_dividend"], check_names=False)


    def test_get_dividend_factor(self):
        df = get_dividend_df(['20200609,1.000000'],
                             ['20180503,0.800000', '20190524,0.800000', '20200609,1.000000'])
        factor = get_dividend_factor(
            df,
            {'datetime': 1525190400000000000, 'open': 201.2, 'high': 212.0, 'low': 201.2, 'close': 204.02, 'volume': 3523300, 'open_oi': 0, 'close_oi': 0},
            {'datetime': 1525276800000000000, 'open': 202.0, 'high': 202.0, 'low': 193.9, 'close': 200.65, 'volume': 3154800, 'open_oi': 0, 'close_oi': 0}
        )
        self.assertAlmostEqual(0.9960788158023723, factor)
        factor = get_dividend_factor(
            df,
            {'datetime': 1558540800000000000, 'open': 305.01, 'high': 307.68, 'low': 299.76, 'close': 300.1, 'volume': 985000, 'open_oi': 0, 'close_oi': 0},
            {'datetime': 1558627200000000000, 'open': 300.0, 'high': 303.9, 'low': 294.6, 'close': 297.0, 'volume': 1197600, 'open_oi': 0, 'close_oi': 0}
        )
        self.assertAlmostEqual(0.9973342219260246, factor)
        factor = get_dividend_factor(
            df,
            {'datetime': 1591545600000000000, 'open': 682.21, 'high': 683.76, 'low': 661.4, 'close': 666.46, 'volume': 2168200, 'open_oi': 0, 'close_oi': 0},
            {'datetime': 1591632000000000000, 'open': 333.0, 'high': 340.0, 'low': 331.36, 'close': 334.8, 'volume': 3846700, 'open_oi': 0, 'close_oi': 0}
        )
        self.assertAlmostEqual(0.49924976742790267, factor)
