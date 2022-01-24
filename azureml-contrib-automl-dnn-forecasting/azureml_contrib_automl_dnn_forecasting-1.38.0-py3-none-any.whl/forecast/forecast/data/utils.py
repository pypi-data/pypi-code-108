"""Utilities which are useful for creating and preparing datasets."""

from __future__ import annotations

import datetime as dt
from typing import List, Optional, Tuple, TypeVar

import numpy as np
import pandas as pd


def split_by_dt(data: pd.DataFrame,
                split_dt: dt.datetime,
                window_size: int,
                dt_field: Optional[str] = None) -> Tuple[np.ndarray, np.ndarray]:
    """Splits a DataFrame into two pieces at a given point in time with `window_size` overlap.

    Parameters:
    ----------
    data: pd.DataFrame
        The DataFrame containing the data
    split_dt: dt.datetime
        The date at which to split
    window_size: int
        The amount of overlap requested
    dt_field: str
        The column name of the datetime field in `data`

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Two overlapping arrays of data

    """
    # ensure the date_field is set
    if not dt_field:
        dt_field = 'date'

    # find the index corresponding to the split date
    test_ind = data[data[dt_field] >= split_dt].index[0]

    # re-index by date
    data = data.set_index(dt_field)

    # convert to np.ndarray, and reshape to (1, features, TS_length)
    arr = data.values
    arr = np.expand_dims(arr.T, 0)

    # split at the index
    data_train, data_test = [], []
    for time_series in arr:
        data_train.append(time_series[:, :test_ind],)
        data_test.append(time_series[:, test_ind - window_size:])

    # convert to np.ndarray
    data_train = np.array(data_train)
    data_test = np.array(data_test)
    return data_train, data_test


def split_by_count(df: pd.DataFrame, num_test_samples: int, window_size: int) -> Tuple[np.ndarray, np.ndarray]:
    """Splits a `pd.DataFrame` such that the last `num_test_samples` are only present in the test set.

    Note: An overlap of min(window_size, TS_LEN - num_test_samples) will be present in the two `np.ndarray`s to allow
    for predictions on the test set.

    Parameters:
    -----------
    df: pd.DataFrame
        A DataFrame whose index are timestamps and whose columns are features. If multiple time series are present,
        the index should be a MultiIndex with level 0 being the time series identifier and level 1 being the timestamp
        itself. In this case, it is assumed that each time series will be of the same length. Regardless of the number
        of time series, ordering of data is preserved across all dimensions.
    num_test_samples: int
        The number of samples to exclude from the training set (i.e., only include in the test set).
    window_size: int
        The number of samples required for prediction. This defines the overlap between the train and test sets, which
        is used to make predictions on the non-overlapping number of samples specified by `num_test_samples`.

    Returns:
    --------
    Tuple[np.ndarray, np.ndarray]
        The train and test sets respectively. Each `np.ndarray` is of shape [NUM_TS, NUM_FEATURES, NUM_SAMPLES].

    """
    # split by last N (including window_size overlap in test data)
    num_ts = len(df.index.levels[0]) if df.index.nlevels > 1 else 1
    ts_len = len(df.loc[df.index.levels[0][0]]) if df.index.nlevels > 1 else len(df.index)

    # validate that all TS are of the same length and sufficiently long
    if num_ts > 1:
        assert df.groupby(level=0).size().nunique() == 1, 'All time series must be of the same length'
    assert num_test_samples < ts_len, 'Requested test length must be less than time series length'

    train_len = ts_len - num_test_samples
    test_len = min(ts_len, num_test_samples + window_size)

    train_data = df.loc[([True] * train_len + [False] * num_test_samples) * num_ts]
    test_data = df.loc[([False] * (ts_len - test_len) + [True] * test_len) * num_ts]

    # a dataset expects (TS, features, time); convert to (TS, time, features) as an intermediate step
    n_feat = len(df.columns)
    train_data = train_data.to_numpy(np.float32).reshape(num_ts, train_len, n_feat)
    test_data = test_data.to_numpy(np.float32).reshape(num_ts, test_len, n_feat)

    # reshape
    train_data = np.swapaxes(train_data, 1, 2)
    test_data = np.swapaxes(test_data, 1, 2)
    return train_data, test_data


def ragged_split_by_count(
        df: pd.DataFrame,
        num_test_samples: int,
        window_size: int,
        pad: bool = True,
        dtype: str = "float32",
) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    """Splits a `pd.DataFrame` such that the last `num_test_samples` are only present in the val/test set.

    Note: An overlap of min(window_size, TS_LEN - num_test_samples) will be present in the two `np.ndarray`s to allow
    for predictions on the test set.

    Unlike split_by_count, this method allows for each group to have different numbers of elements.

    Parameters:
    -----------
    df: pd.DataFrame
        A DataFrame with a MultiIndex, level 0 being the time series identifier and level 1 being the timestamp
        itself. Regardless of the number of time series, ordering of data is preserved across all dimensions.
    num_test_samples: int
        The number of samples to exclude from the training set (i.e., only include in the test set).
    window_size: int
        The number of samples required for prediction. This defines the overlap between the train and test sets, which
        is used to make predictions on the non-overlapping number of samples specified by `num_test_samples`.
    pad: bool, optional
        If True, drops series which are shorter than num_test_samples. If False, drops series which are shorter than
        window_size + num_test_samples.

    Returns:
    --------
    Tuple[List[np.ndarray], List[np.ndarray]]
        The train and val/test sets respectively. Each list is of len NUM_TS and each `np.ndarray` is of shape
        [NUM_FEATURES, NUM_SAMPLES].

    """
    if df.index.nlevels != 2:
        raise ValueError("Index must contain two levels, the 1st being the # of series and the 2nd being the time.")

    # drop series which are too short
    min_len = num_test_samples + 1 if pad else num_test_samples + window_size
    filtered = df.groupby(level=0).filter(lambda grp: len(grp) >= min_len)

    valtest_df = filtered.groupby(level=0).tail(num_test_samples + window_size)  # include part of train for prediction
    train_df = filtered.groupby(level=0).apply(lambda grp: grp.head(len(grp) - num_test_samples))

    train = [d.to_numpy(dtype=dtype).T for _, d in train_df.groupby(level=0)]
    valtest = [d.to_numpy(dtype=dtype).T for _, d in valtest_df.groupby(level=0)]
    return train, valtest


ArrayLike = TypeVar("ArrayLike", np.ndarray, List[np.ndarray])


def to_float32(x: ArrayLike) -> ArrayLike:
    if isinstance(x, np.ndarray):
        return x.astype(np.float32)
    else:
        return [x_.astype(np.float32) for x_ in x]
