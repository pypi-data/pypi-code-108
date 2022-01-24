"""
    Unit tests for different I/O data modalities.
    @author huangyz0918 (huangyz0918@gmail.com)
    @date 06/12/2021
"""

import random
import unittest

from zeef.data import Pool


class TestDataType(unittest.TestCase):

    def test_random_pick(self):
        raw_data = [1.0] * 100
        pool = Pool(raw_data)
        pool.label_by_ids(range(50, 60, 1), [0] * 10)
        x, y = pool.get_labeled_data()
        self.assertEqual(x, [1] * 10)
        self.assertEqual(y, [0] * 10)

    def test_pool_types_label_by_ids(self):
        raw_data = [1.0] * 100
        labels = [0] * 10
        pool = Pool(raw_data)
        pool.label_by_ids(range(50, 60, 1), labels)
        x, y = pool.get_labeled_data()
        self.assertEqual(type(x), list)
        self.assertEqual(type(y), list)
        self.assertEqual(type(x[0]), type(raw_data[0]))
        self.assertEqual(type(y[0]), type(labels[0]))

    def test_pool_types_label(self):
        labels = [0] * 100
        raw_data = random.sample(range(0, 100), 100)
        pool = Pool(raw_data)
        pool.label_by_ids(range(0, 100, 1), labels)
        pool.label(200, 1.0)
        x, y = pool.get_labeled_data()
        # check the values
        self.assertEqual(x[-1], 200)
        self.assertEqual(y[-1], 1.0)
        # check the types
        # self.assertEqual(type(x[-1]), int)
        # self.assertEqual(type(y[-1]), float)


if __name__ == '__main__':
    unittest.main()
