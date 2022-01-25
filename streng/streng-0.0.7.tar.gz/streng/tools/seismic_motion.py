import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import integrate  # optimize, stats
from dataclasses import dataclass, field
from ..common.math.numerical import xy_with_endpoints
from ..common.io.output import OutputTable, OutputExtended
from ..common.io.lists_and_dicts_and_pandas_etc import convert_dict_to_quantity_value
from cached_property import cached_property # https://pypi.org/project/cached-property/


def NigamJennings(acc, periods, damping, dt):
    add_PGA = False
    if periods[0] == 0:
        periods = np.delete(periods, 0)
        add_PGA = True

    num_steps = len(acc)
    num_per = len(periods)
    omega = (2. * np.pi) / np.array(periods)
    omega2 = omega ** 2.
    omega3 = omega ** 3.
    omega_d = omega * math.sqrt(1.0 - (damping ** 2.))
    const = {'f1': (2.0 * damping) / (omega3 * dt),
             'f2': 1.0 / omega2,
             'f3': damping * omega,
             'f4': 1.0 / omega_d}
    const['f5'] = const['f3'] * const['f4']
    const['f6'] = 2.0 * const['f3']
    const['e'] = np.exp(-const['f3'] * dt)
    const['s'] = np.sin(omega_d * dt)
    const['c'] = np.cos(omega_d * dt)
    const['g1'] = const['e'] * const['s']
    const['g2'] = const['e'] * const['c']
    const['h1'] = (omega_d * const['g2']) - (const['f3'] * const['g1'])
    const['h2'] = (omega_d * const['g1']) + (const['f3'] * const['g2'])
    x_a, x_v, x_d = calculate_time_series(num_steps, num_per, acc, const, omega2, dt)

    spectrum = {'Sa': None,
                'Sv': None,
                'Sd': None,
                'T': None,
                'PSv': None,
                'PSa': None,
                'ASI': None,
                'VSI': None,
                'HI': None,
                'Tp': None}

    spectrum['Sa'] = np.max(np.fabs(x_a), axis=0)
    spectrum['Sv'] = np.max(np.fabs(x_v), axis=0)
    spectrum['Sd'] = np.max(np.fabs(x_d), axis=0)
    spectrum['PSv'] = spectrum['Sd'] * omega
    spectrum['PSa'] = spectrum['Sd'] * omega2
    spectrum['T'] = periods

    if add_PGA:
        pga = np.max(np.fabs(acc))
        periods = np.append(0, periods)
        spectrum['Sa'] = np.append(pga, spectrum['Sa'])
        spectrum['Sv'] = np.append(0, spectrum['Sv'])
        spectrum['Sd'] = np.append(0, spectrum['Sd'])
        spectrum['PSv'] = np.append(0, spectrum['PSv'])
        spectrum['PSa'] = np.append(pga, spectrum['PSa'])
        spectrum['T'] = periods

    xy_ASI = xy_with_endpoints(spectrum['T'], spectrum['Sa'], 0.1, 0.5)
    spectrum['ASI'] = integrate.trapz(xy_ASI[1], xy_ASI[0])

    xy_VSI = xy_with_endpoints(spectrum['T'], spectrum['Sv'], 0.1, 2.5)
    spectrum['VSI'] = integrate.trapz(xy_VSI[1], xy_VSI[0])

    xy_HI = xy_with_endpoints(spectrum['T'], spectrum['PSv'], 0.1, 2.5)
    spectrum['HI'] = integrate.trapz(xy_HI[1], xy_HI[0])

    spectrum['Tp'] = (float(np.where(spectrum['Sa'] == max(spectrum['Sa']))[0]) + 1) * (periods[1] - periods[0])

    return spectrum


