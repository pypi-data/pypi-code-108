'''
examples from the docs page
http://docs.xlwings.org/en/stable/udfs.html#array-formulas-with-numpy-and-pandas
'''

import xlwings as xw
import numpy as np
import pandas as pd

@xw.func
def double_sum(x, y):
    """Returns twice the sum of the two arguments"""
    return 2 * (x + y)


@xw.func
def add_one(data):
    return [[cell + 1 for cell in row] for row in data]



# To force Excel to always give you a two-dimensional array, no matter whether the argument is a single cell,
# a column/row or a two-dimensional Range, you can extend the above formula like this:
@xw.func
@xw.arg('data', ndim=2)
def add_one(data):
    return [[cell + 1 for cell in row] for row in data]



@xw.func
@xw.arg('x', np.array, ndim=2)
@xw.arg('y', np.array, ndim=2)
def matrix_mult(x, y):
    return x @ y



@xw.func
@xw.arg('x', pd.DataFrame, index=False, header=False)
@xw.ret(index=False, header=False)
def CORREL2(x):
    """Like CORREL, but as array formula for more than 2 data sets"""
    return x.corr()


@xw.func
@xw.arg('x', pd.DataFrame)
@xw.ret(index=False)
def myfunction(x):
   # x is a DataFrame, do something with it
   return x


import numpy as np

@xw.func
@xw.ret(expand='table')
def dynamic_array(r, c):
    return np.random.randn(int(r), int(c))


