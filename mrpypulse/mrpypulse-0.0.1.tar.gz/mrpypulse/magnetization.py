"""This module contains functions for simulation purposes."""

import numpy as np
import matplotlib.pyplot as plt


def simulate(pulses, off=None, tend=None, pc=None):
    """
    Calculation of the magnetization for different offsets

    Parameters
    ----------
    pulses: list of pulses
        pulses to be applied to magnetization
    off: numpy array of floats
        list of offsets at which to perform the simulation, initialized to
        np.linspace(-0.75*pulses[0].bw, 0.75*pulses[0].bw, 100) if not provided
        (and possible to initialize)
    pc: numpy array of floats
        phase cycling to be used on pulses

    Returns
    -------
    off: ndarray
        if no offset is input, the generated offsets are output
    magn: ndarray
        ndarray containing the magnetisation across the spectral width
    """
    return_off = False
    if off is None:
        limit = 0.75*pulses[0].bw
        off = np.linspace(-limit, limit, 100)
        return_off = True

    if tend is None:
        tend = pulses[-1].end

    if pc is None:
        pc = np.zeros((len(pulses)+1, 1))

    npc = pc.shape[1]
    noff = len(off)

    magn = np.zeros((3, len(off), npc))

    for phase in range(npc):
        for o in range(noff):

            # default: magnetization on z
            M = np.array([0, 0, 1])

            # potential delay before first pulse
            if pulses[0].start > 0:
                M = np.dot(rz(2 * np.pi * off[o] * pulses[0].start), M)

            for i, p in enumerate(pulses):

                # vectorized rotational matrix (contains all the pulse points)
                p_rtot = rtot(p.r, off[o], pc[i, phase] + p.ph, p.tres)

                # apply rotational matrixes to magnetization
                for j in range(p.ns):
                    M = np.dot(p_rtot[:, :, j], M)

                # potential delay between pulses
                if i < len(pulses) - 1:

                    if p.end < pulses[i+1].start:
                        M = np.dot(rz(
                            2 * np.pi * off[o] * (pulses[i+1].start-p.end)),
                            M)

            # potential delay after last pulse
            if pulses[-1].end < tend:
                M = np.dot(rz(
                    2 * np.pi * off[o] * (tend - pulses[-1].end)), M)

            magn[:, o, phase] = np.dot(rz(-pc[-1, phase]), M)

    magn = np.sum(magn, axis=2) / npc  # phase cycling collapse

    if return_off:
        return off, magn
    else:
        return magn


def magn_phase(magn):
    """
    Compute the phase of the magnetisation

    Parameters
    ----------
    magn: numpy array of floats

    Returns
    -------
    phase: 1D numpy array of floats
        phase of the magnetisation
    """
    return np.unwrap(np.angle(magn[1, :] + 1j * magn[0, :]))


def plot_magn(magn, off):
    """
    Plot the magnetization components over the offsets

    Parameters
    ----------
    magn: numpy array of floats
        magnetization to plot
    off: numpy array of floats
        offsets of the magnetization
    """
    plt.figure(figsize=(6, 8))

    Ix = magn[0, :]
    Iy = magn[1, :]
    Iz = magn[2, :]
    Ixy = np.sqrt(Ix**2 + Iy**2)
    phase = magn_phase(magn)

    display = {"Ix": Ix, "Iy": Iy, "Iz": Iz, "Ixy": Ixy, "Phase": phase}

    nb_subplot = 1

    plt.suptitle('Magnetization and phase vs offset')

    for [key, value] in display.items():
        plt.subplot(5, 1, nb_subplot)
        plt.plot(off, value)
        plt.xlim(off[0], off[-1])
        plt.ylim(-1, 1)
        plt.ylabel(key)
        nb_subplot += 1
        if key == "Phase":
            plt.ylim(min(value), max(value))

    plt.xlabel("Offsets")
    plt.tight_layout()


def rx(phi):
    """Returns the rotational matrix for an angle phi around the x-axis

    If phi is an array containing n angles, return an array of n
    rotational matrixes for these angles around the x-axis.
    """
    if type(phi) == np.ndarray:

        m11 = np.full(len(phi), 1)
        m12 = np.full(len(phi), 0)
        m22 = np.cos(phi)
        m23 = np.sin(phi)

        m1 = np.stack((m11, m12, m12), axis=0)
        m2 = np.stack((m12, m22, m23), axis=0)
        m3 = np.stack((m12, m23, m22), axis=0)

        x_rot_mat = np.stack((m1, m2, m3), axis=0)

    else:
        x_rot_mat = np.array(([1, 0, 0],
                              [0, np.cos(phi), np.sin(phi)],
                              [0, np.sin(phi), np.cos(phi)]))

    return x_rot_mat


def ry(phi):
    """Returns the rotational matrix for an angle phi around the y-axis
    """
    if type(phi) == np.ndarray:
        m11 = np.cos(phi)
        m12 = np.full(len(phi), 0)
        m13 = np.sin(phi)
        m22 = np.full(len(phi), 1)

        m1 = np.stack((m11, m12, m13), axis=0)
        m2 = np.stack((m12, m22, m12), axis=0)
        m3 = np.stack((-m13, m12, m11), axis=0)

        y_rot_mat = np.stack((m1, m2, m3), axis=0)

    else:
        y_rot_mat = np.array(([np.cos(phi), 0, np.sin(phi)],
                              [0, 1, 0],
                              [-np.sin(phi), 0, np.cos(phi)]))
    return y_rot_mat


def rz(phi):
    """Returns the rotational matrix for an angle phi around the z-axis
    """
    if type(phi) == np.ndarray:
        m11 = np.cos(phi)
        m12 = np.sin(phi)
        m13 = np.full(len(phi), 0)
        m33 = np.full(len(phi), 1)

        m1 = np.stack((m11, -m12, m13), axis=0)
        m2 = np.stack((m12, m11, m13), axis=0)
        m3 = np.stack((m13, m13, m33), axis=0)

        z_rot_mat = np.stack((m1, m2, m3), axis=0)

    else:
        z_rot_mat = np.array(([np.cos(phi), -np.sin(phi), 0],
                              [np.sin(phi), np.cos(phi), 0],
                              [0, 0, 1]))

    return z_rot_mat


def rtot(omega, off, phi, time):
    """Returns the rotational matrix associated with a linear chirp
    inputs: pulse parameters
        - omega: point radiofrequency  or array containing points
        associated with the B1 field
        - off: point offset
        - phi: point phase
        - time
    output:
        - total_rot_mat: rotational matrix point associated with the
        pulse point or array of rotational matrixes associated with the
        pulse points
    Also computes omega_eff the angular frequency of the effective field
    Beff, theta the angle between Beff and B1 and the flip angle alpha
    for the calculation of total_rot_mat
    """
    # Beff angular frequency
    omega_eff = np.sqrt((2 * np.pi * omega)**2 + (2 * np.pi * off)**2)

    theta = np.arctan2(omega, off)  # angle between Beff and B1
    alpha = time * omega_eff  # flip angle

    if type(phi) == np.ndarray:

        # array with each pulse point rotational matrix
        total_rot_mat = np.einsum('ijh,jkh,klh,lmh,mnh->inh',
                                  rz(phi),
                                  ry(theta),
                                  rz(alpha),
                                  ry(-theta),
                                  rz(-phi))

    else:

        total_rot_mat = \
            rz(phi).dot(ry(theta).dot(rz(alpha).dot(ry(-theta).dot(rz(-phi)))))

    return total_rot_mat
