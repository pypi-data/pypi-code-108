import unittest
from datetime import datetime

from py_dot.core.date import Period
from py_dot.core.route import from_query_string
from py_dot.core.route.route import divide_path


class TestRoute(unittest.TestCase):
    def test_from_query_string(self):
        self.assertDictEqual(
            from_query_string('foo:bar'),
            {
                'foo': 'bar'
            }
        )

        self.assertDictEqual(
            from_query_string('foo:bar,baz'),
            {
                'foo': ['bar', 'baz']
            }
        )

        self.assertEqual(
            from_query_string('foo:bar;baz:qux'),
            {
                'foo': 'bar',
                'baz': 'qux'
            }
        )

        self.assertIsInstance(
            from_query_string('foo:20211130')['foo'],
            datetime
        )

        self.assertIsInstance(
            from_query_string('foo:20211130~21211201')['foo'],
            Period
        )

    def test_divide_path(self):
        self.assertListEqual(
            divide_path('a/b/c|d'),
            ['a/b/c', 'a/b/d']
        )

        result = divide_path('a|b/c|d')
        result.sort()
        expect = ['a/c', 'a/d', 'b/c', 'b/d']
        expect.sort()

        self.assertListEqual(result, expect)

        self.assertListEqual(
            divide_path('a/1|2/b'),
            ['a/1/b', 'a/2/b']
        )
