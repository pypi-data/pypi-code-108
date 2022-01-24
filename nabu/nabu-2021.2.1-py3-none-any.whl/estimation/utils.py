import numpy as np
from scipy.signal import find_peaks

def is_fullturn_scan(angles):
    """
    Return True if the angles correspond to a full-turn (360 degrees) scan.
    """
    angles = angles % (2 * np.pi)
    angles -= angles.min()
    sin_angles = np.sin(angles)
    min_dist = 5 # TODO find a more robust angles-based min distance, though this should cover most of the cases
    maxima = find_peaks(sin_angles, distance=min_dist)[0]
    minima = find_peaks(-sin_angles, distance=min_dist)[0]
    n_max = maxima.size
    n_min = minima.size
    # abs(n_max - n_min) actually means the following:
    #  * 0: All turns are full (eg. 2pi, 4pi)
    #  * 1: At least one half-turn remains (eg. pi, 3pi)
    if abs(n_max - n_min) == 0:
        return True
    else:
        return False


def get_halfturn_indices(angles):
    angles = angles % (2 * np.pi)
    angles -= angles.min()
    sin_angles = np.sin(angles)
    min_dist = 5 # TODO find a more robust angles-based min distance, though this should cover most of the cases
    maxima = find_peaks(sin_angles, distance=min_dist)[0]
    minima = find_peaks(-sin_angles, distance=min_dist)[0]
    extrema = np.sort(np.hstack([maxima, minima]))
    extrema -= extrema.min()
    extrema = np.hstack([extrema, [angles.size - 1]])
    res = []
    for i in range(extrema.size - 1):
        res.append((extrema[i], extrema[i+1]))
    return res