def calculate_time_series(num_steps, num_per, acc, const, omega2, dt):
    """
    Calculates the acceleration, velocities and displacement time series for the SDOF oscillator

    Args:
        num_steps (int): number of input motion steps
        num_per (int): number of periods where values are calculated
        acc (np.array): acceleration values
        const (dict): constants of the algorithm
        omega2 (np.array): squared circular frequency
        dt (float): time increment

    Returns:
        tuple: a tuple containing x_a, x_v, x_d
            - x_a = Acceleration time series
            - x_v = Velocity time series
            - x_d = Displacement time series
    """

    x_d = np.zeros([num_steps - 1, num_per], dtype=float)
    x_v = np.zeros_like(x_d)
    x_a = np.zeros_like(x_d)

    for k in range(0, num_steps - 1):
        dug = acc[k + 1] - acc[k]
        z_1 = const['f2'] * dug
        z_2 = const['f2'] * acc[k]
        z_3 = const['f1'] * dug
        z_4 = z_1 / dt
        if k == 0:
            b_val = z_2 - z_3
            a_val = (const['f5'] * b_val) + (const['f4'] * z_4)
        else:
            b_val = x_d[k - 1, :] + z_2 - z_3
            a_val = (const['f4'] * x_v[k - 1, :]) + \
                    (const['f5'] * b_val) + (const['f4'] * z_4)

        x_d[k, :] = (a_val * const['g1']) + (b_val * const['g2']) + \
                    z_3 - z_2 - z_1
        x_v[k, :] = (a_val * const['h1']) - (b_val * const['h2']) - z_4
        x_a[k, :] = (-const['f6'] * x_v[k, :]) - (omega2 * x_d[k, :])

    return x_a, x_v, x_d

