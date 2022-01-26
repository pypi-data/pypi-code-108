import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from tktl import Tktl

# Generate test data
from tktl.registration.validation import (
    get_input_and_output_for_profiling,
    input_pandas_representation,
    output_pandas_representation,
)

from profiling.convenience import (
    BASE_RESULTS_PATH,
    create_accuracy,
    create_countplot,
    create_dependence,
    create_expectations,
    create_importance,
    create_slice_loss,
)
from profiling.utils import vega_sanitize

X = pd.DataFrame.from_dict(
    {
        "Integer": pd.Series([1, 2, 3], dtype="int64"),
        "Float": pd.Series([None, 2.0, 3.0], dtype="float64"),
        "Object": pd.Series([None, "", "c"], dtype="object"),
        "Bool": pd.Series([True, False, True], dtype="bool"),
        "Categorical": pd.Series(["a", "b", None], dtype="category"),
        "Datetime": pd.Series(
            ["2020-01-01", None, "2020-01-03"], dtype="datetime64[ns]"
        ),
    }
)
X_unsanitized = X.rename(columns={col: col + ".Var-[Brackets]" for col in X.columns})
y_regression = pd.Series([5, 3.2, -0.2], name="Outcome")
y_binary = pd.Series([True, False, True], name="Outcome")

# Instantiate client and generate test endpoints
tktl = Tktl()


@tktl.endpoint(kind="regression", X=X, y=y_regression)
def regression(X):
    return np.random.uniform(size=len(X))


@tktl.endpoint(kind="binary", X=X, y=y_binary)
def binary(X):
    return np.random.uniform(size=len(X))


@tktl.endpoint(kind="binary", X=X, y=y_binary)
def type_sensitive(df):
    assert X.dtypes.equals(df.dtypes)  # ensure types never change during profiling
    return np.random.uniform(size=len(df))


@tktl.endpoint(kind="binary", X=X_unsanitized, y=y_binary)
def unsanitized(X):
    return np.random.uniform(size=len(X))


def test_expectations():
    for endpoint in tktl.endpoints:
        name = endpoint.func.__name__
        x_raw = input_pandas_representation(
            value=endpoint.input_schema.value, reset_index=False
        )
        y_raw = output_pandas_representation(
            value=endpoint.output_schema.value, reset_index=False
        )
        x, y = get_input_and_output_for_profiling(x=x_raw, y=y_raw)
        create_expectations(
            func=endpoint.series_func,
            x=x,
            y=y,
            endpoint_name=name,
            profile_columns=endpoint.profile_columns,
        )

        for var in x.columns:
            path = Path(BASE_RESULTS_PATH, name, "anatomy", "condexp", var + ".json")
            assert path.exists()
    shutil.rmtree(BASE_RESULTS_PATH)


def test_dependence():
    for endpoint in tktl.endpoints:
        name = endpoint.func.__name__
        x_raw = input_pandas_representation(
            value=endpoint.input_schema.value, reset_index=False
        )
        y_raw = output_pandas_representation(
            value=endpoint.output_schema.value, reset_index=False
        )
        x, y = get_input_and_output_for_profiling(x=x_raw, y=y_raw)
        create_dependence(
            func=endpoint.series_func,
            x=x,
            endpoint_name=name,
            profile_columns=endpoint.profile_columns,
        )
        for var in x.columns:
            path = Path(BASE_RESULTS_PATH, name, "anatomy", "partialdep", var + ".json")
            assert path.exists()
    shutil.rmtree(BASE_RESULTS_PATH)


def test_sliceloss():
    for endpoint in tktl.endpoints:
        name = endpoint.func.__name__
        x_raw = input_pandas_representation(
            value=endpoint.input_schema.value, reset_index=False
        )
        y_raw = output_pandas_representation(
            value=endpoint.output_schema.value, reset_index=False
        )
        x, y = get_input_and_output_for_profiling(x=x_raw, y=y_raw)
        create_slice_loss(
            func=endpoint.series_func,
            x=x,
            y=y,
            endpoint_name=name,
            profile_columns=endpoint.profile_columns,
            kind=endpoint.KIND.value,
        )

        for var in x.columns:
            path = Path(BASE_RESULTS_PATH, name, "anatomy", "sliceloss", var + ".json")
            assert path.exists()
    shutil.rmtree(BASE_RESULTS_PATH)


def test_countplot():
    for endpoint in tktl.endpoints:
        name = endpoint.func.__name__
        x_raw = input_pandas_representation(
            value=endpoint.input_schema.value, reset_index=False
        )
        y_raw = output_pandas_representation(
            value=endpoint.output_schema.value, reset_index=False
        )
        x, y = get_input_and_output_for_profiling(x=x_raw, y=y_raw)
        create_countplot(
            x=x, endpoint_name=name, profile_columns=endpoint.profile_columns,
        )

        for var in x.columns:
            print(var)
            path = Path(BASE_RESULTS_PATH, name, "anatomy", "countplot", var + ".json")
            assert path.exists()
    shutil.rmtree(BASE_RESULTS_PATH)


def test_importance():
    for endpoint in tktl.endpoints:
        name = endpoint.func.__name__
        x_raw = input_pandas_representation(
            value=endpoint.input_schema.value, reset_index=False
        )
        y_raw = output_pandas_representation(
            value=endpoint.output_schema.value, reset_index=False
        )
        x, y = get_input_and_output_for_profiling(x=x_raw, y=y_raw)
        create_importance(
            func=endpoint.series_func,
            x=x,
            endpoint_name=name,
            profile_columns=endpoint.profile_columns,
            kind=endpoint.KIND.value,
        )
        assert Path(BASE_RESULTS_PATH, name, "anatomy", "varimp.json").exists()
    shutil.rmtree(BASE_RESULTS_PATH)


def test_accuracy():
    for endpoint in tktl.endpoints:
        name = endpoint.func.__name__
        x_raw = input_pandas_representation(
            value=endpoint.input_schema.value, reset_index=False
        )
        y_raw = output_pandas_representation(
            value=endpoint.output_schema.value, reset_index=False
        )
        x, y = get_input_and_output_for_profiling(x=x_raw, y=y_raw)
        create_accuracy(
            func=endpoint.series_func,
            x=x,
            y=y,
            endpoint_name=name,
            profile_columns=endpoint.profile_columns,
            kind=endpoint.KIND.value,
        )
        assert Path(BASE_RESULTS_PATH, name, "accuracy", "calibration.json").exists()
        assert Path(BASE_RESULTS_PATH, name, "accuracy", "metrics.json").exists()
        assert Path(BASE_RESULTS_PATH, name, "accuracy", "errors.json").exists()
        if endpoint.KIND.value == "binary":
            assert Path(BASE_RESULTS_PATH, name, "accuracy", "roc_curve.json").exists()
    shutil.rmtree(BASE_RESULTS_PATH)


@pytest.mark.parametrize(
    "var,expected",
    [(".", r"\."), ("[", r"\["), ("Var.Unsanitized[1]-.", r"Var\.Unsanitized\[1\]-\.")],
)
def test_sanitize(var, expected):
    var_sanitized = vega_sanitize(var)
    assert var_sanitized == expected
