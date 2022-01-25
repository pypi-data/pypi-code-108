#! /usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from fy_common_ext import core


class TestCore(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_flatten(self):
        self.assertTrue(core.flatten([1, 2, [3, 4], 'abc']), [1, 2, 3, 4, 'abc'])

    def test_remove_prefix(self):
        self.assertEqual(core.remove_prefix('hello', 'hel'), 'lo')
        self.assertEqual(core.remove_prefix('hello', 'hello'), '')
        self.assertEqual(core.remove_prefix('hello', ''), 'hello')
        self.assertEqual(core.remove_prefix('hello', 'hello world'), 'hello')
        self.assertEqual(core.remove_prefix('hello', 'world'), 'hello')

    def test_remove_suffix(self):
        self.assertEqual(core.remove_suffix('hello', 'llo'), 'he')
        self.assertEqual(core.remove_suffix('hello', 'hello'), '')
        self.assertEqual(core.remove_suffix('hello', ''), 'hello')
        self.assertEqual(core.remove_suffix('hello', 'world hello'), 'hello')
        self.assertEqual(core.remove_suffix('hello', 'world'), 'hello')


if __name__ == '__main__':
    unittest.main()
