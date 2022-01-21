import unittest
from parameterized import parameterized

import pathlib

from marlowe_ui.postprocess_lark import final_slavex

class TestFinalSequex(unittest.TestCase):
    def setUp(self):
        self.current_dir = pathlib.Path(__file__).parent

    # input files are at final_sequex_examples/
    @parameterized.expand([
        '01.final_slavex.txt',
        ])
    def test_final_sequex(self, filename):
        p = self.current_dir / 'final_slavex_examples'/ filename
        # print(p)
        # final_sequex.parse(text)
        with p.open('rt') as f:
            result = final_slavex.parse(f.read())
