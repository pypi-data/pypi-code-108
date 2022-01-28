"""Cavity tests."""

import pytest
import numpy as np
from finesse import Model
from finesse.components import Cavity, Mirror, Beamsplitter


@pytest.fixture(scope="module")
def equivalent_cavities():
    """Fixture to provide different types of cavity (2-, 3-, 4-mirror) that are equivalent."""
    T1 = 500e-6
    T2 = 30e-6
    # Equivalent of T2 through 2 mirrors.
    T2T = 1 - (1 - T2) ** (1 / 2)
    # Equivalent of T2 through 3 mirrors.
    T2Q = 1 - (1 - T2) ** (1 / 3)

    # 10 m linear cavity model.
    m11 = Mirror("m11", T=T1, L=0, Rc=12)
    m12 = Mirror("m12", T=T2, L=0)
    model_linear = Model()
    model_linear.connect(m11.p1, m12.p1, L=9)

    # 10 m triple cavity model.
    # Needs to use beam splitters because the incoming and outgoing beams are separate.
    m21 = Beamsplitter("m21", T=T1, L=0, Rc=12)
    m22 = Beamsplitter("m22", T=T2T, L=0)
    m23 = Beamsplitter("m23", T=T2T, L=0)
    model_triple = Model()
    model_triple.connect(m21.p1, m22.p2, L=6)
    model_triple.connect(m22.p1, m23.p2, L=6)
    model_triple.connect(m23.p1, m21.p2, L=6)

    # 10 m quadruple cavity model.
    # Needs to use beam splitters because the incoming and outgoing beams are separate.
    m31 = Beamsplitter("m31", T=T1, L=0, Rc=12)
    m32 = Beamsplitter("m32", T=T2Q, L=0)
    m33 = Beamsplitter("m33", T=T2Q, L=0)
    m34 = Beamsplitter("m34", T=T2Q, L=0)
    model_quad = Model()
    model_quad.connect(m31.p1, m32.p2, L=4.5)
    model_quad.connect(m32.p1, m33.p2, L=4.5)
    model_quad.connect(m33.p1, m34.p2, L=4.5)
    model_quad.connect(m34.p1, m31.p2, L=4.5)

    # Cavity models.
    cav_linear = Cavity("cav_linear", m11.p1.o)
    cav_triple = Cavity("cav_triple", m21.p1.o, m22.p2.i)
    cav_quad = Cavity("cav_quad", m31.p1.o, m32.p2.i)

    model_linear.add(cav_linear)
    model_triple.add(cav_triple)
    model_quad.add(cav_quad)

    # Need to return the models here too because they're only contained inside the cavities as
    # weakrefs and could be lost to garbage collection otherwise.
    return (
        (model_linear, cav_linear),
        (model_triple, cav_triple),
        (model_quad, cav_quad),
    )


def test_equivalent_cavities_round_trip_length(equivalent_cavities):
    """Test that 2-, 3- and 4-mirror cavities with equivalent properties have same round trip \
    length."""
    (_, cav_linear), (_, cav_triple), (_, cav_quad) = equivalent_cavities
    assert (
        cav_linear.round_trip_length
        == cav_triple.round_trip_length
        == cav_quad.round_trip_length
        != 0
    )


def test_equivalent_cavities_abcd(equivalent_cavities):
    """Test that 2-, 3- and 4-mirror cavities with equivalent properties have same ABCD matrices.

    Because only one mirror in each cavity has a radius of curvature, and the round-trip lengths
    are the same, the cavities should have the same ABCD matrices as long as the same surfaces
    are connected (for the Rc sign convention). However, because the triple cavity has an odd
    number of reflections, the x-plane ABCD matrix is flipped.
    """
    (_, cav_linear), (_, cav_triple), (_, cav_quad) = equivalent_cavities
    assert np.all(cav_linear.ABCDx == cav_quad.ABCDx)
    assert np.all(cav_linear.ABCDx == -cav_triple.ABCDx)
    assert np.all(cav_linear.ABCDy == cav_quad.ABCDy)
    assert np.all(cav_linear.ABCDy == cav_triple.ABCDy)


