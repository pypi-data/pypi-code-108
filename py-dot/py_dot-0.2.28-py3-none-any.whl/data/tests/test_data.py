import unittest

from py_dot.core.date import Period
from py_dot.data import get_summary_unit


class TestDataCore(unittest.TestCase):
    def test_get_summary_unit(self):

        self.assertEqual(
            get_summary_unit(
                Period(
                    '20000101000000',
                    '20000101000100'
                )
            ),
            None
        )

        self.assertEqual(
            get_summary_unit(
                Period(
                    '20000101000000',
                    '20000101005959'
                )
            ),
            'minute'
        )