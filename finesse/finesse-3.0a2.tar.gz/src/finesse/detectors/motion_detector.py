"""Motion amplitude and phase detector."""

import logging

import numpy as np

from finesse.detectors.general import Detector
from finesse.detectors.workspace import DetectorWorkspace

LOGGER = logging.getLogger(__name__)


class MotionDetectorWorkspace(DetectorWorkspace):
    def __init__(self, owner, sim):
        super().__init__(owner, sim, needs_signal=True)


class MotionDetector(Detector):
    """Represents a motion detector which calculates the amplitude and phase of surface
    motion.

    Parameters
    ----------
    name : str
        Name of newly created motion detector.

    node : :class:`.Node`
        Node to read output from.
    """

    def __init__(self, name, node):
        Detector.__init__(self, name, node, dtype=np.complex128, label="Motion")

    def _get_workspace(self, sim):
        def output_fn(ws):
            if ws.sim.signal:
                return (
                    ws.sim.signal.get_out(self.node, 0, 0)
                    * ws.sim.model_settings.x_scale
                )

        ws = MotionDetectorWorkspace(self, sim)
        ws.set_output_fn(output_fn)
        return ws
