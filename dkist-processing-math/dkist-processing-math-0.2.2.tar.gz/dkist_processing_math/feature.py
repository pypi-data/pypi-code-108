from typing import Tuple

import numpy
import numpy as np
import peakutils as pku


def find_px_angles(
    hough_accumulator: numpy.ndarray,
    theta: numpy.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """Find the most significant angles in a Hough transform.

    Peaks in the Hough transform a first found with a simple max filter and then refined via interpolation of the
    surrounding peak.

    Note, peak angles are not allowed to be within pi/10 of each other.

    Parameters
    ----------
    hough_accumulator
        A 2D array representing a Hough accumulator

    theta
        A 1D array of the angle values corresponding to hough_accumulator

    Returns
    -------
    peak_theta
        The most significant angles found

    idx
        The index values corresponding to the location in theta of the initial (non-interpolated) guesses for most
        significant angles.

    """
    rss = np.sqrt(np.sum(hough_accumulator ** 2, axis=0))
    # This min distance limits us to only finding the single most prominent angle
    idx = pku.indexes(rss, min_dist=theta.size)
    peak_theta = pku.interpolate(theta, rss, ind=idx)

    return peak_theta
