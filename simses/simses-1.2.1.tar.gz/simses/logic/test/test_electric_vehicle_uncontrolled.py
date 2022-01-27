import os
from configparser import ConfigParser
from datetime import datetime, timezone

import pytest

from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.profile import ProfileConfig
from simses.commons.config.simulation.energy_management import EnergyManagementConfig
from simses.commons.profile.power.file import FilePowerProfile
from simses.commons.profile.technical.binary import BinaryProfile
from simses.commons.state.system import SystemState
from simses.commons.utils.utilities import remove_file
from simses.logic.energy_management.strategy.basic.electric_vehicle import \
    ElectricVehicle
from pathlib import Path

DELIMITER: str = ','
HEADER: str = '# Unit: W'
system_state: SystemState = SystemState(0,0)
START: int = 0
END: int = 4
STEP: int = 1
FILE_NAME_LOAD: str = 'mockup_power_load_profile.csv'
FILE_NAME_BINARY: str = 'mockup_power_home_profile.csv'


def create_load_file():
    name = os.path.join(Path(os.path.dirname(__file__)).parent.parent, 'data\profile\\power\\' + FILE_NAME_LOAD)

    with open(name, mode='w') as file:
        file.write(HEADER + '\n')
        for counter in range(END+1):
            file.write(str(counter) + DELIMITER + str(POWER_VALUES[counter]) + '\n')

    power_load_profile = FilePowerProfile(config=create_general_config(), filename=name,
                                          delimiter=DELIMITER, scaling_factor=1)
    return power_load_profile

def create_binary_file():
    name = os.path.join(Path(os.path.dirname(__file__)).parent.parent, 'data\profile\\technical\\' + FILE_NAME_BINARY)

    with open(name, mode='w') as file:
        file.write(HEADER + '\n')
        for counter in range(END + 1):
            file.write(str(counter) + DELIMITER + str(BINARY_VALUES[counter]) + '\n')

    binary_profile = BinaryProfile(config=create_general_config(), profile_config=create_profile_config())
    return binary_profile

def create_general_config():
    conf: ConfigParser = ConfigParser()
    conf.add_section('GENERAL')
    date = datetime.fromtimestamp(START, timezone.utc)
    conf.set('GENERAL', 'START', date.strftime("%Y-%m-%d %H:%M:%S"))
    date = datetime.fromtimestamp(END, timezone.utc)
    conf.set('GENERAL', 'END', date.strftime("%Y-%m-%d %H:%M:%S"))
    conf.set('GENERAL', 'TIME_STEP', str(STEP))
    return GeneralSimulationConfig(config=conf)

def create_profile_config():
    conf: ConfigParser = ConfigParser()
    conf.add_section('PROFILE')
    conf.set('PROFILE', 'LOAD_PROFILE', FILE_NAME_LOAD)
    conf.set('PROFILE', 'BINARY_PROFILE', FILE_NAME_BINARY)
    return ProfileConfig(config=conf)

def create_ems_config():
    conf: ConfigParser = ConfigParser()
    conf.add_section('ENERGY_MANAGEMENT')
    conf.set('ENERGY_MANAGEMENT', 'STRATEGY', 'ElectricVehicle')
    conf.set('ENERGY_MANAGEMENT', 'EV_CHARGING_STRATEGY', EV_CHARGING_STRATEGY)
    conf.set('ENERGY_MANAGEMENT', 'Max_Power', str(MAX_AC_POWER))
    return EnergyManagementConfig(config=conf)

@pytest.fixture(scope='module')
def uut():
    power_load_profile = create_load_file()
    binary_profile = create_binary_file()
    ems_config = create_ems_config()
    uut = ElectricVehicle(power_load_profile, binary_profile, ems_config)

    yield uut
    uut.close()

    remove_file(power_load_profile._FilePowerProfile__file._FileProfile__filename)
    remove_file(binary_profile._BinaryProfile__file._FileProfile__filename)


POWER_VALUES: list = [5, 6, 7, 8, 9]
BINARY_VALUES: list = [2, 0, 1, 1, 1]
MAX_AC_POWER: int = 17
EV_CHARGING_STRATEGY: str = 'Uncontrolled'

@pytest.mark.parametrize('time, soc, result',
                         [
                            (0, 0, 'ValueError'),       # 1: Binary Profil different value than 0 or 1
                            (1, 0, -6),                 # 2: EV on road => use 5W
                            (2, 1, 0),                  # 3: EV parked but SOC=100% => 0W
                            (3, 0, 17),                 # 4: EV parked and SOC<100% => 7W says power, but charged with 17W
                            (4, 0, 17)                  # 5:
                         ]
                         )
def test_next(time, soc, result, uut):

    system_state.soc = soc
    if time==0:
        with pytest.raises(ValueError):
            uut.next(time, system_state)
    else:
        assert abs(uut.next(time, system_state) - result) <= 1e-10