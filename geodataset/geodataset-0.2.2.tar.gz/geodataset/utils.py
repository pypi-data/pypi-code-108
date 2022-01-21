import numpy as np
from scipy.ndimage.morphology import distance_transform_edt

class InvalidDatasetError(Exception): pass

def fill_nan_gaps(array, distance=5):
    """ Fill gaps in input array
    Parameters
    ----------
    array : 2D numpy.array
        Raster with data
    distance : int
        Minimum size of gap to fill
    Returns
    -------
    array : 2D numpy.array
        Raster with data with gaps filled
    """
    dist, indi = distance_transform_edt(
        np.isnan(array),
        return_distances=True,
        return_indices=True)
    gpi = dist <= distance
    r, c = indi[:, gpi]
    array = np.array(array)
    array[gpi] = array[r, c]
    return array
