from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.profile import ProfileConfig
from simses.commons.profile.technical.soc import SocProfile
from simses.commons.state.energy_management import EnergyManagementState
from simses.commons.state.system import SystemState
from simses.logic.energy_management.strategy.operation_priority import OperationPriority
from simses.logic.energy_management.strategy.operation_strategy import OperationStrategy
from simses.commons.profile.technical.binary import BinaryProfile
from simses.commons.config.simulation.energy_management import EnergyManagementConfig
import numpy as np

class ElectricVehicleSOC(OperationStrategy):

    """
    ElectricVehicleSOC is a basic operation strategy which simulates an EV during trips and recharge. The algorithm
    requires the following profiles and parameters:
    - An SOC profile that contains the SOC of the vehicle. The charging of the vehicle can be changed but also the
    original charging SOC-change can be used
    - A binary profile that contains ones when the EV is parked at home and zeros if not
    - A string for the parameter 'EV_CHARGING_STRATEGY' which can be:
        - "Original": Uses the original SOC-values for the charging
        - "Uncontrolled": Always recharge, if SOC<100% and parked at "home"
        - "Mean_Power": This strategy checks the next departure time (perfect foresight) and chooses the charging power
            to reach 100% SOC exactly at departure time.
        - "Paused, integer threshold value": This strategy charges immediately after arrival until a threshold value
            (e.g. 0.8 -> 80% SOC). Then the charging is paused. The charging continues with maximal grid power at the
            time (t = Delta_E/P) that allows 100% SOC to be reached at the next departure time (with 30 minutes buffer).
    - The maximal grid power is set in the 'ENERGY_MANAGEMENT' section as 'MAX_POWER'

    Whenever the EV is not at home, the EMS just follows the load profile. If the car is parked at home, it is
    recharged depending on 'EV_CHARGING_STRATEGY'. The algorithm can also be used for electric buses.
    """

    def __init__(self, config: GeneralSimulationConfig, profile_config: ProfileConfig, ems_config: EnergyManagementConfig):
        super().__init__(OperationPriority.MEDIUM)

        self.__soc_profile = SocProfile(config, profile_config) # SOC profile is used in this strategy
        self.__binary_profile = BinaryProfile(config, profile_config)
        self.__soc: float = 0.0
        self.__binary: float = 0.0
        self.__charging_strategy = ems_config.ev_charging_strategy
        self.__max_ac_grid_power = ems_config.max_power  # Here maximal grid power

        self.__timestep = config.timestep
        self.__Wh_to_Ws = 3600
        self.__next_time_zero = None
        self.__soc_at_nextzero = None

    def next(self, time: float, system_state: SystemState, power: float = 0) -> float:
        self.__soc = self.__soc_profile.next(time) # SOC
        self.__binary = np.round(self.__binary_profile.next(time))

        if self.__binary!=0 and self.__binary !=1:
            raise ValueError("The binary profile contains values different from 0 or 1!")

        if self.__binary == 0: # EV is driving
            soc_dif = self.__soc - system_state.soc
            capacity_dif = soc_dif * system_state.capacity * self.__Wh_to_Ws
            power = capacity_dif / self.__timestep
            # E-Bus profile contained weired changes of SOC (Delta >0) while driving (not recuperation!?)
            # which is why a student differentiated here: if soc_dif > 0 => power=0

        else: # EV is parked
            if system_state.soc==1: # if already fully charged
                power = 0
            elif self.__charging_strategy == 'Original': # just follow SOC
                soc_dif = self.__soc - system_state.soc
                capacity_dif = soc_dif * system_state.capacity * self.__Wh_to_Ws
                power = capacity_dif / self.__timestep

            elif self.__charging_strategy == 'Uncontrolled': # Recharge with max AC power when parked
                power = self.__max_ac_grid_power

            elif self.__charging_strategy == 'Mean_power': # Charge with mean power to be fully charged at departure time

                if self.__next_time_zero == None:
                    self.__next_time_zero = self.__binary_profile.next_zero(time)

                charging_duration = self.__next_time_zero - time
                capacity_to_charge = (1 - system_state.soc) * system_state.capacity * self.__Wh_to_Ws
                power = capacity_to_charge / charging_duration

                if charging_duration == self.__timestep:
                    self.__next_time_zero = None

            elif self.__charging_strategy[0:6] == 'Paused':
                threshold = float(self.__charging_strategy[-3:])
                if system_state.soc < threshold:
                    power = self.__max_ac_grid_power
                else:
                    if self.__next_time_zero == None:
                        self.__next_time_zero = self.__binary_profile.next_zero(time)
                    else:
                        charging_duration = (1-threshold)*system_state.capacity*self.__Wh_to_Ws/self.__max_ac_grid_power
                        charging_restart_time = self.__next_time_zero - charging_duration - 1800
                        # start recharging after the pause, buffer of 30 minutes (1800s)
                        if time < charging_restart_time:
                            power = 0
                        else:
                            power = self.__max_ac_grid_power
                            if self.__next_time_zero - time < self.__timestep:
                                self.__next_time_zero = None
        return power


    def update(self, energy_management_state: EnergyManagementState) -> None:
        pass

    def clear(self) -> None:
        pass

    def close(self) -> None:
        self.__soc_profile.close()
        self.__binary_profile.close()



