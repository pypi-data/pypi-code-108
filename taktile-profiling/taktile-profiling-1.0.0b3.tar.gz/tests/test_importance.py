import pandas as pd

from profiling.importance import varimp


def predict_float_column(df):
    """Returns float column"""
    return df["Float"].astype("float")


df = pd.DataFrame.from_dict(
    {
        "Object": [None, "", "a", "b", "c", "d", "e"],
        "Integer": [1, 2, 3, 4, 5, 6, 7],
        "Float": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
        "Categorical": pd.Series(["a", "b", "c", "d", "e", "f", "g"], dtype="category"),
        "Index": ["a", "b", "c", "d", "e", "f", "g"],
    }
).set_index("Index")


def test_order():
    chart, varlist = varimp(predict_float_column, df)
    assert varlist[0] == "Float"
    assert chart.data["Variable"].iloc[0] == "Float"
    assert chart.data["Importance"].iloc[0] > 0
    assert all(chart.data["Importance"].iloc[1:] == 0.0)


def test_subset():
    profile_columns = ["Float", "Integer", "Categorical"]
    _, varlist = varimp(predict_float_column, df, profile_columns=profile_columns)
    assert "Object" not in varlist
    assert "Float" in varlist


def test_metric():
    chart, _ = varimp(predict_float_column, df, metric="Mae")
    assert chart.data["Variable"].iloc[0] == "Float"
