"""Plane wave mirror tests."""

# FIXME (ssl): it would be nice to use fixtures with @pytest.mark.parametrize but this isn't allowed
# in pytest as of writing.

import pytest
import numpy as np
from numpy.testing import assert_allclose


@pytest.fixture
def forward_model(model):
    model.parse(
        """
        laser l1 P=1  # Laser with 1W power at the default frequency.
        space s1 l1.p1 m1.p1 L=1 # Space of 1m length.
        mirror m1 R=0.5 T=0.5 phi=0  # Mirror with R=T=0.5 at zero tuning.
        ad ad_trans m1.p2.o 0  # `amplitude' detector for light transmitted through the mirror
        ad ad_refl m1.p1.o 0  # `amplitude' detector for light reflected from the mirror
        """
    )

    return model


@pytest.fixture
def reverse_model(model):
    model.parse(
        """
        laser l1 P=1  # Laser with 1W power at the default frequency.
        space s1 l1.p1 m1.p2 L=1 # Space of 1m length.
        mirror m1 R=0.5 T=0.5 phi=0  # Mirror with R=T=0.5 at zero tuning.
        ad ad_trans m1.p1.o 0  # `amplitude' detector for light transmitted through the mirror
        ad ad_refl m1.p2.o 0  # `amplitude' detector for light reflected from the mirror
        """
    )

    return model


def test_mirror_transmissivity_forward(forward_model):
    """Test sweeping a mirror's transmissivity from forward direction."""
    forward_model.parse(
        """
        xaxis(m1.T, lin, 0.5, 0, 100)  # Sweep mirror transmissivity from 0.5 to 0 with 100 steps
        """
    )

    out = forward_model.run()
    xaxis = np.linspace(0.5, 0, 101)
    transmitted = 1j * xaxis ** 0.5
    reflected = np.ones(101) * 0.5 ** 0.5

    assert_allclose(out["ad_trans"], transmitted, rtol=1e-5, atol=1e-8)
    assert_allclose(out["ad_refl"], reflected, rtol=1e-5, atol=1e-8)


def test_mirror_transmissivity_reverse(reverse_model):
    """Test sweeping a mirror's transmissivity from reverse direction."""
    reverse_model.parse(
        """
        xaxis(m1.T, lin, 0.5, 0, 100)  # Sweep mirror transmissivity from 0.5 to 0 with 100 steps
        """
    )

    out = reverse_model.run()
    xaxis = np.linspace(0.5, 0, 101)
    transmitted = 1j * xaxis ** 0.5
    reflected = np.ones(101) * 0.5 ** 0.5

    assert_allclose(out["ad_trans"], transmitted, rtol=1e-5, atol=1e-8)
    assert_allclose(out["ad_refl"], reflected, rtol=1e-5, atol=1e-8)


def test_mirror_reflectivity_forward(forward_model):
    """Test sweeping a mirror's reflectivity from forward direction."""
    forward_model.parse(
        """
        xaxis(m1.R, lin, 0.5, 0, 100)  # Sweep mirror reflectivity from 0.5 to 0 with 100 steps
        """
    )

    out = forward_model.run()
    xaxis = np.linspace(0.5, 0, 101)
    reflected = xaxis ** 0.5
    transmitted = 1j * np.ones(101) * 0.5 ** 0.5

    assert_allclose(out["ad_trans"], transmitted, rtol=1e-5, atol=1e-8)
    assert_allclose(out["ad_refl"], reflected, rtol=1e-5, atol=1e-8)


def test_mirror_reflectivity_reverse(reverse_model):
    """Test sweeping a mirror's reflectivity from reverse direction."""
    reverse_model.parse(
        """
        xaxis(m1.R, lin, 0.5, 0, 100)  # Sweep mirror reflectivity from 0.5 to 0 with 100 steps
        """
    )

    out = reverse_model.run()
    xaxis = np.linspace(0.5, 0, 101)
    reflected = xaxis ** 0.5
    transmitted = 1j * np.ones(101) * 0.5 ** 0.5

    assert_allclose(out["ad_trans"], transmitted, rtol=1e-5, atol=1e-8)
    assert_allclose(out["ad_refl"], reflected, rtol=1e-5, atol=1e-8)


@pytest.mark.xfail()
def test_mirror_loss_forward(forward_model):
    """Test sweeping a mirror's loss from forward direction."""
    # FIXME: This test will fail until
    forward_model.parse(
        """
        xaxis(m1.L, lin, 0, 1, 100)  # Sweep mirror loss from 0 to 1 with 100 steps
        """
    )

    out = forward_model.run()
    xaxis = np.linspace(0, 1, 101)
    reflected = (0.5 * (1 - xaxis)) ** 0.5
    transmitted = 1j * reflected

    assert_allclose(out["ad_trans"], transmitted, rtol=1e-5, atol=1e-8)
    assert_allclose(out["ad_refl"], reflected, rtol=1e-5, atol=1e-8)


