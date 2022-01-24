import itertools
import math
from datetime import date, datetime
from itertools import permutations

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from profiling.shap import ShapExplainer, comb, n_choose_k, reduce_func, update_columns
from profiling.utils import batched_non_object_col_mode, batched_numeric_col_mean


@pytest.mark.parametrize("n_cols", [1, 2, 3, 4])
def test_coalitions(n_cols):
    """Test construction of coalitions"""
    np.random.seed(1986)
    X = pd.DataFrame(np.random.normal(size=(1, n_cols)))

    def func(x):
        coef = np.ones(len(x))
        return x @ coef

    shap_explainer = ShapExplainer(func, X)
    coalitions = shap_explainer._sample_coalitions(len(X.columns))
    coalitions_expected = set(permutations([False, True] * (n_cols - 1), r=n_cols))
    assert coalitions == coalitions_expected


@pytest.mark.parametrize("coef", [[0], [1], [0.25, 0.5, 0, 0]])
def test_coefficient_recovery(coef):
    """Test that SHAP converges to coefficients in linear model"""
    np.random.seed(1986)
    X = pd.DataFrame(np.zeros(shape=(1, len(coef))))
    intercept = 5.23

    def func(X):
        return X.values @ coef + intercept

    shap_explainer = ShapExplainer(func, X)
    test_row = pd.DataFrame(np.ones((1, len(X.columns))), columns=X.columns)
    ref, shap = shap_explainer.explain(test_row)
    assert np.allclose(ref, intercept)  # reference
    assert np.allclose(shap, coef)  # shapley values
    assert np.allclose(ref + shap.sum(axis=1), func(test_row))  # bookkeeping


def test_large_df():
    """Test that SHAP runs smoothly on large dataframes"""
    np.random.seed(1986)
    n_col = 10
    n_row = 10000
    coef = np.random.randn(n_col)
    X = pd.DataFrame(np.zeros((n_row, n_col)))
    intercept = 5.23

    def func(X):
        return X.values @ coef + intercept

    shap_explainer = ShapExplainer(func, X)
    test_row = pd.DataFrame(np.ones((1, len(X.columns))), columns=X.columns)
    ref, shap = shap_explainer.explain(test_row)
    assert np.allclose(ref, intercept)  # reference
    assert np.allclose(shap, coef)  # shapley values
    assert np.allclose(ref + shap.sum(axis=1), func(test_row))  # bookkeeping


def test_batch():
    """Test that SHAP works in batch mode"""
    np.random.seed(1986)
    coef = [0.5, 0.5, 0, 0]
    X = pd.DataFrame(np.random.randn(10000, len(coef)))
    intercept = 5.23

    def func(X):
        return X.values @ coef + intercept

    shap_explainer = ShapExplainer(func, X)
    n_row = 10
    test_df = X.iloc[:n_row]
    ref, shap = shap_explainer.explain(test_df)
    assert isinstance(ref, pd.Series)
    assert isinstance(shap, pd.DataFrame)
    assert ref.shape == (n_row,)
    assert shap.shape == (n_row, len(coef))
    assert np.allclose(ref + shap.sum(axis=1), func(test_df))  # bookkeeping


def test_various_coltypes():
    X = pd.DataFrame.from_dict(
        {
            "Integer": [1, 2, 3],
            "Float": [None, 2.0, 3.0],
            "Object": [None, "", "c"],
            "Categorical": ["a", "b", "c"],
            "Date": [date(2020, 1, 1), date(2020, 1, 2), date(2020, 1, 3)],
            "Datetime": [datetime(2020, 1, 1), None, datetime(2020, 1, 3)],
            "Nullable Int64": pd.array([1, 3, None], dtype="Int64"),
        }
    )
    X = X.astype({"Categorical": "category"})

    def regression(x: pd.DataFrame) -> pd.Series:
        return pd.Series(np.random.uniform(size=len(x)))

    shap_explainer = ShapExplainer(func=regression, x=X)
    _, _ = shap_explainer.explain(X)


def test_comb():
    """Test n_choose_k and comb function"""
    assert n_choose_k(1, 1) == 1
    assert n_choose_k(2, 1) == 2
    assert n_choose_k(2, 2) == 1
    assert n_choose_k(4, 2) == 6
    assert n_choose_k(100, 50) == 100891344545564193334812497256
    assert np.array_equal(comb(3, np.array([1, 2, 3])), np.array([3, 3, 1]))


