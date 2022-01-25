import copy

import numpy as np
import pandas as pd
import pytest
from sklearn.datasets import load_breast_cancer

from inspec_ai.preprocessing.missing_values import (
    fill_missing_values,
    _fill_missing_values_pandas_dataframe,
    _fill_missing_values_pandas_series,
    _fill_missing_values_numpy,
    KNOWN_IMPUTATION_STRATEGIES,
    X_AND_Y_INVALID_FORMAT_ERROR,
)


def test__fill_missing_values__invalid_inputs__raises_value_error():
    with pytest.raises(ValueError) as e:
        fill_missing_values(1, "b")

    assert str(e.value) == X_AND_Y_INVALID_FORMAT_ERROR


def test__fill_missing_values__does_not_change_inputs():
    x_train, y_train = load_breast_cancer(return_X_y=True)
    replacement_strategies = {0: "most_frequent"}

    x_train[1:6, 0] = np.nan
    x_train[1, 1] = np.nan

    x_train_copy = copy.deepcopy(x_train)
    y_train_copy = copy.deepcopy(y_train)
    replacement_strategies_copy = copy.deepcopy(replacement_strategies)

    fill_missing_values(
        x_train,
        y_train,
        replacement_strategies,
    )

    assert ((x_train == x_train_copy) | np.isnan(x_train)).all()
    assert ((y_train == y_train_copy) | np.isnan(y_train)).all()
    assert replacement_strategies == replacement_strategies_copy


def test__fill_missing_values_pandas_series__some_user_defined_functions__correct_strategies():
    x_train, y_train = load_breast_cancer(return_X_y=True, as_frame=True)

    x_train.loc[1:6, "mean texture"] = np.nan

    x_clean, strategies = _fill_missing_values_pandas_series(
        x_train["mean texture"],
        y_train,
        {"mean texture": "most_frequent"},
    )

    assert strategies["mean texture"] == "most_frequent"


def test__fill_missing_values_pandas_series__no_user_defined_functions__correct_strategies():
    x_train, y_train = load_breast_cancer(return_X_y=True, as_frame=True)

    x_train.loc[1:6, "mean texture"] = np.nan

    x_clean, strategies = _fill_missing_values_pandas_series(
        x_train["mean texture"],
        y_train,
    )

    assert strategies["mean texture"] in KNOWN_IMPUTATION_STRATEGIES


def test__fill_missing_values_pandas_series__no_user_defined_functions_no_series_name__correct_strategies():
    x_train, y_train = load_breast_cancer(return_X_y=True, as_frame=True)

    x_train.loc[1:6, "mean texture"] = np.nan

    x_clean, strategies = _fill_missing_values_pandas_series(
        pd.Series(x_train["mean texture"].values),
        y_train,
    )

    assert strategies[0] in KNOWN_IMPUTATION_STRATEGIES


def test__fill_missing_values_numpy__some_user_defined_functions__correct_strategies():
    x_train, y_train = load_breast_cancer(return_X_y=True)

    x_train[1:6, 0] = np.nan
    x_train[500:510, 1] = np.nan
    x_train[14:114, 2] = np.nan

    x_clean, strategies = _fill_missing_values_numpy(
        x_train,
        y_train,
        {0: "most_frequent", 1: "median"},
    )

    assert strategies[0] == "most_frequent"
    assert strategies[1] == "median"
    assert strategies[2] in KNOWN_IMPUTATION_STRATEGIES


def test__fill_missing_values_pandas_dataframe__some_user_defined_functions__correct_strategies():
    x_train, y_train = load_breast_cancer(return_X_y=True, as_frame=True)

    x_train.loc[1:6, "mean texture"] = np.nan
    x_train.loc[500:510, "mean perimeter"] = np.nan
    x_train.loc[14:114, "mean area"] = np.nan

    x_clean, strategies = _fill_missing_values_pandas_dataframe(
        x_train,
        y_train,
        {"mean texture": "most_frequent", "mean perimeter": "median"},
    )

    assert strategies["mean texture"] == "most_frequent"
    assert strategies["mean perimeter"] == "median"
    assert strategies["mean area"] in KNOWN_IMPUTATION_STRATEGIES


def test__fill_missing_values_pandas_dataframe__all_user_defined_functions__correct_strategies():
    x_train, y_train = load_breast_cancer(return_X_y=True, as_frame=True)

    x_train.loc[1:6, "mean texture"] = np.nan
    x_train.loc[500:510, "mean perimeter"] = np.nan
    x_train.loc[14:114, "mean area"] = np.nan

    x_clean, strategies = _fill_missing_values_pandas_dataframe(
        x_train,
        y_train,
        {
            "mean texture": "most_frequent",
            "mean perimeter": "median",
            "mean area": "mean",
        },
    )

    assert strategies["mean texture"] == "most_frequent"
    assert strategies["mean perimeter"] == "median"
    assert strategies["mean area"] == "mean"


