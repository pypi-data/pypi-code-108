import os
from configparser import ConfigParser
from datetime import datetime, timezone

import pytest

from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.profile.power.file import FilePowerProfile
from simses.commons.state.system import SystemState
from simses.commons.utils.utilities import remove_file
from simses.logic.energy_management.strategy.basic.residential_pv_greedy import \
    ResidentialPvGreedy

DELIMITER: str = ','
HEADER: str = '# Unit: W'
system_state: SystemState = SystemState(0,0)
START: int = 0
END: int = 4
STEP: int = 1
FILE_NAME_LOAD: str = os.path.join(os.path.dirname(__file__), 'mockup_power_load_profile.csv')
FILE_NAME_PV: str = os.path.join(os.path.dirname(__file__), 'mockup_power_pv_profile.csv')


def create_load_file():
    with open(FILE_NAME_LOAD, mode='w') as file:
        file.write(HEADER + '\n')
        value = START
        tstmp = START
        while tstmp <= END:
            file.write(str(tstmp) + DELIMITER + str(value) + '\n')
            tstmp += STEP
            value += 1

    power_load_profile = FilePowerProfile(config=create_general_config(), filename=FILE_NAME_LOAD,
                                          delimiter=DELIMITER, scaling_factor=1)
    return power_load_profile

def create_pv_file():
    with open(FILE_NAME_PV, mode='w') as file:
        file.write(HEADER + '\n')
        value = END
        tstmp = START
        while tstmp <= END:
            file.write(str(tstmp) + DELIMITER + str(value) + '\n')
            tstmp += STEP
            value -= 1

    power_pv_profile = FilePowerProfile(config=create_general_config(), filename=FILE_NAME_PV,
                                          delimiter=DELIMITER, scaling_factor=1)
    return power_pv_profile

def create_general_config():
    conf: ConfigParser = ConfigParser()
    conf.add_section('GENERAL')
    date = datetime.fromtimestamp(START, timezone.utc)
    conf.set('GENERAL', 'START', date.strftime("%Y-%m-%d %H:%M:%S"))
    date = datetime.fromtimestamp(END, timezone.utc)
    conf.set('GENERAL', 'END', date.strftime("%Y-%m-%d %H:%M:%S"))
    conf.set('GENERAL', 'TIME_STEP', str(STEP))
    return GeneralSimulationConfig(config=conf)

@pytest.fixture(scope='module')
def uut():
    power_load_profile = create_load_file()
    power_pv_profile = create_pv_file()
    uut = ResidentialPvGreedy(power_load_profile, power_pv_profile)
    yield uut
    uut.close()
    remove_file(FILE_NAME_LOAD)
    remove_file(FILE_NAME_PV)

# time = power
@pytest.mark.parametrize('time, soc, result',
                         [
                            (0, 0, 4),
                            (1, 0, 2),
                            (2, 0, 0),
                            (3, 0, -2),
                            (4, 0, -4)
                         ]
                         )
def test_next(time, soc, result, uut):
    system_state.soc = soc
    assert abs(uut.next(time, system_state) - result) <= 1e-10