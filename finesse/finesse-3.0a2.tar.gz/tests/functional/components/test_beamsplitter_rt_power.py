"""Test cases for reflected and transmitted power from a single beam splitter."""

import math
import pytest
from finesse.analysis.actions import Noxaxis
from finesse.components import Laser, Space, Beamsplitter
from finesse.detectors import PowerDetector


@pytest.fixture
def laser_and_beamsplitter(model):
    """Model with a laser and beamsplitter separated by a space."""
    model.chain(
        Laser("L0"), Space("s0"), Beamsplitter("BS", R=0.5, T=0.5),
    )
    model.add(PowerDetector("refl", model.BS.p2.o))
    model.add(PowerDetector("trns", model.BS.p3.o))
    return model


def test_fully_reflective(laser_and_beamsplitter):
    """Test fully reflective beamsplitter power."""
    laser_and_beamsplitter.BS.set_RTL(R=1, T=0)

    assert float(laser_and_beamsplitter.BS.T) == 0

    out = laser_and_beamsplitter.run(Noxaxis())

    assert math.isclose(out["refl"], float(laser_and_beamsplitter.L0.P))
    assert out["trns"] == 0


def test_fully_transmissive(laser_and_beamsplitter):
    """Test fully transmissive beamsplitter power."""
    laser_and_beamsplitter.BS.set_RTL(T=1, R=0)

    assert float(laser_and_beamsplitter.BS.R) == 0

    out = laser_and_beamsplitter.run(Noxaxis())

    assert math.isclose(out["trns"], float(laser_and_beamsplitter.L0.P))
    assert out["refl"] == 0


def test_half_reflective(laser_and_beamsplitter):
    """Test half reflective beamsplitter power."""
    laser_and_beamsplitter.BS.set_RTL(T=0.5, R=0.5)

    assert math.isclose(float(laser_and_beamsplitter.BS.T), 0.5)

    out = laser_and_beamsplitter.run(Noxaxis())

    assert math.isclose(out["refl"], 0.5 * float(laser_and_beamsplitter.L0.P))
    assert math.isclose(out["trns"], 0.5 * float(laser_and_beamsplitter.L0.P))
