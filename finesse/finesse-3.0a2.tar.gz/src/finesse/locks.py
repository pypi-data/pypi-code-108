"""Controlling an interferometer via error signals."""

import logging

import finesse.detectors as detectors
from finesse.element import ModelElement

LOGGER = logging.getLogger(__name__)


class Lock(ModelElement):
    """A simple lock which computes and applies the feedback to a given parameter using
    an error signal.

    Parameters
    ----------
    name : str
        Name of newly created lock.

    error_signal : Any
        An error signal parameter or an object capable of producing a real-type error signal. This
        is typically a demodulated :class:`.PowerDetector` instance (or the name of the instance).

    feedback : :class:`.Parameter`
        A parameter of the model to apply the locks' feedback signal to.

    gain : float
        Control loop gain.

    accuracy : float
        Threshold to decide whether the loop is locked.

    disabled : boolean
        If true this lock will not run when the `RunLocks()` action is used. Explicitly specifying
        the name of the lock will override this setting, e.g. `RunLocks(name)`.

    offset : float
        An offset that is applied to the error signal before it is used.
    """

    def __init__(
        self, name, error_signal, feedback, gain, accuracy, *, disabled=False, offset=0
    ):
        super().__init__(name)

        self.__errsig = error_signal
        self.__feedback = feedback
        self.__gain = gain
        self.__accuracy = accuracy
        self.offset = offset
        self.disabled = disabled

    def _on_add(self, model):
        if isinstance(self.__errsig, str):
            self.__errsig = self._model.elements[self.__errsig]
        self.__from_detector = isinstance(self.__errsig, detectors.Detector)

    @property
    def error_signal(self):
        """The error signal of the lock."""
        return self.__errsig

    @property
    def feedback(self):
        """A handle to the parameter which the feedback signal is applied to."""
        return self.__feedback

    @property
    def gain(self):
        return self.__gain

    @gain.setter
    def gain(self, value):
        self.__gain = float(value)

    @property
    def accuracy(self):
        return self.__accuracy

    @accuracy.setter
    def accuracy(self, value):
        self.__accuracy = float(value)
