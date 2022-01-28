import numpy as np

from finesse.components.general import Connector
from finesse.components.workspace import ConnectorWorkspace
from finesse.components.node import NodeDirection, NodeType
from finesse.parameter import float_parameter


class FilterWorkspace(ConnectorWorkspace):
    pass


@float_parameter("gain", "Gain")
class Amplifier(Connector):
    def __init__(self, name, gain=1):
        super().__init__(name)
        self.gain = gain

        self._add_port("p1", NodeType.ELECTRICAL)
        self.p1._add_node("i", NodeDirection.INPUT)

        self._add_port("p2", NodeType.ELECTRICAL)
        self.p2._add_node("o", NodeDirection.OUTPUT)

        self._register_node_coupling("P1_P2", self.p1.i, self.p2.o)

    def _get_workspace(self, sim):
        if sim.signal:
            if self.p1.i.full_name not in sim.signal.nodes:
                return
            refill = sim.model.fsig.f.is_changing or any(
                p.is_changing for p in self.parameters
            )
            ws = FilterWorkspace(self, sim)
            ws.signal.add_fill_function(self.fill, refill)
            ws.frequencies = sim.signal.signal_frequencies[self.p1.i].frequencies
            return ws
        else:
            return None

    def fill(self, ws):
        if ws.signal.connections.P1_P2_idx > -1:
            for _ in ws.frequencies:
                with ws.sim.signal.component_edge_fill3(
                    ws.owner_id,
                    ws.signal.connections.P1_P2_idx,
                    0,
                    0,
                ) as mat:
                    mat[:] = ws.values.gain

    def eval(self, f):
        return float(self.gain)


@float_parameter("gain", "Gain")
class Filter(Connector):
    """This is a generic Filter element that encapsulates some of the Scipy signal
    filter tools. The `sys` attribute is the filter object which can be ZPK, BA, or SOS.

    Parameters
    ----------
    name : str
        Name of element in the model
    gain : Parameter
        Overall floating point value gain to apply to the filter.
    """

    def __init__(self, name, gain=1):
        super().__init__(name)
        self.gain = gain

        self._add_port("p1", NodeType.ELECTRICAL)
        self.p1._add_node("i", NodeDirection.INPUT)

        self._add_port("p2", NodeType.ELECTRICAL)
        self.p2._add_node("o", NodeDirection.OUTPUT)

        self._register_node_coupling("P1_P2", self.p1.i, self.p2.o)

    def _get_workspace(self, sim):
        if sim.signal:
            refill = sim.model.fsig.f.is_changing or any(
                p.is_changing for p in self.parameters
            )
            ws = FilterWorkspace(self, sim)
            ws.signal.add_fill_function(self.fill, refill)
            ws.frequencies = sim.signal.signal_frequencies[self.p1.i].frequencies
            return ws
        else:
            return None

    def fill(self, ws):
        Hz = self.eval(ws.sim.model_settings.fsig)
        if ws.signal.connections.P1_P2_idx > -1:
            for _ in ws.frequencies:
                with ws.sim.signal.component_edge_fill3(
                    ws.owner_id,
                    ws.signal.connections.P1_P2_idx,
                    0,
                    0,
                ) as mat:
                    mat[:] = Hz

    def bode_plot(self, f=None, n=None, return_axes=False):
        """Plots Bode for this filter.

        Parameters
        ----------
        f : optional
            Frequencies to plot for in Hz (Not radians)
        n : int, optional
            number of points to plot

        Returns
        -------
        axis : Matplotlib axis for plot if return_axes=True
        """
        import matplotlib.pyplot as plt
        import scipy
        import scipy.signal

        if f is not None:
            w = 2 * np.pi * f
        else:
            w = None

        # Need to make sure we are converting any symbolics to numerics before
        # handing over to scipy
        sys = (np.array(_, dtype=complex) for _ in self.sys)
        w, mag, phase = scipy.signal.bode(sys, n=n)

        fig, axs = plt.subplots(2, 1, sharex=True)
        axs[0].semilogx(w / 2 / np.pi, mag)
        axs[0].set_ylabel("Amplitude [dB]")

        axs[1].semilogx(w / 2 / np.pi, phase)
        axs[1].set_xlabel("Frequency [Hz]")
        axs[1].set_ylabel("Phase [Deg]")

        fig.suptitle(f"Bode plot for {self.name}")

        if return_axes:
            return axs


