import pytest

from simses.commons.profile.power.constant import ConstantPowerProfile


@pytest.fixture()
def uut(power, scaling_factor):
    return ConstantPowerProfile(power=power, scaling_factor=scaling_factor)


@pytest.mark.parametrize('power, scaling_factor, result',
                         [
                             (0, 0, 0),
                             (1, 0, 0),
                             (0, 1, 0),
                             (1, 1, 1),
                             (5, 3, 15)
                         ]
                         )
def test_next(result, uut):
    tstmp = 0
    while tstmp < 5:
        assert uut.next(tstmp) == result
        tstmp += 1
