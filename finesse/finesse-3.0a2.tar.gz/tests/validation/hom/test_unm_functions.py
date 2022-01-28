"""Tests for u_nm function correctness"""

import numpy as np
from scipy.special import factorial, hermite
from numpy.testing import assert_allclose
import pytest
from finesse.gaussian import HGMode


def analytic_un(n, x, qx):
    """Direct translation of Equation (9.34) from:
    'Interferometer Techniques for Gravitational Wave Detection'
    """
    k = 2 * np.pi / qx.wavelength
    return (
        (2 / np.pi) ** 0.25
        * np.sqrt(1 / (2 ** n * factorial(n) * qx.w0))
        * np.sqrt(1j * qx.zr / qx.q)
        * (1j * qx.zr * qx.conjugate().q / (-1j * qx.zr * qx.q)) ** (n / 2)
        * hermite(n)(np.sqrt(2) * x / qx.w)
        * np.exp(-1j * k * x ** 2 / (2 * qx.q))
    )


@pytest.mark.parametrize(
    "qx_qy", ([1j, 1j], [-1 + 0.6j, -1.1 + 0.6j], [3 + 1.5j, 4.2 + 1.4j]),
)
@pytest.mark.parametrize(
    "n", (0, 1, 4, 9, 22),
)
@pytest.mark.parametrize(
    "m", (0, 2, 3, 6, 23),
)
def test_unm(qx_qy, n, m):
    """Test that u_nm functions in finesse.cymath.homs give correct
    results corresponding to exact analytic form."""
    qx, qy = qx_qy
    HGnm = HGMode([qx, qy], n, m)

    x = np.linspace(-HGnm.qx.w0 * 3, HGnm.qx.w0 * 3, 51)
    y = np.linspace(-HGnm.qy.w0 * 3, HGnm.qy.w0 * 3, 51)
    u_nm = HGnm.unm(x, y)

    expect = np.outer(analytic_un(n, x, HGnm.qx), analytic_un(m, y, HGnm.qy))

    assert_allclose(u_nm, expect)
