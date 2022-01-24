# CFC filter
#
# Author: Martin Schachner
#
# Implementation according to Crash Analysis Criteria Description, v2.1.1
# -----------------------------------------------------------------------

import numpy as np
from scipy import signal


class CFC(object):
    def __init__(self, cfc, T):
        """

        Args:
            cfc: filter type can be (60, 180, 600, 1000)
            T: delta T of the sample  1/f should be checked according to :
        http://zone.ni.com/reference/en-XX/help/370859J-01/crash/misc_cfc/

        Returns:

        """

        assert(cfc in [13, 16, 60, 180, 600, 1000])

        wd = 2. * np.pi * cfc * 2.0775
        wa = np.sin(wd * T.magnitude / 2.) / np.cos(wd * T.magnitude / 2.)

        self._a0 = wa * wa / (1. + np.sqrt(2.) * wa + wa * wa)
        self._a1 = 2. * self._a0
        self._a2 = self._a0
        self._b1 = -2. * (wa**2 - 1.) / (1. + np.sqrt(2.) * wa + wa**2)
        self._b2 = (-1. + np.sqrt(2.) * wa - wa**2) / (1. + np.sqrt(2.) * wa + wa**2)

    def filter(self, sampled_array, time, mirroring_flag):
        """

        Args:
          sampled_array: param time:
          time_to_seconds_factor: param mirroring_flag:
          time: 
          mirroring_flag: 

        Returns:
          filtered signal according to the cfc parameter

        """

        # t = time[0, 0] + time[1:start_index][::-1] * -1
        # extended_time = np.vstack((t, time)).reshape(1, -1)
        # plt.plot(time, sampled_array[0,:])
        # plt.show()

        # 10 ms for data extension!
        #start_index = np.where(time > time[0] + .010 * self._units.ureg("ms"))
        start_index = np.where(time.to_base_units().magnitude > time[0].to_base_units().magnitude + 0.010) #np.where(time > time[0] + .010 * self._units.ureg("ms"))
        assert(len(start_index) > 0)
        start_index = start_index[0][0]

        # Data augmentation
        #  https://law.resource.org/pub/us/cfr/ibr/005/sae.j211-1.1995.pdf
        #
        # 1. pre-event data - mirror data on point of origin
        sampled_array_units = sampled_array.units
        sampled_array = np.array(sampled_array)
        duplicated = np.transpose(np.transpose(sampled_array[:, 1:start_index])[::-1]) * -1
        if mirroring_flag:
            mirroring = np.transpose(np.transpose(sampled_array[:, 1:start_index + 2])[::])
            temp = np.zeros((1, start_index))
            for index, value in enumerate(mirroring[0]):
                if index >= start_index:
                    break
                if index == 0:
                    temp[0][index] = value + (value - mirroring[0][index + 1])
                else:
                    temp[0][index] = temp[0][index - 1] + (value - mirroring[0][index + 1])
            temp = np.transpose(np.transpose(temp[:, 0:start_index])[::-1])

        data_prefix = temp if mirroring_flag else duplicated
        extended_data = np.append(data_prefix, sampled_array, axis=1)

        # t = time[0, 0] + time[1:start_index][::-1] * -1
        # extended_time = np.vstack((t, time)).reshape(1, -1)
        # plt.plot(extended_time[0], extended_data[0])

        # 2. post-event data
        # magnitude method to extend the data array
        # subtract the last values from the
        # x[n+1] = 2 * x[n] - x[n-1]
        # x[n+2] = 2 * x[n] - x[n-2]
        # x[n+3] = 2 * x[n] - x[n-3]
        # etc
        extended_data = np.array(extended_data)
        end_value = np.repeat(np.transpose(extended_data[:, -1]),
                              start_index, axis=0).reshape((sampled_array.shape[0], -1))

        last_n_data_values = sampled_array[:, -(start_index+1):-1]
        extension = 2 * end_value - last_n_data_values
        extended_data = np.append(extended_data, np.transpose(np.transpose(extension)[::-1]), axis=1)

        denominator = [1, -self._b1, -self._b2]
        numerator = [self._a0, self._a1, self._a2]
        output1 = signal.filtfilt(numerator, denominator, extended_data)

        return output1[:, start_index:start_index+time.shape[0]] * sampled_array_units

