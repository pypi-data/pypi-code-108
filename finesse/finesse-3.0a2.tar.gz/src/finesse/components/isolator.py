"""Optical components performing directional suppression of beams."""

import logging

import numpy as np

from finesse.components.general import Connector, InteractionType
from finesse.components.node import NodeDirection, NodeType
from finesse.parameter import float_parameter
from finesse.utilities import refractive_index

LOGGER = logging.getLogger(__name__)


@float_parameter("S", "Power suppression")
class Isolator(Connector):
    """Represents an isolator optical component with a suppression factor.

    Parameters
    ----------
    name : str
        Name of newly created isolator.

    S : float
        Power suppression in dB.
    """

    def __init__(self, name, S=0.0):
        super().__init__(name)

        self.S = S

        self._add_port("p1", NodeType.OPTICAL)
        self.p1._add_node("i", NodeDirection.INPUT)
        self.p1._add_node("o", NodeDirection.OUTPUT)

        self._add_port("p2", NodeType.OPTICAL)
        self.p2._add_node("i", NodeDirection.INPUT)
        self.p2._add_node("o", NodeDirection.OUTPUT)

        # optic to optic couplings
        self._register_node_coupling(
            "P1i_P2o",
            self.p1.i,
            self.p2.o,
            interaction_type=InteractionType.TRANSMISSION,
        )
        self._register_node_coupling(
            "P2i_P1o",
            self.p2.i,
            self.p1.o,
            interaction_type=InteractionType.TRANSMISSION,
        )

    def _get_workspace(self, sim):
        from finesse.components.modal.isolator import IsolatorWorkspace

        _, is_changing = self._eval_parameters()
        refill = sim.is_component_in_mismatch_couplings(self) or len(is_changing)

        ws = IsolatorWorkspace(self, sim)
        # This assumes that nr1/nr2 cannot change during a simulation
        ws.nr1 = refractive_index(self.p1)
        ws.nr2 = refractive_index(self.p2)

        ws.add_fill_function(self._fill_matrix, refill)

        if sim.is_modal:
            ws.set_knm_info(
                "P1i_P2o", nr_from=ws.nr1, nr_to=ws.nr2, is_transmission=True
            )
            ws.set_knm_info(
                "P2i_P1o", nr_from=ws.nr2, nr_to=ws.nr1, is_transmission=True
            )

        return ws

    def _fill_matrix(self, ws):
        values, _ = self._eval_parameters()
        suppression = 10 ** (-values["S"] / 20)

        for freq in ws.sim.frequencies:
            with ws.sim.component_edge_fill3(
                ws.owner_id, ws.connections.P1i_P2o_idx, freq.index, freq.index
            ) as mat:
                mat[:] = ws.K12.data

            with ws.sim.component_edge_fill3(
                ws.owner_id, ws.connections.P2i_P1o_idx, freq.index, freq.index,
            ) as mat:
                np.multiply(suppression, ws.K21.data, out=mat[:])
