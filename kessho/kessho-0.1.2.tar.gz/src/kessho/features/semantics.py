"""
This module contains functions and classes that extract somewhat heuristic semantics from given data
"""

import datetime as dt
from itertools import accumulate
import numpy as np
import pandas as pd


def seasonality(day: dt.date, kappa=200.0):
    """
    computes a 12-dim vector that - given a date - computes for each month a value of how 'that-month-ish' the date is.
    This vector is meant to encode the concept of seasonality such that neural networks can grasp it.
    Example: Feb-01 will have the first components high because it's close to Jan still. It will also
    have a higher Dec component because the last December is not so long ago.
    Example: May-15 will be the most May-ish date with little contributions to the neigbouring months.
    Note that this implies a simplified calendar model with all months of length 365/12 days.
    :param day: the day under consideration
    :param kappa: sharpness of the bell curve, 200 is an ok value. Larger values result in more focus.
    """
    doy = (day - day.replace(day=1, month=1)).days
    return [sum([np.exp(-kappa*(doy/365.-(n+.5)/12.+i)**2) for i in [-1, 0, 1]]) for n in range(12)]


def ema_rema(df, column, smooth=2.0, periods=None, inplace: bool = False,
             decimals=3,
             rema: bool = False) -> pd.DataFrame:
    """
    For a given pandas Dataframe, computes exponential moving averages
    :param df: the original dataframe of daily data
    :param column: the target column to compute the EMAs from
    :param smooth: A smoothing factor. Industry practice suggests 2.0
    :param periods: array of periods in units of days
    :param inplace: whether or not to write into the given dataframe,
    :param decimals: decimals for rounding
    :param rema: whether or not to compute relative EMAs
    """
    periods = periods or [1, 2, 3, 5, 8, 13, 21, 34]
    pairs = zip(periods[:-1], periods[1:])
    if not inplace:
        df = df.copy()

    df.dropna(inplace=True)

    for period in periods:
        df[f'ema_{column}_{period}'] = list(accumulate(df[column],
                                                       lambda x, y: round(
                                                           x * (1. - smooth / (1. + 5 * period)) +
                                                           y * smooth / (1. + 5 * period), decimals)))

    if rema:
        for pair in pairs:
            df[f'rema_{column}_{pair[0]}'] = round(df[f'ema_{column}_{pair[0]}'] /
                                                   df[f'ema_{column}_{pair[1]}'], decimals) - 1.

    return df
