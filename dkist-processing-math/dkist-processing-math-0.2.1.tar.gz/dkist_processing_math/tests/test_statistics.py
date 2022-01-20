import numpy as np
import pytest

from dkist_processing_math.statistics import average_numpy_arrays


@pytest.fixture()
def int_arrays_with_large_values():
    """ Some arrays that when all added together will overflow their datatype """
    arrays = [(np.zeros((10, 10)) + 10000 + (5000 * i)).astype(">i2") for i in range(4)]
    return arrays


def test_average_numpy_arrays_wrong_shape(numpy_arrays_wrong_shape):
    """
    Given: an iterable of numpy arrays that are not all the same shape
    When: averaging arrays
    Then: an error is raised as the shapes are required to be the same
    """
    with pytest.raises(ValueError):
        average_numpy_arrays(numpy_arrays_wrong_shape)


def test_average_numpy_arrays(multiple_test_arrays):
    """
    Given: an iterable of numpy arrays that are all the same shape
    When: calculating the average
    Then: a numpy array containing the average is returned
    """
    if isinstance(multiple_test_arrays, np.ndarray):
        desired_shape = multiple_test_arrays.shape
        desired_result = multiple_test_arrays
    else:
        desired_shape = multiple_test_arrays[0].shape
        desired_result = np.mean(np.array(multiple_test_arrays), axis=0)
    result = average_numpy_arrays(multiple_test_arrays)
    assert isinstance(result, np.ndarray)
    # Dividing an ndarray by an integer is a floating point division
    # and the result is always dtype=float
    assert result.dtype == float
    assert result.shape == desired_shape
    np.testing.assert_allclose(result, desired_result)


def test_average_numpy_arrays_empty_list():
    """
    Given: an empty iterable of numpy arrays
    When: calculating the average
    Then: an error is raised
    """
    with pytest.raises(ValueError):
        average_numpy_arrays([])


def test_average_with_large_values(int_arrays_with_large_values):
    """
    Given: a list of arrays with values that would overflow their datatype if they were all summed
    When: averaging the arrays
    Then: the correct values are returned
    """
    expected = np.ones((10, 10)) * 17500
    np.testing.assert_equal(expected, average_numpy_arrays(int_arrays_with_large_values))
