import zhinst
import zhinst.ziPython
from drivers.M9290A import *
from drivers.N5183B import *
from drivers.znb_besedin import *
from resonator_tools import circlefit
from resonator_tools.circuit import notch_port

from pyquac.fmn_datatools import TwoToneSpectroscopy, timer

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

class Tts(TwoToneSpectroscopy):

    def __init__(self,
                 *, x_min, x_max, y_min, y_max,
                 fr_min: float, fr_max: float,
                 hdawg_port: str = '127.0.0.1', hdawg_port1: int = 8004, hdawg_port2: int = 6,
                 LO_port: str = 'TCPIP0::192.168.180.143::hislip0::INSTR',
                 LO_res_port: str = 'TCPIP0::192.168.180.110::inst0::INSTR',
                 hdawg_channel: int = 5, hdawg_setDouble: str = '/dev8210/sigouts/5/offset',
                 LO_set_power: int = 5,
                 LO_res_set_bandwidth: int = 20, LO_res_set_power: int = -10, LO_res_set_nop=101,
                 base_bandwidth=40, nx_points = None, x_step=None, y_step=None, ny_points=None
                 ):
        """
        Class provides methods for working with live data for Two Tone Spectroscopy
        :param x_min: x minimum value (int | float)
        :param x_max: x maximum value (int | float)
        :param nx_points: x count value (int)
        :param y_min: y minimum value (int | float)
        :param y_max: y maximum value (int | float)
        :param ny_points: y count value (int)

        :param fr_min: min frequency for find resonator
        :param fr_max: max frequency for find resonator
        :param hdawg_port: hdawg = zhinst.ziPython.ziDAQServer(hdawg_port, hdawg_port1, hdawg_port2)
        :param hdawg_port1: hdawg = zhinst.ziPython.ziDAQServer(hdawg_port, hdawg_port1, hdawg_port2)
        :param hdawg_port2: hdawg = zhinst.ziPython.ziDAQServer(hdawg_port, hdawg_port1, hdawg_port2)
        :param LO_port: qubit LO = N5183B('N5183B', LO_port)
        :param LO_res_port: resonator LO_res = Znb(LO_res_port)
        :param hdawg_channel: hdawg.setInt('/dev8210/sigouts/' + str(channel) + '/on', 1)
        :param LO_set_power: base LO power (default 5)
        :param LO_res_set_bandwidth: bandwidth during resonator tuning
        :param LO_res_set_power: base LO_res power (default -10)
        :param base_bandwidth: (int) bandwidth during mesurments
        """
        super().__init__(x_min=x_min, x_max=x_max, nx_points=nx_points, y_min=y_min, y_max=y_max, ny_points=ny_points,
                         x_step=x_step, y_step=y_step)
        self.fr_min = fr_min
        self.fr_max = fr_max

        # HDAWG init
        self.hdawg = zhinst.ziPython.ziDAQServer(hdawg_port, hdawg_port1, hdawg_port2)
        self.hdawg_setDouble = hdawg_setDouble
        # open HDAWG ZI
        hdawgModule = self.hdawg.awgModule()
        channel = hdawg_channel
        self.hdawg.setInt('/dev8210/sigouts/' + str(channel) + '/on', 1)

        # freq generator init
        self.LO = N5183B('N5183B', LO_port)  # cubit
        self.LO_res = Znb(LO_res_port)  # resonator

        self.LO_set_power = LO_set_power

        self.LO_res_set_nop = LO_res_set_nop
        self.LO_res_set_bandwidth = LO_res_set_bandwidth
        self.LO_res_set_power = LO_res_set_power
        self.base_bandwidth = base_bandwidth

        pass

    @property
    def __find_resonator(self):

        self.LO.set_status(0)

        # prior bandwidth
        bandwidth = self.LO_res.get_bandwidth()
        xlim = self.LO_res.get_freq_limits()

        self.LO_res.set_bandwidth(self.LO_res_set_bandwidth)
        self.LO_res.set_nop(self.LO_res_set_nop)
        self.LO_res.set_freq_limits(self.fr_min, self.fr_max)

        # measure S21
        freqs = self.LO_res.get_freqpoints()
        notch = notch_port(freqs, self.LO_res.measure()['S-parameter'])
        notch.autofit(electric_delay=60e-9)
        result = round(notch.fitresults['fr'])

        # Resetting to the next round of measurements
        self.LO_res.set_bandwidth(bandwidth)
        self.LO_res.set_freq_limits(*xlim)
        self.LO_res.set_nop(1)
        self.LO.set_status(1)

        return result

    def run_measurements(self, *, x_key: Union[float, int, Iterable] = None, y_key: Union[float, int, Iterable] = None,
                         x_min=None, x_max=None, y_min=None, y_max=None,
                         sleep=0.007, timeout=None):

        self.iter_setup(x_key=x_key, y_key=y_key,
                        x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max)

        # Set power
        self.LO.set_power(self.LO_set_power)
        self.LO_res.set_power(self.LO_res_set_power)
        # base bandwidth
        self.LO_res.set_bandwidth(self.base_bandwidth)
        try:
            for i in range(len(self.load)):
                if (i == 0) or (self.load[i] != self.load[i - 1]):
                    self.LO_res.set_center(float(self.__find_resonator))
                    if timeout is not None:
                        timer.sleep(timeout)
                    else:
                        pass

                self.hdawg.setDouble(self.hdawg_setDouble, self.load[i])  # Current write
                self.LO.set_frequency(self.frequency[i])  # Frequency write

                result = self.LO_res.measure()['S-parameter']

                self.write(x=self.load[i],
                           y=self.frequency[i],
                           heat=20 * np.log10(abs(result)[0])
                           )
                timer.sleep(sleep)

            self.LO.set_status(0)
        except KeyboardInterrupt:
            pass
