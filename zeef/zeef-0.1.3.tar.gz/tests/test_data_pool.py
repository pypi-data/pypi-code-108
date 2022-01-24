"""
    Unit tests for Pool-based data selection functions.
    @author huangyz0918 (huangyz0918@gmail.com)
    @date 06/12/2021
"""

import random
import unittest

from zeef.data import Pool


class TestDataPool(unittest.TestCase):

    def test_label_simple(self):
        raw_data = [1] * 100
        pool = Pool(raw_data)
        pool.label_by_ids(range(50, 60, 1), [0] * 10)
        x, y = pool.get_labeled_data()
        self.assertEqual(x, [1] * 10)
        self.assertEqual(y, [0] * 10)

    def test_label_random(self):
        label_num = 30
        raw_data = random.sample(range(0, 100), 100)
        x_data = raw_data[:label_num]
        pool = Pool(raw_data)
        pool.label_by_ids(range(0, label_num, 1), [1] * label_num)
        x, y = pool.get_labeled_data()
        self.assertEqual(x, x_data)
        self.assertEqual(y, [1] * label_num)

    def test_label_one(self):
        label_num = 30
        raw_data = random.sample(range(0, 100), 100)
        pool = Pool(raw_data)
        pool.label_by_ids(range(0, label_num, 1), [1] * label_num)
        pool.label(120, 0)  # not in the list, append in the last.
        x, y = pool.get_labeled_data()
        self.assertEqual(x[-1], 120)
        self.assertEqual(y[-1], 0)
        self.assertEqual(y[0], 1)
        self.assertEqual(pool.size, len(raw_data) + 1)
        self.assertEqual(len(pool.labeled_ids), label_num + 1)
        pool.label_by_id(0, 0)
        pool.label_by_id(10, 2)
        x, y = pool.get_labeled_data()
        self.assertEqual(y[0], 0)
        self.assertEqual(y[10], 2)
        self.assertEqual(pool.size, len(raw_data) + 1)
        self.assertEqual(len(pool.labeled_ids), label_num + 1)
        pool.label(120, 1)  # already in the list
        x, y = pool.get_labeled_data()
        self.assertEqual(x[-1], 120)
        self.assertEqual(pool.size, 101)
        self.assertEqual(y[-1], 1)
        pool.label_by_id(10, 120)
        pool.label(120, 2)
        x, y = pool.get_labeled_data()
        self.assertEqual(y[-1], 2)
        self.assertEqual(y[10], 120)

    def test_label_one_multi(self):
        label_num = 100
        raw_data = random.sample(range(0, 100), 100)
        for i in range(10):
            raw_data[30 + i] = 120
        pool = Pool(raw_data)
        pool.label_by_ids(range(0, label_num, 1), [1] * label_num)
        pool.label(120, 0)
        x, y = pool.get_labeled_data()
        self.assertEqual(y[35], 0)
        self.assertEqual(y[32], 0)
        self.assertEqual(y[29], 1)

    def test_get_unlabeled_ids(self):
        label_num = 500
        raw_data = random.sample(range(0, 1000), 1000)
        pool = Pool(raw_data)
        pool.label_by_ids(range(0, label_num, 1), [1] * label_num)
        unlabeled_ids = list(pool.get_unlabeled_ids())

        self.assertEqual(len(unlabeled_ids), 500)
        self.assertEqual(len(pool.labeled_ids), 500)
        pool.label_by_ids(range(label_num + 100, label_num + 200, 1), [0] * 100)
        unlabeled_ids = list(pool.get_unlabeled_ids())
        self.assertEqual(len(unlabeled_ids), 400)
        self.assertEqual(len(pool.labeled_ids), 600)
        self.assertEqual(unlabeled_ids[0], label_num)
        self.assertEqual(unlabeled_ids[-1], len(raw_data) - 1)
        pool.label_by_id(len(raw_data) - 1, 666)
        unlabeled_ids = list(pool.get_unlabeled_ids())
        self.assertEqual(unlabeled_ids[-1], len(raw_data) - 2)


if __name__ == '__main__':
    unittest.main()