@dataclass
class Accelerogram:
    """ Acceleration record.

    Gets acceleration values and dt and calculates several motion parameters.

    Most properties are cached, there was no actual need for that since calculations do not really
    take such a long time. Used the `cached-property package <https://pypi.org/project/cached-property/>`_.

    .. uml::

        class Record {
        .. initialize attributes ..
        + accelerations: np.array
        + dt: float
        .. cached properties ..
        + steps
        + time_total
        + time
        + velocities
        + displacements
        + props
        + husid
        + husid_norm
        .. properties ..
        + output
        + plot_time_series
        .. classmethods - cunstructors ..
        + from_one_column_txt(filename, dt)
        + from_multi_column_txt(filename, dt, skip_header=0, skip_footer=0)
        + from_karakostas_acc(filename, direction)
        .. methods ..
        + significant_duration(start_percentage, end_percentage)

        }

    Attributes:
        accelerations (np.array): an array with the acceleration values. Units should be m/sec2
        dt (float): time increment

    """
    accelerations: np.array
    dt: float

    @classmethod
    def from_one_column_txt(cls, filename, dt, scale=1.0):
        """constructor that loads values from a single column text file"""
        accel = np.loadtxt(filename)
        return cls(dt=dt, accelerations=accel*scale)

    @classmethod
    def from_multi_column_txt(cls, filename, dt, scale=1.0, skip_header=0, skip_footer=0):
        """constructor that loads values from a multicolumn text file

            Args:
                filename: file to load
                dt: time increment
                skip_header (int): number of lines to skip at the beginning of the file
                skip_footer (int): number of lines to skip at the end of the file

        """
        accel = np.genfromtxt(fname=filename, skip_header=skip_header, skip_footer=skip_footer)
        return cls(dt=dt, accelerations=accel.flatten()*scale)

    @classmethod
    def from_athanassiadou_acc(cls, filename, direction, scale=0.01):
        """direction = 'L' or 'T' or 'V'"""
        f_df = pd.read_csv(filename, sep=r"\s+")
        dt = f_df['Time(s)'][1] - f_df['Time(s)'][0]
        col_name = 'Acc' + direction + '(cm/s2)'
        accel = np.array(f_df[col_name].tolist())
        return cls(dt=dt, accelerations=accel*scale)

    def significant_duration(self, start_percentage, end_percentage):
        # self.props['T_Arias5_95'] = self.significant_duration(0.05, 0.95)
        t_start = float(np.interp(start_percentage, self.husid_norm, self.time))
        t_end = float(np.interp(end_percentage, self.husid_norm, self.time))
        return t_end - t_start

    def get_spectra(self, damping, startT=0., endT=4., noTs=401):
        _spec = Spectra(accel=self.accelerations,
                        dt=self.dt)
        return _spec.get_spectra(damping, startT, endT, noTs)

    def show_parameters(self):
        paramlog = []
        paramlog.append('PGA = {:.4f}'.format(self.props['PGA']))
        paramlog.append('time for PGA = {:.4f}'.format(self.props['timePGA']))
        paramlog.append('PGV = {:.4f}'.format(self.props['PGV']))
        paramlog.append('time for PGV = {:.4f}'.format(self.props['timePGV']))
        paramlog.append('PGD = {:.4f}'.format(self.props['PGD']))
        paramlog.append('time for PGD = {:.4f}'.format(self.props['timePGD']))
        paramlog.append('PGV/PGA = {:.4f}'.format(self.props['PGVdivPGA']))
        paramlog.append('aRMS = {:.4f}'.format(self.props['aRMS']))
        paramlog.append('vRMS = {:.4f}'.format(self.props['vRMS']))
        paramlog.append('dRMS = {:.4f}'.format(self.props['dRMS']))
        paramlog.append('Arias Intensity Ia = {:.4f}'.format(self.props['Ia']))
        paramlog.append('Characteristic Intensity Ic = {:.4f}'.format(self.props['Ic']))
        paramlog.append('Specific Energy Density SED = {:.4f}'.format(self.props['SED']))
        paramlog.append('Cumulative Absolute Velocity CAV = {:.4f}'.format(self.props['CAV']))
        # paramlog.append('Significant duration (5-95% in Husid plot) = {:.4f}'.format(self.props['T_Arias5_95']))

        return '\n'.join(paramlog)


    def clear_cached_properties(self):
        del self.__dict__['steps']
        del self.__dict__['time_total']
        del self.__dict__['time']
        del self.__dict__['velocities']
        del self.__dict__['displacements']
        del self.__dict__['props']
        del self.__dict__['husid']
        del self.__dict__['husid_norm']

    @cached_property
    def steps(self):
        """int: number of steps"""
        return len(self.accelerations)

    @cached_property
    def time_total(self):
        """float: total time of the motion"""
        return (self.steps - 1) * self.dt

    @cached_property
    def time(self):
        """np.array: time values"""
        return np.arange(0., self.time_total + 1e-6, self.dt)

    @cached_property
    def velocities(self):
        """np.array: velocity values"""
        return self.dt * integrate.cumtrapz(self.accelerations, initial=0.)

    @cached_property
    def displacements(self):
        """np.array: displacement values"""
        return self.dt * integrate.cumtrapz(self.velocities, initial=0.)

    @cached_property
    def props(self):
        """dict: a dictionary with several input motion parameters"""
        _ppp = dict()

        _ppp['PGA'] = max(np.absolute(self.accelerations))
        _ppp['PGV'] = max(np.absolute(self.velocities))
        _ppp['PGD'] = max(np.absolute(self.displacements))
        _ppp['timePGA'] = float(np.where(np.absolute(self.accelerations) == _ppp['PGA'])[0][0]) * self.dt
        _ppp['timePGV'] = float(np.where(np.absolute(self.velocities) == _ppp['PGV'])[0][0]) * self.dt
        _ppp['timePGD'] = float(np.where(np.absolute(self.displacements) == _ppp['PGD'])[0][0]) * self.dt
        _ppp['PGVdivPGA'] = _ppp['PGV'] / _ppp['PGA']
        _ppp['aRMS'] = math.sqrt((1. / self.time_total) * integrate.trapz(self.accelerations * self.accelerations, self.time))
        _ppp['vRMS'] = math.sqrt(
            (1. / self.time_total) * integrate.trapz(self.velocities * self.velocities, self.time))
        _ppp['dRMS'] = math.sqrt(
            (1. / self.time_total) * integrate.trapz(self.displacements * self.displacements, self.time))
        _ppp['Ia'] = (math.pi / (2 * 9.81)) * integrate.trapz(self.accelerations * self.accelerations, self.time)
        _ppp['Ic'] = _ppp['aRMS'] ** 1.5 * math.sqrt(self.time_total)
        _ppp['SED'] = integrate.trapz(self.velocities * self.velocities, self.time)
        _ppp['CAV'] = integrate.trapz(np.absolute(self.accelerations), self.time)

        return _ppp

    @cached_property
    def husid(self):
        """np.array: values of the Husid plot"""
        return math.pi / (2 * 9.81) * integrate.cumtrapz(self.accelerations * self.accelerations, self.time, initial=0.)

    @cached_property
    def husid_norm(self):
        """np.array: values of the normalized Husid plot"""
        return self.husid / self.props['Ia']

    @property
    def output(self):
        """OutputExtended: A collection of output tables and strings

        Tables:
            - RecordMotionProperties
        """
        _output = OutputExtended()
        _output.outputTables['RecordMotionProperties'] = OutputTable()
        _output.outputTables['RecordMotionProperties'].data = convert_dict_to_quantity_value(self.props)

        return _output

    @property
    def plot_time_series(self):
        """Plots acc, vel, dipl vs time"""
        f, ax = plt.subplots(3, figsize=(14, 12))
        ax[0].plot(self.time, self.accelerations / 9.81, label="accelerations", lw=1, color='blue')
        ax[0].set_ylabel('acceleration (g)', fontsize=12)
        # ax[0].set_xlabel('time (sec)', fontsize=12)
        ax[0].legend(fontsize=12)
        ax[1].plot(self.time, self.velocities * 100, label="velocities", lw=1, color='green')
        ax[1].set_ylabel('velocity (cm/sec)', fontsize=12)
        # ax[1].set_xlabel('time (sec)', fontsize=12)
        ax[1].legend(fontsize=12)
        ax[2].plot(self.time, self.displacements * 100, label="displacements", lw=1, color='red')
        ax[2].set_ylabel('displacement (cm)', fontsize=12)
        ax[2].set_xlabel('time (sec)', fontsize=12)
        ax[2].legend(fontsize=12)
        fig = (f, ax)
        return fig

    def get_spectra(self, damping, startT=0., endT=4., noTs=401):
        T = np.linspace(startT, endT, noTs)
        # self.spectrum = NigamJennings(self.accelerations, T, damping, self.dt)
        return NigamJennings(self.accelerations, T, damping, self.dt)

    @staticmethod
    def show_spectra_parameters(spectrum):
        paramlog = []
        paramlog.append('Acceleration Spectrum Intensity: ASI = {:.4f}'.format(spectrum['ASI']))
        paramlog.append('Velocity Spectrum Intensity: VSI = {:.4f}'.format(spectrum['VSI']))
        paramlog.append('Housner Intensity: HI = {:.4f}'.format(spectrum['HI']))
        paramlog.append('Predominant Period: Tp = {:.4f}'.format(spectrum['Tp']))

        return '\n'.join(paramlog)





