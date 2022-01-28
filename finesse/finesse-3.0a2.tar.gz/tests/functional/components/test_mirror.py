"""Mirror unit tests."""

import pytest
import numpy as np
from finesse.components import Mirror
from . import TestSurface


@pytest.fixture
def component():
    """Set the fixture used by TestMirrorSurface to a mirror."""
    return Mirror


class TestMirrorSurface(TestSurface):
    """Test surface properties (R, T, L, Rc, etc.)."""


@pytest.mark.parametrize(
    "Rcx,Rcy",
    (
        (np.inf, np.inf),
        (np.inf, -np.inf),
        (-np.inf, np.inf),
        (-np.inf, -np.inf),
        (1, 1),
        (1, -1),
        (-1, 1),
        (-1, -1),
        (3.141, 6.282),
        (3.141, -6.282),
        (-3.141, 6.282),
        (-3.141, -6.282),
        (1e9, 1e-6),
        (1e9, -1e-6),
        (-1e9, 1e-6),
        (-1e9, -1e-6),
    ),
)
def test_abcd(Rcx, Rcy):
    """Test that the ABCD matrix of particular combinations of ports shows symmetry with other \
    ports.

    The sign of Rc matters when we test against port pairs on the opposite surface. See
    https://finesse.readthedocs.io/en/latest/api/components/mirror/generated/finesse.components.mirror.Mirror.ABCD.html#finesse.components.mirror.Mirror.ABCD.

    For REFLECTION:

        Mirror( Rcx,  Rcy).p1.i -> Mirror( Rcx,  Rcy).p1.o

                            is equal to:

        Mirror(-Rcx, -Rcy).p2.i -> Mirror(-Rcx, -Rcy).p2.o

    For TRANSMISSION:

        Mirror( Rcx,  Rcy).p1.i -> Mirror( Rcx,  Rcy).p2.o

                            is equal to:

        Mirror(-Rcx, -Rcy).p2.i -> Mirror(-Rcx, -Rcy).p1.o
    """

    m_ref = Mirror("m", Rc=(Rcx, Rcy))
    m_cmp = Mirror("m", Rc=(-Rcx, -Rcy))

    ## Each test below checks x- then y-directions.

    # Reflection
    r_lhs_x = m_ref.ABCD(m_ref.p1.i, m_ref.p1.o, direction="x")
    r_lhs_y = m_ref.ABCD(m_ref.p1.i, m_ref.p1.o, direction="y")

    assert np.all(r_lhs_x == m_cmp.ABCD(m_cmp.p2.i, m_cmp.p2.o, direction="x"))
    assert np.all(r_lhs_y == m_cmp.ABCD(m_cmp.p2.i, m_cmp.p2.o, direction="y"))

    # Transmission
    t_lhs_x = m_ref.ABCD(m_ref.p1.i, m_ref.p2.o, direction="x")
    t_lhs_y = m_ref.ABCD(m_ref.p1.i, m_ref.p2.o, direction="y")

    # (1)
    assert np.all(t_lhs_x == m_cmp.ABCD(m_cmp.p2.i, m_cmp.p1.o, direction="x"))
    assert np.all(t_lhs_y == m_cmp.ABCD(m_cmp.p2.i, m_cmp.p1.o, direction="y"))