@pytest.mark.xfail()
def test_mirror_loss_reverse(reverse_model):
    """Test sweeping a mirror's loss from reverse direction."""
    # FIXME: This test will fail until
    reverse_model.parse(
        """
        xaxis(m1.L, lin, 0, 1, 100)  # Sweep mirror loss from 0 to 1 with 100 steps
        """
    )

    out = reverse_model.run()
    xaxis = np.linspace(0, 1, 101)
    reflected = (0.5 * (1 - xaxis)) ** 0.5
    transmitted = 1j * reflected

    assert_allclose(out["ad_trans"], transmitted, rtol=1e-5, atol=1e-8)
    assert_allclose(out["ad_refl"], reflected, rtol=1e-5, atol=1e-8)


def test_mirror_tuning_forward(forward_model):
    """Test sweeping a mirror's tuning from forward direction."""
    forward_model.parse(
        """
        xaxis(m1.phi, lin, 0, 180, 100)  # Sweep mirror tuning
        """
    )

    out = forward_model.run()
    reflected = 0.5 ** 0.5 * np.exp(2j * np.radians(np.linspace(0, 180, 101)))
    transmitted = 1j * np.ones(101) * 0.5 ** 0.5

    assert_allclose(out["ad_trans"], transmitted, rtol=1e-5, atol=1e-8)
    assert_allclose(out["ad_refl"], reflected, rtol=1e-5, atol=1e-8)


def test_mirror_tuning_reverse(reverse_model):
    """Test sweeping a mirror's tuning from reverse direction."""
    reverse_model.parse(
        """
        xaxis(m1.phi, lin, 0, 180, 100)  # Sweep mirror tuning
        """
    )

    out = reverse_model.run()
    reflected = 0.5 ** 0.5 * np.exp(2j * np.radians(np.linspace(0, 180, 101)))
    transmitted = 1j * np.ones(101) * 0.5 ** 0.5

    assert_allclose(out["ad_trans"], transmitted, rtol=1e-5, atol=1e-8)
    assert_allclose(out["ad_refl"], reflected.conj(), rtol=1e-5, atol=1e-8)


@pytest.fixture
def signal_refl_mech_z_model():
    import finesse

    IFO = finesse.Model()
    IFO.parse(
        """
        fsig(100)

        l l1 P=1
        s s1 l1.p1 m1.p1 L=0
        m m1 R=0.9 T=0.1 phi=100

        ad carrier m1.p1.o 0
        ad upper m1.p1.o &fsig.f
        ad lower m1.p1.o -&fsig.f

        sgen sig m1.mech.z
        """
    )

    return IFO


def test_signal_refl_mech_z_model_sympy(signal_refl_mech_z_model):
    import sympy as sy

    IFO = signal_refl_mech_z_model
    out = IFO.run()
    r, m, k, t, z, Omega, Omega0, phi = sy.var("r m k t z Omega Omega_0 phi", real=True)
    E0 = sy.var("E_0", real=False)
    # extra minus sign here because we are
    # exp(-ikz) usual space propagator and
    # mirror normal motion for z is in the negative direction from port 1 side
    # so overall no minus sign here
    # phi propgation up to mirror suface, then AC term 2kz reflection
    Er = r * E0 * sy.exp(2j * k * z + 1j * phi)
    Er2 = Er.subs(z, z + m * sy.cos(Omega * t))
    Er3 = Er2.series(m, n=2).rewrite(sy.exp).removeO().expand()
    # Extract upper and lower signal side band terms
    a = sy.Wild("a")
    b = sy.Wild("b")
    expr = Er3
    fields = {0: 0, 1: 0, -1: 0}

    for _ in expr.expand().args:
        match = _.match(a * sy.exp(b * 1j * Omega * t))

        if match is None:
            fields[0] += _ * sy.exp(1j * phi)  # phi propagation away from mirror
        else:
            fields[int(match[b])] += match[a] * sy.exp(
                1j * phi * (1 + match[b] * Omega / Omega0)
            )  # plus phi propagation away from mirror

    f0 = 299792458 / IFO.lambda0
    values = {
        r: sy.sqrt(IFO.m1.R),
        E0: sy.sqrt(IFO.l1.P),
        k: 2 * sy.pi / IFO.lambda0,
        m: 1,  # signal amplitude
        phi: np.deg2rad(IFO.m1.phi.value),  # signal phase
        z: 0,
        Omega0: 2 * sy.pi * f0,
        Omega: 2 * sy.pi * (IFO.fsig.f),
    }
    carrier = complex(fields[0].subs(values))
    upper = complex(fields[1].subs(values))
    lower = complex(fields[-1].subs(values))

    assert abs(carrier - out["carrier"]) / abs(carrier) < 1e-15
    assert abs(upper - out["upper"]) / abs(upper) < 1e-15
    assert abs(lower - out["lower"]) / abs(lower) < 1e-15
