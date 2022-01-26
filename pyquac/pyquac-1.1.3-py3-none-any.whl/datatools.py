# built-in libraries
from time import perf_counter
from typing import Iterable
from IPython.display import display

# installable libraries
import pandas as pd
import numpy as np
from ipywidgets import IntProgress  # conda install -c conda-forge ipywidgets | pip install ipywidgets


class Clock:
    """
    Clock class provides accurate variation of time.sleep() method. Example:
    hz_60 = Clock(60) #  create an object for 60 Hz sleep
    hz_60.sleep() #  sleeps for 1. / 60 seconds

    Why to use this? If you would use time.sleep() for 1 iteration, it wouldn't bring you problem, but if your script
    requires a loop with time.sleep() inside, windows OS will ruin your script execution. To explain why this
    happened, Windows OS has its default timer resolution set to 15.625 ms or 64 Hz, which is decently enough for
    most of the applications. However, for applications that need very short sampling rate or time delay, then 15.625
    ms is not sufficient.
    """

    @staticmethod
    def sleep(hz: float):
        deadline = perf_counter() + 1. / hz
        while perf_counter() < deadline:
            pass


class TwoToneSpectroscopy:

    def __init__(self, *, x_min, x_max, x_step, y_min, y_max, y_step):
        """
        Class provides methods for working with live data for Two Tone Spectroscopy
        :param x_min: x minimum value (int | float)
        :param x_max: x maximum value (int | float)
        :param x_step: x step value (int)
        :param y_min: y minimum value (int | float)
        :param y_max: y maximum value (int | float)
        :param y_step: y step value (int)
        """
        self.x_min = x_min
        self.x_max = x_max
        self.x_step = x_step
        self.y_min = y_min
        self.y_max = y_max
        self.y_step = y_step

        self.x_list = np.arange(self.x_min, self.x_max + int(self.x_step),
                                int(self.x_step))
        self.y_list = np.arange(self.y_min, self.y_max + int(self.y_step),
                                int(self.y_step))

        self.__x_ind = 0
        self.__y_ind = 0

        self.__x_raw = []
        self.__y_raw = []
        self.__heat_raw = []

        # self.__iteration_count = len(self.x_list) * len(self.y_list)

    def get_response(self, *, x_key: Iterable = None, y_key: Iterable = None, sleep: float = 344, progress_bar: bool = False):
        """
        generator for pandas object
        :param x_key: (optional) array like object
        :param y_key: (optional) array like object
        :param sleep: time sleep parameter (Hz). Default = 344.
        :param progress_bar: (optional) (bool) if True then shows progress bar of loop
        :return: None
        """

        currents = np.array(x_key) if x_key is not None else self.x_list
        freqs = np.array(y_key) if y_key is not None else self.y_list

        try:
            i = 0
            if not progress_bar:
                pass
            else:
                f = IntProgress(min=0, max=len(currents))
                display(f)

            while self.__x_ind != len(currents):

                self.__x_raw.append(currents[self.__x_ind])
                self.__y_raw.append(freqs[self.__y_ind])
                self.__heat_raw.append(np.random.random())

                if self.__y_ind + 1 == len(freqs):
                    self.__x_ind += 1  # go to the next current
                    self.__y_ind = 0  # go to the next round of frequencies

                    if not progress_bar:
                        pass
                    else:
                        f.value = i

                else:
                    self.__y_ind += 1

                i += 1
                Clock.sleep(sleep)

        except KeyboardInterrupt:
            pass

    @property
    def raw_frame(self):
        return pd.DataFrame({'x_value': self.__x_raw, 'y_value': self.__y_raw, 'heat_value': self.__heat_raw})

    def get_result(self, *, imshow: bool = False) -> pd.DataFrame:
        """
        return resulting Data Frame
        :param imshow: (optional) if True then result returns dataframe for matplotlib.pyplot.imshow()
        :return: Pandas Data Frame. column.names: ['currents', 'frequencies', 'response']
        """
        ny_steps = int((self.y_max - self.y_min) / self.y_step)
        nx_steps = int((self.x_max - self.x_min) // self.x_step)

        x = np.array(self.__x_raw)
        y = np.array(self.__y_raw)
        heat = np.array(self.__heat_raw)

        heat_list = np.empty((nx_steps + 1, ny_steps + 1))
        heat_list[:] = np.nan

        for i in range(len(self.__x_raw)):
            heat_list[int((x[i] - self.x_min) // self.x_step)][int((y[i] - self.y_min) // self.y_step)] = heat[i]

        x_1d = np.repeat(self.x_list, len(self.y_list))
        y_1d = np.tile(self.y_list, len(self.x_list))
        heat_1d = heat_list.ravel()

        if not imshow:
            df = pd.DataFrame({'currents': x_1d, 'frequencies': y_1d, 'response': heat_1d})
        else:
            df = pd.DataFrame(data=heat_list.T, columns=self.x_list, index=self.y_list)

        return df

    def get_approximation_result(self, resolving_zone: float = 0.1, *, imshow: bool = False, fillna: bool = False):
        """
        return resulting approximated Data Frame
        :param resolving_zone: [0:1) - resolving zone for plot
        :param imshow: (optional) if True then result returns dataframe for matplotlib.pyplot.imshow()
        :param fillna: (optional) if True then fill plot with response minimum value
        :return: Pandas Data Frame. column.names: ['currents', 'frequencies', 'response']
        """
        x_set = set(self.raw_frame['x_value'])  # get an array of unique values of x
        tuple_list = ()

        for xx in x_set:
            temp_max_row = tuple(
                self.raw_frame.loc[self.raw_frame[self.raw_frame.x_value == xx].idxmax()['heat_value']])
            tuple_list += (temp_max_row,)

        tuple_of_max_z_values = np.array(tuple_list).T

        max_heat_sample = tuple_of_max_z_values[2].max()
        min_heat_sample = self.raw_frame.heat_value.min() if fillna is True else np.nan

        poly = np.poly1d(np.polyfit(x=tuple_of_max_z_values[0], y=tuple_of_max_z_values[1], deg=2))

        y_for_approximate = []
        for value in poly(self.x_list):
            y_for_approximate.append(self.__find_nearest(value))

        get_result_df = self.get_result()
        get_result_df.loc[:, 'response'] = min_heat_sample

        for i in range(len(y_for_approximate)):
            get_result_mask = (get_result_df['currents'] == self.x_list[i]) & (
                    get_result_df['frequencies'] == y_for_approximate[i])
            get_result_df.loc[get_result_mask, 'response'] = max_heat_sample

        for xx in self.x_list:
            idx = get_result_df[get_result_df.currents == xx].loc[get_result_df.response == max_heat_sample].index[0]
            count_of_resolve_idx = len(self.y_list) * resolving_zone
            get_result_df.iloc[idx + 1:idx + int(count_of_resolve_idx / 2), 2] = max_heat_sample / 2
            get_result_df.iloc[idx - int(count_of_resolve_idx / 2):idx, 2] = max_heat_sample / 2

        if not imshow:
            return get_result_df
        else:
            heat_list = []
            for xx in self.x_list:
                heat_list.append(get_result_df[get_result_df.currents == xx].loc[:, 'response'].values)
            df = pd.DataFrame(data=np.array(heat_list).T, columns=self.x_list, index=self.y_list)
            return df

    def __find_nearest(self, value):
        array = np.asarray(self.y_list)
        idx = (np.abs(array - value)).argmin()
        return array[idx]
