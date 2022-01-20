from typing import Iterable
from typing import Union

import numpy as np


def average_numpy_arrays(arrays: Union[Iterable[np.ndarray], np.ndarray]) -> np.ndarray:
    """
    Given an iterable of numpy arrays, calculate the pixel-wise average and return
    it in a numpy array. This will work for a single array as well, just in case...

    Parameters
    ----------
    arrays
        The arrays to be averaged

    Returns
    -------
    The average of the input arrays

    """
    arrays = [arrays] if isinstance(arrays, np.ndarray) else arrays
    count = 0  # This statement is here only to suppress an uninitialized variable warning
    output = None
    for count, array in enumerate(arrays):
        if output is None:
            output = np.array(array).astype(float)
        else:
            if array.shape != output.shape:
                raise ValueError(
                    f"All arrays must be the same shape. "
                    f"Shape of initial array = {output.shape} "
                    f"Shape of current array = {array.shape}"
                )
            output += array
    if output is not None:
        return output / (count + 1)
    raise ValueError("data_arrays is empty")
