from typing import Tuple

import numpy
import numpy as np
from skimage import transform as skit


def do_hough(
    binary: numpy.ndarray, theta_min: float, theta_max: float, numtheta: int = 1500
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Perform a Hough line transform on input data.

    Resolution in the angle dimension can be increased via numtheta.

    Parameters
    ----------
    binary
        An integer array of 1's and 0's

    theta_min
        The minimum angle to use for the hough transform fitting

    theta_max
        The maximum angle to use for the hough transform fitting

    numtheta
        The number of samples in the theta dimension of the Hough transform.

    Returns
    -------
    The 2D Hough space (i.e., accumulator) of the input image

    A 1D array of the angle values corresponding to the Hough accumulator. Angles will range from -pi/4 to 3/4 pi
    and the length will be equal to numtheta.

    A 1D array of the distance values corresponding to the Hough accumulator. This array is entirely determined
    by skimage.transform.hough_line
    """
    hough = skit.hough_line(binary, theta=np.linspace(theta_min, theta_max, numtheta))
    hough_accumulator = hough[0]
    theta = hough[1]
    rho = hough[2]

    return hough_accumulator, theta, rho
