import random

import numpy as np
import pandas as pd


class MaxPeakShavingLimit:
    """
    Determines minimum peak shaving limit that can be served for a given load profile based on a energy storage
    bucket model.
    """

    def __init__(self, energy: float, power: float, efficiency: float, time_step: float, random_profile: bool, file_path: str = '', scaling_factor: float = 1):
        """

        Parameters
        ----------
        energy : energy in Wh
        power : max power in W on the AC side
        efficiency : efficiency in p.u.
        time_step : time step in s
        random_profile: choose to generate a random profile
        file_path: path for power file
        """
        self.__energy = energy
        self.ac__power_rating = power
        self.__efficiency = efficiency
        self.__time_step = time_step
        if random_profile:
            self.__profile = np.asarray([5e6 + random.randint(-1e6, 1e6) for i in range(35040)])
        else:
            self.__profile = self.__read_full_profile(file_path, time_step, scaling_factor)
        self.__ws_to_wh = 1 / 3600

    def calc_max_peak(self, max_runs: float) -> float:
        max_limit = max(self.__profile)
        min_limit = max(self.__profile) - self.ac__power_rating
        max_limit_valid = self.__check_for_valid_limit(max_limit)
        min_limit_valid = self.__check_for_valid_limit(min_limit)

        # if rated power is a valid limit, use the rated power
        if min_limit_valid:
            print('Minimum Peak Shaving Limit is equal to Max Load Power - Nom. Storage Power: \t' + str(round(min_limit / 1e3, 2)) + ' kW')
            return min_limit
        if not max_limit_valid:
            return 0
        print('Limits after run ' + str(0) + '\t\tMin: ' + '{:.2f}'.format(min_limit / 1e3, 4)
              + ' kW\t\tMax: ' + '{:.2f}'.format(max_limit / 1e3, 4) + ' kW')

        run = 0
        while run < max_runs:
            mid_power = (max_limit + min_limit) / 2
            mid_valid = self.__check_for_valid_limit(mid_power)
            if mid_valid:
                max_limit = mid_power
            else:
                min_limit = mid_power
            print('Limits after run ' + str(run) + '\t\tMin: ' + '{:.2f}'.format(min_limit / 1e3, 4)
                  + ' kW\t\tMax: ' + '{:.2f}'.format(max_limit / 1e3, 4) + ' kW')
            run += 1

        print('\nRESULTS:')
        print('Maximum Peak Shaving Limit: \t' + str(round((max_limit + min_limit) / 2 / 1e3, 2)) + ' kW')
        abs_error = (max_limit - min_limit) / 2
        print('Absolute Error: \t\t\t\t' + str(round(abs_error, 2)) + ' W')
        rel_error = ((max_limit - min_limit) / 2) / ((max_limit + min_limit) / 2) * 100
        print('Relative Error: \t\t\t\t' + str(round(rel_error, 4)) + ' %')
        return min_limit

    def __check_for_valid_limit(self, limit: float) -> bool:
        soc = 1
        net_load_series = (self.__profile - limit)

        for i in range(len(net_load_series)):
            if net_load_series[i] > self.ac__power_rating:
                dc_storage_power = self.ac__power_rating / self.__efficiency
            elif net_load_series[i] < -1 * self.ac__power_rating:
                dc_storage_power = -1 * self.ac__power_rating * self.__efficiency
            else:
                if net_load_series[i] >= 0:
                    dc_storage_power = net_load_series[i] / self.__efficiency
                else:
                    dc_storage_power = net_load_series[i] * self.__efficiency
            # Positive dc_storage_power while charging
            soc += -1 * dc_storage_power * self.__time_step * self.__ws_to_wh / self.__energy
            # If SOC hits 0, the peak cannot be shaved
            if soc < 0:
                return False
            if soc > 1:
                soc = 1
        return True

    def __read_full_profile(self, file_path, sample_time, scaling_factor):
        load_profile_in = pd.read_csv(file_path, delimiter='\n', header=None,)
        print('Done Reading Profile.')

        load_profile = load_profile_in.to_numpy()
        load_profile = load_profile.transpose()
        load_profile = load_profile[0, :]
        original_load_profile_length = load_profile.size
        original_seconds_per_timestep = (8760 / original_load_profile_length) * 3600
        original_timesteps = np.arange(1, 8761, original_seconds_per_timestep/3600)
        np.place(original_timesteps, original_timesteps > 8760, 8760)
        to_interpolate_time_steps = np.arange(1, 8761, sample_time / 3600)
        np.place(to_interpolate_time_steps, to_interpolate_time_steps > 8760, 8760)
        interpolated_load_profile = np.interp(to_interpolate_time_steps, original_timesteps, load_profile) * scaling_factor
        return interpolated_load_profile


if __name__ == '__main__':
    scaling_factor = 1
    path = r"C:\Users\Stefan\Desktop\peakshaving_profil3.csv"
    random_profile = False
    limitfinder = MaxPeakShavingLimit(1370e3, 1e6, 0.9, 600, random_profile, path, scaling_factor)
    limitfinder.calc_max_peak(20)
