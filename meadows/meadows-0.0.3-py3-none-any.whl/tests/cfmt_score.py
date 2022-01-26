"""Unit tests for 
"""
#pylint: disable=import-outside-toplevel
from unittest import TestCase
import numpy
from numpy.testing import assert_array_equal
import pandas


class CfmtScoreTests(TestCase):
    """Unit tests for score_cfmt
    """

    def test_score(self):
        """score_cfmt() adds the "correct" boolean column and a total score
        """
        from meadows.cfmt import score_cfmt
        annotations = pandas.DataFrame([
            ['pract_00_X_01_13_l_li', 1],
            ['pract_00_X_02_00_f_li', 2],
            ['pract_00_X_03_13_r_li', 3], # wrong
            ['intro_00_B_01_13_l_li', 2],
            ['intro_00_B_02_00_f_li', 1], # wrong
            ['intro_00_B_03_13_r_li', 3],
            ['intro_01_D_01_13_l_li', 2],
            ['intro_01_D_02_00_f_li', 3],
            ['intro_05_Z_02_00_f_li', 3],
            ['intro_05_Z_03_13_r_li', 2], # wrong
            ['novel_00_M_05_00_f_hl', 3], # wrong
            ['novel_01_N_08_13_r_dk', 2],
            ['novel_28_N_06_23_l_li', 1],
            ['novel_29_B_05_00_f_hl', 3],
            ['noise_00_Z_12_00_f_li', 2],
            ['noise_01_M_11_23_r_li', 2], # wrong
            ['noise_22_B_11_23_r_li', 1],
            ['noise_23_D_11_23_r_li', 2]  # wrong
        ], columns=['stim1_name', 'label'])
        out_score, out_df = score_cfmt(annotations)
        self.assertEqual(out_score, 10)
        assert_array_equal(out_df.correct.values, numpy.array([
            True, False, True, True, True, True,
            False, False, True, True, True, True, False, True, False
        ]))
