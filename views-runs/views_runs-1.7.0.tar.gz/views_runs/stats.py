
from typing import Callable
import numpy as np
import pandas as pd

def resample(x: np.ndarray, prop: float)-> np.ndarray:
    """
    resample
    ========

    parameters:
        x    (numpy.ndarray[bool])
        prop (float)

    returns:
        numpy.ndarray[int]

    Returns indices that can be used to subset a vector, to yield a new vector
    with a given proportion of True values.
    """
    selection_mask = np.full(x.shape[0], True)

    ratio = prop / x.mean()

    if ratio > 1:
        ratio = 1-(ratio - 1)
        to_subset = ~x
    else:
        to_subset = x

    selection_mask[to_subset] = np.random.choice([True, False], to_subset.sum(), p = [ratio, 1-ratio])

    return np.linspace(0,x.shape[0]-1, x.shape[0], dtype = int)[selection_mask]

def resample_df(
        dataframe: pd.DataFrame,
        prop: float,
        column: str,
        key: Callable[[np.ndarray], np.ndarray] = lambda x: x > 0)-> pd.DataFrame:
    """
    resample_df
    ===========

    parameters:
        dataframe (pandas.DataFrame)
        prop      (float)
        column    (str)
        key       (Callable[[np.ndarray[Any]], np.ndarray[bool]])

    Resamples a dataframe to have a given proportion of values that return true
    after a key function is called The default key function is x > 0.
    """

    return dataframe.loc[resample(key(dataframe[column]), prop)]

