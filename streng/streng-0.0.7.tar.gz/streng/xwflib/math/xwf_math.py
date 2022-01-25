import xlwings as xw
import math

@xw.func
def test_test(x, y):
    return 5 * (x + y)


@xw.func
def xwf_math_linter(x0, x1, y0, y1, x):
    return y0 + (y1-y0)*(x-x0)/(x1-x0)


@xw.func
@xw.arg('x', doc='This is x.')
@xw.arg('y', doc='This is y.')
def xwf_math_double_sum(x, y):
    """Returns twice the sum of the two arguments"""
    return 2 * (x + y)


