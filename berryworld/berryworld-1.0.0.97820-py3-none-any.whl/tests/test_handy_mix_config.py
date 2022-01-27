import unittest
import pandas as pd
import warnings
from bwgds.berryworld.handy_mix import HandyMix

warnings.filterwarnings('ignore')


class TestHandyMix(unittest.TestCase):
    """ Testing the implemented classes """

    def test_handy_functions_flatten_nested_list(self):
        list_sample = [[1], [2, 3]]
        test_result = HandyMix().flatten_nested_list(list_sample)
        self.assertEqual(test_result, [1, 2, 3])

    def test_handy_functions_sql_groupby(self):
        df = pd.DataFrame({'col1': ['a', 'b', 'b'], 'col2': [1, 2, 3]})
        by_cols = 'col1'
        method_agg = 'sum()'
        pd.testing.assert_frame_equal(HandyMix().sql_groupby(df, by_cols, method_agg),
                                      pd.DataFrame({'col1': ['a', 'b'], 'col2': [1, 5]}))

    def test_handy_functions_likely_match(self):
        df = pd.DataFrame({'col1': ['bird', 'bire', 'bear'], 'col2': ['blurr', 'blind', 'bill']}, )
        srs = df['col1']
        match_str = 'bir'
        self.assertEqual(HandyMix().likely_match(srs, match_str, threshold=0.8), [True, False, False])

    def test_handy_remove_line_chars(self):
        text_str = "This is a line \n This is another line"
        self.assertEqual(HandyMix().remove_line_chars(text_str), "This is a line  This is another line")

    def test_handy_coalesce(self):
        a_list = [(10.00, None, None, None), (20.00, None, None, None), (30.00, None, None, None),
                  (40.00, None, None, None), (None, 10000.00, None, None), (None, 20000.00, None, None),
                  (None, 30000.00, None, None), (None, 40000.00, None, None), (None, None, 15000, 3),
                  (None, None, 25000, 2), (None, None, 20000, 6), (None, None, 14000, 4)]
        df = pd.DataFrame(a_list, columns=['hourly_wage', 'salary', 'commission', 'num_sales'])
        res_list = [20800.0, 41600.0, 62400.0, 83200.0, 10000.0, 20000.0, 30000.0, 40000.0, 45000.0, 50000.0, 120000.0,
                    56000.0]
        results_df = pd.Series(res_list)
        pd.testing.assert_series_equal(
                HandyMix().coalesce(df, col_list=['hourly_wage', 'salary', 'commission', 'num_sales'],
                                    col_multipliers=[40 * 52, 1, 1, 1], col_to_multiply=[['num_sales', 'commission']]),
                results_df)


if __name__ == '__main__':
    TestHandyMix().test_handy_functions_flatten_nested_list()
    TestHandyMix().test_handy_functions_sql_groupby()
    TestHandyMix().test_handy_functions_likely_match()
    TestHandyMix().test_handy_remove_line_chars()
    TestHandyMix().test_handy_coalesce()
