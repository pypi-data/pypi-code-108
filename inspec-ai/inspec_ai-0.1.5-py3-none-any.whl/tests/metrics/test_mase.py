import numpy as np
import pandas as pd
import pytest

from inspec.metrics.mase import (
    mase_by_series,
    mean_absolute_scaled_error,
    _mean_absolute_error,
)


@pytest.mark.parametrize(
    "y_true, y_pred, expected_output",
    [
        (np.array([0, 1, 2, 3]), np.array([1, 2, 3, 4]), 1.0),
        (np.array([0, 1, 2, 3]), np.array([0, 1, 2, 3]), 0.0),
        (np.array([0, 10, 20, 30]), np.array([10, 20, 30, 40]), 10.0),
        (np.array([0, 10, 20, 30]), np.array([-10, 20, -30, 40]), 20.0),
        (pd.Series([0, 1, 2, 3]), pd.Series([1, 2, 3, 4]), 1.0),
        (np.array([0, 1, 2, 3]), pd.Series([1, 2, 3, 4]), 1.0),
    ],
)
def test__mean_absolute_error__returns_correct_output(y_true, y_pred, expected_output):
    assert _mean_absolute_error(y_true, y_pred) == expected_output


@pytest.mark.parametrize(
    "y_true, y_pred, expected_output",
    [
        (np.array([0, 1, 2, 3]), np.array([1, 2, 3, 4]), 1.0),
        (np.array([0, 1, 2, 3]), np.array([0, 1, 2, 3]), 0.0),
        (np.array([0, 10, 20, 30]), np.array([10, 20, 30, 40]), 1.0),
        (pd.Series([0, 1, 2, 3]), pd.Series([1, 2, 3, 4]), 1.0),
        (np.array([0, 1, 2, 3]), pd.Series([1, 2, 3, 4]), 1.0),
    ],
)
def test__mean_absolute_scaled_error__returns_correct_output(
    y_true, y_pred, expected_output
):
    assert mean_absolute_scaled_error(y_true, y_pred) == expected_output


def test__mean_absolute_scaled_error__raise_when_y_true_has_different_size_than_y_pred():
    y_true = np.array([0, 1, 2, 3, 0, 1, 2, 3, 0, 10, 20])
    y_pred = np.array([1, 2, 3, 4, 0, 1, 2, 3, 10, 20, 30, 40])

    with pytest.raises(ValueError) as e:
        mean_absolute_scaled_error(y_true, y_pred)

    assert str(e.value) == "The following provided inputs must contain the same number of elements: y_true and y_pred."


def test__mean_absolute_scaled_error__raise_when_y_true_has_less_than_two_values():
    y_true = np.array([0])
    y_pred = np.array([1])

    with pytest.raises(ValueError) as e:
        mean_absolute_scaled_error(y_true, y_pred)
        
    assert str(e.value) == "The following provided inputs must contain at least 2 elements: y_true and y_pred."


def test__mean_absolute_scaled_error__works_with_series_of_length_2():
    """This test was added following a bug where a user could not evaluate the mean_absolute_scaled_error from length 2 series."""
    y = np.array([0, 1])

    assert mean_absolute_scaled_error(y, y) == 0.0


def test__mase_by_series__returns_correct_output():
    y_true = np.array([0, 1, 2, 3, 0, 1, 2, 3, 0, 10, 20, 30])
    y_pred = np.array([1, 2, 3, 4, 0, 1, 2, 3, 10, 20, 30, 40])
    dimension = np.array([0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2])
    time = np.array([1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4])

    mases = mase_by_series(y_true, y_pred, dimension, time)

    expected_output = pd.Series({0: 1, 2: 1, 1: 0})

    assert isinstance(mases, pd.Series)
    assert (mases.index == expected_output.index).all()
    assert (mases.values == expected_output.values).all()


def test__mase_by_series__str_dimension__returns_correct_output():
    y_true = np.array([0, 1, 2, 3, 0, 1, 2, 3, 0, 10, 20, 30])
    y_pred = np.array([1, 2, 3, 4, 0, 1, 2, 3, 10, 20, 30, 40])
    dimension = np.array(["0", "0", "0", "0", "1", "1", "1", "1", "2", "2", "2", "2"])
    time = np.array([1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4])

    mases = mase_by_series(y_true, y_pred, dimension, time)

    expected_output = pd.Series({"0": 1, "2": 1, "1": 0})

    assert isinstance(mases, pd.Series)
    assert (mases.index == expected_output.index).all()
    assert (mases.values == expected_output.values).all()


def test__mase_by_series__works_with_date_dtype():
    y_true = np.array([0, 1, 2, 3, 0, 1, 2, 3, 0, 10, 20, 30])
    y_pred = np.array([1, 2, 3, 4, 0, 1, 2, 3, 10, 20, 30, 40])
    dimension = np.array(["0", "0", "0", "0", "1", "1", "1", "1", "2", "2", "2", "2"])
    time = np.array([np.datetime64(i, "Y") for i in range(0, 4)] * 3)

    mases = mase_by_series(y_true, y_pred, dimension, time)

    expected_output = pd.Series({"0": 1, "2": 1, "1": 0})

    assert isinstance(mases, pd.Series)
    assert (mases.index == expected_output.index).all()
    assert (mases.values == expected_output.values).all()


def test__mase_by_series__raises_when_dimension_not_same_size_as_y_true():
    y_true = np.array([0, 1, 0, 1, 0, 10])
    y_pred = np.array([1, 2, 0, 1, 10, 20])
    dimension = np.array(["0", "0", "0", "1", "1", "1", "2", "2", "2"])
    time = np.array([1, 2, 1, 2, 1, 2])

    with pytest.raises(ValueError) as e:
        mase_by_series(y_true, y_pred, dimension, time)
        
    assert str(e.value) == "The following provided inputs must contain the same number of elements: y_true, y_pred, dimension and time."


def test__mase_by_series__raises_when_time_is_str():
    y_true = np.array([0, 1, 2, 3, 0, 1, 2, 3, 0, 10, 20, 30])
    y_pred = np.array([1, 2, 3, 4, 0, 1, 2, 3, 10, 20, 30, 40])
    dimension = np.array(["0", "0", "0", "0", "1", "1", "1", "1", "2", "2", "2", "2"])
    time = np.array(["1", "2", "3", "4", "1", "2", "3", "4", "1", "2", "3", "4"])

    with pytest.raises(ValueError) as e:
        mase_by_series(y_true, y_pred, dimension, time)
        
    assert str(e.value) == "The time column must contain int, float or dates."


def test__mase_by_series__raises_when_dimension_size_is_lower_than_two():
    y_true = np.array([0, 0, 1, 2, 3, 0, 10, 20, 30])
    y_pred = np.array([1, 0, 1, 2, 3, 10, 20, 30, 40])
    dimension = np.array(["0", "1", "1", "1", "1", "2", "2", "2", "2"])
    time = np.array([1, 1, 2, 3, 4, 1, 2, 3, 4])

    with pytest.raises(ValueError) as e:
        mase_by_series(y_true, y_pred, dimension, time)
        
    assert str(e.value) == "All dimensions must contain more than one observation."
