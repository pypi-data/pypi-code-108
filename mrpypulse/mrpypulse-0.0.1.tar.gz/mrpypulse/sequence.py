""" This module contains the class Sequence."""

import os
import copy

import numpy as np
import matplotlib.pyplot as plt

from . import pulse
from .magnetization import simulate, magn_phase, plot_magn


def pc_rec(phase_cycles, ctp):
    """
    Computes receiver phase

    Parameters
    ----------
    phase_cyles: numpy array of floats
        array containing the phase cycle of each pulse on its line
    ctp: 1D-numpy array of floats
        vector containing the coherence transfer pathway of the pulses

    Returns
    -------
    ph_rec
        array containing the phase cycle of the receiver

    example: 90  -  180 - 180 - detection

    ctp = [-1, +2, -2]
    +1                 ******
    0 **********      *      *
    -1          ******        *************

    ph_pulses = [ph1, ph2, ph3]

    ph1 =    0 0 0 0 0 0 0 0 2 2 2 2 2 2 2 2
    ph2 =    0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1
    ph3 =    0 0 1 1 2 2 3 3 0 0 1 1 2 2 3 3
    ph_rec = 0 2 2 0 0 2 2 0 2 0 0 2 2 0 0 2
    """
    if len(phase_cycles) != len(ctp):
        raise IndexError("ctp list length not equal to number of pulses")

    ph_rec = np.zeros(len(phase_cycles[0]))

    for i, elem in enumerate(phase_cycles):
        ph_rec += elem * ctp[i]

    ph_rec = ph_rec % 4  # modulation

    return ph_rec.astype(int)


class Sequence:

    """
    Class representing a pulse sequence
    """

    def __init__(self, pulses, total_time=None, pc=None, ID=None):
        """
        Parameters
        ----------
        pulses: list of pulse objects
            the pulses of the sequence
        total_time: float
            Total duration of the sequence (s)
        pc: numpy array of floats
            phase cycling tables of the sequence
        """
        if ID is not None:
            self.ID = ID
        else:
            self.ID = 'unnamed_seq'

        self.pulses = pulses

        if total_time is None:
            self.total_time = pulses[-1].end
        else:
            if total_time >= pulses[-1].end:
                self.total_time = total_time
            else:
                raise ValueError('total_time should be longer than the last'
                                 ' pulse end.')

        self.w1max = 0
        for p in pulses:
            if self.w1max < p.w1:
                self.w1max = p.w1

        if pc is not None:
            self.pc = pc

    def __eq__(self, seq):
        """
        Parameters
        ----------
        seq: Sequence object
            sequence to compare
        Returns
        True/False: boolean

        2 sequences are considered equal if they have the same total duration,
        the same pulses and all of their pulses are placed at the same
        position.
        """

        if self.total_time != seq.total_time:
            return False

        if self.pulses != seq.pulses:
            return False

        for p1, p2 in zip(self.pulses, seq.pulses):
            if p1.start != p2.start:
                return False

        return True

    def insert(self, position, elem):
        """
        Parameters
        ----------
        elem: pulse object or float
            element to insert in the sequence (pulse or delay)
        position: int
            where the pulse/delay should be inserted in the pulse list
        """
        if isinstance(elem, pulse.Pulse):

            # insert pulse in pulses list
            if position == len(self.pulses):
                elem.start = self.pulses[-1].end
            else:
                elem.start = self.pulses[position].start
            self.pulses.insert(position, elem)

            # pulses position shift
            for i in range(len(self.pulses)):
                if i > position:
                    self.pulses[i].start += elem.tp

            self.total_time += elem.tp

            if self.w1max < elem.w1:
                self.w1max = elem.w1

        elif isinstance(elem, float):  # delay case

            # pulses position shift
            for i in range(len(self.pulses)):
                if i >= position:
                    self.pulses[i].start += elem

            # update total time
            self.total_time += elem

    def append(self, elem):
        """
        Parameters
        ----------
        elem: pulse object or float
            element to insert in the sequence (pulse or delay in s)
        """
        self.insert(len(self.pulses), elem)

    def pulses_sum(self):
        """
        Returns the sum of the sequence pulses
        """
        return sum(self.pulses)

    def plot(self):
        """
        Plots the sequence pulses
        """
        p = sum(self.pulses)

        # potential initial delay
        if not np.isclose(0, self.pulses[0].start, rtol=1e-6, atol=1e-15):
            delay = pulse.NoPulse(tp=self.pulses[0].start,
                                  tres=self.tres, start=0)
            p += delay

        # potential final delay
        if not np.isclose(p.tp, self.total_time, rtol=1e-6, atol=1e-15):
            delay = pulse.NoPulse(tp=self.total_time - p.tp,
                                  tres=self.tres, start=p.tp)
            p += delay

        p.plot()
        plt.xlim(0, self.total_time)

    def seq2topspin(self, path=None):
        """
         Export sequence to folder of name self.ID containing TopSpin shape
         files

        Parameters
        ----------
        path: string
            where the folder with the .shp files is created, default is
            current directory
        """
        if path is None:
            path = os.getcwd()
        path = os.path.join(path, self.ID)

        # create folder to store shape files
        if not os.path.exists(path):
            os.mkdir(path)

        # export pulse shapes
        for p in self.pulses:
            p.topspin_file(path)

    def seq2xepr(self, path=None, shp_nb=400):
        """
        Export sequence to folder of name self.ID containing Xepr shape files

        Parameters
        ----------
        shp_nb: int
            shape number used for file names and number
        path: string
            where the folder with the .shp files is created, default is
            current directory

        Generates the shape with 4 different phase for possible phase cycling
        (0, pi/2, pi, 3*pi/4).
        """
        if path is None:
            path = os.getcwd()
        path = os.path.join(path, self.ID)

        # create folder to store .shp files
        if not os.path.exists(path):
            os.mkdir(path)

        # export pulse shape files
        pulses = copy.deepcopy(self.pulses)
        shp_paths = []
        for p in pulses:

            for phi0 in [0., np.pi/2, np.pi, 3*np.pi/2]:

                p.phi0 = phi0  # add phase cycle
                p.xepr_file(shp_nb, path)

                # add shape file name to shp_paths
                shp_paths.append(os.path.join(
                                 path, str(shp_nb) + '.shp'))
                shp_nb += 1

        shps_path = os.path.join(path, str(shp_nb) + '_merged.shp')

        # merge shape files together
        with open(shps_path, 'w') as merged_file:
            for names in shp_paths:
                with open(names) as infile:
                    merged_file.write(infile.read())


