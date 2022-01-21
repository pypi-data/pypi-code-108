#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Benjamin Vial
# License: MIT


import jax.numpy as jnp
import scipy.special as sp

"""
j0 implementation from Cephes
https://github.com/jeremybarnes/cephes
"""

DR1 = 5.78318596294678452118e0
DR2 = 3.04712623436620863991e1
RP = [
    -4.79443220978201773821e9,
    1.95617491946556577543e12,
    -2.49248344360967716204e14,
    9.70862251047306323952e15,
]

RQ = [
    4.99563147152651017219e2,
    1.73785401676374683123e5,
    4.84409658339962045305e7,
    1.11855537045356834862e10,
    2.11277520115489217587e12,
    3.10518229857422583814e14,
    3.18121955943204943306e16,
    1.71086294081043136091e18,
]
PP = [
    7.96936729297347051624e-4,
    8.28352392107440799803e-2,
    1.23953371646414299388e0,
    5.44725003058768775090e0,
    8.74716500199817011941e0,
    5.30324038235394892183e0,
    9.99999999999999997821e-1,
]
PQ = [
    9.24408810558863637013e-4,
    8.56288474354474431428e-2,
    1.25352743901058953537e0,
    5.47097740330417105182e0,
    8.76190883237069594232e0,
    5.30605288235394617618e0,
    1.00000000000000000218e0,
]

QP = [
    -1.13663838898469149931e-2,
    -1.28252718670509318512e0,
    -1.95539544257735972385e1,
    -9.32060152123768231369e1,
    -1.77681167980488050595e2,
    -1.47077505154951170175e2,
    -5.14105326766599330220e1,
    -6.05014350600728481186e0,
]

QQ = [
    6.43178256118178023184e1,
    8.56430025976980587198e2,
    3.88240183605401609683e3,
    7.24046774195652478189e3,
    5.93072701187316984827e3,
    2.06209331660327847417e3,
    2.42005740240291393179e2,
]


def j0small(x):
    z = x ** 2
    p = (z - DR1) * (z - DR2)
    P = jnp.polyval(jnp.array(RP), z)
    Q = jnp.polyval(jnp.array([1.0]) + jnp.array(RQ), z)
    p *= P / Q
    return jnp.where(x <= 1.0e-5, 1.0 - z / 4.0, p)


def j0large(x):
    w = 5.0 / x
    q = 25.0 / x ** 2
    p = jnp.polyval(jnp.array(PP), q) / jnp.polyval(jnp.array(PQ), q)
    q = jnp.polyval(jnp.array(QP), q) / jnp.polyval(jnp.array([1.0]) + jnp.array(QQ), q)

    xn = x - jnp.pi / 4
    p = p * jnp.cos(xn) - w * q * jnp.sin(xn)
    return p * jnp.sqrt(2 / jnp.pi) / jnp.sqrt(x)


def j0(x):
    x *= jnp.sign(x)
    return jnp.where(x <= 5, j0small(x), j0large(x))


def j0_scipy(z):
    return sp.j0(z)


def j0_approx(z, N=100):
    a = (
        1 / 6
        + 1 / 3 * jnp.cos(z / 2)
        + 1 / 3 * jnp.cos(3 ** 0.5 * z / 2)
        + 1 / 6 * jnp.cos(z)
    )

    b = (2 / (1e-10 + jnp.pi * jnp.abs(z))) ** 0.5 * jnp.cos(
        z - jnp.pi / 4 * jnp.sign(jnp.real(z))
    )

    smooth = 1 / (1 + (z / 7) ** 6)
    out = a * smooth + b * (1 - smooth)
    # out = jnp.where(jnp.abs(z<7),a,b)
    # out = out.at[0].set(1)
    return out


def j0_int(z, N=100):
    Nz = z.size
    pi = jnp.pi
    t = jnp.linspace(0, pi, N) * jnp.ones((Nz, N))
    integrand = jnp.exp(1j * z * jnp.cos(t.T))
    out_int = jnp.trapz(integrand.T, t, axis=1) / pi
    out_int = out_int.at[0].set(0)
    return out_int


# def j0(z):
#     return j0_approx(z, N=100)
#
#
# from jax.scipy.special import i0
#
# def j0(z):
#     return jnp.where(jnp.imag(z) >= 5, i0(-1j*z), i0(1j*z))
#


if __name__ == "__main__":

    from jax import grad

    for z in jnp.linspace(1000, 1000, 1):
        zc = z * (1 + 1 * 1j)

        print(sp.jn(0, zc))
        print(-sp.jn(1, zc))

        print(j0(zc))
        print(grad(j0, holomorphic=True)(zc))
