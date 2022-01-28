"""Collection of tools for computing different maps."""
import numpy as np
from scipy.special import erf


def circular_aperture(x, y, R_ap, x_offset=0, y_offset=0):
    """Circular aperture map.

    Parameters
    ----------
    x, y : array
        1D arrays describing uniform 2D grid to compute map
        over in meters
    R : double
        Radius of aperture in meters
    x_offset, y_offset : double, optional
        Offset of aperture from origin
    """
    X, Y = np.meshgrid(x, y)
    R = np.sqrt((X - x_offset) ** 2 + (Y - y_offset) ** 2)
    ap_map = np.ones_like(X)
    ap_map[R > R_ap] = 0
    return ap_map


def surface_point_absorber(
    xs, ys, w, h, power_absorbed, alpha=0.55e-6, kappa=1.38, zero_min=False
):
    """Models the surface deformation from a small point absorber in a coating of a
    mirror. It calcaultes the thermo-elastic deformation due to excess heat being
    deposited in the mirror.

    Parameters
    ----------
    xs, ys : array
        1D array for the x and y axis to calculate the distortion over
    w : double
        Area of the absorber size
    h : double
        Thickness of mirror
    power_absorbed : double
        Amount of power absorbed over the area w
    alpha : double, optional
        Thermo-elastic coefficient of material, default value for fused silica
    kappa : double, optional
        Thermal conductivity of the material, default value for fused silica

    Returns
    -------
    Height map in meters

    Notes
    -----
    Equation from:
        A. Brooks, et.al "Point absorbers in Advanced LIGO," Appl. Opt. (2021)
    """
    dx = xs[1] - xs[0]
    dy = ys[1] - ys[0]
    r = np.sqrt(np.add.outer(ys ** 2, xs ** 2))
    c0 = -1 / 2 - np.log((h ** 2 + np.sqrt(w ** 2 + h ** 2)) / w)
    out = np.zeros_like(r)
    # most of the time the absorber is very small, much smaller than
    # the discretisation of the map, so we can simplify this calculation
    if w > dx or w > dy:
        b1 = np.abs(r) <= w
        b2 = np.abs(r) > w
        out[b1] = -1 / 2 * (r[b1] / w) ** 2
        out[b2] = c0 + np.log((h ** 2 + np.sqrt(r[b2] ** 2 + h ** 2)) / r[b2])
    else:
        out = c0 + np.log((h ** 2 + np.sqrt(r ** 2 + h ** 2)) / r)

    if zero_min:
        out -= np.min(out)

    return alpha * power_absorbed / (2 * np.pi * kappa) * out


def overlap_tilt_coefficients(x, y, z, weight_spot: float):
    """Computes the amount of yaw and pitch terms present in a map's displacement data.

    This is computed by evaluating a weighted Hermite polynomial overlap integral in an
    efficient manner.
    """
    weight_spot /= np.sqrt(2)

    dx = (x[1] - x[0]) / weight_spot
    dy = (y[1] - y[0]) / weight_spot

    Wx = np.exp(-((x / weight_spot) ** 2))
    Wy = np.exp(-((y / weight_spot) ** 2))

    Hn = 2 * x / weight_spot * Wx
    Hm = 2 * y / weight_spot * Wy

    k10 = np.dot((z @ Hn), Wy) * dx / (np.sqrt(np.pi) * 2) * dy / (np.sqrt(np.pi) * 2)
    k01 = np.dot((z @ Wx), Hm) * dx / (np.sqrt(np.pi) * 2) * dy / (np.sqrt(np.pi) * 2)

    return (
        # convert back to normal x units in displacement map
        4 * k10 / weight_spot,
        4 * k01 / weight_spot,
    )


