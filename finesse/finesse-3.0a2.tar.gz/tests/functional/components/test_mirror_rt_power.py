"""Test cases for reflected and transmitted power from a single mirror."""

import math
import pytest
from finesse.analysis.actions import Noxaxis
from finesse.components import Laser, Space, Mirror
import finesse.detectors as detectors


@pytest.fixture
def laser_and_mirror(model):
    """Model with a laser and mirror separated by a space."""
    model.chain(Laser("L0"), Space("s0"), Mirror("M", R=0.5, T=0.5))
    model.add(detectors.PowerDetector("refl", model.M.p1.o))
    model.add(detectors.PowerDetector("trns", model.M.p2.o))
    return model


def test_fully_reflective(laser_and_mirror):
    """Test fully reflective mirror power."""
    laser_and_mirror.M.set_RTL(R=1, T=0)
    assert float(laser_and_mirror.M.T) == 0

    out = laser_and_mirror.run(Noxaxis())
    assert math.isclose(out["refl"], float(laser_and_mirror.L0.P))
    assert out["trns"] == 0


def test_fully_transmissive(laser_and_mirror):
    """Test fully transmissive mirror power."""
    laser_and_mirror.M.set_RTL(T=1, R=0)
    assert float(laser_and_mirror.M.R) == 0

    out = laser_and_mirror.run(Noxaxis())

    assert math.isclose(out["trns"], float(laser_and_mirror.L0.P))
    assert out["refl"] == 0


def test_half_reflective(laser_and_mirror):
    """Test half reflective mirror power."""
    laser_and_mirror.M.set_RTL(0.5, 0.5)

    assert math.isclose(float(laser_and_mirror.M.T), 0.5)

    out = laser_and_mirror.run(Noxaxis())

    assert math.isclose(out["refl"], 0.5 * float(laser_and_mirror.L0.P))
    assert math.isclose(out["trns"], 0.5 * float(laser_and_mirror.L0.P))