def test__fill_missing_values_pandas_dataframe__all_user_defined_functions__correct_output():
    x_train, y_train = load_breast_cancer(return_X_y=True, as_frame=True)

    x_train.loc[1:4, "mean texture"] = np.nan
    x_train.loc[1:4, "mean perimeter"] = np.nan
    x_train.loc[1:4, "mean area"] = np.nan

    x_clean, strategies = _fill_missing_values_pandas_dataframe(
        x_train,
        y_train,
        {
            "mean texture": "most_frequent",
            "mean perimeter": "median",
            "mean area": "mean",
        },
    )

    x_expected = copy.deepcopy(x_train)

    x_expected.loc[1:4, "mean texture"] = x_expected["mean texture"].mode().min()
    x_expected.loc[1:4, "mean perimeter"] = x_expected["mean perimeter"].median()
    x_expected.loc[1:4, "mean area"] = x_expected["mean area"].mean()

    assert (x_clean == x_expected).all().all()


def test__fill_missing_values_pandas_dataframe__no_user_defined_functions__correct_strategies():
    x_train, y_train = load_breast_cancer(return_X_y=True, as_frame=True)

    x_train.loc[1:6, "mean texture"] = np.nan
    x_train.loc[500:510, "mean perimeter"] = np.nan
    x_train.loc[14:114, "mean area"] = np.nan

    x_clean, strategies = _fill_missing_values_pandas_dataframe(x_train, y_train)

    assert strategies["mean texture"] in KNOWN_IMPUTATION_STRATEGIES
    assert strategies["mean perimeter"] in KNOWN_IMPUTATION_STRATEGIES
    assert strategies["mean area"] in KNOWN_IMPUTATION_STRATEGIES


def test__fill_missing_values_pandas_dataframe__all_nan_column__does_not_fill():
    x_train, y_train = load_breast_cancer(return_X_y=True, as_frame=True)

    x_train.loc[1:6, "mean texture"] = np.nan
    x_train.loc[500:510, "mean perimeter"] = np.nan
    x_train["mean area"] = np.nan

    x_clean, strategies = _fill_missing_values_pandas_dataframe(x_train, y_train)

    assert strategies["mean texture"] in KNOWN_IMPUTATION_STRATEGIES
    assert strategies["mean perimeter"] in KNOWN_IMPUTATION_STRATEGIES
    assert not strategies["mean area"]


def test__fill_missing_values_pandas_dataframe__all_nan_column__raises_warning():
    x_train, y_train = load_breast_cancer(return_X_y=True, as_frame=True)
    x_train["mean area"] = np.nan

    with pytest.warns(Warning) as w:
        _fill_missing_values_pandas_dataframe(x_train, y_train)

    assert (
        str(w[0].message)
        == "Could not fill missing values for column 'mean area' since it does not contain any non-missing value."
    )


def test__fill_missing_values_pandas_dataframe__all_nan_column_in_user_options__does_not_fill():
    x_train, y_train = load_breast_cancer(return_X_y=True, as_frame=True)

    x_train.loc[1:6, "mean texture"] = np.nan
    x_train.loc[500:510, "mean perimeter"] = np.nan
    x_train["mean area"] = np.nan

    x_clean, strategies = _fill_missing_values_pandas_dataframe(
        x_train, y_train, {"mean area": "mean"}
    )

    assert strategies["mean texture"] in KNOWN_IMPUTATION_STRATEGIES
    assert strategies["mean perimeter"] in KNOWN_IMPUTATION_STRATEGIES
    assert not strategies["mean area"]


def test__fill_missing_values_pandas_dataframe__all_nan_column_in_user_options__raises_warning():
    x_train, y_train = load_breast_cancer(return_X_y=True, as_frame=True)
    x_train["mean area"] = np.nan

    with pytest.warns(Warning) as w:
        _fill_missing_values_pandas_dataframe(x_train, y_train, {"mean area": "mean"})

    assert (
        str(w[0].message)
        == "Could not fill missing values for column 'mean area' with strategy 'mean' since it does not contain any non-missing value."
    )


def test__fill_missing_values_pandas_dataframe__replacement_strategy_key_not_in_x_column__raises_error():
    x_train, y_train = load_breast_cancer(return_X_y=True, as_frame=True)

    with pytest.raises(ValueError) as e:
        _fill_missing_values_pandas_dataframe(x_train, y_train, {"wrong entry": "mean"})

    assert (
        str(e.value)
        == "'wrong entry' is not a column of the x dataset. Please ensure that the keys of replacement_strategies are columns of the x dataset."
    )


def test__fill_missing_values_pandas_dataframe__invalid_replacement_strategy__raises_error():
    x_train, y_train = load_breast_cancer(return_X_y=True, as_frame=True)

    with pytest.raises(ValueError) as e:
        _fill_missing_values_pandas_dataframe(
            x_train, y_train, {"mean area": "not an actual strategy"}
        )

    assert (
        str(e.value)
        == "'not an actual strategy' is not an available missing value replacement strategy. Please ensure that"
        "the values of replacement_strategies are valid replacement strategies. The valid"
        "replacement strategies are: 'mean', 'median', 'most_frequent'"
    )
