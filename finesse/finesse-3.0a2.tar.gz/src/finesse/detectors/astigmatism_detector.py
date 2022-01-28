import numpy as np

from finesse.detectors.general import Detector
from finesse.detectors.compute.gaussian import AstigmatismDetectorWorkspace


class AstigmatismDetector(Detector):
    """Detector for astigmatism figure-of-merit at a given node.

    The computed quantity is given via one minus :meth:`finesse.gaussian.BeamParam.overlap`.

    Parameters
    ----------
    name : str
        Name of the detector.

    node : :class:`.OpticalNode`
        Node to compute astigmatism at.
    """

    def __init__(self, name, node):
        super().__init__(name, node, dtype=np.float64, label="Astigmatism")

    @property
    def needs_fields(self):
        return False

    @property
    def needs_trace(self):
        return True

    def _get_workspace(self, sim):
        return AstigmatismDetectorWorkspace(self, sim)
