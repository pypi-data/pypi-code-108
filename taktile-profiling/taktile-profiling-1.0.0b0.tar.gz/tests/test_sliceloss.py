from datetime import datetime

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from profiling.sliceloss import slice_loss_cat, slice_loss_datetime, slice_loss_num


def predict(df):
    return pd.Series(data=np.ones(len(df)), index=df.index).astype(int)


X_unique_vals = pd.DataFrame(
    {
        "num": np.arange(1, 10),
        "cat": np.arange(1, 10),
        "time": pd.date_range("2021", freq="D", periods=9),
    }
).astype({"num": "int64", "cat": "category", "time": "datetime64[ns]"})

y_unique_vals = pd.Series(
    data=np.concatenate([np.zeros(4), np.ones(5)]), index=X_unique_vals.index
).astype(int)

pred_unique_vals = pd.DataFrame(
    {
        "num": X_unique_vals["num"].unique(),
        "cat": X_unique_vals["cat"].cat.categories,
        "time": X_unique_vals["time"].unique(),
        "Accuracy": np.concatenate([np.zeros(4), np.ones(5)]),
        "Counts": np.ones(9),
    },
).astype(
    {"num": "int64", "cat": "category", "time": "datetime64[ns]", "Counts": "int64"}
)


X_repeated_vals = pd.DataFrame(
    {
        "num": np.concatenate([[1] * 15, [2] * 30, [3] * 60, [4] * 30, [5] * 15]),
        "cat": np.concatenate([[1] * 15, [2] * 30, [3] * 60, [4] * 30, [5] * 15]),
        "time": np.concatenate(
            [
                [datetime(2021, 1, 1)] * 15,
                [datetime(2021, 1, 2)] * 30,
                [datetime(2021, 1, 3)] * 60,
                [datetime(2021, 1, 4)] * 30,
                [datetime(2021, 1, 5)] * 15,
            ]
        ),
    }
).astype({"num": "int64", "cat": "category", "time": "datetime64[ns]"})

y_repeated_vals = pd.Series(
    data=np.concatenate(
        [
            np.zeros(15),
            np.ones(15),
            np.zeros(15),
            np.ones(15),
            np.zeros(45),
            np.zeros(5),
            np.ones(25),
            np.ones(3),
            np.zeros(12),
        ]
    ),
    index=X_repeated_vals.index,
).astype(int)

pred_repeated_values = pd.DataFrame(
    {
        "num": X_repeated_vals["num"].unique(),
        "cat": X_repeated_vals["cat"].cat.categories,
        "time": X_repeated_vals["time"].unique(),
        "Accuracy": [0, 0.5, 0.25, 5 / 6, 0.2],
        "Counts": [15, 30, 60, 30, 15],
    }
).astype(
    {"num": "int64", "cat": "category", "time": "datetime64[ns]", "Counts": "int64"}
)


@pytest.mark.parametrize(
    "func, x, y, pred",
    [
        (predict, X_unique_vals, y_unique_vals, pred_unique_vals),
        (predict, X_repeated_vals, y_repeated_vals, pred_repeated_values),
    ],
)
def test_slice_loss_num(func, x, y, pred):

    data = slice_loss_num(func, x, y, "num", "Accuracy").data
    pred_num = pred[["num", "Accuracy", "Counts"]]
    assert_frame_equal(data, pred_num)


@pytest.mark.parametrize(
    "func, x, y, pred",
    [
        (predict, X_unique_vals, y_unique_vals, pred_unique_vals),
        (predict, X_repeated_vals, y_repeated_vals, pred_repeated_values),
    ],
)
def test_slice_loss_cat(func, x, y, pred):

    data = slice_loss_cat(func, x, y, "cat", "Accuracy").data.sort_values(by="cat")
    pred_cat = pred[["cat", "Accuracy", "Counts"]]
    assert_frame_equal(data, pred_cat)


@pytest.mark.parametrize(
    "func, x, y, pred",
    [
        (predict, X_unique_vals, y_unique_vals, pred_unique_vals),
        (predict, X_repeated_vals, y_repeated_vals, pred_repeated_values),
    ],
)
def test_slice_loss_datetime(func, x, y, pred):

    data = slice_loss_datetime(func, x, y, "time", "Accuracy").data.sort_values(
        by="time"
    )
    pred_time = pred[["time", "Accuracy", "Counts"]]
    assert_frame_equal(data, pred_time)
