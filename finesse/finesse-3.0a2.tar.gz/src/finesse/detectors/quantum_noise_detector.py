"""
Photodiode quantum noise detector.
"""

import numpy as np
from finesse.detectors.compute.quantum import (
    QND0Workspace,
    QNDNWorkspace,
    QShot0Workspace,
    QShotNWorkspace,
    QuantumNoiseDetectorWorkspace,
)
from finesse.detectors.general import Detector, NoiseDetector
from finesse.components.general import NoiseType
from finesse.parameter import float_parameter


class QuantumNoiseDetector(Detector, NoiseDetector):
    """
    Represents a quantum noise detector with no RF demodulations.

    It calculates the amplitude spectral density of the photocurrent
    noise of a photodiode output demodulated at the signal frequency.

    Parameters
    ----------
    name : str
        Name of newly created quantum noise detector.

    node : :class:`.Node`
        Node to read output from.

    nsr : bool, optional
        If true, calculate the noise-to-signal ratio rather than the absolute
        noise value.

    sources : list of :class:`.Connector`, optional
        If given, only detect quantum noise contributions from these components.

    exclude_sources : list of :class:`.Connector`, optional
        If given, don't detect quantum noise contributions from any of
        these components, even if given in `sources`.
    """

    def __init__(self, name, node, nsr=False, sources=None, exclude_sources=None):
        Detector.__init__(
            self, name, node, dtype=np.float64, unit="1/sqrt(Hz)", label="ASD"
        )
        NoiseDetector.__init__(self, NoiseType.QUANTUM)

        self.nsr = nsr
        self.sources = sources
        self.exclude_sources = exclude_sources

        self._request_selection_vector(name)

    def _has_sources(self):
        return self.sources is not None or self.exclude_sources is not None

    def _get_workspace(self, sims):
        ws = QND0Workspace(self, sims, self.nsr, self.sources, self.exclude_sources)
        return ws


@float_parameter("f", "Frequency")
@float_parameter("phase", "Phase")
class QuantumNoiseDetectorDemod1(Detector, NoiseDetector):
    """
    Represents a quantum noise detector with 1 RF demodulation.

    It calculates the amplitude spectral density of the photocurrent
    noise of a photodiode output demodulated at the signal frequency.

    Parameters
    ----------
    name : str
        Name of newly created quantum noise detector.

    node : :class:`.Node`
        Node to read output from.

    f : float
        Demodulation frequency in Hz

    phase : float
        Demodulation phase in degrees

    nsr : bool, optional
        If true, calculate the noise-to-signal ratio rather than the absolute
        noise value.

    sources : list of :class:`.Connector`, optional
        If given, only detect quantum noise contributions from these components.
    """

    def __init__(
        self, name, node, f, phase, nsr=False, sources=None, exclude_sources=None
    ):
        Detector.__init__(
            self, name, node, dtype=np.float64, unit="1/sqrt(Hz)", label="ASD"
        )
        NoiseDetector.__init__(self, NoiseType.QUANTUM)

        self.f = f
        self.phase = phase
        self.nsr = nsr
        self.sources = sources
        self.exclude_sources = exclude_sources

        self._request_selection_vector(name)

    def _has_sources(self):
        return self.sources is not None or self.exclude_sources is not None

    def _get_workspace(self, sims):
        ws = QNDNWorkspace(self, sims, 1, self.nsr, self.sources, self.exclude_sources)
        return ws


@float_parameter("f1", "Frequency")
@float_parameter("f2", "Frequency")
@float_parameter("phase1", "Phase")
@float_parameter("phase2", "Phase")
class QuantumNoiseDetectorDemod2(Detector, NoiseDetector):
    """
    Represents a quantum noise detector with 2 RF demodulations.

    It calculates the amplitude spectral density of the photocurrent
    noise of a photodiode output demodulated at the signal frequency.

    Parameters
    ----------
    name : str
        Name of newly created quantum noise detector.

    node : :class:`.Node`
        Node to read output from.

    f1 : float
        First demodulation frequency in Hz

    phase1 : float
        First demodulation phase in degrees

    f2 : float
        Second demodulation frequency in Hz

    phase2 : float
        Second demodulation phase in degrees

    nsr : bool, optional
        If true, calculate the noise-to-signal ratio rather than the absolute
        noise value.

    sources : list of :class:`.Connector`, optional
        If given, only detect quantum noise contributions from these components.
    """

    def __init__(
        self,
        name,
        node,
        f1,
        phase1,
        f2,
        phase2,
        nsr=False,
        sources=None,
        exclude_sources=None,
    ):
        Detector.__init__(
            self, name, node, dtype=np.float64, unit="1/sqrt(Hz)", label="ASD"
        )
        NoiseDetector.__init__(self, NoiseType.QUANTUM)

        self.f1 = f1
        self.f2 = f2
        self.phase1 = phase1
        self.phase2 = phase2
        self.nsr = nsr
        self.sources = sources
        self.exclude_sources = exclude_sources

        self._request_selection_vector(name)

    def _has_sources(self):
        return self.sources is not None or self.exclude_sources is not None

    def _get_workspace(self, sims):
        ws = QNDNWorkspace(self, sims, 2, self.nsr, self.sources, self.exclude_sources)
        return ws


