#!/usr/bin/env python
#  -*- coding: utf-8 -*-
__author__ = 'limin'

import unittest
from datetime import datetime

from tqsdk.rangeset import _range_intersection, _range_union, _range_subtraction, _rangeset_length, _rangeset_head, \
    _rangeset_slice, _rangeset_intersection, _rangeset_difference, _rangeset_union


class TestRange(unittest.TestCase):
    """
    两个 Range 集合可能有的情况：
    ------*****------   [10, 20)
    -------------###-   [25, 35)

    -----*****-------   [10, 20)
    ----------###----   [20, 30)

    ------------------------------------------------------

    -----*****-------   [10, 20)
    ------#######----   [12, 30)

    -----*****-------   [10, 20)
    ------####-------   [12, 20)

    -----*****-------   [10, 20)
    ------###--------   [12, 15)

    ------------------------------------------------------

    -----*****-------   [10, 20)
    -----#########---   [10, 30)

    -----*****-------   [10, 20)
    -----#####-------   [10, 20)

    -----*****-------   [10, 20)
    -----###---------   [10, 15)

    ------------------------------------------------------

    -----*****-------   [10, 20)
    --############---   [2, 30)

    -----*****-------   [10, 20)
    --########-------   [2, 20)

    -----*****-------   [10, 20)
    --######---------   [2, 15)

    -----*****-------   [10, 20)
    --###------------   [2, 10)

    -----*****-------   [10, 20)
    --##-------------   [2, 5)
    """
    def test_range_intersection(self):
        self.assertEqual(_range_intersection((10, 20), (25, 35)), [])
        self.assertEqual(_range_intersection((10, 20), (20, 30)), [])

        self.assertEqual(_range_intersection((10, 20), (12, 30)), [(12, 20)])
        self.assertEqual(_range_intersection((10, 20), (12, 20)), [(12, 20)])
        self.assertEqual(_range_intersection((10, 20), (12, 15)), [(12, 15)])

        self.assertEqual(_range_intersection((10, 20), (10, 30)), [(10, 20)])
        self.assertEqual(_range_intersection((10, 20), (10, 20)), [(10, 20)])
        self.assertEqual(_range_intersection((10, 20), (10, 15)), [(10, 15)])

        self.assertEqual(_range_intersection((10, 20), (2, 30)), [(10, 20)])
        self.assertEqual(_range_intersection((10, 20), (2, 20)), [(10, 20)])
        self.assertEqual(_range_intersection((10, 20), (2, 15)), [(10, 15)])
        self.assertEqual(_range_intersection((10, 20), (2, 10)), [])
        self.assertEqual(_range_intersection((10, 20), (2, 5)), [])

    def test_range_union(self):
        self.assertEqual(_range_union((10, 20), (25, 35)), [(10, 20), (25, 35)])
        self.assertEqual(_range_union((10, 20), (20, 30)), [(10, 30)])

        self.assertEqual(_range_union((10, 20), (12, 30)), [(10, 30)])
        self.assertEqual(_range_union((10, 20), (12, 20)), [(10, 20)])
        self.assertEqual(_range_union((10, 20), (12, 15)), [(10, 20)])

        self.assertEqual(_range_union((10, 20), (10, 30)), [(10, 30)])
        self.assertEqual(_range_union((10, 20), (10, 20)), [(10, 20)])
        self.assertEqual(_range_union((10, 20), (10, 15)), [(10, 20)])

        self.assertEqual(_range_union((10, 20), (2, 30)), [(2, 30)])
        self.assertEqual(_range_union((10, 20), (2, 20)), [(2, 20)])
        self.assertEqual(_range_union((10, 20), (2, 15)), [(2, 20)])
        self.assertEqual(_range_union((10, 20), (2, 10)), [(2, 20)])
        self.assertEqual(_range_union((10, 20), (2, 5)), [(2, 5), (10, 20)])

    def test_range_subtraction(self):
        self.assertEqual(_range_subtraction((10, 20), (25, 35)), [(10, 20)])
        self.assertEqual(_range_subtraction((10, 20), (20, 30)), [(10, 20)])

        self.assertEqual(_range_subtraction((10, 20), (12, 30)), [(10, 12)])
        self.assertEqual(_range_subtraction((10, 20), (12, 20)), [(10, 12)])
        self.assertEqual(_range_subtraction((10, 20), (12, 15)), [(10, 12), (15, 20)])

        self.assertEqual(_range_subtraction((10, 20), (10, 30)), [])
        self.assertEqual(_range_subtraction((10, 20), (10, 20)), [])
        self.assertEqual(_range_subtraction((10, 20), (10, 15)), [(15, 20)])

        self.assertEqual(_range_subtraction((10, 20), (2, 30)), [])
        self.assertEqual(_range_subtraction((10, 20), (2, 20)), [])
        self.assertEqual(_range_subtraction((10, 20), (2, 15)), [(15, 20)])
        self.assertEqual(_range_subtraction((10, 20), (2, 10)), [(10, 20)])
        self.assertEqual(_range_subtraction((10, 20), (2, 5)), [(10, 20)])


