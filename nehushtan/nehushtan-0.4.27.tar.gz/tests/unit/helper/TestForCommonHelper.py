import unittest

from nehushtan.helper.CommonHelper import CommonHelper
from nehushtan.logger.NehushtanFileLogger import NehushtanFileLogger


class TestForCommonHelper(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        print('setUpClass', cls)

    @classmethod
    def tearDownClass(cls) -> None:
        print('tearDownClass', cls)

    def setUp(self):
        print('setUp')

    def tearDown(self):
        print('tearDown')

    def test_read_anything(self):
        target_1 = {
            'A': {
                "B": {
                    "C": "D",
                    "E": 0,
                    "F": False,
                    "G": True,
                    "H": None,
                },
                "I": [
                    "J",
                    {"K": "L"},
                    ["M"],
                ],
            },
        }
        # match
        self.assertEqual(
            target_1['A'],
            CommonHelper.read_target(target_1, ('A',))
        )
        self.assertEqual(
            target_1['A']['B'],
            CommonHelper.read_target(target_1, ('A', 'B')),
        )
        self.assertEqual(
            target_1['A']['B']['C'],
            CommonHelper.read_target(target_1, ('A', 'B', 'C'))
        )
        self.assertEqual(
            target_1['A']['B']['E'],
            CommonHelper.read_target(target_1, ('A', 'B', 'E'))
        )
        self.assertEqual(
            target_1['A']['B']['F'],
            CommonHelper.read_target(target_1, ('A', 'B', 'F'))
        )
        self.assertEqual(
            target_1['A']['B']['G'],
            CommonHelper.read_target(target_1, ('A', 'B', 'G'))
        )
        self.assertEqual(
            target_1['A']['B']['H'],
            CommonHelper.read_target(target_1, ('A', 'B', 'H'))
        )
        self.assertEqual(
            target_1['A']['I'],
            CommonHelper.read_target(target_1, ('A', 'I',))
        )
        self.assertEqual(
            target_1['A']['I'][0],
            CommonHelper.read_target(target_1, ('A', 'I', 0))
        )
        self.assertEqual(
            target_1['A']['I'][1],
            CommonHelper.read_target(target_1, ('A', 'I', 1))
        )
        self.assertEqual(
            target_1['A']['I'][1]['K'],
            CommonHelper.read_target(target_1, ('A', 'I', 1, 'K'))
        )
        self.assertEqual(
            target_1['A']['I'][2],
            CommonHelper.read_target(target_1, ('A', 'I', 2)),
        )
        # default
        self.assertEqual(
            'DEFAULT',
            CommonHelper.read_target(target_1, tuple(), 'DEFAULT')
        )
        self.assertEqual(
            'DEFAULT',
            CommonHelper.read_target(None, tuple(), 'DEFAULT')
        )
        self.assertEqual(
            'DEFAULT',
            CommonHelper.read_target(target_1, ('Z', 'Y', 'X',), 'DEFAULT')
        )
        self.assertEqual(
            'DEFAULT',
            CommonHelper.read_target(target_1, ('A', 'C', 0,), 'DEFAULT')
        )

    def test_write_dictionary(self):
        target = {}
        self.assertEqual(
            {'A': {'B': 'C'}},
            CommonHelper.write_dictionary(target, ('A', 'B',), 'C')
        )
        self.assertEqual(
            {'A': {'B': 'D'}},
            CommonHelper.write_dictionary(target, ('A', 'B',), 'D')
        )
        self.assertEqual(
            {'A': {'B': 'D', 'E': 'F'}, },
            CommonHelper.write_dictionary(target, ('A', 'E',), 'F')
        )

    def test_seek_class(self):
        self.assertIsInstance(
            NehushtanFileLogger(),
            CommonHelper.class_with_class_path('nehushtan.logger.NehushtanFileLogger', 'NehushtanFileLogger')
        )
