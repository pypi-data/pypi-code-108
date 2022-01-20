import numpy
import numpy as np
from skimage import filters as skif


def make_binary(data: numpy.ndarray, numotsu: int = 1) -> np.ndarray:
    """Generate a binary image from an input float or int array.

    A threshold value is chosen via Otsu's method and all values below the threshold are set to 1 while everything
    else is set to 0. Thus the result is technically an _inverse_ binary image, which is useful for isolating the
    target grid as a feature of interest.

    Parameters
    ----------
    data
        Data to convert to binary

    numotsu
        The number of times to perform thresholding using Otsu's method. Numbers larger than 1 are useful if the
        pixel distribution of the data has > 2 modes.

    Returns
    -------
    An array of 1's and 0's corresponding to the thresholded input data.
    """
    threshold = np.inf
    for i in range(numotsu):
        tmp = skif.threshold_otsu(data[data < threshold])
        frac = np.sum(data < tmp) / data.size
        # TODO: make this a parameter
        if frac < 1e-3:
            break
        threshold = tmp
    binary = np.array(data < threshold, dtype=int)
    return binary
