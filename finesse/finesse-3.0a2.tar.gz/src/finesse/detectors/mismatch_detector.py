"""Detectors for calculating mode mismatches in an optical configuration."""

import numpy as np

from ..components.node import OpticalNode, Port
from .general import Detector
from .compute.gaussian import ModeMismatchDetectorWorkspace


class ModeMismatchDetector(Detector):
    """Detector for mode mismatch figure-of-merit for a specified node coupling.

    The computed quantity is given in :meth:`finesse.gaussian.BeamParam.mismatch` where
    :math:`q_1` is the input beam parameter at `node1` propagated via the associated
    ABCD matrix to `node2`, and :math:`q_2` is the beam parameter at `node2`.

    As mode mismatches cannot occur over spaces in Finesse, `node1` must be an input
    node and `node2` must be an output node.

    Parameters
    ----------
    name : str
        Name of the detector.

    node1 : :class:`.OpticalNode` or :class:`.Port`
        Input node or port. If a :class:`.Port` instance is given then this
        node will be the input node of that port. Note that this node cannot
        be an output node.

    node2 : :class:`.OpticalNode` or :class:`.Port`
        Output node or port. If a :class:`.Port` instance is given then this
        node will be the output node of that port. Note that this node cannot
        be an input node.

    direction : str, optional; default: "x"
        Plane of computation, defaults to "x" for the tangential plane. Changing
        to "y" will compute the mode mismatch in the sagittal plane.

    percent : bool, optional; default: True
        Whether to calculate the mode mismatch as a fraction (default behaviour)
        or a percentage.
    """

    def __init__(self, name, node1, node2, direction="x", percent=False):
        if isinstance(node1, Port):
            node1 = node1.i
        if isinstance(node2, Port):
            node2 = node2.o

        if not isinstance(node1, OpticalNode):
            raise TypeError("Argument node1 must be an OpticalNode.")

        if not isinstance(node2, OpticalNode):
            raise TypeError("Argument node2 must be an OpticalNode.")

        if not node1.is_input:
            raise ValueError("Expected node1 to be an input node.")
        if node2.is_input:
            raise ValueError("Expected node2 to be an output node.")

        if node1.component != node2.component:
            raise ValueError(
                "Expected node1 and node2 to be owned by the same component."
            )

        label = f"Mode mismatch\n{node1.full_name}->{node2.full_name}"
        unit = "%" if percent else ""
        super().__init__(name, dtype=np.float64, label=label, unit=unit)

        comp = node1.component
        comp.check_coupling(node1, node2)

        self.__node1 = node1
        self.__node2 = node2
        self.__direction = direction
        self.__percent = percent

    @property
    def in_node(self):
        """Input node.

        :getter: Returns the input node. Read-only.
        """
        return self.__node1

    @property
    def out_node(self):
        """Output node.

        :getter: Returns the output node. Read-only.
        """
        return self.__node2

    @property
    def component(self):
        """The component at which the mode mismatch is calculated.

        :getter: Returns the associated component. Read-only.
        """
        return self.in_node.component

    @property
    def in_percent(self):
        """Flag indicating whether the mismatch is computed as a percentage.

        :getter: Returns the percentage flag.
        :setter: Sets the percentage flag.
        """
        return self.__percent

    @in_percent.setter
    def in_percent(self, value):
        self.__percent = bool(value)

    @property
    def direction(self):
        """The plane in which the mode mismatch is calculated.

        A value of "x" represents the tangential plane, whilst "y" gives
        the sagittal plane.

        :getter: Returns the plane of computation as a string representation. Read-only.
        """
        return self.__direction

    @property
    def needs_fields(self):
        return False

    @property
    def needs_trace(self):
        return True

    def _get_workspace(self, sim):
        return ModeMismatchDetectorWorkspace(self, sim)
