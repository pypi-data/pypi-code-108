import zhinst
import zhinst.ziPython
from drivers.M9290A import *
from drivers.N5183B import *
from drivers.znb_besedin import *
from resonator_tools import circlefit
from resonator_tools.circuit import notch_port

from fmn_datatools import TwoToneSpectroscopy, timer


class Tts(TwoToneSpectroscopy):

    def __init__(self,
                 *, x_min, x_max, nx_points, y_min, y_max, ny_points,
                 x_step, y_step,
                 fr_min: float, fr_max: float,
                 hdawg_port: str = '127.0.0.1', hdawg_port1: int = 8004, hdawg_port2: int = 6,
                 LO_port: str = 'TCPIP0::192.168.180.143::hislip0::INSTR',
                 LO_res_port: str = 'TCPIP0::192.168.180.134::inst0::INSTR',
                 hdawg_channel: int = 4, hdawg_setDouble: str = '/dev8210/sigouts/4/offset',
                 LO_set_power: int = 10,
                 LO_res_set_bandwidth: int = 20, LO_res_set_power: int = -20, LO_res_set_averages=1, LO_res_set_nop=101
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
        :param LO_set_power:
        :param LO_res_set_bandwidth:
        :param LO_res_set_power:
        :param LO_res_set_averages:
        """
        super().__init__(x_min=x_min, x_max=x_max, nx_points=nx_points, y_min=y_min, y_max=y_max, ny_points=ny_points,
                         x_step=x_step, y_step=y_step)
        self.fr_min = fr_min
        self.fr_max = fr_max

        # HDAWG init
        self.hdawg = zhinst.ziPython.ziDAQServer(hdawg_port, hdawg_port1, hdawg_port2)
        self.hdawg_setDouble = hdawg_setDouble
        # open HDAWG ZI
        hdawgModule = hdawg.awgModule()
        channel = hdawg_channel
        self.hdawg.setInt('/dev8210/sigouts/' + str(channel) + '/on', 1)

        # freq generator init
        self.LO = N5183B('N5183B', LO_port)  # cubit
        self.LO_res = Znb(LO_res_port)  # resonator

        self.LO_set_power = LO_set_power

        self.LO_res_set_nop = LO_res_set_nop
        self.LO_res_set_bandwidth = LO_res_set_bandwidth
        self.LO_res_set_power = LO_res_set_power

        pass

    @property
    def __find_resonator(self):

        lo1_status = self.LO.get_status()
        self.LO.set_status(0)
        self.LO_res.set_nop(self.LO_res_set_nop)

        bandwidth = self.LO_res.get_bandwidth()
        self.LO_res.set_bandwidth(self.LO_res_set_bandwidth)

        xlim = self.LO_res.get_freq_limits()

        self.LO_res.set_nop(self.LO_res_set_nop)
        self.LO_res.autoscale_all()
        self.LO_res.set_freq_limits(self.fr_min, self.fr_max)

        freqs = self.LO_res.get_freqpoints()
        S21s = self.LO_res.measure()['S-parameter']

        # measure S21
        notch = notch_port(freqs, S21s)
        notch.autofit(electric_delay=50e-9)
        result = notch.fitresults['fr']

        # перенастройка на следующей раунд измерений
        self.LO_res.set_nop(1)
        self.LO_res.set_bandwidth(bandwidth)
        self.LO_res.set_freq_limits(*xlim)
        self.LO_res.set_status(lo1_status)

        return result

    def run_measurements(self, *, x_key: Union[float, int, Iterable] = None, y_key: Union[float, int, Iterable] = None,
                         x_min=None, x_max=None, y_min=None, y_max=None,
                         sleep=0.03):

        self.iter_setup(x_key=x_key, y_key=y_key,
                        x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max)

        self.LO.set_power(self.LO_set_power)
        self.LO_res.set_power(self.LO_res_set_power)

        try:

            for i in range(len(self.load)):

                if (i == 0) or (self.load[i] != self.load[i - 1]):
                    self.LO_res.set_center(float(self.__find_resonator))

                self.hdawg.setDouble(self.hdawg_setDouble, self.load[i])  # Current write
                self.LO.set_frequency(self.frequency[i])  # Frequency write

                result = self.LO_res.measure()['S-parameter']

                self.write(x=self.load[i],
                           y=self.frequency[i],
                           heat=20*np.log10(abs(result)[0])
                           )
                timer.sleep(sleep)

        except KeyboardInterrupt:
            pass
