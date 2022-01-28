"""Tests for the phase of the light field as propagated over a space."""

import pytest
import numpy as np

from finesse.analysis.actions import Noxaxis, Xaxis
import finesse.constants as constants
from finesse.components import Laser, Space, Mirror
from finesse.detectors import AmplitudeDetector


@pytest.fixture
def laser_and_mirror_with_ad(model):
    """Model with a laser and mirror separated by a space, with amplitude detector."""
    model.chain(Laser("L0"), Space("s0"), Mirror("M", R=1, T=0))
    model.add(AmplitudeDetector("ad_lsr", model.L0.p1.o, model.L0.f.ref))
    model.add(AmplitudeDetector("ad_in", model.M.p1.i, model.L0.f.ref))
    model.add(AmplitudeDetector("ad_refl", model.M.p1.o, model.L0.f.ref))
    model.add(AmplitudeDetector("ad_back", model.L0.p1.i, model.L0.f.ref))
    return model


@pytest.mark.parametrize("L", (0, 1, 3.141, 1000, 3141))
def test_propagation__carrier(laser_and_mirror_with_ad, L):
    """Test carrier amplitude doesn't change with 0-length propagation."""
    laser_and_mirror_with_ad.spaces.s0.L = L
    out = laser_and_mirror_with_ad.run(Noxaxis())
    assert out["ad_lsr"] == out["ad_in"]
    assert out["ad_lsr"] == out["ad_refl"]
    assert out["ad_lsr"] == out["ad_back"]


@pytest.mark.parametrize("L", (0, 1, 3.141, 1000, 3141))
def test_propagation__frequency_offset(laser_and_mirror_with_ad, L):
    """Test frequency offset amplitudes don't change with 0-length propagation."""
    laser_and_mirror_with_ad.spaces.s0.L = L

    freqs = np.linspace(-1e3, 1e3, 100)

    out = laser_and_mirror_with_ad.run(Xaxis(
        "L0.f", "lin", freqs[0], freqs[-1], freqs.size - 1
    ))

    # Assert that field at L0.p1.o doesn't change.
    assert np.allclose(
        np.diff(out["ad_lsr"]), np.zeros(freqs.size - 1, dtype=np.complex128)
    )

    s0_L = laser_and_mirror_with_ad.elements["s0"].L.value
    s0_n = laser_and_mirror_with_ad.elements["s0"].nr.value

    # Test that the field propagation across the space (towards mirror M) is equal to expected
    # analytic result.
    prop = np.exp(-1j * 2 * np.pi * freqs * s0_L * s0_n / constants.C_LIGHT)
    assert np.allclose(out["ad_in"], prop)

    # And test that the field propagation across the space in the other direction (back towards
    # laser L0) is equal to just another factor of the propagation term from above.
    assert np.allclose(out["ad_back"], prop ** 2)
