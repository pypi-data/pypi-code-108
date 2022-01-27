import pytest

from simses.system.auxiliary.pump.fixeta_centrifugal import FixEtaCentrifugalPump


@pytest.fixture(scope='function')
def uut(eta_pump):
    return FixEtaCentrifugalPump(eta_pump)


@pytest.mark.parametrize('eta_pump, pressure_loss, result', [(0.5, 100, 200)])
def test_get_pump(uut, pressure_loss, result):
    uut.calculate_pump_power(pressure_loss)
    assert uut.get_pump_power() == result