def test_equivalent_cavities_gouy(equivalent_cavities):
    """Test that 2- and 4-mirror cavities with equivalent properties have same gouy phase, but \
    that the 3-mirror equivalent does not.

    The triple cavity has an odd number of reflections, so the gouy phase in the x-direction is
    different.
    """
    (_, cav_linear), (_, cav_triple), (_, cav_quad) = equivalent_cavities

    assert cav_linear.gouy_x != 0
    assert cav_linear.gouy_x != cav_triple.gouy_x
    assert cav_linear.gouy_x == cav_quad.gouy_x

    assert cav_linear.gouy_y != 0
    assert cav_linear.gouy_y == cav_triple.gouy_y
    assert cav_linear.gouy_y == cav_quad.gouy_y


def test_equivalent_cavities_power_and_loss(equivalent_cavities):
    """Test that 2-, 3- and 4-mirror cavities with equivalent properties have same power and \
    loss."""
    (_, cav_linear), (_, cav_triple), (_, cav_quad) = equivalent_cavities

    assert cav_linear.loss != 0
    assert cav_triple.loss != 0
    assert cav_quad.loss != 0
    assert np.isclose(cav_linear.loss, cav_triple.loss)
    assert np.isclose(cav_linear.loss, cav_quad.loss)


def test_equivalent_cavities_finesse(equivalent_cavities):
    """Test that 2-, 3- and 4-mirror cavities with equivalent properties have same finesse."""
    (_, cav_linear), (_, cav_triple), (_, cav_quad) = equivalent_cavities

    assert cav_linear.finesse != 0
    assert cav_triple.finesse != 0
    assert cav_quad.finesse != 0
    assert np.isclose(cav_linear.finesse, cav_triple.finesse)
    assert np.isclose(cav_linear.finesse, cav_quad.finesse)


def test_equivalent_cavities_fsr(equivalent_cavities):
    """Test that 2-, 3- and 4-mirror cavities with equivalent properties have same FSR."""
    (_, cav_linear), (_, cav_triple), (_, cav_quad) = equivalent_cavities

    assert cav_linear.FSR != 0
    assert cav_triple.FSR != 0
    assert cav_quad.FSR != 0
    assert cav_linear.FSR == cav_triple.FSR
    assert cav_linear.FSR == cav_quad.FSR


def test_equivalent_cavities_fwhm(equivalent_cavities):
    """Test that 2-, 3- and 4-mirror cavities with equivalent properties have same FWHM."""
    (_, cav_linear), (_, cav_triple), (_, cav_quad) = equivalent_cavities

    assert cav_linear.FWHM != 0
    assert cav_triple.FWHM != 0
    assert cav_quad.FWHM != 0
    assert np.isclose(cav_linear.FWHM, cav_triple.FWHM)
    assert np.isclose(cav_linear.FWHM, cav_quad.FWHM)


def test_equivalent_cavities_pole(equivalent_cavities):
    """Test that 2-, 3- and 4-mirror cavities with equivalent properties have same pole."""
    (_, cav_linear), (_, cav_triple), (_, cav_quad) = equivalent_cavities

    assert cav_linear.pole != 0
    assert cav_triple.pole != 0
    assert cav_quad.pole != 0
    assert np.isclose(cav_linear.pole, cav_triple.pole)
    assert np.isclose(cav_linear.pole, cav_quad.pole)


