import nose

import sys
import os

sys.path.insert(0, os.path.join(__file__, '..', '..'))

from postprocess.fixedfieldparser import FixedFieldParser


def test_transration_from_form_to_struct():
    # field struct is 6X,3X,A18,6G16.6
    strip = lambda a: a.strip()
    parser = FixedFieldParser(
        [(None, 6, None),
         (None, 3, None),
         ('name', 18, strip),
         ('Mean', 16, float),
         ('Variance', 16, float),
         ('Skewness', 16, float),
         ('Kurtosis', 16, float),
         ('Std Dev', 16, float),
         ('Error', 16, float)])

    nose.tools.eq_(parser.struct, [
        ('name', (9, 27), strip, None),
        ('Mean', (27, 43), float, None),
        ('Variance', (43, 59), float, None),
        ('Skewness', (59, 75), float, None),
        ('Kurtosis', (75, 91), float, None),
        ('Std Dev', (91, 107), float, None),
        ('Error', (107, 123), float, None)])


def test_parse():
    # field struct is 6X,3X,A18,6G16.6
    strip = lambda a: a.strip()
    parser = FixedFieldParser(
        [(None, 6, None),
         (None, 3, None),
         ('name', 18, strip),
         ('Mean', 16, float),
         ('Variance', 16, float),
         ('Skewness', 16, float),
         ('Kurtosis', 16, float),
         ('Std Dev', 16, float),
         ('Error', 16, float)])

    inputline = '         Radial Range           6.21071         19.8342         ' \
                + '1.46031         1.73116         4.45356        0.447600    '

    ans = {'name': 'Radial Range',
           'Mean': float(6.21071),
           'Variance': float(19.8342),
           'Skewness': float(1.46031),
           'Kurtosis': float(1.73116),
           'Std Dev': float(4.45356),
           'Error': float(0.447600)}

    nose.tools.eq_(parser.parse(inputline), ans)


def test_assertion_pass():
    strip = lambda a: a.strip()
    parser = FixedFieldParser(
        [(None, 6, None),
         (None, 3, None),
         ('name', 18, strip, 'Radial Range'),
         ('Mean', 16, float),
         ('Variance', 16, float),
         ('Skewness', 16, float),
         ('Kurtosis', 16, float),
         ('Std Dev', 16, float),
         ('Error', 16, float)])

    inputline = '         Radial Range           6.21071         19.8342         ' \
                + '1.46031         1.73116         4.45356        0.447600    '

    ans = {'name': 'Radial Range',
           'Mean': float(6.21071),
           'Variance': float(19.8342),
           'Skewness': float(1.46031),
           'Kurtosis': float(1.73116),
           'Std Dev': float(4.45356),
           'Error': float(0.447600)}

    nose.tools.eq_(parser.parse(inputline), ans)


def test_skipped_field():
    strip = lambda a: a.strip()
    parser = FixedFieldParser(
        [(None, 6, None),
         (None, 3, None),
         ('_name', 18, strip, 'Radial Range'),
         ('Mean', 16, float),
         ('Variance', 16, float),
         ('Skewness', 16, float),
         ('Kurtosis', 16, float),
         ('_Std Dev', 16, float),
         ('Error', 16, float)])

    inputline = '         Radial Range           6.21071         19.8342         ' \
                + '1.46031         1.73116         4.45356        0.447600    '

    ans = {  # 'name': 'Radial Range',
             'Mean': float(6.21071),
             'Variance': float(19.8342),
             'Skewness': float(1.46031),
             'Kurtosis': float(1.73116),
             # 'Std Dev': float(4.45356),
             'Error': float(0.447600)}

    nose.tools.eq_(parser.parse(inputline), ans)
