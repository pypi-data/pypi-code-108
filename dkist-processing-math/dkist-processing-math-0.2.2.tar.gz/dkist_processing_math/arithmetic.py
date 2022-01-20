from typing import Generator
from typing import Iterable
from typing import Union

import numpy as np
from dkist_processing_common.models.fits_access import FitsAccessBase


def subtract_array_from_arrays(
    arrays: Union[Iterable[np.ndarray], np.ndarray],
    array_to_subtract: np.ndarray,
) -> Generator[np.ndarray, None, None]:
    """
    Subtract a single array from an iterable of arrays. This will work if
    a single array is used in lieu of an iterable as well.

    Parameters
    ----------
    arrays
        The arrays from which to subtract
    array_to_subtract
        The array to be subtracted

    Returns
    -------
    An generator of modified arrays

    """
    arrays = [arrays] if isinstance(arrays, np.ndarray) else arrays
    for array in arrays:
        if array.shape != array_to_subtract.shape:
            raise ValueError(
                f"All arrays must be the same shape. "
                f"Shape of subtraction array = {array_to_subtract.shape} "
                f"Shape of current array = {array.shape}"
            )
        yield array - array_to_subtract


def subtract_array_from_fits_access(
    access_objs: Union[Iterable[FitsAccessBase], FitsAccessBase], array_to_subtract: np.ndarray
) -> Generator[FitsAccessBase, None, None]:
    """
    Subtract a single array from an iterable of FitsAccess objects. This will work if
    a single object is used in lieu of an iterable as well. The objects themselves are modified in place.

    Parameters
    ----------
    access_objs
        The objects from which to subtract

    array_to_subtract
        The array to be subtracted

    Returns
    -------
    An generator of modified FitsAccess objects
    """
    access_objs = [access_objs] if isinstance(access_objs, FitsAccessBase) else access_objs
    for obj in access_objs:
        obj.data = next(subtract_array_from_arrays(obj.data, array_to_subtract))
        yield obj


def divide_arrays_by_array(
    arrays: Union[Iterable[np.ndarray], np.ndarray],
    array_to_divide_by: np.ndarray,
) -> Generator[np.ndarray, None, None]:
    """
    Divide an iterable of arrays by a single array. This will work if
    a single array is used in lieu of an iterable as well.

    Parameters
    ----------
    arrays
        The arrays to be divided
    array_to_divide_by
        The array ny which to divide

    Returns
    -------
    A generator of modified arrays

    """
    arrays = [arrays] if isinstance(arrays, np.ndarray) else arrays
    for array in arrays:
        if array.shape != array_to_divide_by.shape:
            raise ValueError(
                f"All arrays must be the same shape. "
                f"Shape of array to divide by = {array_to_divide_by.shape} "
                f"Shape of current array = {array.shape}"
            )
        yield array / array_to_divide_by


def divide_fits_access_by_array(
    access_objs: Union[Iterable[FitsAccessBase], FitsAccessBase], array_to_divide_by: np.ndarray
) -> Generator[FitsAccessBase, None, None]:
    """
    Divide an iterable of FitsAccess objects by a single array. This will work if
    a single object is used in lieu of an iterable as well. The objects themselves are modified in place.

    Parameters
    ----------
    access_objs
        The FitsAccess objects to be divided

    array_to_divide_by
        The array ny which to divide

    Returns
    -------
    A generator of modified FitsAccess objects
    """
    access_objs = [access_objs] if isinstance(access_objs, FitsAccessBase) else access_objs
    for obj in access_objs:
        obj.data = next(divide_arrays_by_array(obj.data, array_to_divide_by))
        yield obj
