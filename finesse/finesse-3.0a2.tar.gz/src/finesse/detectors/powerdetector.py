"""Computes the laser power in an interferometer output or the power from an electrical
signal."""

import logging

import numpy as np
from finesse.components.node import Node
from finesse.detectors import pdtypes
from finesse.detectors.general import MaskedDetector
from finesse.parameter import float_parameter

LOGGER = logging.getLogger(__name__)


@float_parameter("f", "Frequency")
@float_parameter("phase", "Phase")
class PowerDetectorDemod1(MaskedDetector):
    """Represents a power detector with one RF demodulation. It calculates the RF beat
    power at a node in Watts of optical power.

    If no demodulation phase is specified then this detector outputs a
    complex value `I+1j*Q`.

    Parameters
    ----------
    name : str
        Name of newly created power detector.

    node : :class:`.Node`
        Node to read output from.

    f : float
        Demodulation frequency in Hz

    phase : float, optional
        Demodulation phase in degrees
    """

    def __init__(self, name: str, node: Node, f, phase=None, pdtype=None):
        self.pdtype = pdtypes.get_pdtype(pdtype)

        if f is None:
            raise ValueError("A demodulation frequency must be provided")

        if phase is not None:
            self.__mode = "mixer_real"
            dtype = np.float64
        else:
            self.__mode = "mixer_complex"
            dtype = np.complex128

        self._beats = None

        MaskedDetector.__init__(self, name, node, dtype=dtype, unit="W", label="Power")
        self.f = f
        self.phase = phase

    def _get_workspace(self, sim):
        from finesse.detectors.compute.power import PD1Workspace

        return PD1Workspace(self, sim, self.f, self.phase, pdtype=self.pdtype)


@float_parameter("f1", "Frequency 1")
@float_parameter("phase1", "Phase 1")
@float_parameter("f2", "Frequency 2")
@float_parameter("phase2", "Phase 2")
class PowerDetectorDemod2(MaskedDetector):
    """Represents a power detector with two RF demodulation. It calculates the RF beat
    power at a node in Watts of optical power.

    If no demodulation phase is specified for the final demodulation
    this detector outputs a complex value `I+1j*Q` where I and Q are
    the in-phase and quadrature parts of the signal.

    Parameters
    ----------
    name : str
        Name of newly created power detector.

    node : :class:`.Node`
        Node to read output from.

    f1 : float
        First demodulation frequency in Hz

    phase1 : float
        First demodulation phase in degrees

    f2 : float
        Second demodulation frequency in Hz

    phase2 : float, optional
        Second demodulation phase in degrees
    """

    def __init__(self, name: str, node: Node, f1, phase1, f2, phase2=None, pdtype=None):
        self.pdtype = pdtypes.get_pdtype(pdtype)

        if phase2 is not None:
            self.__mode = "mixer_real"
            dtype = np.float64
        else:
            self.__mode = "mixer_complex"
            dtype = np.complex128

        self._beats = None

        MaskedDetector.__init__(self, name, node, dtype=dtype, unit="W", label="Power")
        self.f1 = f1
        self.phase1 = phase1
        self.f2 = f2
        self.phase2 = phase2

    def _get_workspace(self, sim):
        from finesse.detectors.compute.power import PD2Workspace

        return PD2Workspace(
            self, sim, self.f1, self.phase1, self.f2, self.phase2, pdtype=self.pdtype
        )


class PowerDetector(MaskedDetector):
    """Represents a power detector with no RF demodulations. It calculates the DC laser
    power at a node in Watts of optical power.

    Parameters
    ----------
    name : str
        Name of newly created power detector.

    node : :class:`.Node`
        Node to read output from.
    """

    def __init__(self, name: str, node: Node, *, pdtype=None):
        MaskedDetector.__init__(
            self, name, node, dtype=np.float64, unit="W", label="Power"
        )
        self.pdtype = pdtypes.get_pdtype(pdtype)

    def _get_workspace(self, sim):
        from finesse.detectors.compute.power import PD0Workspace

        return PD0Workspace(self, sim, pdtype=self.pdtype)
