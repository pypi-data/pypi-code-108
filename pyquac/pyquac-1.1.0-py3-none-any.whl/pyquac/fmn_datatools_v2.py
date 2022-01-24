# built-in libraries
from time import perf_counter
from typing import Iterable, Union
import time
# installable libraries
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import stats
import numba as nb


# @nb.jit(nopython=True)
# def _complicated(heat_list_, raw_array_x, raw_array_y, raw_array_z, x_min_, x_step_, y_min_, y_step_,
#                  len_y_):
#
#     for k in range(len(raw_array_x)):
#         x_ind = np.around((raw_array_x[k] - x_min_) / x_step_)
#         y_ind = np.around((raw_array_y[k] - y_min_) / y_step_)
#
#         for i in range(len(heat_list_)):
#             if i == int(x_ind * len_y_ + y_ind):
#                 heat_list_[i] = raw_array_z[k]
#             else:
#                 pass
#             pass
#         pass
#     return heat_list_

@nb.jit(nopython=True)
def _complicated(raw_array_x, raw_array_y, x_min_, x_step_, y_min_, y_step_,
                 len_y_):
    ind_array = np.zeros(len(raw_array_x))

    if len(ind_array) >= 2:
        for k in range(len(raw_array_x)):
            x_ind = np.around((raw_array_x[k] - x_min_) / x_step_)
            y_ind = np.around((raw_array_y[k] - y_min_) / y_step_)

            ind_array[k] = x_ind * len_y_ + y_ind
            pass

        return ind_array
    else:
        pass


# @nb.jit(nopython=True)
# def _complicated(heat_list_, raw_array_x, raw_array_y, raw_array_z, x_min_, x_step_, y_min_, y_step_,
#                  heat_container):
#     k = 0
#     heat_container[:len(raw_array_z)] = raw_array_z
#
#     unique_x = np.unique(raw_array_x)
#     unique_y = np.unique(raw_array_y)
#
#     for i in range(len(unique_x)):
#         for j in range(len(unique_y)):
#             x_ind = np.around((unique_x[i] - x_min_) / x_step_)
#             y_ind = np.around((unique_y[j] - y_min_) / y_step_)
#
#             if (i == x_ind) & (j == y_ind):
#                 heat_list_[j, i] = heat_container[k]
#                 k = k + 1
#     return heat_list_


