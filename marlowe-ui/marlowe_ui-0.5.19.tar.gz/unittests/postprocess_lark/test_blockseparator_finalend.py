import unittest
from parameterized import parameterized

from marlowe_ui.postprocess_lark import blockseparator

class TestFinalEnd(unittest.TestCase):
    def setUp(self):
        self.finalend = blockseparator.FinalEnd()

    # given by final/marlox.mfs MRLX1900
    @parameterized.expand([
        'Computation time 0.1000     seconds      Maximum cascade storage  1000',
        'Computation time  10.10     seconds      Maximum cascade storage  1000',
        'Computation time  1.668     minutes      Maximum cascade storage  1000',
        'Computation time  2.778     hours        Maximum cascade storage  1000',
        'Computation time  2.315     days         Maximum cascade storage  1000',
        'Computation time         10 days         Maximum cascade storage100000',
        'Computation time  3.140     days         Maximum cascade storage******',
        'Computation time  1.250     seconds      Maximum cascade storage    72',
        'Computation time  1.589     minutes      Maximum cascade storage 17662'
        ])
    def test_startswith(self, text):
        self.assertIsNotNone(self.finalend.startswith(text))
