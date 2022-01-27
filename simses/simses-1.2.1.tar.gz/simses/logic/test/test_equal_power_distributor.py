import pytest

from simses.commons.state.system import SystemState
from simses.logic.power_distribution.equal import EqualPowerDistributor


@pytest.fixture()
def uut():
    return EqualPowerDistributor()


def create_state(soc: float) -> SystemState:
    state: SystemState = SystemState(0, 0)
    state.soc = soc
    return state


@pytest.mark.parametrize('power, soc_low, soc_high',
                         [
                             (0, 0, 0),
                             (0, 0, 1),
                             (0, 1, 1),
                             (10, 0, 0),
                             (10, 0.3, 0.7),
                             (10, 0, 1),
                             (10, 1, 1),
                             (10, 3, 5)
                         ]
                         )
def test_power(soc_high, soc_low, uut: EqualPowerDistributor, power):
    state_high = create_state(soc_high)
    state_low = create_state(soc_low)
    states: list = list()
    states.append(state_high)
    states.append(state_low)
    uut.set(0.0, states, 0)
    assert uut.get_power_for(power, state_low) == uut.get_power_for(power, state_high)
