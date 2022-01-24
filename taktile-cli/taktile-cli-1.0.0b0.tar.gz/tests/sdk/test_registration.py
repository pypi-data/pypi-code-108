import random
from typing import Any, Callable, List

import numpy as np
import pandas
import pandas as pd
import pytest
from pydantic import BaseModel

from tktl import Tktl
from tktl.core.exceptions import ValidationException
from tktl.core.utils import DelayedLoaderX, DelayedLoaderY
from tktl.registration.validation import (
    get_input_and_output_for_profiling,
    input_pandas_representation,
    output_pandas_representation,
)


@pytest.mark.parametrize(
    "X,y",
    [
        (pd.DataFrame({"a": [1, 2, 3]}), pd.Series([4, 5, 5])),  # pandas
        (np.array([[1], [2], [3]]), np.array([4, 5, 5])),  # numpy
        ({"a": [1, 2, 3]}, [4, 5, 5]),  # base
    ],
)
def test_creation(X, y):
    tktl = Tktl()

    @tktl.endpoint(X=X, y=y, kind="tabular")
    def predict(X):
        return [0] * 3

    endpoint = tktl.endpoints[0]
    assert endpoint.input_schema.pandas_convertible is True
    assert endpoint.output_schema.pandas_convertible is True
    pred = endpoint.func(pd.DataFrame(X))
    assert pred == [0, 0, 0]


@pytest.mark.parametrize("kind", ["tabular", "regression", "binary"])
def test_tabular_kinds(kind):
    tktl = Tktl()
    X = pd.DataFrame({"a": [1, 2, 3]})
    y = pd.Series([4, 5, 5])

    @tktl.endpoint(X=X, y=y, kind=kind)
    def predict(X):
        return [0] * len(X)

    endpoint = tktl.endpoints[0]
    assert isinstance(endpoint.input_schema.value, pd.DataFrame)
    assert isinstance(endpoint.output_schema.value, pd.Series)
    pred = endpoint.func(pd.DataFrame(X))
    assert pred == [0, 0, 0]


def test_custom_kind():
    tktl = Tktl()

    @tktl.endpoint(kind="custom")
    def predict_untyped(x):
        return x

    @tktl.endpoint(kind="custom", payload_model=Any, response_model=Any)
    def predict_untyped_any(x):
        return x

    class Payload(BaseModel):
        a: List

    class Response(BaseModel):
        a: int
        b: float
        c: List

    @tktl.endpoint(kind="custom", payload_model=Payload, response_model=Response)
    def predict_typed_input_schemas(x):
        return x

    for endpoint in tktl.endpoints:
        assert isinstance(endpoint.func, Callable)
        assert endpoint.func(["foo"]) == ["foo"]

    x = pd.DataFrame([{"a": 1, "b": 2}, {"a": 1, "b": 2}, {"a": 1, "b": 2}])
    y = pd.Series([1, 2, 3])

    @tktl.endpoint(kind="custom", X=x, y=y)
    def predict_typed_input_frames(x):
        return x

    schema = tktl.endpoints[3].input_schema.pydantic.schema()
    assert schema["title"] == "DataFrame__predict_typed_input_frames__input"
    assert schema["example"] == [{"a": 1, "b": 2}]


def test_func_shape():
    tktl = Tktl()
    X = {"a": [1, 2, 3]}
    y = [4, 5, 5]

    @tktl.endpoint(X=X, y=y)
    def predict(X):
        return [0] * (len(X) - 1)

    assert tktl.endpoints[0].profiling_supported is False


def test_input_shape():
    tktl = Tktl()
    X = {"a": [1, 2, 3]}
    y = [4, 5]

    @tktl.endpoint(X=X, y=y)
    def predict(X):
        return [0] * len(X)

    assert tktl.endpoints[0].profiling_supported is False


def test_validate_func():
    tktl = Tktl()

    X = {"a": [1, 2, 3]}
    y = [4, 5, 5]

    @tktl.endpoint(X=X, y=y, kind="regression")
    def predict_regression(X):
        return ["a", "b", "c"]  # must be numeric

    assert tktl.endpoints[0].profiling_supported is False

    tktl = Tktl()
    X = {"a": [1, 2, 3]}
    y = [4, 5, 5]

    with pytest.raises(ValidationException):

        @tktl.endpoint(X=X, y=y, kind="binary")
        def predict_binary(X):
            return [-2, 0, 1.5]  # must be in [0, 1]

        _ = tktl.endpoints[0].profiling_supported


def test_unknown_kind():
    with pytest.raises(ValidationException):
        tktl = Tktl()
        X = {"a": [1, 2, 3]}
        y = [4, 5, 5]

        @tktl.endpoint(X=X, y=y, kind="unknown kind")
        def predict(X):
            return [0] * len(X)


def test_missing():
    tktl = Tktl()
    X = pd.DataFrame({"a": [1, 2, 3]})
    y = pd.Series([0.1, 0.2, None])

    @tktl.endpoint(X=X, y=y, kind="regression")
    def predict(X):
        return [0] * len(X)

    with pytest.warns(UserWarning):
        x_raw = input_pandas_representation(
            value=tktl.endpoints[0].input_schema.value, reset_index=False
        )
        y_raw = output_pandas_representation(
            value=tktl.endpoints[0].output_schema.value, reset_index=False
        )
        get_input_and_output_for_profiling(x=x_raw, y=y_raw)


def test_large():
    tktl = Tktl()
    n = int(1e6) + 1
    X = pd.DataFrame({"a": np.random.uniform(size=n)})
    y = pd.Series(np.random.uniform(size=n))

    with pytest.warns(UserWarning):

        @tktl.endpoint(X=X, y=y, kind="regression")
        def predict(X):
            return [0] * len(X)


def test_custom():
    tktl = Tktl()

    class Payload(BaseModel):
        a: str

    class Response(BaseModel):
        a: str

    @tktl.endpoint(kind="custom", payload_model=Payload, response_model=Response)
    def string_endpoint(x):
        return x


def test_delayed_loaded_frame(create_proj):
    tktl = Tktl()
    path = "sample_project/assets/loans_test.pqt"

    @tktl.endpoint(X=path, y="Repaid", kind="binary")
    def repayment(df):
        return pandas.Series([random.random() for _ in range(len(df))])

    assert tktl.endpoints[0].profiling_supported is True
    input_schema = tktl.endpoints[0].input_schema
    output_schema = tktl.endpoints[0].output_schema
    assert isinstance(input_schema.value, DelayedLoaderX)
    assert isinstance(output_schema.value, DelayedLoaderY)