@float_parameter("gain", "Gain")
class ZPKFilter(Filter):
    """A zero-pole-gain filter element that is used for shaping signals in simulations.
    It is a two port element. `p1` is the input port and `p2` is the output port. Each
    one has a single node: `p1.i` and `p2.o`.

    Parameters
    ----------
    name : str
        Name of element in the model
    z : array_like[float | Symbols]
        A 1D-array of zeros. Use `[]` if none are required. By default these are provided
        in units of radians, not Hz.
    p : array_like[float | Symbols]
        A 1D-array of poles. Use `[]` if none are required. By default these are provided
        in units of radians, not Hz.
    k : [float | Symbol], optional
        Gain factor for the zeros and poles. If `None` then its value is automatically
        set to generate a unity gain at DC.
    fQ : bool, optional
        When True the zeros and poles can be specified in a tuple of
        (frequency, quality factor) for each pole and zero. This automatically
        adds the complex conjugate pair.
    gain : Parameter
        Overall gain for the filter. Differs from `k` as this is a `Parameter` so
        can be easily switched on/off or varied during a simulation.

    Examples
    --------
    Below are a few examples of using a ZPK filter in a simple simulation and
    plotting the output.

    >>> import finesse
    >>> finesse.init_plotting()
    >>> model = finesse.Model()
    >>> model.parse(\"\"\"
    ... # Finesse always expects some optics to be present
    ... # so we make a laser incident on some photodiode
    ... l l1 P=1
    ... readout_dc PD l1.p1.o
    ... # Amplitude modulate a laser
    ... sgen sig l1.amp
    ...
    ... zpk ZPK_unity [] []
    ... link(PD.DC, ZPK_unity)
    ... ad unity ZPK_unity.p2.o f=&fsig
    ...
    ... zpk ZPK_1 [] [-10*2*pi]
    ... link(PD.DC, ZPK_1)
    ... ad zpk1 ZPK_1.p2.o f=&fsig
    ...
    ... zpk ZPK_2 [-10*2*pi] []
    ... link(PD.DC, ZPK_2)
    ... ad zpk2 ZPK_2.p2.o f=&fsig
    ...
    ... # Using symbolics
    ... variable a 20*2*pi
    ... zpk ZPK_symbol [] [-1j*&a, 1j*&a] -1
    ... link(PD.DC, ZPK_symbol)
    ... ad symbol ZPK_symbol.p2.o f=&fsig
    ...
    ... # Using gain parameter instead of k keeps the unity response at DC but
    ... # just flips the sign
    ... zpk ZPK_symbol2 [] [-1j*&a, 1j*&a] gain=-1
    ... link(PD.DC, ZPK_symbol2)
    ... ad symbol_gain ZPK_symbol2.p2.o f=&fsig
    ...
    ... # Symbolics for an RC low pass filter
    ... variable R 100
    ... variable C 10u
    ... zpk ZPK_RC [] [-1/(&R*&C)]
    ... link(PD.DC, ZPK_RC)
    ... ad RC ZPK_RC.p2.o f=&fsig
    ...
    ... fsig(1)
    ... xaxis(fsig, log, 0.1, 10k, 1000)
    ... \"\"\")

    >>> sol = model.run()
    >>> sol.plot(log=True)
    """

    def __init__(self, name, z, p, k=None, *, fQ=False, gain=1):
        super().__init__(name, gain)
        import cmath

        if k is None:
            k = np.prod(np.abs(p)) / np.prod(np.abs(z))

        root = lambda f, Q: -2 * np.pi * f / (2 * Q) + cmath.sqrt(
            (2 * np.pi * f / (2 * Q)) ** 2 - (2 * np.pi * f) ** 2
        )

        if fQ:
            self.z = []
            for f, Q in z:
                r = root(f, Q)
                self.z.append(r)
                self.z.append(r.conjugate())

            self.p = []
            for f, Q in p:
                r = root(f, Q)
                self.p.append(r)
                self.p.append(r.conjugate())
        else:
            self.z = z
            self.p = p
        self.k = k

    @property
    def sys(self):
        """The scipy `sys` object.

        In this case it is a tuple of (zeros, poles, k). This does not convert any
        symbolics used into numerics.
        """
        return (self.z, self.p, self.k * self.gain)

    def eval(self, f):
        """Calculate the value of this filter over some frequencies.

        Parameters
        ----------
        f : array_like
            Frequencies in units of Hz

        Returns
        -------
        H : array_like
            Complex valued filter output
        """
        import scipy.signal as signal

        return float(self.gain) * signal.freqs_zpk(
            np.array(self.z, dtype=complex),
            np.array(self.p, dtype=complex),
            float(self.k),
            2 * np.pi * f,
        )[1]


@float_parameter("gain", "Gain")
class ButterFilter(ZPKFilter):
    def __init__(self, name, order, btype, frequency, *, gain=1, analog=True):
        super().__init__(name, [], [], [], gain=gain)
        self.__order = order
        self.__btype = btype
        self.__analog = analog
        self.__frequency = frequency
        self.set_zpk()

    def set_zpk(self):
        import scipy.signal as signal

        z, p, k = signal.butter(
            self.order,
            2 * np.pi * np.array(self.frequency),
            btype=self.btype,
            analog=self.analog,
            output="zpk",
        )
        self.z = z
        self.p = p
        self.k = k

    @property
    def frequency(self):
        return self.__frequency

    @frequency.setter
    def frequency(self, value):
        self.__frequency = value
        self.set_zpk()

    @property
    def order(self):
        return self.__order

    @order.setter
    def order(self, value):
        self.__order = value
        self.set_zpk()

    @property
    def btype(self):
        return self.__btype

    @btype.setter
    def btype(self, value):
        self.__btype = value
        self.set_zpk()

    @property
    def analog(self):
        return self.__analog

    @analog.setter
    def analog(self, value):
        self.__analog = value
        self.set_zpk()


@float_parameter("gain", "Gain")
class Cheby1Filter(ZPKFilter):
    def __init__(self, name, order, rp, btype, frequency, *, gain=1, analog=True):
        import scipy.signal as signal

        zpk = signal.cheby1(
            order,
            rp,
            2 * np.pi * np.array(frequency),
            btype=btype,
            analog=analog,
            output="zpk",
        )
        super().__init__(name, *zpk, gain=gain)
