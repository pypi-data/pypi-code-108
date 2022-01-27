import os
from configparser import ConfigParser
from datetime import datetime, timezone

import pytest
import time

from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.profile import ProfileConfig
from simses.commons.config.simulation.energy_management import EnergyManagementConfig
from simses.commons.profile.technical.soc import SocProfile
from simses.commons.profile.technical.binary import BinaryProfile
from simses.commons.state.system import SystemState
from simses.commons.utils.utilities import remove_file
from simses.logic.energy_management.strategy.basic.electric_vehicle_soc import \
    ElectricVehicleSOC
from pathlib import Path

DELIMITER: str = ','
HEADER: str = '# Unit: W'
system_state: SystemState = SystemState(0,0)
START: int = 0
STEP: int = 1
FILE_NAME_SOC: str = 'mockup_power_soc_profile.csv'
FILE_NAME_BINARY: str = 'mockup_power_home_profile.csv'
PATH_NAME_BINARY = os.path.join(Path(os.path.dirname(__file__)).parent.parent, 'data\profile\\technical\\' + FILE_NAME_BINARY)

def create_soc_file():
    name = os.path.join(Path(os.path.dirname(__file__)).parent.parent, 'data\profile\\technical\\' + FILE_NAME_SOC)

    with open(name, mode='w') as file:
        file.write(HEADER + '\n')
        for counter in range(END):
            file.write(str(counter) + DELIMITER + str(SOC_VALUES[counter]) + '\n')

    power_load_profile = SocProfile(config=create_general_config(), profile_config=create_profile_config())
    return power_load_profile

def create_binary_file():
    name = os.path.join(Path(os.path.dirname(__file__)).parent.parent, 'data\profile\\technical\\' + FILE_NAME_BINARY)

    with open(name, mode='w') as file:
        file.write(HEADER + '\n')
        for counter in range(END):
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
    conf.set('PROFILE', 'SOC_PROFILE', FILE_NAME_SOC)
    conf.set('PROFILE', 'BINARY_PROFILE', FILE_NAME_BINARY)
    return ProfileConfig(config=conf)

def create_ems_config():
    conf: ConfigParser = ConfigParser()
    conf.add_section('ENERGY_MANAGEMENT')
    conf.set('ENERGY_MANAGEMENT', 'STRATEGY', 'ElectricVehicleSOC')
    conf.set('ENERGY_MANAGEMENT', 'EV_CHARGING_STRATEGY', EV_CHARGING_STRATEGY)
    conf.set('ENERGY_MANAGEMENT', 'Max_Power', str(MAX_AC_POWER))
    return EnergyManagementConfig(config=conf)

@pytest.fixture(scope='module')
def uut():
    soc_profile = create_soc_file()
    binary_profile = create_binary_file()
    ems_config = create_ems_config()
    general_config = create_general_config()
    profile_config = create_profile_config()
    uut = ElectricVehicleSOC(general_config, profile_config, ems_config)

    yield uut
    soc_profile.close()
    binary_profile.close()
    uut.close()

    remove_file(soc_profile._SocProfile__file._FileProfile__filename)
    remove_file(binary_profile._BinaryProfile__file._FileProfile__filename)


SOC_VALUES: list = [1, 0.4, 0.5, 0.8, 0.8, 0.9, 0.9]
BINARY_VALUES: list = [2, 0, 1, 1, 1, 1, 0]
MAX_AC_POWER: int = 17
END: int = len(BINARY_VALUES)
EV_CHARGING_STRATEGY: str = 'Mean_power'

@pytest.mark.parametrize('time, soc_state, capacity, result',
                         [
                            (0, 0.5, 10, 'ValueError'),     # 1: Binary Profil different value than 0 or 1
                            (1, 0.5, 10, -3600),            # 2: EV on road, capacity=10, SOC_state=0.5, SOC_new=0.4 => Diff=0.1; =>-3600Ws => -3600W
                            (2, 1, 10, 0),                  # 3: EV parked but SOC=100% => 0W
                            (3, 0.8, 10, 2400),             # 4: EV parked and SOC=80% => next departure: 3s
                                                            #    => Delta_SOC=20%, capacity 10Wh => 7200Ws in 3s => 2400 W
                             (4, 0.8, 10, 3600)             # 5: Same as 4 but only 2s left to charge
                         ]
                         )
def test_next(time, soc_state, capacity, result, uut):

    system_state.soc = soc_state
    system_state.capacity = capacity
    if time==0:
        with pytest.raises(ValueError):
            uut.next(time, system_state)
    else:
        assert abs(uut.next(time, system_state) - result) <= 1e-10