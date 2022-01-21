import numpy as np


def interpolate_gaps(data, limit: int = None) -> np.ndarray:
    """
    interpolates gaps in data series with np.nan
    :param data: the data to interpolate
    :param limit: the maximum gap size to fill
    :return: the fi;;ed data
    """
    data = np.array(data)
    i = np.arange(data.size)
    valid = np.isfinite(data)
    filled = np.interp(i, i[valid], data[valid])

    if limit is not None:
        invalid = ~valid
        for n in range(1, limit + 1):
            invalid[:-n] &= invalid[n:]
        filled[invalid] = np.nan

    return filled
