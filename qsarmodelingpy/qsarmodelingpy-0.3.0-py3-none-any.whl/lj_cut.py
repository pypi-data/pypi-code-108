r"""Implements a data transformation for Lennard-Jones data. When some calculation point happens to be "inside" an atom, Lennard-Jones interaction goes to infinity. This module implement a workaround using a logarithm to encode values greater than a limit `cut`.
"""
import numpy as np
import math


def ljCut(value, cut):
    calValue = value/4.18
    if calValue >= cut:
        calValue = cut + math.log10(calValue-(cut-1))
    calValue = calValue*4.18
    return calValue


def transform(dfLj):
    m, n = dfLj.shape
    for i in range(m):
        for j in range(n):
            dfLj.values[i, j] = ljCut(dfLj.values[i, j], 30)
    return dfLj
