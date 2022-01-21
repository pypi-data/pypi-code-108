import unittest
from parameterized import parameterized

import pathlib

from marlowe_ui.postprocess_lark import cascade_report_summary

class TestCascadeReportSummary(unittest.TestCase):
    def setUp(self):
        self.current_dir = pathlib.Path(__file__).parent

    # input files are at final_sequex_examples/
    @parameterized.expand([
        '01.cascade_report_summary.txt',
        '02.cascade_report_summary.txt',
        ])
    def test_final_sequex(self, filename):
        p = self.current_dir / 'cascade_report_summary_examples'/ filename
        # print(p)
        # final_sequex.parse(text)
        with p.open('rt') as f:
            result = cascade_report_summary.parse(f.read())