def test_background_data():
    """Test background data computation"""
    data = pd.DataFrame(
        {
            "Float": [1, 2.1, 2.3],
            "Repeated Values": [1, 1, 1],
            "Float with Nones": [None, 1.0, None],
            "Float with NaNs": [float("NaN"), 1.0, None],
            "Object": ["a", "c", "c"],
            "Object with Nones": [None, None, "c"],
            "Only NaNs": [float("NaN"), float("NaN"), float("NaN")],
            "Nullable Int64": pd.array([1, 3, None], dtype="Int64"),
            "Nullable Int8": pd.array([1, 3, None], dtype="Int8"),
            "Empty Nullable": pd.array([None, None, None], dtype="Int64"),
        }
    )

    expected = pd.DataFrame(
        {
            "Float": [1.8],
            "Repeated Values": [1],
            "Float with Nones": [1.0],
            "Float with NaNs": [1.0],
            "Object": ["c"],
            "Object with Nones": ["c"],
            "Only NaNs": [float("NaN")],
            "Nullable Int64": pd.array([2], dtype="Int64"),
            "Nullable Int8": pd.array([2], dtype="Int8"),
            "Empty Nullable": pd.array([pd.NA], dtype="Int64"),
        }
    )
    x_batched_init, x_batched = itertools.tee((data for _ in range(4)), 2)
    x_full = pd.concat([data for _ in range(4)])

    y_batched_init, y_batched = itertools.tee(
        (pd.Series([1, 1, 1]) for _ in range(4)), 2
    )

    full_explainer = ShapExplainer(func=lambda x: x, x=x_full)
    batched_explainer = ShapExplainer(
        func=lambda x: x, x=x_batched_init, y=y_batched_init
    )
    result_from_x_full = full_explainer._create_background_data(x_full)
    result_from_x_batched = batched_explainer._create_background_data(
        x_batched, y=y_batched
    )

    assert_frame_equal(result_from_x_full, expected)
    assert_frame_equal(result_from_x_batched, expected)


def test_mapping():
    X = pd.DataFrame.from_dict({"Integer": [3, 2, 2], "Categorical": ["a", "a", "b"]})
    X = X.astype({"Categorical": "category"})

    def regression(x):
        return pd.Series(np.random.uniform(size=len(x)))

    shap_explainer = ShapExplainer(func=regression, x=X)
    test_row = pd.DataFrame({"Integer": [5], "Categorical": ["d"]}).astype(X.dtypes)

    # full coalition
    coalition = {(True, True)}
    mapped_features = shap_explainer._map_features(coalition, test_row)
    expected = test_row
    assert mapped_features.equals(expected)

    # empty coalition
    coalition = {(False, False)}
    mapped_features = shap_explainer._map_features(coalition, test_row)
    expected = shap_explainer.x  # background dataset
    assert mapped_features.equals(expected)

    # mixed coalitions
    coalition = {(False, True)}
    mapped_features = shap_explainer._map_features(coalition, test_row)
    expected = pd.DataFrame({"Integer": [2], "Categorical": ["d"]}).astype(X.dtypes)
    assert mapped_features.equals(expected)

    coalition = {(True, False)}
    mapped_features = shap_explainer._map_features(coalition, test_row)
    expected = pd.DataFrame({"Integer": [5], "Categorical": ["a"]}).astype(X.dtypes)
    assert mapped_features.equals(expected)


def test_axioms():
    """Test Missingness, Local Accuracy, and Consistency properties of Shapley values"""
    np.random.seed(1986)
    n_col = 3
    X = pd.DataFrame(np.random.normal(size=(10000, n_col)))

    def func0(x):
        return x.loc[:, 0] * x.loc[:, 1] ** 2

    def func1(x):
        return x.loc[:, 0] * x.loc[:, 1] ** 2 + x.loc[:, 0].abs()

    explainer0 = ShapExplainer(func0, X)
    explainer1 = ShapExplainer(func1, X)

    test_row = pd.DataFrame(np.ones(shape=(1, n_col)))
    ref0, shap0 = explainer0.explain(test_row)
    ref1, shap1 = explainer1.explain(test_row)

    # missingness
    assert np.isclose(shap0[2], 0)
    assert np.isclose(shap1[2], 0)

    # local accuracy
    assert np.isclose(ref0 + np.sum(shap0, axis=1), func0(test_row))
    assert np.isclose(ref1 + np.sum(shap1, axis=1), func1(test_row))

    # consistency
    assert np.all(shap0[0] < shap1[0])
    assert np.all(shap0 < shap1 + 1e-9)


def test_profile_columns():
    """Test Shapley value calculation for a subset of columns"""
    np.random.seed(1986)
    n_col = 10
    n_row = 1000
    coef = np.random.randn(n_col)
    X = pd.DataFrame(np.zeros(shape=(n_row, n_col)))
    intercept = 5.23

    def func(x):
        return x.values @ coef + intercept

    profile_columns = X.columns[:-1]
    shap_explainer = ShapExplainer(func, X, profile_columns=profile_columns)
    test_row = pd.DataFrame(
        np.ones(shape=(1, len(profile_columns))), columns=profile_columns
    )
    ref, shap = shap_explainer.explain(test_row)
    assert np.allclose(ref, intercept)  # reference
    assert np.allclose(shap, coef[:-1])  # shapley values
    assert np.allclose(
        ref + shap.sum(axis=1), shap_explainer.func(test_row)
    )  # bookkeeping


