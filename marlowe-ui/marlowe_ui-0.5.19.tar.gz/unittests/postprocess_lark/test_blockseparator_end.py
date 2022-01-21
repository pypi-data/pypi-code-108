import unittest
from parameterized import parameterized

from marlowe_ui.postprocess_lark import blockseparator

class TestEnd(unittest.TestCase):
    def setUp(self):
        self.finalend = blockseparator.End()

    # given by initial/projex.mfs PRJX0980?
    @parameterized.expand([
            'End of program:  total time  1.250    seconds',
            'End of program:  total time  1.589    minutes',
            'End of program:  total time  2.778    hours',
            'End of program:  total time  2.315    days',
            'End of program:  total time        10 days',
        ])
    def test_startswith(self, text):
        self.assertIsNotNone(self.finalend.startswith(text))