def int_to_rangeset(origin_int, width):
    arr = [2 ** i for i in range(width-1, -1, -1)]
    rangeset = []
    start_id = None
    for i in range(width):
        if origin_int & arr[i] > 0:
            if start_id is None:
                start_id = i
            if i == width - 1:
                rangeset.append((start_id, width))
        else:
            if start_id is not None:
                rangeset.append((start_id, i))
                start_id = None
    return rangeset


class TestRangeSet(unittest.TestCase):
    def test_rangeset_length(self):
        length = 8
        arr = [2 ** i for i in range(length - 1, -1, -1)]
        int_rangeset_dict = {i: int_to_rangeset(i, length) for i in range(2 ** length)}
        for i in range(2 ** length):
            rs = int_rangeset_dict[i]
            self.assertEqual(_rangeset_length(rs), sum([1 if i & j > 0 else 0 for j in arr]))

        self.assertEqual(_rangeset_length([(10, 50)]), 40)
        self.assertEqual(_rangeset_length([(10, 20), (25, 35)]), 20)

    def test_rangeset_head(self):
        length = 8
        arr = [2 ** i for i in range(length - 1, -1, -1)]
        int_rangeset_dict = {i: int_to_rangeset(i, length) for i in range(2 ** length)}
        for i in range(2 ** length):
            rs = int_rangeset_dict[i]
            for l in range(length):
                if l == 0:
                    self.assertEqual(_rangeset_head(rs, l), [])
                    continue
                sum_length = 0
                head_num = 0
                for k in arr:
                    if i & k > 0:
                        sum_length += 1
                        head_num += k
                    if sum_length == l:
                        break
                self.assertEqual(_rangeset_head(rs, l), int_rangeset_dict[head_num])

        self.assertEqual(_rangeset_head([(10, 50)], 10), [(10, 20)])
        self.assertEqual(_rangeset_head([(10, 20), (25, 35)], 12), [(10, 20), (25, 27)])
        self.assertEqual(_rangeset_head([(10, 20), (25, 35)], 20), [(10, 20), (25, 35)])
        self.assertEqual(_rangeset_head([(10, 20), (25, 35)], 26), [(10, 20), (25, 35)])

    def test_rangeset_slice(self):
        self.assertEqual(_rangeset_slice([(10, 20), (25, 35)], 10, 50), [(10, 20), (25, 35)])
        self.assertEqual(_rangeset_slice([(10, 20), (25, 60)], 10, 50), [(10, 20), (25, 50)])
        self.assertEqual(_rangeset_slice([(10, 20), (21, 23), (50, 60)], 10, 50), [(10, 20), (21, 23)])

    def test_rangeset_intersection(self):
        length = 8
        int_rangeset_dict = {i: int_to_rangeset(i, length) for i in range(2 ** length)}
        for i in range(2 ** length):
            rs1 = int_rangeset_dict[i]
            for j in range(2 ** length):
                rs2 = int_rangeset_dict[j]
                self.assertEqual(_rangeset_intersection(rs1, rs2), int_rangeset_dict[i & j])

    def test_rangeset_difference(self):
        length = 8
        int_rangeset_dict = {i: int_to_rangeset(i, length) for i in range(2 ** length)}
        for i in range(2 ** length):
            rs1 = int_rangeset_dict[i]
            for j in range(2 ** length):
                rs2 = int_rangeset_dict[j]
                self.assertEqual(_rangeset_difference(rs1, rs2), int_rangeset_dict[i & (i ^ j)])

        r1 = [(1514736000000000000, 1609430400000000000)]
        r2 = [(1522598400000000000, 1527868800000000000), (1546358400000000000, 1609257600000000000)]
        diff = _rangeset_difference(r1, r2)
        self.assertEqual(diff, [(1514736000000000000, 1522598400000000000), (1527868800000000000, 1546358400000000000), (1609257600000000000, 1609430400000000000)])

    def test_rangeset_union(self):
        length = 8
        int_rangeset_dict = {i: int_to_rangeset(i, length) for i in range(2 ** length)}
        for i in range(2 ** length):
            rs1 = int_rangeset_dict[i]
            for j in range(2 ** length):
                rs2 = int_rangeset_dict[j]
                self.assertEqual(_rangeset_union(rs1, rs2), int_rangeset_dict[i | j])
