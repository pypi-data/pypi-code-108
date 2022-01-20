import unittest
import matplotlib.pyplot as plt
from ..xpd import *
from .. import xplt

monkey_patch()
xplt.monkey_patch()


class TestXPD(unittest.TestCase):
    def test_decorate(self):
        df = pandas.DataFrame({'Aaaaa': [1, 1, 2, 2, 3, 3], 'Bbbbb': [1, 2, 3, 4, 5, 6]})
        df.x_rename(columns={'Aaaaa': 'a', 'Bbbbb': 'b'}, inplace=True)
        df.x_rename(columns={'a': 'my_a'}, inplace=True)
        plt.scatter(df.my_a, df.b); plt.show()
        plt.hist(df.my_a); plt.show()
