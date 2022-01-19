import unittest

from . import utils


class TestUtils(unittest.TestCase):
    """TestUtils."""

    def test_split_x_of_parts(self):
        tt = [
            {"name": "Test True", "p": b"0101", "expect": True},
            {"name": "Test False", "p": b"0104", "expect": False},
        ]

        def _inner(name, p, expect):
            res = utils.split_x_of_parts(p)
            self.assertEqual(res, expect)

        for test in tt:
            _inner(**test)

    def test_check_last_part(self):
        tt = [{"name": "Test True", "p": b"1", "expect": True}, {"name": "Test False", "p": b"0", "expect": False}]

        def _inner(name, p, expect):
            res = utils.check_last_part(p)
            self.assertEqual(res, expect)

        for test in tt:
            _inner(**test)
