# -*- coding: utf-8 -*-
r"""
Utilities for lattice operations
"""
import numpy as np
from scipy.optimize import fmin


def theta(r: np.ndarray, c: float, w: float) -> np.ndarray:
    r"""
    Theta function for example needed to create skyrmion
    Args:
        c(float): size of the domain in the middle of the skyrmion
        w(float): size of the region where the spins tilt (domain wall width)
    """
    comp1 = np.arcsin(np.tanh((-r - c) * 2 / w))
    comp2 = np.arcsin(np.tanh((-r + c) * 2 / w))
    return np.pi + comp1 + comp2


def dtheta_dr(r: np.ndarray, c: float, w: float) -> np.ndarray:
    r"""
    Calculates the derivative of the theta function of the skyrmion.

    Args:
        r(np.ndarray): 2-dimensional points of the lattice
        c(float): size of the domain in the middle of the skyrmion
        w(float): size of the region where the spins tilt (domain wall width)

    Returns:
        the derivative at the input points
    """
    comp1 = 2.0 * np.sqrt(-np.tanh(2.0 * (-c + np.abs(r)) / w) ** 2 + 1) / w
    comp2 = 2.0 * np.sqrt(-np.tanh(2.0 * (c + np.abs(r)) / w) ** 2 + 1) / w
    return -comp1 - comp2


def phi(p: np.ndarray, vorticity: float, helicity: float) -> np.ndarray:
    r"""
    Theta function for example needed to create skyrmion
    """
    return vorticity * p + helicity


def sk_2dprofile(r: np.ndarray, centerx: float, centery: float, c: float, w: float) -> np.ndarray:
    r"""
    Args:
        r(np.ndarray): 2-dimensional points of the lattice
        centerx(float): (2d) xcenter of the skyrmion
        centery(float): (2d) ycenter of the skyrmion
        c(float): size of the domain in the middle of the skyrmion
        w(float): size of the region where the spins tilt (domain wall width)
    Returns:
        the theta angle calculated with sz-components of the skyrmion profile.
    """
    center = np.array([centerx, centery])
    if (np.shape(r)[1] != 2) or (len(center) != 2):
        raise ValueError('Wrong dimension of input points or center variable.')
    return np.cos(theta(np.linalg.norm(r - center,axis=1), c, w))


def sk_radius(c: float, w: float) -> float:
    r"""
    Calculates the skyrmion radius using lilley criteria

    Args:
        c(float): size of the domain in the middle of the skyrmion
        w(float): size of the region where the spins tilt (domain wall width)
    Returns:
        the skyrmion radius in units of the lattice constant.
    """
    x0 = fmin(lambda x: dtheta_dr(x, c, w), 0, disp=False, xtol=1.0E-10)[0]
    rad = x0 - theta(x0, c, w) / dtheta_dr(x0, c, w)
    return rad


def spherical_area(s1: np.ndarray, s2: np.ndarray, s3: np.ndarray) -> float:
    r"""
    Calculates the spherical area of three spins. The sign of the area is the sign of the product:
    s1 * (s2 x s3).
    Implementation taken from userlibrary by Moritz Goerzen

    Args:
        s1: spin 1
        s2: spin 2
        s3: spin 3
    Returns:
        the spherical area
    """
    con = 1 + np.dot(s1, s2) + np.dot(s2, s3) + np.dot(s3, s1)
    # all spins are parallel -> no spherical area
    if con >= 4. - 10e-8:
        area = 0.
    else:
        mat = [s1, s2, s3]
        det_mat = np.linalg.det(mat)
        # EXCEPTIONAL CASE
        if abs(con) <= 10e-8 and abs(det_mat) <= 10e-8:
            area = 0.
        # NON-EXCEPTIONAL NON-COLINEAR CASE
        else:
            area = 2.0 * np.arctan2(det_mat, con)
    return area