class mrange:

    @classmethod
    def cust_range(cls, *args, rtol=1e-05, atol=1e-08, include=[True, False]):
        """
        Combines numpy.arange and numpy.isclose to mimic
        open, half-open and closed intervals.
        Avoids also floating point rounding errors as with
        numpy.arange(1, 1.3, 0.1)
        array([1. , 1.1, 1.2, 1.3])

        args: [start, ]stop, [step, ]
            as in numpy.arange
        rtol, atol: floats
            floating point tolerance as in numpy.isclose
        include: boolean list-like, length 2
            if start and end point are included
        """
        # process arguments
        if len(args) == 1:
            start = 0
            stop = args[0]
            step = 1
        elif len(args) == 2:
            start, stop = args
            step = 1
        else:
            assert len(args) == 3
            start, stop, step = tuple(args)

        # determine number of segments
        n = (stop - start) / step + 1

        # do rounding for n
        if np.isclose(n, np.round(n), rtol=rtol, atol=atol):
            n = np.round(n)

        # correct for start/end is exluded
        if not include[0]:
            n -= 1
            start += step
        if not include[1]:
            n -= 1
            stop -= step

        return np.linspace(start, stop, int(n))

    @classmethod
    def crange(cls, *args, **kwargs):
        return mrange.cust_range(*args, **kwargs, include=[True, True])

    @classmethod
    def orange(cls, *args, **kwargs):
        return mrange.cust_range(*args, **kwargs, include=[True, False])


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

    def __init__(self,
                 *, x_min, x_max, x_step, y_min, y_max, y_step):
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
        self.x_step = float(x_step)
        self.y_min = y_min
        self.y_max = y_max
        self.y_step = float(y_step)

        self.load = None
        self.frequency = None

        self.__x_step_DP = len(str(self.x_step).split(".")[1])
        self.__y_step_DP = len(str(self.y_step).split(".")[1])
        self.__max_step_DP = max([self.__x_step_DP, self.__y_step_DP])

        self.x_list = mrange.orange(self.x_min, self.x_max + self.x_step,
                                    self.x_step)
        self.y_list = mrange.orange(self.y_min, self.y_max + self.y_step,
                                    self.y_step)

        self.x_list = np.around(self.x_list, decimals=self.__x_step_DP)
        self.y_list = np.around(self.y_list, decimals=self.__y_step_DP)

        self.x_raw = []
        self.y_raw = []
        self.heat_raw = []

        self.heat_container = np.zeros(len(self.x_list) * len(self.y_list))
        self.heat_container[:] = np.nan

        self.heat_container1 = np.zeros(len(self.x_list) * len(self.y_list))
        self.heat_container1[:] = np.nan

        self.len_y = len(self.y_list)

        self.x_container = np.zeros(len(self.x_list) * len(self.y_list))
        self.y_container = np.zeros(len(self.x_list) * len(self.y_list))

        self.nx_steps = len(self.x_list)
        self.ny_steps = len(self.y_list)

        self.heat_list = np.empty((self.ny_steps, self.nx_steps))
        self.heat_list[:, :] = np.nan

        self.heat_samples = np.array([])
        self.heat_mins = np.array([])
        self.heat_maxs = np.array([])

        self.glob_h_mi = 0
        self.glob_h_ma = 0
        self.glob_samp = 0

        self.x_1d = np.repeat(self.x_list, len(self.y_list))
        self.y_1d = np.tile(self.y_list, len(self.x_list))

        x1 = 2000
        y1 = 70e3

        x2 = 3000
        y2 = 350e3

        k = (y1 - y2) / (x1 - x2)
        self.timing = np.arange(1000, 40000, 100)

        b = y2 - k * x2

        self.count_of_elements = k * self.timing + b

        self.x_for_approximate_idxs = []

    def iter_setup(self, *, x_key: Union[float, int, Iterable] = None, y_key: Union[float, int, Iterable] = None,
                   x_min=None, x_max=None, y_min=None, y_max=None):
        """
        measurement setup. if all optional params are None then setup self.load and self.frequency for measuring all data
        :param x_key: x value(s) for measurement
        :param y_key: y value(s) for measurement
        :param x_min: x min value of measurement
        :param x_max: x max value of measurement
        :param y_min: y min value of measurement
        :param y_max: y max value of measurement
        :return:
        """
        if x_key is not None:
            x_key = self.__config_closest_values(x_key, self.x_list)

        if y_key is not None:
            if np.array(y_key).dtype == object:
                pass
            else:
                y_key = self.__config_closest_values(y_key, self.y_list)

        "set x_min x_max arrays"
        if (y_min != None) | (y_max != None) | (x_min != None) | (x_max != None):
            x_key = self.__config_arrays_from(min_value=x_min, max_value=x_max, step=self.x_step,
                                              array=self.x_list, array_set_input_in_func=x_key, column='x_value')

            y_key = self.__config_arrays_from(min_value=y_min, max_value=y_max, step=self.y_step,
                                              array=self.y_list, array_set_input_in_func=y_key, column='y_value')

        if x_key is not None:
            x_key = x_key if isinstance(x_key, Iterable) else [x_key, ]

        x = np.array(x_key) if x_key is not None else np.array(self.x_list)

        """config frequencies"""
        if y_key is not None:
            y_key = y_key if isinstance(y_key, Iterable) else [y_key, ]
            if np.array(y_key).dtype != object:
                y_key = np.tile(y_key, [len(x), 1])
            elif np.array(y_key).dtype == object and x_key is not None:
                ind_list = []
                for x_k in x_key:
                    ind_list.append(list(self.x_list).index(x_k))
                y_key = y_key[ind_list]

            else:
                pass

            if np.array(y_key).dtype == object:
                freqs = []
                for i in range(len(y_key)):
                    freqs += list(y_key[i])
                freqs = np.array(freqs)

            else:
                freqs = y_key.ravel()


        else:
            freqs = np.tile(self.y_list, len(x))
            pass

        """config currents"""
        if y_key is not None:
            if np.array(y_key).dtype == object:
                current_encapsulated = []
                for i, y_i in enumerate(y_key):
                    current_encapsulated.append([x[i], ] * len(y_i))
                # currents = np.array(current_encapsulated).ravel()

                if np.array(y_key).dtype == object:
                    currents = []
                    for i in range(len(current_encapsulated)):
                        currents += list(current_encapsulated[i])
                    currents = np.array(currents)

                else:
                    currents = np.array(current_encapsulated).ravel()

            else:
                current_encapsulated = []
                for i, y_i in enumerate(y_key):
                    current_encapsulated.append([x[i], ] * len(y_i))
                currents = np.array(current_encapsulated).ravel()
                pass

        else:
            currents = np.repeat(x, len(self.y_list))

        "collect all together"
        temp_df = pd.DataFrame({'x_value': currents, 'y_value': freqs})
        raw_frame_without_nans = self.raw_frame.dropna(axis=0)

        index1 = pd.MultiIndex.from_arrays([temp_df[col] for col in ['x_value', 'y_value']])
        index2 = pd.MultiIndex.from_arrays([raw_frame_without_nans[col] for col in ['x_value', 'y_value']])
        temp_df = temp_df.loc[~index1.isin(index2)]

        self.load = temp_df['x_value'].values
        self.frequency = temp_df['y_value'].values

        pass

    def write(self, *, x: Union[float, int] = None, y: Union[float, int] = None,
              heat: Union[float, int] = None):
        """
        writes load, frequency ans response to class entity
        :param x: load value
        :param y: frequency value
        :param z: response value
        """
        self.x_raw.append(x)  # Current write to DF
        self.y_raw.append(y)  # Frequency write to DF
        self.heat_raw.append(heat)  # Response write to DF
        pass

    def check_stop_on_iter(self, i):
        if len(self.x_raw) == len(self.y_raw) == len(self.heat_raw):
            pass
        else:
            max_l = max([len(self.x_raw), len(self.y_raw), len(self.heat_raw)])
            i = i + 1 if i < len(self.frequency) else i
            if len(self.y_raw) < max_l: self.y_raw.append(self.frequency[i])
            if len(self.heat_raw) < max_l: self.heat_raw.append(np.nan)

    @property
    def raw_frame(self):
        """
        generates raw Data Frame with columns [x_value, y_value, heat_value]
        :return: dataframe
        """
        if len(self.x_raw) == len(self.y_raw) == len(self.heat_raw):
            return pd.DataFrame({'x_value': self.x_raw, 'y_value': self.y_raw, 'heat_value': self.heat_raw})
        else:
            pass

    @property
    def raw_array(self):
        """
        generates raw 2-d numpy array np.array([y_value, x_value])
        :return:
        """
        if len(self.x_raw) == len(self.y_raw) == len(self.heat_raw):
            return np.array([self.x_raw, self.y_raw, self.heat_raw])
        else:
            pass

    def get_result(self, *, imshow: bool = False) -> pd.DataFrame:
        """
        return resulting Data Frame
        :param imshow: (optional) if True then result returns dataframe for matplotlib.pyplot.imshow()
        :return: Pandas Data Frame. column.names: ['currents', 'frequencies', 'response']
        """
        l_h = len(self.heat_container[:len(self.heat_raw)])
        l_x = len(self.x_container[:len(self.x_raw)])
        l_y = len(self.y_container[:len(self.y_raw)])

        if l_h == l_x == l_y:
            self.heat_container[:len(self.heat_raw)] = self.heat_raw
            self.x_container[:len(self.x_raw)] = self.x_raw
            self.y_container[:len(self.y_raw)] = self.y_raw
        else:
            pass

        for i in range(len(self.x_raw)):
            self.heat_list[round((self.y_container[i] - self.y_min) / self.y_step),
                           round((self.x_container[i] - self.x_min) / self.x_step)] = self.heat_container[i]

        heat_1d = self.heat_list.ravel(order='F')

        if not imshow:
            df = pd.DataFrame({'currents': self.x_1d, 'frequencies': self.y_1d, 'response': heat_1d})
        else:
            df = pd.DataFrame(data=self.heat_list, columns=self.x_list, index=self.y_list)

        return df

    @property
    def non_njit_result(self):
        """
        generates resulting 2-d array
        :return: numpy.ndarray[y_values, x_values]
        """

        if len(self.x_raw) >= 2:
            array = np.array(self.raw_array)
            z_val = array[2, :]
            x_val = array[0, :]
            y_val = array[1, :]

            for i in range(len(z_val)):
                self.heat_list[round((y_val[i] - self.y_min) / self.y_step),
                               round((x_val[i] - self.x_min) / self.x_step)] = z_val[i]

            return self.heat_list

        else:
            pass

    @property
    def njit_result(self):
        """
        generates CPU accelerated resulting 2-d array
        :return: numpy.ndarray[y_values, x_values]
        """
        # array = np.copy(self.raw_array)
        array_to_njit = self.raw_array
        z_val = array_to_njit[2, :]
        x_val = array_to_njit[0, :]
        y_val = array_to_njit[1, :]


        ind_array = _complicated(x_val, y_val,
                                 self.x_min, self.x_step, self.y_min, self.y_step,
                                 self.len_y)
        if len(self.x_raw) >= 2:
            array_to_process = np.copy(self.heat_container1)
            array_to_process[ind_array.astype(int)] = z_val

            return array_to_process
        else:
            pass

    def approximate(self, resolving_zone: float = 0.1, *, fillna: bool = False, info=False,
                    plot: bool = False):
        """
        return dict object with keys:
        1) y_key - an object containing y values for each x of self.x_list
        2) mask - mask of values that would be measured. it can be plotted with plotly's Heatmap
        3) imshow_mask - mask of values that would be measured. it can be plotted with plotly's Heatmap
        4) poly_line - approximated np.poly1d() curve
        :param resolving_zone: [0:1) - resolving zone for plot
        :param fillna: (optional) if True then fill plot with response minimum value
        :param info: (optional) set True if you would like to get information of approximation process
        :param plot: (optional) set True if you would like to get density plots of outliers on measured x values
        :return: dictionary. keys: ['y_key', 'mask', 'imshow_mask', 'poly_line']
        """
        X = self.raw_frame.copy()

        """rows that we are looking for (every x_value)"""
        x_set = np.unique(X['x_value'].values)  # get an array of unique values of x

        glob_samp, glob_h_mi, glob_h_ma = self.__define_heat_sample_on(x_set, info=info, plot=plot, q_max=80, q_min=20)

        self.glob_samp = glob_samp
        self.glob_h_mi = glob_h_mi
        self.glob_h_ma = glob_h_ma

        for xxx in x_set:
            heat_sample, heat_min, heat_max = self.__define_heat_sample_on(xxx, info=info, plot=plot)

            self.heat_samples = np.append(self.heat_samples, heat_sample)
            self.heat_mins = np.append(self.heat_mins, heat_min)
            self.heat_maxs = np.append(self.heat_maxs, heat_max)

        self.__change_outlier_heatsamples()  # change bad heat samples

        tuple_list = ()
        ip = 0
        for xx in x_set:

            heat_sample, heat_min, heat_max = self.heat_samples[ip], self.heat_mins[ip], self.heat_maxs[ip]
            ip += 1
            # bad_y = self.__bad_outliers_on(xx)

            y_min, y_max = self.__find_min_max_y_on_(xx, heat_sample)

            if len(self.raw_frame[X.x_value == xx].y_value) <= 0.7 * len(self.y_list):
                temp_y_idx = (X[X.x_value == xx].heat_value - heat_sample).abs().idxmin()
            else:
                temp_y_idx = (X[(X.x_value == xx) & (X.y_value >= y_min) & (X.y_value <= y_max)
                                ].heat_value - heat_sample).abs().idxmin()

            temp_max_row = tuple(X.iloc[temp_y_idx])

            tuple_list += (temp_max_row,)

        # clear arrays
        self.heat_samples = np.array([])
        self.heat_mins = np.array([])
        self.heat_maxs = np.array([])

        # rotating array
        tuple_of_max_z_values = np.array(tuple_list).T

        poly = np.poly1d(np.polyfit(x=tuple_of_max_z_values[0], y=tuple_of_max_z_values[1], deg=2))

        print('x', tuple_of_max_z_values[0])
        print('y', tuple_of_max_z_values[1])

        """getting freq values for approximation"""
        y_for_approximate = []
        self.x_for_approximate_idxs = []
        x_for_approximate_ind = 0
        for value in poly(self.x_list):
            y_for_approximate.append(self.__find_nearest(value))
            if (value <= self.y_min) or (value >= self.y_max):
                self.x_for_approximate_idxs.append(x_for_approximate_ind)
            x_for_approximate_ind += 1

        """masking"""

        min_heat_sample = X.heat_value.min() if fillna is True else np.nan
        max_heat_sample = tuple_of_max_z_values[2].mean()

        get_result_df = self.get_result()
        get_result_df.loc[:, 'response'] = min_heat_sample

        for i in range(len(y_for_approximate)):
            get_result_mask = (get_result_df['currents'] == self.x_list[i]) & (
                    get_result_df['frequencies'] == y_for_approximate[i])
            get_result_df.loc[get_result_mask, 'response'] = max_heat_sample

        """approximation"""
        y_keys = []

        for xx in self.x_list:
            idx = get_result_df[get_result_df.currents == xx].loc[get_result_df.response == max_heat_sample].index[0]

            count_of_resolve_idx = len(self.y_list) * resolving_zone
            get_result_df.iloc[idx + 1:idx + round(count_of_resolve_idx / 2), 2] = max_heat_sample / 2

            get_result_df.iloc[idx - round(count_of_resolve_idx / 2):idx, 2] = max_heat_sample / 2
            y_keys.append(
                get_result_df.iloc[idx - int(count_of_resolve_idx / 2):idx + int(count_of_resolve_idx / 2),
                1].to_list())

            self.approximation_y_keys = np.array(y_keys, dtype=object)

        """checking for zero-length list. and fix it. what did I do here???????"""
        for i in range(len(y_keys)):
            if len(y_keys[i]) == 0:
                if i == len(y_keys) - 1:
                    y_keys[i] = list(y_keys[i - 1])
                else:
                    y_keys[i] = list(y_keys[i + 1])

        """config returning values"""
        """imshow"""
        heat_list = []
        for xx in self.x_list:
            heat_list.append(get_result_df[get_result_df.currents == xx].loc[:, 'response'].values)
        get_imshow_result_df = pd.DataFrame(data=np.array(heat_list).T, columns=self.x_list, index=self.y_list)

        "deleting bad x approximation"
        # y_keys = np.delete(y_keys, self.x_for_approximate_idxs)
        x_keys = np.delete(self.x_list, self.x_for_approximate_idxs)

        return dict(y_key=np.array(y_keys, dtype=object),
                    x_key=x_keys,
                    mask=get_result_df,
                    imshow_mask=get_imshow_result_df,
                    poly_line={'x': self.x_list, 'y': poly(self.x_list)})

    def clean_up(self):
        """
        cleans data after approximation
        """
        i = 0
        tolerance = 1e-3
        for x in np.array(self.x_list, dtype=float):
            # array1 = np.array(self.raw_frame['y_value'].to_numpy(), dtype=float)
            array2 = np.array(self.approximation_y_keys[i], dtype=float)
            mask_arr = ~np.isclose(self.raw_frame['y_value'].values[:, None], array2, atol=.1).any(axis=1)
            idx = self.raw_frame[(mask_arr) & (self.raw_frame['x_value'] == x)].index
            #             mask_array = np.zeros(len(array1), dtype=bool)
            #             for value in array2:
            #                 for j in range(len(array1)):
            #                     if abs(value - array1[j]) < tolerance:
            #                         mask_array[j] = True

            # self.raw_frame[~np.isclose(self.raw_frame['y_value'].values[:, None], array2, atol=.001).any(axis=1)]
            # mask = ~(np.isin(array1,array2))

            self.x_raw = np.delete(self.x_raw, idx)
            self.y_raw = np.delete(self.y_raw, idx)
            self.heat_raw = np.delete(self.heat_raw, idx)
            self.heat_list[:, i] = self.heat_list[:, i] * np.nan
            i += 1

        self.x_raw = list(self.x_raw)
        self.y_raw = list(self.y_raw)
        self.heat_raw = list(self.heat_raw)

        self.heat_container[:] = np.nan
        self.x_container[:] = 0
        self.y_container[:] = 0

    def drop(self, x: Union[float, int, Iterable] = None, y: Union[float, int, Iterable] = None,
             x_min=None, x_max=None, y_min=None, y_max=None):
        """
        drops specific values (x, y)
        :param x: x value(s) [float, int, Iterable]
        :param y: x value(s) [float, int, Iterable]
        :param x_min: minimum x value [float, int]
        :param x_max: maximum x value [float, int]
        :param y_min: minimum y value [float, int]
        :param y_max: maximum y value [float, int]
        """
        """if x list is given then find nearest values in self.x_list"""
        if x is not None:
            x = self.__config_closest_values(x, self.raw_array[0, :])

        """if y list is given then find nearest values in self.y_list"""
        if y is not None:
            y = self.__config_closest_values(y, self.raw_array[1, :])

        "set min max arrays"
        if (y_min != None) | (y_max != None) | (x_min != None) | (x_max != None):
            x = self.__config_arrays_from(min_value=x_min, max_value=x_max, step=self.x_step,
                                          array=self.raw_array[0, :], array_set_input_in_func=x, column='x_value')

            y = self.__config_arrays_from(min_value=y_min, max_value=y_max, step=self.y_step,
                                          array=self.raw_array[1, :], array_set_input_in_func=y, column='y_value')

        if (x is not None) and (y is None):
            self.__drop_the('x_value', x)
            pass

        if (y is not None) and (x is None):
            self.__drop_the('y_value', y)
            pass

        if (x is not None) and (y is not None):
            self.__drop_the_cols(x, y)
            pass

    def __drop_the(self, column: str, value_s):

        decimals = self.__x_step_DP if column == 'x_value' else self.__y_step_DP

        value_s = list(value_s) if isinstance(value_s, Iterable) else [value_s, ]
        value_s = np.around(value_s, decimals=decimals)
        idx = self.raw_frame[self.raw_frame[column].isin(value_s)].index

        self.x_raw = list(np.delete(self.x_raw, idx))
        self.y_raw = list(np.delete(self.y_raw, idx))
        self.heat_raw = list(np.delete(self.heat_raw, idx))

        # for i in idx:
        #     self.heat_raw[i] = np.nan

        self.heat_container[:] = np.nan
        self.x_container[:] = 0
        self.y_container[:] = 0

        column_var = list(self.x_list) if column == 'x_value' else list(self.y_list)

        col_idx_list = [list(column_var).index(value_s[i]) for i in range(len(value_s))]

        if column == 'x_value':
            for i in col_idx_list:
                self.heat_list[:, i] = self.heat_list[:, i] * np.nan
        else:
            for i in col_idx_list:
                self.heat_list[i] = self.heat_list[i] * np.nan

        pass

    def __drop_the_cols(self, x_values, y_values):

        x_decimals, y_decimals = self.__x_step_DP, self.__y_step_DP

        # x mask
        x_value_s = list(x_values) if isinstance(x_values, Iterable) else [x_values, ]
        x_value_s = np.around(x_value_s, decimals=x_decimals)
        x_mask = np.logical_or.reduce(np.isclose(self.raw_frame['x_value'].to_numpy()[None, :], x_value_s[:, None]))

        # y mask
        y_value_s = list(y_values) if isinstance(y_values, Iterable) else [y_values, ]
        y_value_s = np.around(y_value_s, decimals=y_decimals)
        y_mask = np.logical_or.reduce(np.isclose(self.raw_frame['y_value'].to_numpy()[None, :], y_value_s[:, None]))

        # idx
        msk = pd.DataFrame({'y': y_mask, 'x': x_mask}).all(axis=1)
        idx = self.raw_frame[msk].index

        self.x_raw = list(np.delete(self.x_raw, idx))
        self.y_raw = list(np.delete(self.y_raw, idx))
        self.heat_raw = list(np.delete(self.heat_raw, idx))

        self.heat_container[:] = np.nan
        self.x_container[:] = 0
        self.y_container[:] = 0

        x_col_idx_list = [list(self.x_list).index(x_value_s[i]) for i in range(len(x_value_s))]
        y_col_idx_list = [list(self.y_list).index(y_value_s[i]) for i in range(len(y_value_s))]

        for i in x_col_idx_list:
            for j in y_col_idx_list:
                self.heat_list[j, i] = self.heat_list[j, i] * np.nan
        pass

    def __config_closest_values(self, input_value, base_array):

        """if x list is given then find nearest values in self.x_list"""

        if isinstance(input_value, float) or isinstance(input_value, int):
            input_value = self.__find_nearest_universal(base_array, input_value)
        else:
            input_value_temp = []
            for value in input_value:
                input_value_temp.append(self.__find_nearest_universal(base_array, value))
            input_value = np.array(input_value_temp)
        return input_value

    def __config_arrays_from(self, min_value, max_value, step, array, array_set_input_in_func, column='x_value'):

        """configurate arrays from given values"""

        if (min_value is not None) and (max_value is not None):
            min_value = self.__find_nearest_universal(array, min_value)
            max_value = self.__find_nearest_universal(array, max_value)
            array = mrange.orange(min_value, max_value + step, step)
            return array

        elif (min_value is not None) and (max_value is None):
            if column == 'x_value':
                max_v = self.x_max
                step_v = self.x_step
            else:
                max_v = self.y_max
                step_v = self.y_step

            min_value = self.__find_nearest_universal(array, min_value)
            array = mrange.orange(min_value, max_v + step_v, step_v)
            return array
        elif (min_value is None) and (max_value is not None):
            if column == 'x_value':
                min_v = self.x_min
                step_v = self.x_step
            else:
                min_v = self.y_min
                step_v = self.y_step

            max_value = self.__find_nearest_universal(array, max_value)
            array = mrange.orange(min_v, max_value + step_v, step_v)
            return array

        else:
            return array_set_input_in_func

    def __define_heat_sample_on(self, xx, info, plot, q_max=80, q_min=20):

        xx = xx if isinstance(xx, Iterable) else [xx, ]

        """initial params"""
        x_lw = np.array([0, 0])
        y_lw = np.array([0, 0])

        x_uw = np.array([0, 0])
        y_uw = np.array([0, 0])

        """define outliers"""
        #         new_arr = self.__smooth_list_gaussian(self.raw_frame[self.raw_frame['x_value'].isin(xx)
        #                                                             ].heat_value.values, degree=3)
        q75, q25 = np.percentile(self.raw_frame[self.raw_frame['x_value'].isin(xx)
                                 ].heat_value.values, [q_max, q_min])
        iqr = q75 - q25
        lower_whisker = q25 - 1.5 * iqr
        upper_whisker = q75 + 1.5 * iqr

        lower_mask = self.raw_frame['heat_value'].values < lower_whisker
        upper_mask = self.raw_frame['heat_value'].values > upper_whisker

        lw_outlier_cnt = len(self.raw_frame['heat_value'].values[lower_mask])
        up_outlier_cnt = len(self.raw_frame['heat_value'].values[upper_mask])

        lw_len = len(self.raw_frame['heat_value'].values[lower_mask])
        uw_len = len(self.raw_frame['heat_value'].values[upper_mask])

        """split outliers in data"""
        # lower whisker
        if lw_len > 1:
            xmin_lw = min(self.raw_frame['heat_value'].values[lower_mask])
            xmax_lw = max(self.raw_frame['heat_value'].values[lower_mask])
            x_lw = np.linspace(xmin_lw, xmax_lw, 1000)  # get 1000 points on x axis

            # get actual kernel density.
            density_lw = stats.gaussian_kde(self.raw_frame['heat_value'].values[lower_mask].flatten())
            y_lw = np.array(density_lw(x_lw))

        # upper whisker
        if uw_len > 1:
            xmin_uw = min(self.raw_frame['heat_value'].values[upper_mask])
            xmax_uw = max(self.raw_frame['heat_value'].values[upper_mask])
            x_uw = np.linspace(xmin_uw, xmax_uw, 1000)  # get 1000 points on x axis

            # get actual kernel density.
            density_uw = stats.gaussian_kde(self.raw_frame['heat_value'].values[upper_mask].flatten())
            y_uw = np.array(density_uw(x_uw))

        if (lw_len <= 1) and (uw_len <= 1):
            heat_min = self.glob_h_mi
            heat_max = self.glob_h_ma
            heat_sample = self.glob_samp
        else:
            """comparing outliers"""
            x = x_lw if max(np.fabs(y_lw)) > max(np.fabs(y_uw)) else x_uw
            y = y_lw if max(np.fabs(y_lw)) > max(np.fabs(y_uw)) else y_uw

            heat_min = xmin_lw if max(np.fabs(y_lw)) > max(np.fabs(y_uw)) else xmin_uw
            heat_max = xmax_lw if max(np.fabs(y_lw)) > max(np.fabs(y_uw)) else xmax_uw

            """getting heat sample"""
            heat_sample = x[list(y).index(min(y))]

        """info part"""
        if info:
            print('lower_whisker', lower_whisker)
            print('upper_whisker', upper_whisker)
            print('count of lower outliers', len(self.raw_frame['heat_value'].values[lower_mask]))
            print('count of upper outliers', len(self.raw_frame['heat_value'].values[upper_mask]))
            print('heat_sample', heat_sample)

        """plot part"""
        if plot:
            if list(x_lw) != [0, 0]:
                plt.plot(x_lw, y_lw, label='x = {}'.format(xx))
            if list(x_uw) != [0, 0]:
                plt.plot(x_uw, y_uw, label='x = {}'.format(xx))
            plt.legend()
            plt.show()

        return heat_sample, heat_min, heat_max

    def __smooth_list_gaussian(self, list1, degree=5):
        window = degree * 2 - 1
        weight = np.array([1.0] * window)
        weightGauss = []
        for i in range(window):
            i = i - degree + 1
            frac = i / float(window)
            gauss = 1 / (np.exp((4 * (frac)) ** 2))
            weightGauss.append(gauss)
        weight = np.array(weightGauss) * weight
        smoothed = [0.0] * (len(list1) - window)
        for i in range(len(smoothed)):
            smoothed[i] = sum(np.array(list1[i:i + window]) * weight) / sum(weight)
        return np.array(smoothed)

    def __find_nearest_universal(self, arr, value):
        array = np.asarray(arr)
        idx = (np.abs(array - value)).argmin()
        return array[idx]

    def __find_min_max_y_on_(self, x, heat_sample, n_steps=10):

        if len(self.raw_frame[self.raw_frame.x_value == x].y_value) <= 0.7 * len(self.y_list):
            smooth_heat = self.__smooth_list_gaussian(self.raw_frame[self.raw_frame.x_value == x
                                                                     ].heat_value.values, degree=1)
        else:
            smooth_heat = self.__smooth_list_gaussian(self.raw_frame[self.raw_frame.x_value == x
                                                                     ].heat_value.values, degree=7)

        smooth_y = np.linspace(self.y_min, self.y_max, len(smooth_heat))

        idx = list(smooth_heat).index(self.__find_nearest_universal(smooth_heat, heat_sample))
        y_min = smooth_y[idx] - n_steps * self.y_step
        y_max = smooth_y[idx] + n_steps * self.y_step

        return y_min, y_max

    def __change_outlier_heatsamples(self):
        stdev = np.std(self.heat_samples)
        print(stats.mode(self.heat_samples))
        mode = stats.mode(self.heat_samples)[0][0]

        outliers_mask = np.abs(self.heat_samples - mode) > stdev

        self.heat_samples[outliers_mask] = np.mean(self.heat_samples[~outliers_mask])
        self.heat_mins[outliers_mask] = np.mean(self.heat_mins[~outliers_mask])
        self.heat_maxs[outliers_mask] = np.mean(self.heat_maxs[~outliers_mask])

    def __find_nearest(self, value):
        array = np.asarray(self.y_list)
        idx = (np.abs(array - value)).argmin()
        return array[idx]

    @property
    def interval(self):
        raw_len = len(self.raw_array[1, :])

        current_count = self.__find_nearest_universal(self.count_of_elements, raw_len)
        idx = list(self.count_of_elements).index(current_count)
        return self.timing[idx]
