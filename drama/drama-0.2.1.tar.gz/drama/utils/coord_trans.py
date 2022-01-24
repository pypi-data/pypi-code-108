import numpy as np

import drama.constants as const


def rotation_matrix(axis, theta):
    """Return the rotation matrix associated with counterclockwise rotation
        about he given axis by theta radians.
        # np.dot(rotation_matrix(axis,theta), vector)

    Parameters
    ----------
    axis :
        axis to be rotated, either as a 1 to 3 number or as a
        vector
    theta :
        angle in radian

    Returns
    -------

    """
    axis = np.asarray(axis)
    if axis.size == 1:
        axs = np.zeros(3)
        axs[axis - 1] = 1
    else:
        axs = axis
    theta = np.asarray(theta)
    axs = axs / np.sqrt(np.dot(axs, axs))
    a = np.cos(theta / 2)
    b, c, d = -axs * np.sin(theta / 2)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array(
        [
            [aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
            [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
            [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc],
        ]
    )


def squinted_versor(squint, n_ver, v_ecf_ver):
    """Rotates the versor perpendicular to orbital position and velocity
    (in ecef coordinates) of a mechanical squint.

    author: Paco Lopez-Dekker

    Parameters
    ----------
    squint : float
        squint angle to be applied [deg].
    n_ver : float 2-D array
        perpendicular versor in the case of zero squint
    v_ecf_ver : float 2-D array
        orbital velocity (ecef).

    Returns
    -------
    float 2-D array 
        the versor rotated of the squint angle
    """
    squint_rad = np.radians(squint)
    n_ver_sq = n_ver * np.cos(squint_rad) + v_ecf_ver * np.sin(squint_rad)

    return n_ver_sq


def rot_matrix(x_rot, y_rot, z_rot):
    """
    Computes the rotation matrix corresponding to a rotation of x_rot
    about the x-axis, y_rot about the y-axis and z_rot about the
    z-axis.

    Parameters
    ----------
    x_rot : float
        angle of rotation about x-axis
    y_rot : float
        angle of rotation about y-axis
    z_rot : float
        angle of rotation about z-axis

    Returns
    -------
    ndarray 3-by-3
        rotation matrix
    """
    c_theta = np.cos(y_rot)
    s_theta = np.sin(y_rot)
    c_psi = np.cos(z_rot)
    s_psi = np.sin(z_rot)
    c_phi = np.cos(x_rot)
    s_phi = np.sin(x_rot)
    m = np.array(
        [
            [c_theta * c_psi, c_theta * s_psi, -s_theta],
            [
                s_phi * s_theta * c_psi - c_phi * s_psi,
                s_phi * s_theta * s_psi + c_phi * c_psi,
                s_phi * c_theta,
            ],
            [
                c_phi * s_theta * c_psi + s_phi * s_psi,
                c_phi * s_theta * s_psi - s_phi * c_psi,
                c_phi * c_theta,
            ],
        ]
    )
    return m


def rot_z(vector, angle, inverse_transform=False):
    """Rotates vector by angle around z-axis

    Parameters
    ----------
    vector : ndarray
        3 dimensional vector to rotate
    angle : float
        angle of rotation [deg]
    inverse_transform : bool
        Perform inverse rotation around z-axis (Default value = False)

    Returns
    -------
    ndarray
        rotated vector coordinates
    """
    if vector.shape[0] != 3:
        vector = vector.T
    if vector.ndim == 1:
        vector = vector.reshape((3, 1))
    angle_rad = np.deg2rad(angle)
    if inverse_transform:
        angle_rad == -angle_rad

    xp = np.cos(angle_rad) * vector[0] + np.sin(angle_rad) * vector[1]
    yp = -np.sin(angle_rad) * vector[0] + np.cos(angle_rad) * vector[1]
    zp = vector[2]
    return np.array([xp, yp, zp])


def rot_z_prime(vector, angle, inverse_transform=False):
    """Derivative of rot_z matrix w.r.t time (Need to be further multiplied
        by the argument's derivative of the angle)

    Parameters
    ----------
    vector : ndarray
        3 dimensional vector to rotate
    angle :
        angle of of rotation [deg]
    inverse_transform : bool
        Perform inverse rotation around z-axis (Default value = False)

    Returns
    -------
    ndarray
        rotated vector coordinates
    """
    if vector.shape[0] != 3:
        vector = vector.T
    if vector.ndim == 1:
        vector = vector.reshape((3, 1))
    angle_rad = np.deg2rad(angle)
    if inverse_transform:
        angle_rad == -angle_rad

    xp = -np.sin(angle_rad) * vector[0] + np.cos(angle_rad) * vector[1]
    yp = -np.cos(angle_rad) * vector[0] - np.sin(angle_rad) * vector[1]
    zp = np.zeros_like(xp)
    return np.array([xp, yp, zp])


def rot_x(vector, angle, inverse_transform=False):
    """Rotates vector by angle around x-axis

    Parameters
    ----------
    vector : ndarray
        3 dimensional vector to rotate
    angle : float
        angle [deg]
    inverse_Transform : bool
        Perform inverse rotation around x-axis (Default value = False)

    Returns
    -------
    ndarray
        rotated vector coordinates
    """
    if vector.shape[0] != 3:
        vector = vector.T
    if vector.ndim == 1:
        vector = vector.reshape((3, 1))
    angle_rad = np.deg2rad(angle)
    if inverse_transform:
        angle_rad == -angle_rad

    xp = vector[0]
    yp = np.cos(angle_rad) * vector[1] + np.sin(angle_rad) * vector[2]
    zp = -np.sin(angle_rad) * vector[1] + np.cos(angle_rad) * vector[2]
    return np.array([xp, yp, zp])
