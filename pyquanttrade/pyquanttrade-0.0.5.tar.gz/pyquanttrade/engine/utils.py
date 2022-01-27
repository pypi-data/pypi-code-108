# -*- coding: utf-8 -*-
"""Functions from market data"""

__author__ = "Miguel Martin"
__version__ = "1"

import numpy as np

# Get maximum drawdown of Serie
def max_drawdown_value(vec):
    maximums = np.maximum.accumulate(vec)
    drawdowns = maximums - vec
    return np.max(drawdowns)


def max_drawdown_ratio(vec):
    maximums = np.maximum.accumulate(vec)
    drawdowns = 1 - vec / maximums
    return np.max(drawdowns)


# Safe sum. If list is empty return Nan
def safe_sum(l):
    if len(l) == 0:
        return np.NaN
    return np.sum(l)


# Safe div. If list is empty return Nan
def safe_div(a, b):
    if b == 0:
        return np.NaN
    return a / b


# Safe min. If list is empty return Nan
def safe_min(l):
    if len(l) == 0:
        return 0
    return -np.min(l)


def safe_mean(l):
    if len(l) == 0:
        return np.NaN
    return np.mean(l)
