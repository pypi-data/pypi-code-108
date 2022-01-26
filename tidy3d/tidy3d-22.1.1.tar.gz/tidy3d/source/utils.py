import numpy as np

from ..constants import fp_eps, ETA_0, C_0

def gaussian_beam_params(w0, z, k):
    """Compute the parameters needed to evaluate a Gaussian beam at z.
    
    Parameters
    ----------
    w0 : float
        Waist radius.
    z : float
        Axial distance from the beam focus.
    k : float
        Wave vector magnitude.
    """

    zR = w0**2 * k / 2
    wz = w0 * np.sqrt(1 + (z / zR)**2)
    Rz = (z + fp_eps) * (1 + (zR / (z + fp_eps))**2)
    psi_G = np.arctan(z / zR)

    return wz, Rz, psi_G


def paraxial_gaussian_beam(x, y, z, w0, k):
    """Compute the paraxial approximatin Gaussian beam field distribution
    at an array of points with coordinates x, y, z, given waist radius w0, and
    wave vector magnitude k.

    x, y, z must have the same shape.
    """

    wz, Rz, psi_G = gaussian_beam_params(w0, z, k)
    r2 = x**2 + y**2
    G = w0 / wz
    G *= np.exp(-r2 / wz**2)
    G = G * np.exp(1j * (k*z + k*r2/2/Rz - psi_G))

    return G


def pol_vectors(dir_vec, pol_angle):
    """E and H basis vectors for linear polarization given normalized k-vector
    dir_vec, defined by pol_angle, assuming z-normal axis.
    """

    # Unit vector along axis normal to injection plane
    norm_vec = np.array([0, 0, 1])

    # Unit vector for S polarization
    # Add a tiny bit of offset to break S-P degeneracy at theta = 0
    dvec = np.copy(dir_vec)
    if np.linalg.norm(np.cross(norm_vec, dvec)) < fp_eps:
        dvec[0] += fp_eps
    S_vec = np.cross(norm_vec, dvec)
    S_vec /= np.sqrt(S_vec.dot(S_vec))

    # Unit vector for P polarization
    P_vec = np.cross(S_vec, dir_vec)
    P_vec /= np.sqrt(P_vec.dot(P_vec))

    # E-field polarization vector
    E_vec = np.cos(pol_angle)*P_vec + np.sin(pol_angle)*S_vec
    # H-field polarization vector
    H_vec = - np.sin(pol_angle)*P_vec + np.cos(pol_angle)*S_vec

    return E_vec, H_vec
