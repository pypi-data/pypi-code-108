"""
In our paper, we presented the helicity measures starting from a volume in
cylindrical coordinates. This was mainly useful for giving an intuitive
explanation, but can be skipped in the implementation (see the
``heliq.helicity`` module). However, it can still be useful to analyze the
cylindrical sections because in some cases they can nicely visualize the
helical features of a structure.
"""
import numpy as np

from scipy import ndimage
from typing import Union, Sequence


def cylindrical_sections(data: np.ndarray,
                         rho: Union[float, Sequence[float]] = None,
                         n_theta: int = 360,
                         ) -> np.ndarray:
    """Get cylindrical sections from a volume in Cartesian coordinates

    The volume should be aligned such that the helical axis goes through the
    center and is parallel to the z-axis.

    Note that the pixels will not be square (different width and height) and
    that the real width of the pixels will be different at different
    cylindrical sections. If the voxel size is :math:`d`, then the height of
    the pixels is also :math:`h = d`, and the width can be calculated using
    :math:`w = d \\cdot \\rho \\cdot \\arctan{ \\left( 360° / n_{\\theta} \\right) }`.

    Args:
        data:
            A 3D array containing the volumetric data of the object.
        rho:
            A list of the radii at which to create cylindrical sections,
            expressed in voxels, the default radii are calculated using
            ``rho = numpy.arange(0, min(data.shape[:2]))``.
        n_theta:
            The number of pixels in the θ-direction of the cylindrical sections.

    Returns:
        A 3D array with axes (z, θ, ρ).
    """
    if rho is None:
        rho = np.arange(0, min(data.shape[:2]))
    else:
        rho = np.asarray(rho, dtype=float)

    assert data.ndim == 3
    assert np.all(rho >= 0)
    assert n_theta > 0

    theta, z, rho = np.meshgrid(np.linspace(0, 2 * np.pi, n_theta, dtype=float),
                                np.arange(data.shape[2], dtype=float),
                                rho)

    x = rho * np.cos(theta) + data.shape[1] / 2
    y = rho * np.sin(theta) + data.shape[0] / 2

    return ndimage.map_coordinates(data, (y, x, z), order=1)
