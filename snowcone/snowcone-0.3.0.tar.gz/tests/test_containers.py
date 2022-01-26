"""Tests for the container functions"""


import unittest
from snowcone.containers import Array


class TestArray(unittest.TestCase):
    """Tests for Array class"""

    def test_filter(self):
        data = [{"key": 1}, {"key": 2}, {"key": 2}]
        array = Array(data)
        array = array.filter(lambda x: x["key"] == 2)
        self.assertEqual(2, array.length())
        self.assertTrue(all([x["key"] == 2 for x in array.all()]))

    def test_map(self):
        data = [{"key": 1}, {"key": 2}, {"key": 2}]
        array = Array(data)
        keys = array.map(lambda x: x["key"])
        self.assertCountEqual([1, 2, 2], keys.all())

    def test_flatten(self):
        data = [[1, 2, 3], [4, 5, 6]]
        array = Array(data)
        flattened = array.flatten()
        self.assertCountEqual([1, 2, 3, 4, 5, 6], flattened.all())

    def test_all(self):
        data = [{"key": 1}, {"key": 2}, {"key": 2}]
        array = Array(data)
        self.assertCountEqual(data, array.all())

    def test_length(self):
        data = [{"key": 1}, {"key": 2}, {"key": 2}]
        array = Array(data)
        self.assertEqual(len(data), array.length())

    def test_get(self):
        data = [{"key": 1}, {"key": 2}, {"key": 2}]
        array = Array(data)
        self.assertEqual(data[0], array.get(0))
        with self.subTest("Test None returned"):
            array = Array([])
            self.assertIsNone(array.get(0))

    def test_first(self):
        data = [{"key": 1}, {"key": 2}, {"key": 2}]
        array = Array(data)
        self.assertEqual(data[0], array.first())
        with self.subTest("Test None returned"):
            array = Array([])
            self.assertIsNone(array.first())
