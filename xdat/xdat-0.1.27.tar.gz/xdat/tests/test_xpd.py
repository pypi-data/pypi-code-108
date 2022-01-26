import unittest
from ..xpd import *
from ..xchecks import *

monkey_patch()


class TestXPD(unittest.TestCase):
    def test_x_groupby(self):
        df = pandas.DataFrame({'a': [1, 1, 2, 2, 3, 3], 'b': [1, 2, 3, 4, 5, 6]})
        df_g = df.x_groupby(['a'], {'max_b': xagg.Max('b'), 'any_b': xagg.Any('b'), 'xx_b': xagg.Lambda('b', np.mean), 'n': xagg.Count()})
        check_same_sets(df['a'], df_g['a'])
        check_no_dups(df_g['a'])

    def test_x_calc_rank_num(self):
        df = pandas.DataFrame({'a': [1, 1, 2, 2, 3, 3], 'b': [1, 2, 3, 4, 5, 6]})
        df['rank_id'] = df.x_calc_rank_num('a', 'b')
        check_same_sets([1, 2], df.rank_id)

    def test_x_history(self):
        df = pandas.DataFrame({'a': [1, 1, 2, 2, 3, 3], 'b': [1, 2, 3, 4, 5, 6]})
        df.x_add_history('h1', 'yo')
        return
