import nose

import sys
import os

sys.path.insert(0, os.path.join(__file__, '..', '..'))

from postprocess.statistical_analysis_of_data import Parser


def test_headermatch():
    p = Parser()
    m = p.match('Statistical Analysis of Data from     100 Cascades')

    nose.tools.ok_(m)
    nose.tools.eq_(m['samples'], 100)


def test_columnheader():
    p = Parser()

    nose.tools.eq_(
        p.columnheader,
        '        .....Total number of.....         Mean         Variance       '
        'Skewness       Kurtosis       Std Dev         Error  \n')
