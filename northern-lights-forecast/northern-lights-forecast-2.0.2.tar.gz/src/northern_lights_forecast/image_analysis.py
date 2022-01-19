"""Find a white line and plot the line.

From
https://stackoverflow.com/questions/60051941/find-the-
coordinates-in-an-image-where-a-specified-colour-is-detected
"""
import os
from typing import Tuple

import cv2
import matplotlib.pyplot as plt
import numpy as np

from northern_lights_forecast.savgol.savitzky_golay import (
    savitzky_golay as savgol_filter,
)


def mean_x(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Compute the mean value along all identical x values.

    Parameters
    ----------
    x: np.ndarray
        x coordinates
    y: np.ndarray
        y coordinates

    Returns
    -------
    tuple:
        The new x and y arrays

    Raises
    ------
    ValueError
        If input arrays have different shapes
    """
    if x.shape != y.shape:
        raise ValueError("Input arrays x and y have different shapes!")
    idx = np.unique(x)
    x_ = np.array([])
    y_ = np.array([])
    for i in idx:
        x_ = np.r_[x_, np.mean(x[x == i])]
        y_ = np.r_[y_, np.mean(y[x == i])]
    return x_, y_


def remove_line(x: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Remove the horizontal zero-line.

    Since the x-axis of the original plot with magnetometer data is included in the x and
    y arrays, we look for the occurrences of y-values and remove all elements that
    correspond to y-values that occur more than one hundred times. If, for some reason,
    some noise makes so the x-axis has fewer elements than some other y-value, we should
    remove both.

    Parameters
    ----------
    x: np.ndarray
        x coordinates
    y: np.ndarray
        y coordinates

    Returns
    -------
    tuple:
        The new x and y arrays
    """
    (values, counts) = np.unique(y, return_counts=True)
    values = values[np.argsort(counts)]
    counts = counts[np.argsort(counts)]
    idx = np.argwhere(counts > 100)
    val = values[idx]
    for v in val:
        x = x[y != v]
        y = y[y != v]
    return x, y


def grab_blue_line(scaling: float, img_file: str = None) -> float:
    """Find a continuous line from a black/white image (will look in 'out/new_im.jpg').

    Parameters
    ----------
    scaling: float
        How 'y' axis scale to number of pixels
    img_file: str
        If given, should be the path to a black/white image.

    Returns
    -------
    float
        Minimum derivative from the last 20% of the line.

    Raises
    ------
    ValueError
        If image file is not found.
    """
    if img_file is None:
        file = "out/new_im.jpg"
    else:
        file = img_file
        if not os.path.isfile(file):
            raise ValueError(f"Cannot find the file {img_file}.")
    # Load image
    im = cv2.imread(file)

    # Define the blue colour we want to find - remember OpenCV uses BGR ordering. At this
    # point we should only have one line (except horizontal lines) that is completely
    # white.
    blue = [255, 255, 255]

    # Get x and y coordinates of all blue pixels
    y_where, x_where = np.where(np.all(im == blue, axis=2))

    x = x_where[np.argsort(x_where)]
    y = y_where[np.argsort(x_where)]
    # Remove the zero-line
    x, y = remove_line(x, y)
    y = scaling * y

    # There might be many points in the graph along the y-axis that are identified as
    # blue, therefore, we choose the mean of those that land on the same x-value.
    x_mean, y_mean = mean_x(x, y)
    x_ = np.linspace(np.min(x_mean), np.max(x_mean), 10000)
    y_i = -np.interp(x_, x_mean, y_mean)
    dy = savgol_filter(y_i, 501, 3, deriv=1)
    dy = dy[int(len(x_) * 0.8) :]

    # === < Plot the result > ===
    # import matplotlib.pyplot as plt

    y_ = savgol_filter(y_i, 501, 3)  # window size 501, polynomial order 3
    # Rescale x-axis to 22-hour plot
    # TODO: find the exact timespan used in the image
    # x = (x - np.min(x)) / (np.max(x) - np.min(x)) * 22
    # x_ = (x_ - np.min(x_)) / (np.max(x_) - np.min(x_)) * 22
    plt.figure()
    plt.imshow(im)
    plt.plot(x, y / scaling, "b")
    plt.plot(x_, -y_ / scaling, "r")

    # plt.figure()
    # plt.plot(x_[int(len(x_) * .8):], y_[int(len(x_) * .8):], 'r')
    # plt.savefig('after.png', dpi=200)
    # plt.figure()
    # plt.plot(x_, dy, 'r')
    if img_file is None:
        plt.savefig("out/plot.pdf", dpi=300, bbox_inches="tight", format="pdf")
    # plt.show()
    # === </ Plot the result > ===

    return float(np.min(dy))


if __name__ == "__main__":
    _ = grab_blue_line(3)