@dataclass
class Spectra:
    """ A class for calculating the response spectra using the Nigam Jennings approach.
    Adopted code found at the
    `The GEMScienceTools - Risk Modellers Toolkit (RMTK) <https://github.com/GEMScienceTools/rmtk>`_.

    .. uml::

        class Record {
        .. initialize attributes ..
        + accelerations: np.array
        + dt: float

        .. classmethods ..
        + calculate_time_series()
        + NigamJennings()

        .. staticmethods ..
        + show_spectra_parameters

        .. methods ..
        + get_spectra

        }

    Attributes:
        accelerations (np.array): an array with the acceleration values. Units should be m/sec2
        dt (float): time increment
    """
    accel: np.array  # = np.array([])
    dt: float  # = None

    @classmethod
    def calculate_time_series(cls, num_steps, num_per, acc, const, omega2, dt):
        """
        Calculates the acceleration, velocities and displacement time series for the SDOF oscillator

        Args:
            num_steps (int): number of input motion steps
            num_per (int): number of periods where values are calculated
            acc (np.array): acceleration values
            const (dict): constants of the algorithm
            omega2 (np.array): squared circular frequency
            dt (float): time increment

        Returns:
            tuple: a tuple containing x_a, x_v, x_d
                - x_a = Acceleration time series
                - x_v = Velocity time series
                - x_d = Displacement time series
        """

        x_d = np.zeros([num_steps - 1, num_per], dtype=float)
        x_v = np.zeros_like(x_d)
        x_a = np.zeros_like(x_d)

        for k in range(0, num_steps - 1):
            dug = acc[k + 1] - acc[k]
            z_1 = const['f2'] * dug
            z_2 = const['f2'] * acc[k]
            z_3 = const['f1'] * dug
            z_4 = z_1 / dt
            if k == 0:
                b_val = z_2 - z_3
                a_val = (const['f5'] * b_val) + (const['f4'] * z_4)
            else:
                b_val = x_d[k - 1, :] + z_2 - z_3
                a_val = (const['f4'] * x_v[k - 1, :]) + \
                        (const['f5'] * b_val) + (const['f4'] * z_4)

            x_d[k, :] = (a_val * const['g1']) + (b_val * const['g2']) + \
                        z_3 - z_2 - z_1
            x_v[k, :] = (a_val * const['h1']) - (b_val * const['h2']) - z_4
            x_a[k, :] = (-const['f6'] * x_v[k, :]) - (omega2 * x_d[k, :])

        return x_a, x_v, x_d

    @classmethod
    def NigamJennings(cls, acc, periods, damping, dt):
        add_PGA = False
        if periods[0] == 0:
            periods = np.delete(periods, 0)
            add_PGA = True

        num_steps = len(acc)
        num_per = len(periods)
        omega = (2. * np.pi) / np.array(periods)
        omega2 = omega ** 2.
        omega3 = omega ** 3.
        omega_d = omega * math.sqrt(1.0 - (damping ** 2.))
        const = {'f1': (2.0 * damping) / (omega3 * dt),
                 'f2': 1.0 / omega2,
                 'f3': damping * omega,
                 'f4': 1.0 / omega_d}
        const['f5'] = const['f3'] * const['f4']
        const['f6'] = 2.0 * const['f3']
        const['e'] = np.exp(-const['f3'] * dt)
        const['s'] = np.sin(omega_d * dt)
        const['c'] = np.cos(omega_d * dt)
        const['g1'] = const['e'] * const['s']
        const['g2'] = const['e'] * const['c']
        const['h1'] = (omega_d * const['g2']) - (const['f3'] * const['g1'])
        const['h2'] = (omega_d * const['g1']) + (const['f3'] * const['g2'])
        x_a, x_v, x_d = cls.calculate_time_series(num_steps, num_per, acc, const, omega2, dt)

        spectrum = {'Sa': None,
                    'Sv': None,
                    'Sd': None,
                    'T': None,
                    'PSv': None,
                    'PSa': None,
                    'ASI': None,
                    'VSI': None,
                    'HI': None,
                    'Tp': None}

        spectrum['Sa'] = np.max(np.fabs(x_a), axis=0)
        spectrum['Sv'] = np.max(np.fabs(x_v), axis=0)
        spectrum['Sd'] = np.max(np.fabs(x_d), axis=0)
        spectrum['PSv'] = spectrum['Sd'] * omega
        spectrum['PSa'] = spectrum['Sd'] * omega2
        spectrum['T'] = periods

        if add_PGA:
            pga = np.max(np.fabs(acc))
            periods = np.append(0, periods)
            spectrum['Sa'] = np.append(pga, spectrum['Sa'])
            spectrum['Sv'] = np.append(0, spectrum['Sv'])
            spectrum['Sd'] = np.append(0, spectrum['Sd'])
            spectrum['PSv'] = np.append(0, spectrum['PSv'])
            spectrum['PSa'] = np.append(pga, spectrum['PSa'])
            spectrum['T'] = periods

        xy_ASI = xy_with_endpoints(spectrum['T'], spectrum['Sa'], 0.1, 0.5)
        spectrum['ASI'] = integrate.trapz(xy_ASI[1], xy_ASI[0])

        xy_VSI = xy_with_endpoints(spectrum['T'], spectrum['Sv'], 0.1, 2.5)
        spectrum['VSI'] = integrate.trapz(xy_VSI[1], xy_VSI[0])

        xy_HI = xy_with_endpoints(spectrum['T'], spectrum['PSv'], 0.1, 2.5)
        spectrum['HI'] = integrate.trapz(xy_HI[1], xy_HI[0])

        spectrum['Tp'] = (float(np.where(spectrum['Sa'] == max(spectrum['Sa']))[0]) + 1) * (periods[1] - periods[0])

        return spectrum

    @staticmethod
    def show_spectra_parameters(spectrum):
        paramlog = []
        paramlog.append('Acceleration Spectrum Intensity: ASI = {:.4f}'.format(spectrum['ASI']))
        paramlog.append('Velocity Spectrum Intensity: VSI = {:.4f}'.format(spectrum['VSI']))
        paramlog.append('Housner Intensity: HI = {:.4f}'.format(spectrum['HI']))
        paramlog.append('Predominant Period: Tp = {:.4f}'.format(spectrum['Tp']))

        return '\n'.join(paramlog)

    def get_spectra(self, damping, startT=0., endT=4., noTs=401):
        T = np.linspace(startT, endT, noTs)
        # self.spectrum = NigamJennings(self.accelerations, T, damping, self.dt)
        return self.NigamJennings(self.accel, T, damping, self.dt)



