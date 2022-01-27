#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'mayanqiong'

import unittest

from tqsdk.utils import _bisect_value


class TestUtils(unittest.TestCase):
    """
    增加对边界状况的测试
    """

    def test_bisect_value(self):
        a = [i * 100 + 100 for i in range(5)] + [i * 100 + 200 for i in range(5)]
        a.sort()
        print(a)  # [100, 200, 200, 300, 300, 400, 400, 500, 500, 600]

        self.assertEqual(_bisect_value(a, 80, priority="left"), 100)
        self.assertEqual(_bisect_value(a, 100, priority="left"), 100)
        self.assertEqual(_bisect_value(a, 200, priority="left"), 200)
        self.assertEqual(_bisect_value(a, 220, priority="left"), 200)
        self.assertEqual(_bisect_value(a, 250, priority="left"), 200)
        self.assertEqual(_bisect_value(a, 260, priority="left"), 300)
        self.assertEqual(_bisect_value(a, 300, priority="left"), 300)
        self.assertEqual(_bisect_value(a, 550, priority="left"), 500)
        self.assertEqual(_bisect_value(a, 580, priority="left"), 600)
        self.assertEqual(_bisect_value(a, 680, priority="left"), 600)

        self.assertEqual(_bisect_value(a, 80, priority="right"), 100)
        self.assertEqual(_bisect_value(a, 100, priority="right"), 100)
        self.assertEqual(_bisect_value(a, 200, priority="right"), 200)
        self.assertEqual(_bisect_value(a, 220, priority="right"), 200)
        self.assertEqual(_bisect_value(a, 250, priority="right"), 300)
        self.assertEqual(_bisect_value(a, 260, priority="right"), 300)
        self.assertEqual(_bisect_value(a, 300, priority="right"), 300)
        self.assertEqual(_bisect_value(a, 550, priority="right"), 600)
        self.assertEqual(_bisect_value(a, 580, priority="right"), 600)
        self.assertEqual(_bisect_value(a, 680, priority="right"), 600)
