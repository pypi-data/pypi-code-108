"""
The helicity of an objct can be analyzed in different ways. The main method
presented in our paper is to calculate the helicity function
(``helicity_function``), which gives the helicity as a function of the distance
between the helical axis and the inclination angle. It is also possible to get
the total helicity (``total_helicity``), which is a single value between -1 and
+1 that indicates the total helicity of an object based on the results of the
helicity function.

If you want to analyze the distribution of helical features across an object,
you can use ``helicity_map``, which returns an array that indicates the local
helicity around each voxel. Use ``helicity_descriptor`` for more controll about
how to calculate this helicity map, this function is internally used by
``helicity_function`` and ``helicity_descriptor`` and returns two arrays: one
array containing the magnitude of helicity (i.e. the gradient magnitude) in
each voxel and one array containing the inclination angle. That way, you can
select for example only the parts of your object that have a certain
inclination angle.
"""
import numpy as np
import dataclasses
import matplotlib.pyplot as plt
from scipy import ndimage
from matplotlib.image import AxesImage
from typing import Tuple


@dataclasses.dataclass
class HelicityFunction:
    """Holds the contents of a helicity function."""
    delta_alpha: float
    delta_rho: float
    histogram: np.ndarray


def _cylindrical_coordinates(shape):
    x, y, z = np.meshgrid(np.arange(shape[1]) - shape[1] / 2,
                          np.arange(shape[0]) - shape[0] / 2,
                          np.arange(shape[2]) - shape[2] / 2)
    rho = np.sqrt(x ** 2 + y ** 2)
    phi = np.arctan2(y, x)
    return rho, phi, z


def _gradient_3d(data, kernel_size):
    assert data.ndim == 3
    assert np.max(data) > np.min(data)
    assert kernel_size > 1 and kernel_size % 2 == 1

    # The gradient is calculated using Sobel filters
    s = np.arange(kernel_size, dtype=float) - kernel_size // 2
    sx, sy, sz = np.meshgrid(s, s, s)
    sr = sx ** 2 + sy ** 2 + sz ** 2
    # prevent division by zero, of which the result should be zero in this case
    sr[sr == 0] = np.Inf

    # For some reason, this custom implementation that doesn't use the
    # separability of the Sobel kernel is about 2x faster than the Scipy
    # implementation
    gx = ndimage.convolve(data, sx / sr)
    gy = ndimage.convolve(data, sy / sr)
    gz = ndimage.convolve(data, sz / sr)
    return gx, gy, gz


def helicity_descriptor(data: np.ndarray,
                        kernel_size: int = 5,
                        ) -> Tuple[np.ndarray, np.ndarray]:
    """Calculate the inclination angle and gradient magnitude in each voxel.

    This is not a measure of helicity itself, but is used as the first step in
    most other methods. It can however be used to analyze the helicity of a
    particle with a custom method.

    Args:
        data:
            The voxel data as a 3D array that describes the object.
        kernel_size:
            The size of the Sobel kernel used for calculating the gradient,
            should be an odd integer.

    Returns:
        A tuple of two elements, the first is the normalized gradient magnitude
        in each voxel and the second element is the inclination angle in
        degrees in each voxel.
    """
    # Calculate the gradient and project it on cylindrical planes
    gx, gy, gz = _gradient_3d(data, kernel_size)
    _, phi, _ = _cylindrical_coordinates(data.shape)
    gphi = - gx * np.sin(phi) + gy * np.cos(phi)

    # alpha should be in the range [-90°, 90°] because inclination angles with
    # a difference of n*180° are equivalent, and gmag should be normalized such
    # that the helicity function is bounded to [-1, +1]
    alpha = 90 + np.arctan2(gz, gphi) * 180 / np.pi
    alpha[alpha > 90] -= 180
    gmag = np.sqrt(gphi ** 2 + gz ** 2)
    gmag /= np.sum(np.sqrt(gx ** 2 + gy ** 2 + gz ** 2))
    return gmag, alpha


