from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.profile.power.power_profile import PowerProfile
from simses.commons.profile.technical.binary import BinaryProfile
from simses.commons.config.simulation.profile import ProfileConfig
from simses.commons.config.simulation.energy_management import EnergyManagementConfig
from simses.commons.state.energy_management import EnergyManagementState
from simses.commons.state.system import SystemState
from simses.logic.energy_management.strategy.operation_priority import OperationPriority
from simses.logic.energy_management.strategy.operation_strategy import OperationStrategy


class ElectricVehicle(OperationStrategy):

    """
    ElectricVehicle is a basic operation strategy which simulates an EV during trips and recharge. The algorithm
    requires the following profiles and parameters:
    - A load profile that contains the required (and recuperated) power while driving
    - A binary profile that contains ones when the EV is parked at home and zeros if not
    - A string for the parameter 'EV_CHARGING_STRATEGY' which can be:
        - Uncontrolled: Always recharge, if SOC<100%
        - Smart: ...
        - ...
    - The maximal grid power is set in the 'ENERGY_MANAGEMENT' section as 'MAX_POWER'
    - Using load and binary profile from emobpy, the LOAD_SCALING_FACTOR in [PROFILE] section should be set to 1

    Whenever the EV is not at home, the EMS just follows the load profile. If the car is parked at home, it is
    recharged depending on 'EV_CHARGING_STRATEGY'.
    """

    def __init__(self, power_profile: PowerProfile, binary_profile: BinaryProfile, ems_config: EnergyManagementConfig):
        super().__init__(OperationPriority.MEDIUM)

        self.__load_profile_driving: PowerProfile = power_profile
        self.__binary_profile: BinaryProfile = binary_profile

        self.__power: float = 0.0
        self.__binary: float = 0.0
        self.__charging_strategy = ems_config.ev_charging_strategy
        self.__max_ac_grid_power = ems_config.max_power

    def next(self, time: float, system_state: SystemState, power: float = 0) -> float:
        self.__power = self.__load_profile_driving.next(time)
        self.__binary = round(self.__binary_profile.next(time))

        if self.__binary!=0 and self.__binary !=1:
            raise ValueError("The binary profile contains values different from 0 or 1!")

        if self.__binary == 0:                      # if EV is not at home: use load profile value
            power = -1.0 * self.__power
        elif system_state.soc == 1:                 # if EV is at home and SOC=100%: do nothing
            power = 0
        elif self.__charging_strategy == 'Uncontrolled':   # if EV is at home and SOC!=100%: Recharge with charging strategy
            power = self.__max_ac_grid_power
        return power

    def update(self, energy_management_state: EnergyManagementState) -> None:
        energy_management_state.load_power = self.__power

    def clear(self) -> None:
        self.__power = 0.0

    def close(self) -> None:
        self.__binary_profile.close()
        self.__load_profile_driving.close()

