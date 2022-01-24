import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal, assert_series_equal

from profiling.countplot import (
    countplot_cat,
    countplot_datetime,
    countplot_num,
    get_bins,
    trim_outliers,
)


def test_get_bins():
    X_num = pd.Series(
        data=np.concatenate([np.arange(1, 26), np.arange(5, 21)]),
        dtype="Int64",
        name="num",
    )

    X_num_binned = pd.DataFrame(
        {
            "num": pd.Categorical(
                [
                    13.0,
                    10.12,
                    18.76,
                    17.8,
                    16.84,
                    15.88,
                    14.92,
                    13.96,
                    12.04,
                    11.08,
                    9.16,
                    8.2,
                    7.24,
                    6.28,
                    5.32,
                    19.72,
                    20.68,
                    21.64,
                    22.6,
                    23.56,
                    1.468,
                    2.44,
                    4.36,
                    3.4,
                    24.52,
                ],
                ordered=True,
            ),
            "Counts": np.concatenate([[2] * 16, [1] * 9]),
        }
    )

    assert_frame_equal(
        get_bins(X_num), X_num_binned, check_exact=False, check_categorical=False
    )


def test_trim_outliers():
    X_norm = pd.Series([i for i in range(1, 100)], name="var")
    outliers = pd.Series([pow(10, 4), -1 * pow(10, 4)], name="var")
    X_outliers = pd.concat([X_norm, outliers])

    X_trimmed = trim_outliers(X_outliers)
    assert_series_equal(X_trimmed, X_norm)


X = pd.DataFrame(
    {
        "num": np.concatenate([[10] * 10, [20] * 30, [30] * 40, [-10000]]),
        "cat_ordered": pd.Categorical(
            np.concatenate([[1, 2, 3, 4, 5, 6] * 13, [1, 2, 3]]),
            categories=np.arange(1, 7),
            ordered=True,
        ),
        "cat_unordered": pd.Categorical(
            np.concatenate([["a"] * 5, ["b"] * 10, ["c"] * 66]),
            categories=["b", "c", "a"],
            ordered=False,
        ),
        "datetimes": np.concatenate(
            [
                pd.date_range("2021", freq="D", periods=60).values,
                pd.date_range("2021", freq="D", periods=15).values,
                pd.date_range("2021", freq="D", periods=5).values,
                pd.date_range("2080", freq="D", periods=1).values,
            ]
        ),
    }
).astype({"num": "int64", "datetimes": "<M8[ns]"})

count_num = pd.DataFrame(
    {"num": pd.Categorical([29.60, 20, 10.39], ordered=True,), "Counts": [40, 30, 10],}
)  # slight change in data when calculating bin midpoint
count_cat_unordered = pd.DataFrame(
    {
        "cat_unordered": pd.Categorical(
            ["c", "b", "a"], categories=["b", "c", "a"], ordered=False
        ),
        "Counts": [66, 10, 5],
    }
)
count_cat_ordered = pd.DataFrame(
    {
        "cat_ordered": pd.Categorical(
            [1, 2, 3, 4, 5, 6], categories=[1, 2, 3, 4, 5, 6], ordered=True,
        ),
        "Counts": np.concatenate([3 * [14], 3 * [13]]),
    }
)  #  cut due to n_categories, ordering changed but corrected in final plot
count_datetime = pd.DataFrame(
    {
        "datetimes": [
            "2021-01-02T03:36:43.200000000",
            "2021-01-06T21:36:00.000000000",
            "2021-01-13T23:31:12.000000000",
            "2021-01-04T12:57:36.000000000",
            "2021-01-09T06:14:24.000000000",
            "2021-01-11T14:52:48.000000000",
            "2021-01-28T03:21:36.000000000",
            "2021-02-23T02:24:00.000000000",
            "2021-02-16T00:28:48.000000000",
            "2021-02-08T22:33:36.000000000",
            "2021-02-01T20:38:24.000000000",
            "2021-02-27T19:40:48.000000000",
            "2021-01-21T01:26:24.000000000",
            "2021-01-25T18:43:12.000000000",
            "2021-01-23T10:04:48.000000000",
            "2021-02-04T05:16:48.000000000",
            "2021-02-06T13:55:12.000000000",
            "2021-02-11T07:12:00.000000000",
            "2021-02-13T15:50:24.000000000",
            "2021-01-18T16:48:00.000000000",
            "2021-02-18T09:07:12.000000000",
            "2021-02-20T17:45:36.000000000",
            "2021-01-16T08:09:36.000000000",
            "2021-02-25T11:02:24.000000000",
            "2021-01-30T12:00:00.000000000",
        ],
        "Counts": np.concatenate([1 * [9], 3 * [6], 2 * [4], 7 * [3], 12 * [2]]),
    }
).astype({"datetimes": "<M8[ns]"})


@pytest.mark.parametrize(
    "countplot_func, x_var, count_df",
    [
        (countplot_num, X["num"], count_num),
        (countplot_cat, X["cat_ordered"], count_cat_ordered),
        (countplot_cat, X["cat_unordered"], count_cat_unordered),
        (countplot_datetime, X["datetimes"], count_datetime),
    ],
)
def test_countplot_data(countplot_func, x_var, count_df):
    count_determined = countplot_func(x_var).data.query("Counts>0")
    assert_frame_equal(
        count_determined, count_df, check_exact=False, check_categorical=False
    )


def test_nunique_num_regression():
    """Regression test for countplot nunique==1 failure case numerical columns."""
    _ = countplot_num(pd.Series([1, 1, 1, 1, 1], name="float_col"))


def test_nunique_datetime_regression():
    """Regression test for countplot nunique==1 failure case datetime columns."""
    _ = countplot_datetime(
        pd.Series(
            [
                "2021-01-01T01:00:00",
                "2021-01-01T01:00:00",
                "2021-01-01T01:00:00",
                "2021-01-01T01:00:00",
                "2021-01-01T01:00:00",
            ],
            name="datatime_col",
        ).astype("<M8[ns]")
    )
