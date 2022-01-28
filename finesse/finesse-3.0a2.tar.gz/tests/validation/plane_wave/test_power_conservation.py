import pytest
import finesse
import numpy as np
from numpy.testing import assert_allclose


@pytest.fixture
def model_m():
    kat = finesse.Model()
    kat.parse(
        """
    l l1
    m m1 R=0.5 T=0.5
    s s1 m1.p2 m2.p1
    m m2 R=0 T=1
    l l2

    link(l1, m1)
    link(l2, m2)

    pd P1 l1.p1.i
    pd P2 l2.p1.i
    """
    )
    return kat


@pytest.fixture
def model_bs():
    kat = finesse.Model()
    kat.parse_legacy(
        """
    l i1 1 0 0 nlaser
    s sin 0 nlaser nBS1

    bs BS 0.5 0.5 0 0 nBS1 nBS2 nBS3 nAS
    s sX 0 1 nBS3 nX
    s sY 0 1 nBS2 nY

    m mX 1 0 0 nX dump
    m mY 1 0 0 nY dump

    pd PIN nlaser*
    pd PREFL nlaser
    pd PAS nAS

    xaxis* BS phi lin 0 90 10
    yaxis lin abs:deg

    maxtem off
    """
    )
    return kat


@pytest.mark.parametrize("f", (0, 0.001, 1e15))
@pytest.mark.parametrize("angle", (0, -89, 45))
@pytest.mark.parametrize("nr", (1, 1.45))
@pytest.mark.parametrize("phi", (0, 1, 1130123.3))
@pytest.mark.parametrize("flag", (True, False))
def test_bs_power_conservation(model_bs, f, angle, nr, phi, flag):
    model_bs._settings.phase_config.v2_transmission_phase = flag
    model_bs.i1.f = f
    model_bs.BS.alpha = angle
    model_bs.BS.phi = phi
    model_bs.spaces.sX.nr = nr
    model_bs.spaces.sY.nr = nr
    out = model_bs.run()
    assert_allclose(out["PREFL"] + out["PAS"], out["PIN"], rtol=1e-14, atol=1e-14)


@pytest.mark.parametrize("f", (0, 0.001, 1e15))
@pytest.mark.parametrize("nr", (1, 1.45))
@pytest.mark.parametrize("phi1", (0, 1, 2 * np.pi, -2 * np.pi))
@pytest.mark.parametrize("phi2", (0, 1, 2 * np.pi, -2 * np.pi))
@pytest.mark.parametrize("flag", (True, False))
def test_mirror_power_conservation(model_m, f, nr, phi1, phi2, flag):
    model_m._settings.phase_config.v2_transmission_phase = flag
    model_m.l1.f = f
    model_m.l2.f = f
    model_m.m1.phi = phi1
    model_m.m2.phi = phi2
    model_m.spaces.s1.nr = nr
    out = model_m.run()
    assert_allclose(out["P1"] + out["P2"], 2, rtol=1e-14, atol=1e-14)


@pytest.mark.xfail(reason="numerical precision problems with large phi values")
@pytest.mark.parametrize("f", (0, 0.001, 1e15))
@pytest.mark.parametrize("nr", (1, 1.45))
@pytest.mark.parametrize("phi1", (1130123000.3,))
@pytest.mark.parametrize("phi2", (1130123000.3,))
@pytest.mark.parametrize("flag", (False,))
def test_mirror_power_conservation_large_phi(model_m, f, nr, phi1, phi2, flag):
    model_m._settings.phase_config.v2_transmission_phase = flag
    model_m.l1.f = f
    model_m.l2.f = f
    model_m.m1.phi = phi1
    model_m.m2.phi = phi2
    model_m.spaces.s1.nr = nr
    out = model_m.run()
    assert_allclose(out["P1"] + out["P2"], 2, rtol=1e-14, atol=1e-14)
