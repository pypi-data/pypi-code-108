#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'limin'

import random
import unittest

import numpy as np
from pandas import DataFrame

from tqsdk import utils
from tqsdk.algorithm.twap import _gen_random_list
from tqsdk.lib.utils import _check_time_table


class TestTwap(unittest.TestCase):
    """
    增加对边界状况的测试
    """

    def test_download(self):
        utils.RD = random.Random(4)
        self.assertEqual([6], _gen_random_list(sum_val=6, min_val=1, max_val=6, length=1))
        self.assertEqual([1], _gen_random_list(sum_val=1, min_val=1, max_val=6, length=1))
        self.assertEqual([3], _gen_random_list(sum_val=3, min_val=1, max_val=6, length=1))
        self.assertEqual([4, 3, 4, 4, 5], _gen_random_list(sum_val=20, min_val=1, max_val=6, length=5))
        self.assertEqual([6, 6, 6, 6, 6], _gen_random_list(sum_val=30, min_val=1, max_val=6, length=5))
        self.assertEqual([1, 1, 1, 1, 1, 1, 1, 1, 1, 1], _gen_random_list(sum_val=10, min_val=1, max_val=6, length=10))

        self.assertEqual([11, 5], _gen_random_list(sum_val=16, min_val=11, max_val=15))
        self.assertEqual([97, 6], _gen_random_list(sum_val=103, min_val=97, max_val=101))

    def test_check_time_table(self):
        df = DataFrame([], columns=['interval', 'target_pos', 'price'])
        _check_time_table(df)

        df = DataFrame([
            [10, -5, 'PASSIVE']
        ], columns=['interval', 'target_pos', 'price'])
        _check_time_table(df)

        df = DataFrame([
            [10.3, -5, 'PASSIVE'],
            [9.5, -5, 'ACTIVE'],
            [10, 0, None],
        ], columns=['interval', 'target_pos', 'price'])
        _check_time_table(df)

        def price(dir):
            print(dir)
            return 20

        time_table = DataFrame([
            [25, 10, "PASSIVE"],
            [5, 10, "ACTIVE"],
            [25, 20, price],
            [5, 20, price],
        ], columns=['interval', 'target_pos', 'price'])
        _check_time_table(time_table)  # price 也可以是函数类型

        self.assertRaises(Exception,
                          _check_time_table,
                          DataFrame([
                              [10.3, 3, 'PASSIVE'],
                              [9.5, 5, 'ACTIVE'],
                              [10, 0, None],
                          ], columns=['interval', 'volume', 'price']))  # 列名错误

        self.assertRaises(Exception,
                          _check_time_table,
                          DataFrame([
                              [10.3, 3.4, 'PASSIVE'],
                              [9.5, 5, 'ACTIVE'],
                              [10, 0, None],
                          ], columns=['interval', 'target_pos', 'price']))  # 数据类型错误

        self.assertRaises(Exception,
                          _check_time_table,
                          DataFrame([
                              [np.nan, 3, 'PASSIVE'],
                              [9.5, 5, 'ACTIVE'],
                              [10, 0, None],
                          ], columns=['interval', 'target_pos', 'price']))  # 数据类型错误

        self.assertRaises(Exception,
                          _check_time_table,
                          DataFrame([
                              [-7.8, 3, 'PASSIVE'],
                              [9.5, 5, 'ACTIVE'],
                              [10, 0, None],
                          ], columns=['interval', 'target_pos', 'price']))  # 数据类型错误

        self.assertRaises(Exception,
                          _check_time_table,
                          DataFrame([
                              [7.8, 3, 'PASSIVE'],
                              [9.5, 5, 'None'],
                              [10, 0, None],
                          ], columns=['interval', 'target_pos', 'price']))  # 数据类型错误
