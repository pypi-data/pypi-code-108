import numpy as np
import pandas as pd

from profiling.expectations import condexp_num

X = pd.DataFrame.from_dict(
    {
        "Single Value": pd.Series([0]),
        "Integer": pd.Series(list(range(11)) + 100 * [0], dtype="int64"),
        "Large Integer": pd.Series(list(range(11)) + 100 * [1e9], dtype="int64"),
    }
)

y = pd.Series(np.random.uniform(size=len(X)))


def predict(X):
    return pd.Series([0] * len(X))


def test_condexp():
    condexp_num(func=predict, x=X, y=y, var="Integer")
    condexp_num(func=predict, x=X, y=y, var="Large Integer")
