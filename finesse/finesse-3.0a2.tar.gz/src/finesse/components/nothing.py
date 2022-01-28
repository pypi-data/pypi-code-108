"""Contains the class :class:`.Nothing` which represents an empty/null point in a
configuration."""

import numpy as np

from finesse.components.general import Connector, InteractionType
from finesse.components.node import NodeType, NodeDirection
from finesse.components.workspace import ConnectorWorkspace


class NothingWorkspace(ConnectorWorkspace):
    def __init__(self, owner, sim):
        super().__init__(owner, sim, False, False)


class Nothing(Connector):
    """Represents an empty point in the interferometer configuration.

    `Nothing` is just some point in space that can be connected to. For example, you can use this to
    propagate a beam from some component out to some arbitrary point to make a measurement at. You
    can also use this to split spaces up, if you wanted to measure something inbetween two
    components. It can also be used to replace a component, for example if you want to remove a lens
    or a mirror in some beam path.

    Parameters
    ----------
    name : str
        Name of newly created nothing.
    """

    def __init__(self, name):
        super().__init__(name)

        # Here we register that fact this component will
        # want to have some ports and nodes as well as
        # the couplings between them
        self._add_port("p1", NodeType.OPTICAL)  # front
        self._add_port("p2", NodeType.OPTICAL)  # back
        # input and output optical fields at port 1 (Front face)
        self.p1._add_node("i", NodeDirection.INPUT)
        self.p1._add_node("o", NodeDirection.OUTPUT)
        # input and output optical fields at port 2 (Back face)
        self.p2._add_node("i", NodeDirection.INPUT)
        self.p2._add_node("o", NodeDirection.OUTPUT)
        # Optic to optic couplings
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
        ws = NothingWorkspace(self, sim)
        ws.I = np.eye(sim.model_settings.num_HOMs, dtype=np.complex128)
        ws.carrier.add_fill_function(self._fill_carrier, False)
        ws.signal.add_fill_function(self._fill_signal, False)
        return ws

    def _fill_optical_matrix(self, ws, matrix, connections):
        for freq in matrix.optical_frequencies.frequencies:
            with matrix.component_edge_fill3(
                ws.owner_id,
                connections.P1i_P2o_idx,
                freq.index,
                freq.index,
            ) as mat:
                mat[:] = ws.I

            with matrix.component_edge_fill3(
                ws.owner_id,
                connections.P2i_P1o_idx,
                freq.index,
                freq.index,
            ) as mat:
                mat[:] = ws.I

    def _fill_carrier(self, ws):
        self._fill_optical_matrix(ws, ws.sim.carrier, ws.carrier.connections)

    def _fill_signal(self, ws):
        self._fill_optical_matrix(ws, ws.sim.signal, ws.signal.connections)
