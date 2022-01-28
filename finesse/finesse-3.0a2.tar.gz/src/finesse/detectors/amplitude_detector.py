"""
Single-frequency amplitude and phase detector.
"""

import numbers
import logging

import numpy as np

from finesse.detectors.compute.amplitude import ADWorkspace
from finesse.detectors.general import MaskedDetector
from finesse.parameter import float_parameter

LOGGER = logging.getLogger(__name__)


@float_parameter("f", "Frequency", units="Hz")
class AmplitudeDetector(MaskedDetector):
    """Represents an amplitude detector which calculates the amplitude and phase of light fields
    at one frequency.

    Parameters
    ----------
    name : str
        Name of newly created detector.

    node : :class:`.Node`
        Node to read output from.

    f : float
        Frequency of light to detect (in Hz).

    n : int, optional; default: None
        Tangential mode index to probe. Defaults to None such that
        all fields of the given frequency are summed.

    m : int, optional; default: None
        Sagittal mode index to probe. Defaults to None such that
        all fields of the given frequency are summed.
    """

    def __init__(self, name, node, f, n=None, m=None):
        MaskedDetector.__init__(
            self, name, node, dtype=np.complex128, label="Amplitude"
        )

        self.f = f

        if (n is None and m is not None) or (m is None and n is not None):
            raise ValueError(
                f"Error in amplitude detector {self.name}:\n"
                f"    Expected both OR neither of n and m to be specified but "
                f"got n = {n} and m = {m}"
            )

        self.__check_mode_number(n, "n")
        self.__check_mode_number(m, "m")

        self.__n = n
        self.__m = m

    def __check_mode_number(self, k, mode_str):
        if k is not None:
            if (
                not isinstance(k, numbers.Number)
                or k < 0
                or (
                    hasattr(k, "is_integer")
                    and not k.is_integer()
                    and not isinstance(k, numbers.Integral)
                )
            ):
                raise ValueError(
                    f"Error in amplitude detector {self.name}:\n"
                    f"    Expected argument {mode_str} to be None or a positive integer "
                    f"but got {mode_str} = {k}"
                )

    @property
    def n(self):
        """The tangential mode index to probe.

        :getter: Returns the tangential mode index being probed (read-only).
        """
        return self.__n

    @property
    def m(self):
        """The sagittal mode index to probe.

        :getter: Returns the sagittal mode index being probed (read-only).
        """
        return self.__m

    def _get_workspace(self, sim):
        return ADWorkspace(self, sim)