class Exc_3fs(Sequence):

    """
    Class representing an excitation from 3 frequency-swept pulses (CHORUS,
                                                                   ABSTRUSE)
    Parameters
    ----------
    t90min
        minimal excitation pulse duration (s)
    t180min
        minimal refocusing pulse duration (s)
    bw
        bandwidth of the sequence (Hz)
    tres
        time resolution of the sequence (s)
    Q_exc
        adiabaticity factor of the excitation pulse (default, 0.441)
    Q_ref
        adiabaticity factor of the refocusing pulses (default, 5)
    pulse_args
    t_del: float
        delay used to extend the sequence duration, placed before and after the
        last pulse
    polyfit: boolean
        to apply polynomial fitting of the phase
    polyfit_args: dict
        polynomial fitting parameters (cf. pulse.Parametrized.add_ph_polyfit())
    plot: boolean
        to plot the sequence, its simulatin and potential polynomial fitting
        operation
    ID: string
        cf. Sequence (default 'exc_3fs')
    """

    def __init__(self, t90min, t180min, bw, tres,
                 Q_exc=0.4412712003053, Q_ref=5, pulse_args={}, t_del=0,
                 polyfit=False, polyfit_args={},
                 plot=False, ID='exc_3fs'):

        p1 = pulse.Parametrized(tp=t90min, bw=bw, Q=Q_exc,
                                tres=tres, ID='p1', **pulse_args)
        p2 = pulse.Parametrized(tp=t180min+t90min/2, bw=bw, Q=Q_ref,
                                tres=tres, ID='p2', start=t90min, **pulse_args)
        p3 = pulse.Parametrized(tp=t180min, bw=bw, Q=Q_ref, tres=tres, ID='p3',
                                start=p2.end + t90min/2 + t_del, **pulse_args)

        pulses = [p1, p2, p3]

        pc1 = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        pc2 = np.array([0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3])
        pc3 = np.array([0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3])

        pc31 = pc_rec([pc1, pc2, pc3], [-1, +2, -2])

        # pc31 = np.array([0, 2, 0, 2, 2, 0, 2, 0, 0, 2, 0, 2, 2, 0, 2, 0])
        pc = np.pi/2*np.stack((pc1, pc2, pc3, pc31))

        if polyfit:
            limit = 0.5*pulses[0].bw
            off = np.linspace(-0.5*pulses[0].bw+p1.delta_f,
                              0.5*pulses[0].bw+p1.delta_f, 51)
            magn = simulate(pulses, off, pc=pc)

            if plot:
                plot_magn(magn, off)

            p1.add_ph_polyfit(magn_phase(magn), **polyfit_args, plot=plot)

        Sequence.__init__(self, pulses, total_time=p3.end+t_del, pc=pc, ID=ID)

        self.t90min = t90min
        self.t180min = t180min
        self.bw = bw
        self.tres = tres
        self.Q_exc = Q_exc
        self.Q_ref = Q_ref
        self.pulse_args = pulse_args
        self.t_del = t_del
        self.polyfit = polyfit
        self.polyfit_args = polyfit_args

        if plot:
            limit = 0.5*pulses[0].bw
            off = np.linspace(-limit, limit, 100)
            magn = simulate(self.pulses, off, pc=self.pc)

            plot_magn(magn, off)

            plt.figure()
            self.plot()