def test_update_columns():
    # base case
    base = pd.DataFrame({"a": [1]})
    update = pd.DataFrame({"a": [2]})
    expected = pd.DataFrame({"a": [2]})
    result = update_columns(base, update)
    assert result.equals(expected)

    # broadcasting
    base = pd.DataFrame({"a": [1], "b": [True]})
    update = pd.DataFrame({"a": [2, 3]})
    expected = pd.DataFrame({"a": [2, 3], "b": [True, True]})
    result = update_columns(base, update)
    assert result.equals(expected)

    # index mismatch handled gracefully
    base = pd.DataFrame({"a": [1], "b": [True]}, index=[0])
    update = pd.DataFrame({"a": [2, 3]}, index=[1, 2])
    expected = pd.DataFrame({"a": [2, 3], "b": [True, True]}, index=[1, 2])
    result = update_columns(base, update)
    assert result.equals(expected)

    # column mismatch
    with pytest.raises(KeyError):
        base = pd.DataFrame({"a": [1]})
        update = pd.DataFrame({"b": [2, 3]})
        result = update_columns(base, update)


def test_reduce_func():
    X_orig = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    X_subset = X_orig.drop(columns=["a"])

    def predict(x: pd.DataFrame) -> pd.Series:
        assert list(x.columns) == ["a", "b"]
        return pd.Series([0] * len(x))

    with pytest.raises(AssertionError):
        predict(X_subset)

    predict_subset = reduce_func(func=predict, x=X_orig)
    pred = predict_subset(X_subset)
    pd.testing.assert_series_equal(pred, pd.Series([0, 0]))


def test_batched_means():
    x_data = [
        {"a": [1, 3], "b": [3, None]},
        {"a": [1, 3, 1, 0], "b": [3, 2.0, None, 1]},
        {"a": [1, 9], "b": [7, 7]},
    ]
    y_data = [[1, 3, 1, 0], [1, 3]]

    # duplicate iterators
    batched_x_a, batched_x_b = itertools.tee((pd.DataFrame(x) for x in x_data[1:]), 2)
    batched_y_a, batched_y_b = itertools.tee(
        (pd.Series(y, name="y") for y in y_data), 2
    )

    first = pd.DataFrame(x_data[0])

    col_mean = batched_numeric_col_mean(
        x=batched_x_a, y=batched_y_a, first=first, col="a"
    )
    flat_a, flat_b = (
        sum([x["a"] for x in x_data], []),
        sum([x["b"] for x in x_data], []),
    )
    assert col_mean == np.mean([f for f in flat_a if f is not None])
    col_mean = batched_numeric_col_mean(
        x=batched_x_b, y=batched_y_b, first=first, col="b"
    )
    assert col_mean == np.mean([f for f in flat_b if f is not None])


def test_empty_mean():
    x_data = [
        {"a": [None, None], "b": [3, None]},
        {"a": [None, None], "b": [None, None]},
    ]
    y_data = [[1, 2], [1, 3]]

    # duplicate iterators
    batched_x_a, batched_x_b = itertools.tee((pd.DataFrame(x) for x in x_data[1:]), 2)
    batched_y_a, batched_y_b = itertools.tee(
        (pd.Series(y, name="y") for y in y_data), 2
    )

    first = pd.DataFrame(x_data[0])

    col_mean = batched_numeric_col_mean(
        x=batched_x_a, y=batched_y_a, first=first, col="a"
    )
    assert math.isnan(col_mean)
    col_mean = batched_numeric_col_mean(
        x=batched_x_b, y=batched_y_b, first=first, col="b"
    )
    assert col_mean == 3


def test_batched_modes():
    x_data = [{"a": ["A", "A"]}, {"a": ["C", "A"]}, {"a": ["A", "B"]}]
    y_data = [[0, 0], [1, 3]]

    batched_x = (pd.DataFrame(x) for x in x_data[1:])
    batched_y = (pd.Series(y, name="y") for y in y_data)

    first = pd.DataFrame(x_data[0])

    col_mode = batched_non_object_col_mode(
        x=batched_x, y=batched_y, first=first, col="a"
    )
    assert col_mode == "A"


def test_emtpy_modes():
    x_data = [{"a": [None]}, {"a": [None, None]}, {"a": [None, None]}]
    y_data = [[0, 0], [1, 3]]

    batched_x = (pd.DataFrame(x) for x in x_data[1:])
    batched_y = (pd.Series(y, name="y") for y in y_data)

    first = pd.DataFrame(x_data[0])

    col_mode = batched_non_object_col_mode(
        x=batched_x, y=batched_y, first=first, col="a"
    )
    assert col_mode == None
