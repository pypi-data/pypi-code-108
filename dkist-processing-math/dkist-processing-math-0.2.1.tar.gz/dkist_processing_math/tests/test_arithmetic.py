from typing import Generator

import numpy as np
import pytest
from astropy.io import fits
from dkist_processing_common.models.fits_access import FitsAccessBase

from dkist_processing_math.arithmetic import divide_arrays_by_array
from dkist_processing_math.arithmetic import divide_fits_access_by_array
from dkist_processing_math.arithmetic import subtract_array_from_arrays
from dkist_processing_math.arithmetic import subtract_array_from_fits_access


@pytest.fixture(params=["multiple", "single"])
def multiple_test_fits_access(request, numpy_arrays):

    access_list = []
    for i, array in enumerate(numpy_arrays):
        hdu = fits.PrimaryHDU(data=array)
        hdu.header["TEST"] = i
        access_list.append(FitsAccessBase(hdu=hdu))
    if request.param == "multiple":
        return access_list
    return access_list[0]


def test_subtract_array_from_arrays(multiple_test_arrays, numpy_array):
    """
    Given: an iterable of numpy arrays that are all the same shape
    When: subtracting a fixed array from each array in the iterable
    Then: an Generator of subtracted arrays is returned
    """
    if isinstance(multiple_test_arrays, np.ndarray):
        desired_shape = multiple_test_arrays.shape
        desired_result = [multiple_test_arrays - numpy_array]
    else:
        desired_shape = multiple_test_arrays[0].shape
        desired_result = multiple_test_arrays - numpy_array
    result = subtract_array_from_arrays(multiple_test_arrays, numpy_array)
    assert isinstance(result, Generator)
    for result_array, test_array in zip(result, desired_result):
        assert result_array.shape == desired_shape
        assert result_array.dtype == np.result_type(test_array)
        np.testing.assert_allclose(result_array, test_array)


def test_subtract_array_from_fits_access(multiple_test_fits_access, numpy_array):
    """
    Given: an iterable of or single FitsAccess object(s) with data
    When: subtracting an array from all input objects
    Then: a generator of FitsAccess objects is returned with correctly subtracted data
    """
    if isinstance(multiple_test_fits_access, FitsAccessBase):
        desired_result = [multiple_test_fits_access.data - numpy_array]
        desired_header_val = [multiple_test_fits_access.header["TEST"]]
    else:
        desired_result = [i.data - numpy_array for i in multiple_test_fits_access]
        desired_header_val = [i.header["TEST"] for i in multiple_test_fits_access]

    result = subtract_array_from_fits_access(multiple_test_fits_access, numpy_array)
    assert isinstance(result, Generator)

    for result_obj, test_array, test_header_val in zip(result, desired_result, desired_header_val):
        assert result_obj.data.dtype == np.result_type(test_array)
        assert result_obj.header["TEST"] == test_header_val
        np.testing.assert_allclose(result_obj.data, test_array)


def test_subtract_array_from_arrays_wrong_shape(numpy_arrays_wrong_shape, numpy_array):
    """
    Given: an iterable of numpy arrays that are not all the same shape
    When: subtracting arrays
    Then: an error is raised as the shapes are required to be the same
    """
    with pytest.raises(ValueError):
        list(subtract_array_from_arrays(numpy_arrays_wrong_shape, numpy_array))


def test_divide_arrays_by_array(multiple_test_arrays, numpy_array):
    """
    Given: an iterable of numpy arrays that are all the same shape
    When: dividing each array in the iterable by a fixed array
    Then: an Generator of divided arrays is returned
    """
    if isinstance(multiple_test_arrays, np.ndarray):
        desired_shape = multiple_test_arrays.shape
        desired_result = [multiple_test_arrays / numpy_array]
    else:
        desired_shape = multiple_test_arrays[0].shape
        desired_result = multiple_test_arrays / numpy_array
    result = divide_arrays_by_array(multiple_test_arrays, numpy_array)
    assert isinstance(result, Generator)
    for result_array, test_array in zip(result, desired_result):
        assert result_array.shape == desired_shape
        assert result_array.dtype == np.result_type(test_array)
        np.testing.assert_allclose(result_array, test_array)


def test_divide_fits_access_by_array(multiple_test_fits_access, numpy_array):
    """
    Given: an iterable of or single FitsAccess object(s) with data
    When: dividing an array from all input objects
    Then: a generator of FitsAccess objects is returned with correctly subtracted data
    """
    if isinstance(multiple_test_fits_access, FitsAccessBase):
        desired_result = [multiple_test_fits_access.data / numpy_array]
        desired_header_val = [multiple_test_fits_access.header["TEST"]]
    else:
        desired_result = [i.data / numpy_array for i in multiple_test_fits_access]
        desired_header_val = [i.header["TEST"] for i in multiple_test_fits_access]

    result = divide_fits_access_by_array(multiple_test_fits_access, numpy_array)
    assert isinstance(result, Generator)

    for result_obj, test_array, test_header_val in zip(result, desired_result, desired_header_val):
        assert result_obj.data.dtype == np.result_type(test_array)
        assert result_obj.header["TEST"] == test_header_val
        np.testing.assert_allclose(result_obj.data, test_array)


def test_divide_arrays_by_array_wrong_shape(numpy_arrays_wrong_shape, numpy_array):
    """
    Given: an iterable of numpy arrays that are not all the same shape
    When: dividing arrays
    Then: an error is raised as the shapes are required to be the same
    """
    with pytest.raises(ValueError):
        list(divide_arrays_by_array(numpy_arrays_wrong_shape, numpy_array))
