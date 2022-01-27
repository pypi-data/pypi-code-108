import math

from simses.commons.log import Logger
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.profile.power.generation import GenerationProfile
from simses.commons.state.energy_management import EnergyManagementState
from simses.commons.state.system import SystemState
from simses.logic.energy_management.strategy.operation_priority import OperationPriority
from simses.logic.energy_management.strategy.operation_strategy import OperationStrategy


class ResidentialPvFeedInDamp(OperationStrategy):
    """
    Operation Strategy for a residential home storage system in combination with PV generation.
    The algorithm plans the charging of the lithium_ion according to a PV prediction. It tries to provide a fully charged
    BESS at sundown.
    """

    def __init__(self, power_profile, general_config: GeneralSimulationConfig, pv_generation_profile: GenerationProfile):
        super().__init__(OperationPriority.MEDIUM)
        self.__log: Logger = Logger(type(self).__name__)
        self.__start = general_config.start
        self.__end = general_config.end
        self.__timestep = general_config.timestep
        self.__load_profile = power_profile
        self.__pv_profile = pv_generation_profile
        self.__p_pv_peak = 1
        self.__Wh_to_Ws = 3600
        self.__s_per_day = 86400
        self.__steps_per_day = int(self.__s_per_day / self.__timestep)
        self.__last_pv_generation: list = self.pv_prediction(pv_generation_profile)
        self.__pv_power = 0
        self.__load_power = 0

        self.__eta = 0.95


    def next(self, time: float, system_state: SystemState, power: float = 0) -> float:
        self.__pv_power = self.__pv_profile.next(time)
        self.__load_power = self.__load_profile.next(time)

        residual_load = self.__pv_power - self.__load_power
        if residual_load > 0 and self.__pv_power > 0:
            day = math.floor(
                (time - self.__start) / self.__s_per_day)
            capacity_remaining = system_state.capacity * (1 - system_state.soc)

            energy_remaining = capacity_remaining * self.__Wh_to_Ws
            remaining_time = self.__last_pv_generation[
                                   day] - time - 3600  # An hour before last pv production the storage should be filled
            if remaining_time > 0:  # Preventing division by 0
                power_ref = energy_remaining / (remaining_time * self.__eta)  # Ws
            else:
                power_ref = energy_remaining / (1 * self.__eta)  # Ws
            battery_power = min(power_ref, residual_load)
        else:
            battery_power = residual_load

        return battery_power

    def pv_prediction(self, pv_generation_profile: GenerationProfile) -> list:
        """
        Function do determine the last pv production of every day of the simulation
        and storing the timestamps into a list.

        Returns
        -------
        list:
            timestamps of the last pv production of every day of the simulation.
        """
        self.__log.info('PV Prediction is performed this may take some time.')
        pv_profile: list = pv_generation_profile.profile_data_to_list()
        pv = pv_profile.copy()

        timesteps = (self.__end - self.__start) / self.__timestep
        days = int(timesteps / self.__steps_per_day) + 1

        last_pv_generation = []
        for day in range(days):
            if day == days - 1:  # Last day special consideration (not full day)
                beginning_of_day = day * self.__steps_per_day * self.__timestep
                remaining_steps = int(
                    (self.__end - self.__start - beginning_of_day) / self.__timestep)
                for step in range(remaining_steps):
                    current_step = day * self.__steps_per_day + remaining_steps - step
                    if pv[current_step - 1] > 0:
                        last_pv_generation.append(self.__start + current_step * self.__timestep)
                        break
                    if step == remaining_steps - 1:  # No Generation on this day
                        last_pv_generation.append(None)
            else:
                for step in range(self.__steps_per_day):
                    current_step = (day + 1) * self.__steps_per_day - step
                    if pv[current_step] > 0:
                        last_pv_generation.append(self.__start + current_step * self.__timestep)
                        break
                    if step == self.__steps_per_day - 1:  # No Generation on this day
                        last_pv_generation.append(None)
        self.__log.info('PV Prediction done.')
        return last_pv_generation

    def update(self, energy_management_state: EnergyManagementState) -> None:
        energy_management_state.pv_power = self.__pv_power
        energy_management_state.load_power = self.__load_power

    def clear(self) -> None:
        self.__pv_power = 0.0
        self.__load_power = 0.0

    def close(self) -> None:
        self.__load_profile.close()
        self.__pv_profile.close()
