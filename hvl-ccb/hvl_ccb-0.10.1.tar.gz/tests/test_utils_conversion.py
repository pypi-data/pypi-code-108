#  Copyright (c) 2021-2022 ETH Zurich, SIS ID and HVL D-ITET
#
"""
Tests for Unit Conversion Utils
"""

import pytest
import numpy as np
from typing import NamedTuple
from collections import namedtuple

from hvl_ccb.utils.conversion_unit import (
    Temperature,
    Pressure,
)


class TestTempNamedTuple(NamedTuple):
    field_a: float = 273.15
    field_b: float = 293.15
    field_c: float = 313.15


TestTempNamedTuple2 = namedtuple(
    "TestTempNamedTuple2", ["field_a", "field_b", "field_c"]
)


def test_temperature():
    assert Temperature.convert(293.15) == 20.
    assert Temperature.convert(273.15) == 0.
    assert round(Temperature.convert(293), 2) == 19.85
    assert Temperature.convert(
        300, source=Temperature.CELSIUS, target=Temperature.FAHRENHEIT
    ) == 572
    assert Temperature.convert(
        572, source=Temperature.FAHRENHEIT, target=Temperature.CELSIUS
    ) == 300
    assert Temperature.convert(
        302., source=Temperature.FAHRENHEIT, target=Temperature.KELVIN
    ) == 423.15
    assert Temperature.convert(
        423.15, source=Temperature.KELVIN, target=Temperature.FAHRENHEIT
    ) == 302.
    assert Temperature.convert(
        125., source=Temperature.CELSIUS, target=Temperature.KELVIN
    ) == 398.15
    assert Temperature.convert([273.15, 293.15, 313.15]) == [0, 20, 40]
    assert Temperature.convert((273.15, 293.15, 313.15)) == (0, 20, 40)
    with pytest.raises(TypeError):
        Temperature.convert([273.15, '293.15', 313.15])
    assert Temperature.convert(
        {'temp1': 273.15, 'temp2': 293.15}) == {'temp1': 0, 'temp2': 20}
    assert np.all(
        Temperature.convert(np.array([273.15, 293.15, 313.15])) == np.array([0, 20, 40])
    )
    assert Temperature.convert(
        20, source=Temperature.KELVIN, target=Temperature.KELVIN
    ) == 20
    assert Temperature.convert(TestTempNamedTuple()) == TestTempNamedTuple(0, 20, 40)
    assert Temperature.convert(
        TestTempNamedTuple2(273.15, 293.15, 313.15)) == TestTempNamedTuple2(0, 20, 40)
    with pytest.raises(TypeError):
        Temperature.convert(
            '20.', source=Temperature.KELVIN, target=Temperature.KELVIN
        )
    with pytest.raises(ValueError):
        Temperature.convert(
            20., source='k', target=Temperature.CELSIUS
        )
    with pytest.raises(TypeError):
        Temperature.convert(
            [20, 'a'], source='k', target=Temperature.CELSIUS
        )


def test_pressure():
    assert Pressure.convert(1., source=Pressure.BAR, target=Pressure.PASCAL) == 1e5
    assert round(Pressure.convert(
        1., source=Pressure.MMHG, target=Pressure.PASCAL
    ), 3) == 133.322
    assert Pressure.convert(
        1., source=Pressure.ATMOSPHERE, target=Pressure.PASCAL) == 101325
    assert round(Pressure.convert(
        1., source=Pressure.PSI, target=Pressure.PASCAL
    ), 2) == 6894.76
    assert round(Pressure.convert(
        1., source=Pressure.TORR, target=Pressure.PASCAL
    ), 2) == 133.32
    assert Pressure.convert(
        100_000., source=Pressure.PASCAL, target=Pressure.BAR
    ) == 1.
    assert round(Pressure.convert(
        100_000., source=Pressure.PASCAL, target=Pressure.MMHG
    ), 5) == 750.06158
    assert round(Pressure.convert(
        100_000., source=Pressure.PASCAL, target=Pressure.ATMOSPHERE
    ), 8) == 0.98692327
    assert round(Pressure.convert(
        100_000., source=Pressure.PASCAL, target=Pressure.PSI
    ), 5) == 14.50377
    assert round(Pressure.convert(
        100_000., source=Pressure.PASCAL, target=Pressure.TORR
    ), 5) == 750.06168
    assert Pressure.convert(
        100_000., source=Pressure.PASCAL, target=Pressure.PASCAL) == 100_000.
    with pytest.raises(ValueError):
        Pressure.convert(1., source='Bar', target=Pressure.MMHG)
