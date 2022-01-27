import os
from configparser import ConfigParser
from datetime import datetime, timezone

import pytest

from simses.commons.config.simulation.energy_management import EnergyManagementConfig
from simses.commons.profile.power.file import FilePowerProfile
from simses.commons.state.system import SystemState
from simses.commons.utils.utilities import remove_file
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.logic.energy_management.strategy.basic.peak_shaving_simple import \
    SimplePeakShaving

DELIMITER: str = ','
HEADER: str = '# Unit: W'
system_state: SystemState = SystemState(0,0)
START: int = 0
END: int = 5
STEP: int = 1
MAX_POWER: int = 3
FILE_NAME: str = os.path.join(os.path.dirname(__file__), 'mockup_power_profile.csv')


def create_file():
    with open(FILE_NAME, mode='w') as file:
        file.write(HEADER + '\n')
        value = START
        tstmp = START
        while tstmp <= END:
            file.write(str(tstmp) + DELIMITER + str(value) + '\n')
            tstmp += STEP
            value += 1

    power_profile = FilePowerProfile(config=create_general_config(), filename=FILE_NAME,
                                          delimiter=DELIMITER, scaling_factor=1)
    return power_profile

def create_general_config():
    conf: ConfigParser = ConfigParser()
    conf.add_section('GENERAL')
    date = datetime.fromtimestamp(START, timezone.utc)
    conf.set('GENERAL', 'START', date.strftime("%Y-%m-%d %H:%M:%S"))
    date = datetime.fromtimestamp(END, timezone.utc)
    conf.set('GENERAL', 'END', date.strftime("%Y-%m-%d %H:%M:%S"))
    conf.set('GENERAL', 'TIME_STEP', str(STEP))
    return GeneralSimulationConfig(config=conf)

def create_ems_config():
    conf: ConfigParser = ConfigParser()
    conf.add_section('ENERGY_MANAGEMENT')
    conf.set('ENERGY_MANAGEMENT', 'MAX_POWER', str(MAX_POWER))
    return EnergyManagementConfig(config=conf)


@pytest.fixture(scope='module')
def uut():
    power_profile = create_file()
    uut = SimplePeakShaving(power_profile=power_profile, ems_config=create_ems_config())
    yield uut
    uut.close()
    remove_file(FILE_NAME)

# time = power
@pytest.mark.parametrize('time, soc, power_offset, result',
                         [
                            (0, 0, 0, 3),
                            (0, 1, 0, 0),
                            (1, 0, 0, 2),
                            (1, 0, 1, 1),
                            (2, 0, 0, 1),
                            (2, 1, 0, 0),
                            (3, 0, 0, 0),
                            (3, 1, 0, 0),
                            (3, 0, 1, -1),
                            (3, 1, -1, 0),
                            (4, 0, 0, -1),
                            (4, 1, 0, -1),
                            (5, 0, 0, -2),
                            (5, 0, 2, -4)
                         ]
                         )
def test_next(time, soc, power_offset, result, uut):
    power_offset = power_offset
    system_state.soc = soc
    assert abs(uut.next(time, system_state, power_offset) - result) <= 1e-10