def helicity_function(data: np.ndarray,
                      voxel_size: float,
                      delta_alpha: float = 1.0,
                      delta_rho: float = None,
                      kernel_size: int = 5,
                      ) -> HelicityFunction:
    """Calculate the helicity function for a given object.

    Args:
        data:
            The voxel data as a 3D array that describes the object.
        voxel_size:
            The width of the voxels in the data.
        delta_alpha:
            The bin size for the inclination angles in degrees.
        delta_rho:
            The bin size in the radial direction in the same units as the
            voxel_size, by default ``delta_rho = voxel_size``.
        kernel_size:
            The size of the Sobel kernel used for calculating the gradient,
            should be an odd integer.

    Returns:
        A ``HelicityFunction`` containing the results.
    """
    if delta_rho is None:
        delta_rho = voxel_size

    assert voxel_size > 0
    assert delta_alpha > 0
    assert delta_rho > 0

    # For binning we need the inclination angle and gradient magnitude, but the
    # gradient magnitude should have the correct sign (+ for right-handed and -
    # for left-handed). After setting the correct sign, we are only interested
    # in the absolute value of the inclination angle.
    gmag, alpha = helicity_descriptor(data, kernel_size)
    gmag *= np.sign(alpha)
    alpha = np.abs(alpha)

    # Currently, alpha is defined in the range [0°, 90°], but the binning only
    # works for [0°, 90°), the next line deals with values of 90°.
    alpha[alpha == 90] -= 1e-6

    assert alpha.min() >= 0
    assert alpha.max() < 90

    rho, _, _ = _cylindrical_coordinates(data.shape)
    rho *= voxel_size

    nbins_rho = int(np.ceil(np.max(rho) / delta_rho))
    nbins_alpha = int(np.ceil(90. / delta_alpha))
    bins = np.zeros((nbins_rho, nbins_alpha), dtype=float)

    m = np.floor_divide(rho, delta_rho).astype(int)
    n = np.floor_divide(alpha, delta_alpha).astype(int)
    for i in range(gmag.shape[0]):
        for j in range(gmag.shape[1]):
            for k in range(gmag.shape[2]):
                mm = m[i, j, k]
                nn = n[i, j, k]
                bins[mm, nn] += gmag[i, j, k]

    # The helicity function should be divided by the bin area, which makes it
    # possible to compare intensities between helicity functions with different
    # bin sizes. This does not influence the total helicity, because it takes
    # this into account already in the integration.
    bins /= (voxel_size * delta_rho * delta_alpha)
    return HelicityFunction(delta_alpha, delta_rho, bins)


def plot_helicity_function(hfunc: HelicityFunction,
                           vmax: float = None,
                           axis: plt.Axes = None,
                           cmap: str = 'coolwarm',
                           ) -> AxesImage:
    """Plot the helicity function.

    Args:
        hfunc:
            The helicity function of the object.
        vmax:
            The limits for the intensity will be [-vmax, vmax], by default this
            will be calculated as ``max(abs(helicity_function))``.
        axis:
            The axis on which to draw the helicity function. If not provided,
            the currect active axis will be used.
        cmap:
            The colormap that will be applied, which should ideally be a
            diverging colormap to properly visualize the difference between
            left- and right-handed helicity.

    Returns:
        A matplotlib axis image containing the helicity function.
    """
    if vmax is None:
        vmax = np.max(np.abs(hfunc.histogram))
    if axis is None:
        axis = plt.gca()

    assert vmax > 0

    im = axis.imshow(hfunc.histogram,
                     interpolation='nearest',
                     origin='lower',
                     extent=(0, 90, 0, hfunc.histogram.shape[0] * hfunc.delta_rho),
                     cmap=cmap)
    im.set_clim(-vmax, vmax)
    axis.set_aspect('auto')
    return im


def total_helicity(hfunc: HelicityFunction) -> float:
    """Calculate the total helicity of an object.

    The total helicity is a value between +1 and -1 that indicates the total
    helicity of the object: a value close to zero indicates achirality, while a
    value close to +/-1 indicates near-perfect helicity. Positive values
    indicate right-handed helicity and negative values indicate left-handed
    helicity.

    Args:
        hfunc:
            The helicity function of the object.

    Returns:
        The total helicity of the object.
    """
    return np.sum(hfunc.histogram) * hfunc.delta_rho * hfunc.delta_alpha


def helicity_map(data: np.ndarray,
                 sigma: float,
                 threshold: float = None,
                 kernel_size: int = 5,
                 ) -> np.ndarray:
    """Create a helicity map that indicates the helicity around each voxel

    Args:
        data:
            The voxel data (3D array) that describes the object.
        sigma:
            The effective size of a region over which the local helicity will
            be averaged, this is done using Gaussian smoothing in 3D.
        threshold:
            If specified, all voxels in the result where ``data < threshold``
            will be set to zero.
        kernel_size:
            The size of the Sobel kernel used for calculating the gradient,
            should be an odd integer.

    Returns:
        A 3D array with the same shape as ``data`` that contains the 3D
        helicity map.
    """
    assert sigma >= 0

    gmag, alpha = helicity_descriptor(data, kernel_size)
    hmap = ndimage.gaussian_filter(gmag * np.sign(alpha), sigma, mode='constant')

    if threshold is not None:
        hmap[data < threshold] = 0

    return hmap
