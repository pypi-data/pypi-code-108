import unittest
from parameterized import parameterized

import pathlib

from marlowe_ui.postprocess_lark import cascade_detail_projectile

class TestCascadeDetailProjectile(unittest.TestCase):
    def setUp(self):
        self.current_dir = pathlib.Path(__file__).parent

    # input files are at final_sequex_examples/
    @parameterized.expand([
        '01.cascade_detail_projectile.txt',
        '02.cascade_detail_projectile.txt',
        ])
    def test_cascade_detail_projectile(self, filename):
        p = self.current_dir / 'cascade_detail_projectile_examples'/ filename
        with p.open('rt') as f:
            result = cascade_detail_projectile.parse(f.read())
