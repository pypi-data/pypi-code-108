from functools import partial
from typing import Iterable
from typing import Iterator
from typing import Union

import numpy as np
from skimage import transform as skit


def bin_arrays(
    arrays: Union[Iterable[np.ndarray], np.ndarray], bin_factors: (int, int)
) -> Iterator[np.ndarray]:
    """
    Bin an iterable of arrays by summation over an integral number of pixels in each dimension.

    Parameters
    ----------
    arrays
        The arrays to be binned

    bin_factors
        The bin factors for each axis, which must be integral divisors of each array dimension

    Returns
    -------
    An Iterator yielding the binned arrays

    """
    arrays = [arrays] if isinstance(arrays, np.ndarray) else arrays
    partial_bin = partial(_bin_array, bin_factors=bin_factors)
    return map(partial_bin, arrays)


def _bin_array(array: np.ndarray, bin_factors: (int, int)) -> np.ndarray:
    """
    Bin an array by summation over an integral number of pixels in each dimension.

    Parameters
    ----------
    array
        The array to be binned

    bin_factors
        The bin factors for each axis, which must be integral divisors of each array dimension

    Returns
    -------
    The binned array

    """
    input_shape = array.shape
    if input_shape[0] % bin_factors[0] or input_shape[1] % bin_factors[1]:
        raise ValueError(
            "Array dimensions must be an integral multiple of the binning factor\n"
            f"Shape of array = {input_shape}, binning factors = {bin_factors}"
        )
    return skit.downscale_local_mean(array, bin_factors)
