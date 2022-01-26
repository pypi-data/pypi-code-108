#!/usr/bin/env python

"""Axially symmetric diffusion kurtosis imaging."""

import jax
import jax.numpy as jnp
import numpy as np


# Parameter array elements are:
#
# params[..., 0] = log(s0)
# params[..., 1] = u[0]
# params[..., 2] = u[1]
# params[..., 3] = u[2]
# params[..., 4] = AD
# params[..., 5] = RD
# params[..., 6] = MTK
# params[..., 7] = ATK
# params[..., 8] = RTK


def params_to_D(params):
    """Return the diffusion tensor corresponding to a parameter array.

    Parameters
    ----------
    params : numpy.ndarray
        Floating-point array with shape (9,).

    Returns
    -------
    numpy.ndarray
    """
    return (
        params[5] * np.eye(3)
        + (params[4] - params[5])
        * params[1:4][:, np.newaxis]
        @ params[1:4][np.newaxis, :]
    )


def params_to_W(params):
    """Return the kurtosis tensor corresponding to a parameter array.

    Parameters
    ----------
    params : numpy.ndarray
        Floating-point array with shape (9,).

    Returns
    -------
    numpy.ndarray
    """

    def d(i, j):
        """Kronecker delta."""
        if i == j:
            return 1
        else:
            return 0

    u = params[1:4]

    P = np.zeros((3, 3, 3, 3))
    for i in range(3):
        for j in range(3):
            for k in range(3):
                for l in range(3):
                    P[i, j, k, l] = u[i] * u[j] * u[k] * u[l]

    Q = np.zeros((3, 3, 3, 3))
    for i in range(3):
        for j in range(3):
            for k in range(3):
                for l in range(3):
                    Q[i, j, k, l] += (
                        u[i] * u[j] * d(k, l)
                        + u[i] * u[k] * d(j, l)
                        + u[i] * u[l] * d(j, k)
                        + u[j] * u[k] * d(i, l)
                        + u[j] * u[l] * d(i, k)
                        + u[k] * u[l] * d(i, j)
                    ) / 6

    I = np.zeros((3, 3, 3, 3))
    for i in range(3):
        for j in range(3):
            for k in range(3):
                for l in range(3):
                    I[i, j, k, l] += (
                        d(i, j) * d(k, l) + d(i, k) * d(j, l) + d(i, l) * d(j, k)
                    ) / 3

    return (
        0.5 * (10 * params[8] + 5 * params[7] - 15 * params[6]) * P
        + params[8] * I
        + 1.5 * (5 * params[6] - params[7] - 4 * params[8]) * Q
    )


@jax.jit
def _jit_signal(params, bten):
    """Predict signal from axially symmetric DKI parameters.

    Parameters
    ----------
    params : numpy.ndarray or jaxlib.xla_extension.DeviceArray
        Floating-point array with shape (9,).
    btens : numpy.ndarray or jaxlib.xla_extension.DeviceArray
        Floating-point array with shape (3, 3)

    Return
    ------
    float
    """
    return jnp.exp(
        params[0]
        - (
            jnp.trace(bten) * params[5]
            + (params[4] - params[5])
            * params[1:4][:, jnp.newaxis].T
            @ bten
            @ params[1:4][:, jnp.newaxis]
        )
        + ((params[4] + 2 * params[5]) / 3) ** 2
        / 6
        * (
            0.5
            * (10 * params[8] + 5 * params[7] - 15 * params[6])
            * (params[1:4][:, jnp.newaxis].T @ bten @ params[1:4][:, jnp.newaxis]) ** 2
            + 0.5
            * (5 * params[6] - params[7] - 4 * params[8])
            * (
                params[1:4][:, jnp.newaxis].T
                @ bten
                @ params[1:4][:, jnp.newaxis]
                * jnp.trace(bten)
                + 2
                * params[1:4][:, jnp.newaxis].T
                @ bten
                @ bten
                @ params[1:4][:, jnp.newaxis]
            )
            + params[8]
            / 3
            * (
                jnp.trace(bten) ** 2
                + 2 * jnp.trace(jnp.trace(jnp.tensordot(bten, bten, axes=0)))
            )
        )
    )[0, 0]


def _signal(params, btens):
    """Predict signal from axially symmetric DKI parameters.

    Parameters
    ----------
    params : numpy.ndarray
        Floating-point array with shape (9,).
    btens : numpy.ndarray
        Floating-point array with shape (number of acquisitions, 3, 3).

    Return
    ------
    numpy.ndarray
    """
    S = np.zeros(len(btens))
    for i, bten in enumerate(btens):
        S[i] = _jit_signal(params, bten)
    return S
