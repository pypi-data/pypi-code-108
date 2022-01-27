import numpy as np

from simses.commons.config.simulation.energy_management import EnergyManagementConfig
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.config.simulation.profile import ProfileConfig
from simses.commons.config.simulation.system import StorageSystemConfig
from simses.commons.profile.power.power_profile import PowerProfile
from simses.commons.state.energy_management import EnergyManagementState
from simses.commons.state.system import SystemState
from simses.logic.energy_management.strategy.operation_priority import OperationPriority
from simses.logic.energy_management.strategy.operation_strategy import OperationStrategy


class PeakShavingPerfectForesight(OperationStrategy):
    """
        Peak Shaving under the assumption of perfect foresight for the load profile in order to reduce calendar
        degradation.
        The BESS will only charge up to the energy that is needed for the next load peak, right before the load peak
        occurs.
    """
    def __init__(self, general_config: GeneralSimulationConfig, power_profile: PowerProfile, forecast_profile: PowerProfile,
                 energy_management_config: EnergyManagementConfig, system_config: StorageSystemConfig,
                 profile_config: ProfileConfig):
        super().__init__(OperationPriority.VERY_HIGH)

        # configurable
        self.__efficiency = 0.9
        self.__soc_margin = 0.1  # to prevent missing peaks due to non-accurate efficiency
        forecasting_time_hours = 72  # select forecast time for data horizon in the future that is considered
        forecasting_steps = int(round(forecasting_time_hours*60*60 / general_config.timestep))

        self.__load_profile = power_profile
        self.__delta_t = general_config.timestep
        self.__ps_limit: float = energy_management_config.max_power
        nameplate_power = 0
        for system in system_config.storage_systems_ac:
            nameplate_power += float(system[1])
        self.__peak_energy_forecaster = PeakEnergyForecaster(forecast_profile, forecasting_steps, self.__ps_limit, nameplate_power,
                                                             self.__efficiency, general_config, profile_config)
        self.__power = 0

    def next(self, time: float, system_state: SystemState, power: float = 0) -> float:
        # Only charge BESS to PeakShavingEnergy that is required during the next forecast cycle for reduced ageing.
        # If forecasting horizon is chosen too short, the BESS may not be able to charge up before the peak.
        self.__power = self.__load_profile.next(time) + power

        peak_shaving_energy_delta = -1 * self.__peak_energy_forecaster.next(time, self.__power) * 1/3600

        net_load = self.__power - self.__ps_limit
        if net_load >= 0:
            target_power = -1 * net_load
        else:
            if (system_state.soc - self.__soc_margin) * system_state.capacity < peak_shaving_energy_delta:
                # adapt power for long simulation steps to prevent overshoot
                # otherwise: target_power = -1 * net_load
                missing_wh = peak_shaving_energy_delta - (system_state.soc - self.__soc_margin) * system_state.capacity
                missing_wh *= 1 / self.__efficiency
                target_power = missing_wh * 3600 / self.__delta_t
                if target_power > -1 * net_load:
                    target_power = -1 * net_load
            elif self.__soc_margin > system_state.soc:
                missing_wh = (self.__soc_margin - system_state.soc) * system_state.capacity
                target_power = missing_wh * 3600 / self.__delta_t
                if target_power > -1 * net_load:
                    target_power = -1 * net_load
            else:
                target_power = 0

        return target_power

    def update(self, energy_management_state: EnergyManagementState) -> None:
        energy_management_state.load_power = self.__power
        energy_management_state.peakshaving_limit = self.__ps_limit

    def clear(self) -> None:
        self.__power = 0.0

    def close(self) -> None:
        pass


class PeakEnergyForecaster:

    def __init__(self, profile: PowerProfile, forecasting_steps: int, ps_limit: float, p_max: float,
                 efficiency: float, general_config: GeneralSimulationConfig, profile_config: ProfileConfig):

        # open second load profile for forecasts
        # self.__load_profile: LoadProfile = LoadProfile(profile_config, general_config)
        self.__load_profile: PowerProfile = profile

        # needed for algorithm
        self.__efficiency = efficiency
        self.__delta_t = general_config.timestep
        self.__forecasting_steps = forecasting_steps
        self.__start_t = general_config.start
        self.__nameplate_power = p_max
        self.__ps_limit = ps_limit
        power_values = list()
        # for i in range(forecasting_steps):
        for i in range(1, forecasting_steps+1):
            power_values.append(self.__load_profile.next(self.__start_t+i*self.__delta_t))

        # calculate initial energy surplus for every future peak within the load forecast timeframe in Ws
        self.__energy_surpluses = [0]
        self.__time_peak_end = []  # time at which the respective peak ends
        self.__sign = np.sign(ps_limit - power_values[0])
        for i in range(len(power_values)):
            delta_p = self.limit(ps_limit - power_values[i], self.__nameplate_power)
            if delta_p > 0:
                delta_p *= self.__efficiency
            if np.sign(delta_p) <= self.__sign:
                self.__energy_surpluses[-1] += delta_p * self.__delta_t
            else:
                self.__energy_surpluses.append(self.__energy_surpluses[-1])
                self.__time_peak_end.append(self.__start_t + (i+1) * self.__delta_t)
                self.__energy_surpluses[-1] += delta_p * self.__delta_t
            self.__sign = np.sign(delta_p)

    @staticmethod
    def limit(delta: float, max_abs: float) -> float:
        if delta < - max_abs:
            return -max_abs
        elif delta > max_abs:
            return max_abs
        else:
            return delta

    def next(self, time, current_load) -> float:
        # check if a peak has passed
        if self.__time_peak_end:
            if self.__time_peak_end[0] <= time:
                self.__time_peak_end.pop(0)
                self.__energy_surpluses.pop(0)

        # subtract current peak energy from energy of future peaks
        delta_p_now = self.limit(self.__ps_limit - current_load, self.__nameplate_power)
        if delta_p_now > 0:
            delta_p_now *= self.__efficiency
        self.__energy_surpluses = [e - delta_p_now * self.__delta_t for e in self.__energy_surpluses]

        # look for new peaks
        delta_p_future = self.limit(
            self.__ps_limit - self.__load_profile.next(time + self.__forecasting_steps * self.__delta_t),
            self.__nameplate_power)
        if delta_p_future > 0:
            delta_p_future *= self.__efficiency
        if np.sign(delta_p_future) <= self.__sign:
            self.__energy_surpluses[-1] += delta_p_future * self.__delta_t
        else:
            self.__energy_surpluses.append(self.__energy_surpluses[-1])
            self.__time_peak_end.append(time + self.__forecasting_steps * self.__delta_t)
            self.__energy_surpluses[-1] += delta_p_future * self.__delta_t
        self.__sign = np.sign(delta_p_future)
        return min(self.__energy_surpluses)
