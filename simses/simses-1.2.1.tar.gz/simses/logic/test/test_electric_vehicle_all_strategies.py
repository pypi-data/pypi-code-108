# import os
# from configparser import ConfigParser
# from datetime import datetime, timezone
#
# import pytest
#
# from simses.commons.config.simulation.general import GeneralSimulationConfig
# from simses.commons.config.simulation.profile import ProfileConfig
# from simses.commons.config.simulation.energy_management import EnergyManagementConfig
# from simses.commons.profile.power.file import FilePowerProfile
# from simses.commons.profile.technical.binary import BinaryProfile
# from simses.commons.state.system import SystemState
# from simses.commons.utils.utilities import remove_file
# from simses.logic.energy_management.strategy.basic.electric_vehicle import \
#     ElectricVehicle
# from pathlib import Path
#
# DELIMITER: str = ','
# HEADER: str = '# Unit: W'
# system_state: SystemState = SystemState(0, 0)
# START: int = 0
# STEP: int = 1
# FILE_NAME_LOAD: str = 'mockup_power_load_profile.csv'
# FILE_NAME_BINARY: str = 'mockup_power_home_profile.csv'
# FILE_PATH_LOAD = os.path.join(Path(os.path.dirname(__file__)).parent.parent, 'data\profile\\power\\' + FILE_NAME_LOAD)
# FILE_PATH_BINARY = os.path.join(Path(os.path.dirname(__file__)).parent.parent, 'data\profile\\technical\\' + FILE_NAME_BINARY)
#
#
# def create_load_file():
#     with open(FILE_PATH_LOAD, mode='w') as file:
#         file.write(HEADER + '\n')
#         for counter in range(END):
#             file.write(str(counter) + DELIMITER + str(POWER_VALUES[counter]) + '\n')
#
#     power_load_profile = FilePowerProfile(config=create_general_config(), filename=FILE_PATH_LOAD,
#                                           delimiter=DELIMITER, scaling_factor=1)
#     return power_load_profile
#
#
# def create_binary_file():
#     with open(FILE_PATH_BINARY, mode='w') as file:
#         file.write(HEADER + '\n')
#         for counter in range(END):
#             file.write(str(counter) + DELIMITER + str(BINARY_VALUES[counter]) + '\n')
#
#     binary_profile = BinaryProfile(config=create_general_config(), profile_config=create_profile_config())
#     return binary_profile
#
#
# def create_general_config():
#     conf: ConfigParser = ConfigParser()
#     conf.add_section('GENERAL')
#     date = datetime.fromtimestamp(START, timezone.utc)
#     conf.set('GENERAL', 'START', date.strftime("%Y-%m-%d %H:%M:%S"))
#     date = datetime.fromtimestamp(END, timezone.utc)
#     conf.set('GENERAL', 'END', date.strftime("%Y-%m-%d %H:%M:%S"))
#     conf.set('GENERAL', 'TIME_STEP', str(STEP))
#     return GeneralSimulationConfig(config=conf)
#
#
# def create_profile_config():
#     conf: ConfigParser = ConfigParser()
#     conf.add_section('PROFILE')
#     conf.set('PROFILE', 'LOAD_PROFILE', FILE_NAME_LOAD)
#     conf.set('PROFILE', 'BINARY_PROFILE', FILE_NAME_BINARY)
#     return ProfileConfig(config=conf)
#
#
# def create_ems_config(ev_charging_strategy):
#     conf: ConfigParser = ConfigParser()
#     conf.add_section('ENERGY_MANAGEMENT')
#     conf.set('ENERGY_MANAGEMENT', 'STRATEGY', 'ElectricVehicle')
#     conf.set('ENERGY_MANAGEMENT', 'EV_CHARGING_STRATEGY', ev_charging_strategy)
#     conf.set('ENERGY_MANAGEMENT', 'Max_Power', str(MAX_AC_POWER))
#     return EnergyManagementConfig(config=conf)
#
#
# @pytest.fixture(scope='module')
# def uut0():
#     power_load_profile = create_load_file()
#     binary_profile = create_binary_file()
#     ems_config = create_ems_config(EV_CHARGING_STRATEGY[0])
#     uut0 = ElectricVehicle(power_load_profile, binary_profile, ems_config)
#
#     yield uut0
#
#
# @pytest.fixture(scope='module')
# def uut1():
#     power_load_profile = create_load_file()
#     binary_profile = create_binary_file()
#     ems_config = create_ems_config(EV_CHARGING_STRATEGY[1])
#     uut1 = ElectricVehicle(power_load_profile, binary_profile, ems_config)
#
#     yield uut1
#
#
# POWER_VALUES: list = [5, 6, 7, 8, 9, 10]
# END: int = len(POWER_VALUES)
# BINARY_VALUES: list = [2, 0, 1, 1, 1, 1]
# MAX_AC_POWER: int = 17
# EV_CHARGING_STRATEGY: list = ['Uncontrolled', 'Smart']
#
# @pytest.mark.parametrize('strategy, time, soc, result',
#              [
#                 (EV_CHARGING_STRATEGY[0], 0, 0, 'ValueError'),       # 1: Binary Profil different value than 0 or 1
#                 (EV_CHARGING_STRATEGY[0], 1, 0, -6),                 # 2: EV on road => use 5W
#                 (EV_CHARGING_STRATEGY[0], 2, 1, 0),                  # 3: EV parked but SOC=100% => 0W
#                 (EV_CHARGING_STRATEGY[0], 3, 0, 17),                 # 4: EV parked and SOC<100% => 7W says power, but charged with 17W
#                 (EV_CHARGING_STRATEGY[1], 4, 0, 8.5),                # 5:
#                 (EV_CHARGING_STRATEGY[1], 5, 0, 8.5)                 # 6:
#              ]
#                          )
# def test_next(strategy, time, soc, result, uut0, uut1):
#
#     system_state.soc = soc
#     if strategy == EV_CHARGING_STRATEGY[0]:
#         if time==0:
#             with pytest.raises(ValueError):
#                 uut0.next(time, system_state)
#         else:
#             assert abs(uut0.next(time, system_state) - result) <= 1e-10
#
#     elif strategy == EV_CHARGING_STRATEGY[1]:
#         assert abs(uut1.next(time, system_state) - result) <= 1e-10
#
#     if time== END-1:
#         uut0.close()
#         uut1.close()
#         remove_file(FILE_PATH_BINARY)
#         remove_file(FILE_PATH_LOAD)
#
