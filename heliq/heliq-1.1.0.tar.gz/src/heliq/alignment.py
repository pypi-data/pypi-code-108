"""
To calculate the helicity of a certain object, it is important to make sure
that the helical axis is aligned to the z-axis and is centered in the volume.
This can be done by finding the center and orientation of your object and
entering that information in ``align_helical_axis``. That function will rotate
and translate your data such that the given orientation becomes parallel with
the z-axis and is centered in the volume. You can find the orientation of the
helical axis and the center either manually using external 3D visualization
software, or for relatively simple objects these can also be found
automatically using ``center_of_mass`` and/or ``helical_axis_pca``. The former
assumes that the helical axis goes through the center of mass of you object and
will therefore select the center of mass as the center of the object. The
latter assumes that the object is longer in one direction compared to the other
directions, and will use this direction as the helical axis. Don't use these
functions if these assumptions are not correct for your object!
"""
from typing import Sequence

from scipy import ndimage
from scipy import spatial

import numpy as np


def center_of_mass(data: np.ndarray) -> np.ndarray:
    """Calculate the center of mass of a 3D object.

    Args:
        data:
            A 3D array containing the shape of an object. The shape of the
            array should correspond to the (y, x, z) axes.

    Returns:
        An array of 3 elements (x, y, z) of the center of mass of the object.
    """
    assert data.ndim == 3
    return np.asarray(ndimage.center_of_mass(data))[[1, 0, 2]]


def helical_axis_pca(data: np.ndarray,
                     threshold: float,
                     ) -> np.ndarray:
    """Estimate the orientation of the helical axis of a 3D object using PCA.

    The helical axis is assumed to be along the longest direction of the
    object. This is often true for rods, wires or similar shapes, but is not
    guaranteed to be the case. The longest direction can be detected using
    principal component analysis (PCA) by binarizing it using a certain
    threshold value. A list will then be made with the (x, y, z) coordinates of
    all the voxels that are considered part of the object, i.e. all the voxels
    with an intensity that is larger than the threshold value. PCA is executed
    on this list of coordinates such that the component with the largest score
    will be oriented in the direction along which the points are spread the
    most. This is the direction along which the object is the longest.

    Args:
        data:
            A 3D array containing the shape of an object. The shape of the
            array should correspond to the (y, x, z) axes.
        threshold:
            The threshold that will be used to binarize the data. Only voxels
            with a value larger than this threshold will be used.

    Returns:
        An array of 3 elements (x, y, z) of the orientation of the estimated
        helical axis.
    """
    assert data.ndim == 3

    points = np.argwhere(data > threshold)[:, (1, 0, 2)]  # (y,x,z) to (x,y,z)
    eigval, eigvec = np.linalg.eig(np.cov(points.T))

    orientation = eigvec[:, np.argmax(eigval)]
    return orientation / np.linalg.norm(orientation)


def align_helical_axis(data: np.ndarray,
                       orientation: Sequence[float],
                       center: Sequence[float],
                       ) -> np.ndarray:
    """Transform a 3D object to align its helical axis to the z-axis.

    Args:
        data:
            A 3D array containing the shape of a (helical) object. The shape
            of the array should correspond to the (y, x, z) axes.
        orientation:
            A vector that points in the direction of the helical axis. The
            vector should be a numpy array, tuple or list with three components
            (x, y, z).
        center:
            The location of the center of the object represented as a nnumpy
            array, tuple or list with components (x, y, z). This is typically
            the center of mass of the object.

    Returns:
        The transformed data. The helical axis of this object is parallel with
        the z-axis and is positioned in the center of the array in each
        dimension.
    """
    orientation = np.asarray(orientation)
    center = np.asarray(center)
    assert data.ndim == 3
    assert orientation.ndim == 1 and orientation.shape[0] == 3
    assert center.ndim == 1 and center.shape[0] == 3
    assert np.linalg.norm(orientation) > 0

    ymax, xmax, zmax = data.shape
    x, y, z = np.meshgrid(np.arange(xmax, dtype=float) - xmax / 2,
                          np.arange(ymax, dtype=float) - ymax / 2,
                          np.arange(zmax, dtype=float) - zmax / 2)

    # Rotate such that orientation is aligned with z-axis
    orientation = orientation / np.linalg.norm(orientation)
    zaxis = np.array((0, 0, 1))

    angle = np.arccos(np.dot(zaxis, orientation))
    if angle > 1e-7:
        rvec = np.cross(zaxis, orientation)
        rvec = rvec * angle / np.linalg.norm(rvec)
        rmat = spatial.transform.Rotation.from_rotvec(rvec).as_matrix()
        x, y, z = (rmat[0, 0] * x + rmat[0, 1] * y + rmat[0, 2] * z,
                   rmat[1, 0] * x + rmat[1, 1] * y + rmat[1, 2] * z,
                   rmat[2, 0] * x + rmat[2, 1] * y + rmat[2, 2] * z)

    # Translate such that center is at origin
    x += center[0]
    y += center[1]
    z += center[2]

    # Linearly interpolate data
    return ndimage.map_coordinates(data, (y, x, z), order=1)