class QuantumShotNoiseDetector(Detector):
    """
    Represents a quantum shot noise detector with no RF demodulations.

    It calculates the amplitude spectral density of the photocurrent
    noise of a photodiode output demodulated at the signal frequency,
    considering only vacuum noise contributions (ignoring radiation
    pressure and squeezing effects).

    Parameters
    ----------
    name : str
        Name of newly created quantum shot noise detector.

    node : :class:`.Node`
        Node to read output from.

    nsr : bool, optional
        If true, calculate the noise-to-signal ratio rather than the absolute
        noise value.
    """

    def __init__(self, name, node, nsr=False):
        self.nsr = nsr

        Detector.__init__(
            self, name, node, dtype=np.float64, unit="W/sqrt(Hz)", label="ASD"
        )

    def _get_workspace(self, sims):
        ws = QShot0Workspace(self, sims, self.nsr)
        return ws


@float_parameter("f", "Frequency")
@float_parameter("phase", "Phase")
class QuantumShotNoiseDetectorDemod1(Detector):
    """
    Represents a quantum shot noise detector with 1 RF demodulation.

    It calculates the amplitude spectral density of the photocurrent
    noise of a photodiode output demodulated at the signal frequency,
    considering only vacuum noise contributions (ignoring radiation
    pressure and squeezing effects).

    Parameters
    ----------
    name : str
        Name of newly created quantum shot noise detector.

    node : :class:`.Node`
        Node to read output from.

    f : float
        Demodulation frequency in Hz

    phase : float
        Demodulation phase in degrees

    nsr : bool, optional
        If true, calculate the noise-to-signal ratio rather than the absolute
        noise value.
    """

    def __init__(self, name, node, f, phase, nsr=False):
        Detector.__init__(
            self, name, node, dtype=np.float64, unit="W/sqrt(Hz)", label="ASD"
        )

        self.f = f
        self.phase = phase
        self.nsr = nsr

    def _get_workspace(self, sims):
        ws = QShotNWorkspace(self, sims, 1, self.nsr)
        return ws


@float_parameter("f1", "Frequency")
@float_parameter("f2", "Frequency")
@float_parameter("phase1", "Phase")
@float_parameter("phase2", "Phase")
class QuantumShotNoiseDetectorDemod2(Detector):
    """
    Represents a quantum shot noise detector with 2 RF demodulations.

    It calculates the amplitude spectral density of the photocurrent
    noise of a photodiode output demodulated at the signal frequency,
    considering only vacuum noise contributions (ignoring radiation
    pressure and squeezing effects).

    Parameters
    ----------
    name : str
        Name of newly created quantum shot noise detector.

    node : :class:`.Node`
        Node to read output from.

    f1 : float
        First demodulation frequency in Hz

    phase1 : float
        First demodulation phase in degrees

    f2 : float
        Second demodulation frequency in Hz

    phase2 : float
        Second demodulation phase in degrees

    nsr : bool, optional
        If true, calculate the noise-to-signal ratio rather than the absolute
        noise value.
    """

    def __init__(self, name, node, f1, phase1, f2, phase2, nsr=False):
        Detector.__init__(
            self, name, node, dtype=np.float64, unit="1/sqrt(Hz)", label="ASD"
        )

        self.f1 = f1
        self.f2 = f2
        self.phase1 = phase1
        self.phase2 = phase2
        self.nsr = nsr

    def _get_workspace(self, sims):
        ws = QShotNWorkspace(self, sims, 2, self.nsr)
        return ws


class GeneralQuantumNoiseDetector(Detector, NoiseDetector):
    """
    Represents a quantum noise detector.

    This detector calculates the amplitude spectral density of the
    photocurrent noise of a DC or demodulated photodiode output.

    Parameters
    ----------
    name : str
        Name of newly created quantum noise detector.

    node : :class:`.Node`
        Node to read output from.

    freqs : list of float or :class:`.Frequency`, optional
        List of mixer demodulation frequencies (in Hz).

    phases : list of float, optional
        List of mixer demodulation phases (in Hz).

    shot_only : bool, optional
        If True, detect only vacuum noise contributions.
    """

    def __init__(self, name, node, freqs=None, phases=None, shot_only=False):
        if freqs is None:
            freqs = []
        if phases is None:
            phases = []

        Detector.__init__(
            self, name, node, dtype=np.float64, unit="1/sqrt(Hz)", label="ASD"
        )
        NoiseDetector.__init__(self, NoiseType.QUANTUM)

        if len(freqs) == 0:
            self.__mode = "dc"
        elif len(phases) == len(freqs):
            self.__mode = "mixer"
        else:
            raise ValueError("'phases' must be as long as 'freqs'.")
        self.freqs = np.array(freqs)
        self.phases = np.array(phases)
        self.shot_only = shot_only
        self._request_selection_vector(name)

    def _get_workspace(self, sims):
        ws = QuantumNoiseDetectorWorkspace(self, sims)
        return ws
