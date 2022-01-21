import unittest
from parameterized import parameterized

from marlowe_ui.postprocess_lark import blockseparator

class TestFinalEnd(unittest.TestCase):
    def setUp(self):
        self.finalend = blockseparator.CascadeEnd()

    # in cascades/detail.mfs DETL2880
    @parameterized.expand([
        'Computation time 0.1000     seconds      Cascade storage  1000',
        'Computation time  10.10     seconds      Cascade storage  1000',
        'Computation time  1.668     minutes      Cascade storage  1000',
        'Computation time  2.778     hours        Cascade storage  1000',
        'Computation time  2.315     days         Cascade storage  1000',
        'Computation time         10 days         Cascade storage100000',
        'Computation time  3.140     days         Cascade storage******',
        ])

    def test_startswith(self, text):
        self.assertIsNotNone(self.finalend.startswith(text))
