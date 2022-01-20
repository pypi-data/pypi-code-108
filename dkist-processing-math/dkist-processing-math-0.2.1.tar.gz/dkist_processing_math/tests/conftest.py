import numpy as np
import pytest

rng = np.random.default_rng()


@pytest.fixture()
def numpy_arrays():
    """
    Create an iterable of random 10 x 10 arrays

    Returns
    -------
    List[np.ndarray]

    """
    arrays = [rng.standard_normal((10, 10)), rng.standard_normal((10, 10))]
    return arrays


@pytest.fixture()
def numpy_array(numpy_arrays):
    """
    Create a single random 10 x 10 array

    Returns
    -------
    np.ndarray

    """
    return numpy_arrays[0]


@pytest.fixture()
def numpy_arrays_wrong_shape():
    """
    Create an iterable of random arrays of differing sizes

    Returns
    -------
    List[np.ndarray]

    """
    arrays = [rng.standard_normal((10, 10)), rng.standard_normal((10, 15))]
    return arrays


@pytest.fixture(params=["multiple", "single"])
def multiple_test_arrays(request, numpy_arrays):
    """
    Create an input test array or list of test arrays

    Parameters
    ----------
    request: Union['multiple, 'single']
        indicates whether to return a single array or an iterable of arrays
    numpy_arrays: List[np.ndarray]
        the arrays from which the return value is selected

    Returns
    -------
    Union[List[np.ndarray], np.ndarray]

    """
    if request.param == "multiple":
        return numpy_arrays
    else:
        return numpy_arrays[0]
