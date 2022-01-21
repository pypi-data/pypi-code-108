import unittest
from parameterized import parameterized

import pathlib

from marlowe_ui.postprocess_lark import cascade_sequin

class TestCascadeSequinParseNarrow3I3(unittest.TestCase):
    # input files are at final_sequex_examples/
    @parameterized.expand([
        ('1 2 3', [1, 2, 3]),
        ('129130 52', [129, 130, 52]),
        ('129130-11', [129, 130, -11]),
        ('  1  2333', [1, 2, 333]),
        ('111  2333', [111, 2, 333]),
        ('     1234      5678  989', [1234, 5678, 989]),
        ])
    def test_cascade_sequin_parse_nallow_3I3(self, in_, out):
        self.assertEqual(cascade_sequin.Transformer.parse_narrow_3I3(in_), out)


class TestCascadeSequin(unittest.TestCase):
    def setUp(self):
        self.current_dir = pathlib.Path(__file__).parent

    # input files are at final_sequex_examples/
    @parameterized.expand([
        '01.cascade_sequin.txt',
        '02.cascade_sequin.txt',
        '03.cascade_sequin.txt',
        ])
    def test_cascade_sequin(self, filename):
        p = self.current_dir / 'cascade_sequin_examples'/ filename
        # print(p)
        # final_sequex.parse(text)
        with p.open('rt') as f:
            result = cascade_sequin.parse(f.read())
            # print(result)