def overlap_curvature_coefficients(x, y, z, weight_spot: float):
    """Computes the amount of x and y curvature terms present in a map's displacement
    data.

    This is computed by evaluating a weighted Hermite polynomial overlap integral in an
    efficient manner.
    """
    weight_spot /= np.sqrt(2)

    dx = (x[1] - x[0]) / weight_spot
    dy = (y[1] - y[0]) / weight_spot

    Wx = np.exp(-((x / weight_spot) ** 2))
    Wy = np.exp(-((y / weight_spot) ** 2))

    Hn = ((2 * x / weight_spot) ** 2 - 2) * Wx
    Hm = ((2 * y / weight_spot) ** 2 - 2) * Wy

    k20 = np.dot((z @ Hn), Wy) * dx / (np.sqrt(np.pi) * 2 ** 3) * dy / (np.sqrt(np.pi))
    k02 = np.dot((z @ Wx), Hm) * dx / (np.sqrt(np.pi) * 2 ** 3) * dy / (np.sqrt(np.pi))

    return (
        # convert back to normal x units in displacement map
        4 * k20 / weight_spot / weight_spot,
        4 * k02 / weight_spot / weight_spot,
    )


def overlap_1D_curvature_coefficients(x, z, weight_spot: float):
    """Computes the amount of spot size weighted quadratic `x**2` term there is present
    in some 1D data.

    Parameters
    ----------
    x : ndarray(dtype=float)
        Sample points, ideally should be symmetric about 0.
    z : ndarray(dtype=float)
        function at sample points x
    weight_spot : float
        Spot size to use as weighting

    Returns
    -------
    quadratic_term : double
        Weighted quadratic term of z

    Notes
    -----
    This function is essentially evaluating a weighted Hermite polynomial
    overlap integral with `z(x)` to determine the linear term.

    .. math::

        \\int_{\\min(x)}^{\\max(x)} H_{2}(x) z(x) W(x) dx

    Where the weighting function is :math:`W(x) = exp(-x**2)`.
    """
    weight_spot /= np.sqrt(2)
    dx = (x[1] - x[0]) / weight_spot
    # exponential weighting of spot size
    W = np.exp(-((x / weight_spot) ** 2))
    # Second order Hermite, H_2(x)
    Hn = ((2 * x / weight_spot) ** 2 - 2) * W
    # normalisation constant as integral of H_0(x) over
    # domain is not 1
    norm = (
        0.5 * np.sqrt(np.pi) * (erf(x.max() / weight_spot) - erf(x.min() / weight_spot))
    )
    k20 = (z @ Hn).sum() * dx / norm
    return (
        # convert back to normal x units in displacement map
        k20
        / weight_spot
        / weight_spot
        / 2
    )


def overlap_1D_tilt_coefficients(x, z, weight_spot: float):
    """Computes the amount of spot size weighted linear `x` term there is present in
    some 1D data.

    Parameters
    ----------
    x : ndarray(dtype=float)
        Sample points, ideally should be symmetric about 0.
    z : ndarray(dtype=float)
        function at sample points x
    weight_spot : float
        Spot size to use as weighting

    Returns
    -------
    linear_term : double
        Weighted linear term of z

    Notes
    -----
    This function is essentially evaluating a weighted Hermite polynomial
    overlap integral with `z(x)` to determine the linear term.

    .. math::

        \\int_{\\min(x)}^{\\max(x)} H_{1}(x) z(x) W(x) dx

    Where the weighting function is :math:`W(x) = exp(-x**2)`.
    """
    weight_spot /= np.sqrt(2)
    dx = (x[1] - x[0]) / weight_spot
    # exponential weighting of spot size
    W = np.exp(-((x / weight_spot) ** 2))
    # Second order Hermite, H_1(x)
    Hn = 2 * x / weight_spot * W
    # normalisation constant as integral of H_0(x) over
    # domain is not 1
    norm = np.sqrt(np.pi) * (erf(x.max() / weight_spot) - erf(x.min() / weight_spot))
    k10 = (z @ Hn).sum() * dx / norm
    return (
        # convert back to normal x units in displacement map
        2
        * k10
        / weight_spot
    )
