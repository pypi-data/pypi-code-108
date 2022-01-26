# built-in libraries
from time import perf_counter
from typing import Iterable
# from IPython.display import display

# installable libraries
import pandas as pd
import numpy as np


# from ipywidgets import IntProgress  # conda install -c conda-forge ipywidgets | pip install ipywidgets


class timer:
    """
    timer class provides accurate variation of time.sleep() method. Example:
    timer.sleep(1) #  sleeps for 1. second

    Why to use this? If you would use time.sleep() for 1 iteration, it wouldn't bring you problem, but if your script
    requires a loop with time.sleep() inside, windows OS will ruin your script execution. To explain why this
    happened, Windows OS has its default timer resolution set to 15.625 ms or 64 Hz, which is decently enough for
    most of the applications. However, for applications that need very short sampling rate or time delay, then 15.625
    ms is not sufficient.
    """

    @staticmethod
    def sleep(sec: float):
        deadline = perf_counter() + sec
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

        self.x_list = np.arange(self.x_min, self.x_max + self.x_step,
                                self.x_step)
        self.y_list = np.arange(self.y_min, self.y_max + self.y_step,
                                self.y_step)

        self.__x_raw = []
        self.__y_raw = []
        self.__heat_raw = []

        self.heat_container = np.zeros(len(self.x_list) * len(self.y_list))
        self.heat_container[:] = np.nan

        self.x_container = np.zeros(len(self.x_list) * len(self.y_list))
        self.y_container = np.zeros(len(self.x_list) * len(self.y_list))

        self.nx_steps = len(self.x_list)
        self.ny_steps = len(self.y_list)

        self.heat_list = np.empty((self.nx_steps, self.ny_steps))
        self.heat_list[:] = np.nan

        self.bar_indicator = 0

        # self.__iteration_count = len(self.x_list) * len(self.y_list)

    def get_response(self, *, x_key: Iterable = None, y_key: Iterable = None, sleep: float = 0.05):
        """
        generator for pandas object
        :param x_key: (optional) array like object
        :param y_key: (optional) array like object
        :param sleep: time sleep parameter (Hz). Default = 344.
        :return: None
        """

        x = x_key if x_key is not None else self.x_list

        """config frequencies"""
        if y_key is not None:
            if np.array(y_key).ndim == 1:
                y_key = np.tile(y_key, [len(x), 1])
            elif np.array(y_key).ndim > 1 and x_key is not None:
                ind_list = []
                for x_k in x_key:
                    ind_list.append(list(self.x_list).index(x_k))
                y_key = y_key[ind_list]

            else:
                pass

            freqs = y_key.ravel()

        else:
            freqs = np.tile(self.y_list, len(x))
            pass

        """config currents"""
        if y_key is not None:
            current_encapsulated = []
            for i, y_i in enumerate(y_key):
                current_encapsulated.append([x[i], ] * len(y_i))
            currents = np.array(current_encapsulated).ravel()
        else:
            currents = np.repeat(x, len(self.y_list))

        temp_df = pd.DataFrame({'x_value': currents, 'y_value': freqs})

        index1 = pd.MultiIndex.from_arrays([temp_df[col] for col in ['x_value', 'y_value']])
        index2 = pd.MultiIndex.from_arrays([self.raw_frame[col] for col in ['x_value', 'y_value']])
        temp_df = temp_df.loc[~index1.isin(index2)]

        currents = temp_df['x_value'].values
        freqs = temp_df['y_value'].values

        try:
            i = 0

            # if not progress_bar:
            #     pass
            # else:
            #     f = IntProgress(min=0, max=len(currents))
            #     display(f)

            for _ in range(len(currents)):
                self.__x_raw.append(currents[i])
                self.__y_raw.append(freqs[i])
                self.__heat_raw.append(np.random.random())

                # if not progress_bar:
                #     pass
                # else:
                #     f.value = self.bar_indicator
                #
                # self.bar_indicator += 1

                i += 1
                timer.sleep(sleep)

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

        self.heat_container[:len(self.__heat_raw)] = self.__heat_raw
        self.x_container[:len(self.__x_raw)] = self.__x_raw
        self.y_container[:len(self.__y_raw)] = self.__y_raw

        for i in range(len(self.__x_raw)):
            self.heat_list[int((self.x_container[i] - self.x_min) // self.x_step)][
                int((self.y_container[i] - self.y_min) // self.y_step)] = self.heat_container[i]

        x_1d = np.repeat(self.x_list, len(self.y_list))
        y_1d = np.tile(self.y_list, len(self.x_list))
        heat_1d = self.heat_list.ravel()

        if not imshow:
            df = pd.DataFrame({'currents': x_1d, 'frequencies': y_1d, 'response': heat_1d})
        else:
            df = pd.DataFrame(data=self.heat_list.T[::-1], columns=self.x_list, index=self.y_list)

        return df

    def approximate(self, resolving_zone: float = 0.1, *, imshow: bool = False, fillna: bool = False):
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
                self.raw_frame.loc[self.raw_frame[self.raw_frame.x_value == xx]['heat_value'].abs().idxmax()])
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

        y_keys = []

        for xx in self.x_list:
            idx = get_result_df[get_result_df.currents == xx].loc[get_result_df.response == max_heat_sample].index[0]
            count_of_resolve_idx = len(self.y_list) * resolving_zone
            get_result_df.iloc[idx + 1:idx + int(count_of_resolve_idx / 2), 2] = max_heat_sample / 2
            get_result_df.iloc[idx - int(count_of_resolve_idx / 2):idx, 2] = max_heat_sample / 2

            y_keys.append(
                get_result_df.iloc[idx - int(count_of_resolve_idx / 2):idx + int(count_of_resolve_idx / 2), 1])

        if not imshow:
            return dict(mask=get_result_df,
                        y_key=np.array(y_keys))
        else:
            heat_list = []
            for xx in self.x_list:
                heat_list.append(get_result_df[get_result_df.currents == xx].loc[:, 'response'].values)
            df = pd.DataFrame(data=np.array(heat_list).T[::-1], columns=self.x_list, index=self.y_list)
            return dict(mask=df,
                        y_key=np.array(y_keys))

    def __find_nearest(self, value):
        array = np.asarray(self.y_list)
        idx = (np.abs(array - value)).argmin()
        return array[idx]