def test_equivalent_cavities_mode_separation(equivalent_cavities):
    """Test that 2-, 3- and 4-mirror cavities with equivalent properties have same mode \
    separation.

    The triple cavity has an odd number of reflections, so the mode separation in the x-direction is
    different.
    """
    (_, cav_linear), (_, cav_triple), (_, cav_quad) = equivalent_cavities

    assert cav_linear.mode_separation_x != 0
    assert cav_triple.mode_separation_x != 0
    assert cav_quad.mode_separation_x != 0
    assert cav_linear.mode_separation_x != cav_triple.mode_separation_x
    assert np.isclose(cav_linear.mode_separation_x, cav_quad.mode_separation_x)

    assert cav_linear.mode_separation_y != 0
    assert cav_triple.mode_separation_y != 0
    assert cav_quad.mode_separation_y != 0
    assert np.isclose(cav_linear.mode_separation_y, cav_triple.mode_separation_y)
    assert np.isclose(cav_linear.mode_separation_y, cav_quad.mode_separation_y)


def test_equivalent_cavities_q(equivalent_cavities):
    """Test that 2-, 3- and 4-mirror cavities with equivalent properties have same q."""
    (_, cav_linear), (_, cav_triple), (_, cav_quad) = equivalent_cavities

    assert cav_linear.qx != 0
    assert cav_triple.qx != 0
    assert cav_quad.qx != 0
    assert cav_linear.qx == cav_triple.qx
    assert cav_linear.qx == cav_quad.qx

    assert cav_linear.qy != 0
    assert cav_triple.qy != 0
    assert cav_quad.qy != 0
    assert cav_linear.qy == cav_triple.qy
    assert cav_linear.qy == cav_quad.qy


def test_equivalent_cavities_resolution(equivalent_cavities):
    """Test that 2-, 3- and 4-mirror cavities with equivalent properties have same resolution.

    The triple cavity has an odd number of reflections, so the resolution in the x-direction is
    different.
    """
    (_, cav_linear), (_, cav_triple), (_, cav_quad) = equivalent_cavities

    assert cav_linear.Sx != 0
    assert cav_triple.Sx != 0
    assert cav_quad.Sx != 0
    assert cav_linear.Sx != cav_triple.Sx
    assert np.isclose(cav_linear.Sx, cav_quad.Sx)

    assert cav_linear.Sy != 0
    assert cav_triple.Sy != 0
    assert cav_quad.Sy != 0
    assert np.isclose(cav_linear.Sy, cav_triple.Sy)
    assert np.isclose(cav_linear.Sy, cav_quad.Sy)


def test_equivalent_cavities_g(equivalent_cavities):
    """Test that 2-, 3- and 4-mirror cavities with equivalent properties have same g (stability).

    The triple cavity has an odd number of reflections, so the resolution in the x-direction is
    different.
    """
    (_, cav_linear), (_, cav_triple), (_, cav_quad) = equivalent_cavities

    assert cav_linear.gx != 0
    assert cav_triple.gx != 0
    assert cav_quad.gx != 0
    assert cav_linear.gx != cav_triple.gx
    assert cav_linear.gx == cav_quad.gx

    assert cav_linear.gy != 0
    assert cav_triple.gy != 0
    assert cav_quad.gy != 0
    assert cav_linear.gy == cav_triple.gy
    assert cav_linear.gy == cav_quad.gy


def test_equivalent_cavities_stable(equivalent_cavities):
    """Test that 2-, 3- and 4-mirror cavities with equivalent properties are equally stable."""
    (_, cav_linear), (_, cav_triple), (_, cav_quad) = equivalent_cavities

    assert all((cav_linear.is_stable_x, cav_triple.is_stable_x, cav_quad.is_stable_x))
    assert all((cav_linear.is_stable_y, cav_triple.is_stable_y, cav_quad.is_stable_y))


def test_equivalent_cavities_critical(equivalent_cavities):
    """Test that 2-, 3- and 4-mirror cavities with equivalent properties are equally (not) \
    critical."""
    (_, cav_linear), (_, cav_triple), (_, cav_quad) = equivalent_cavities

    assert not any(
        (cav_linear.is_critical_x, cav_triple.is_critical_x, cav_quad.is_critical_x)
    )
    assert not any(
        (cav_linear.is_critical_x, cav_triple.is_critical_x, cav_quad.is_critical_x)
    )
