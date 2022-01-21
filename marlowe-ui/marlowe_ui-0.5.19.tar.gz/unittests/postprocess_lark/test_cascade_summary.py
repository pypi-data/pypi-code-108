import unittest
import json
from parameterized import parameterized

import pathlib

from marlowe_ui.postprocess_lark import cascade_summary

class TestCascadeSummary(unittest.TestCase):
    def setUp(self):
        self.current_dir = pathlib.Path(__file__).parent

    # input files are at final_sequex_examples/
    @parameterized.expand([
        ('01.cascade_summary.txt', '01.cascade_summary_out.json')
        ])
    def test_cascade_summary(self, filename, jsonfile):
        p = self.current_dir / 'cascade_summary_examples'/ filename
        jp = self.current_dir / 'cascade_summary_examples'/ jsonfile
        # print(p)
        # cascade_summary.parse(text)
        with p.open('rt') as f, jp.open('rt') as jf:
            result = cascade_summary.parse(f.read())
            jdata = json.load(jf)
            self.assertEqual(result, jdata)
