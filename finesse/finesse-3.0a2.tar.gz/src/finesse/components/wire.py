"""Wire-type objects representing electrical connections between components."""

import logging

import numpy as np

from finesse.exceptions import FinesseException

from .general import Connector, borrows_nodes
from .node import NodeType, NodeDirection, SignalNode, Port
from .workspace import ConnectorWorkspace
from ..env import warn
from ..parameter import float_parameter

# from ..exceptions import FinesseException


LOGGER = logging.getLogger(__name__)


class WireWorkspace(ConnectorWorkspace):
    pass


@float_parameter("delay", "Delay", validate="_check_delay", units="s")
@borrows_nodes()
class Wire(Connector):
    """A wire represents a flow of information between signal nodes. It connects two
    specific signal nodes. Signal nodes have a direction associated with them: input,
    output, or bidirectional. Depending on what direction each node has depends on what
    the wire will setup when it is connected. The rules for node-to-node connections
    are:

    - input and output: a connection will be formed from the input to the output
      node
    - input to input or output to output: is not allowed.
    - input to bidirectional: a connection will be made from the input node into
      the bidirectional node
    - output to bidirectional: a connection will be made from the bidirectional
      node into the output node
    - bidirectional to bidirectional: two connections will be made that lets
      information flow in both directions between the two nodes.

    When connecting ports the wire will look at the name of each node in the port
    and connect nodes with the same name

    Parameters
    ----------
    name : str, optional
        Name of newly created wire.

    nodeA, nodeB : :class:`.SignalNode`
        Signal nodes to connect together.

    delay : float, optional
        A delay time for the signal to flow from A to B in seconds
    """

    def __init__(self, name=None, nodeA=None, nodeB=None, delay=0):
        given_name = name
        if (nodeA is None) != (nodeB is None):
            warn(
                "Cannot construct a wire with only one port connected; ignoring ports."
            )
            nodeA = None
            nodeB = None

        if nodeA is not None and nodeA.type not in (
            NodeType.ELECTRICAL,
            NodeType.MECHANICAL,
        ):
            raise RuntimeError(
                f"{nodeA!r} is not an electrical or mechanical port or node"
            )
        if nodeB is not None and nodeB.type not in (
            NodeType.ELECTRICAL,
            NodeType.MECHANICAL,
        ):
            raise RuntimeError(
                f"{nodeB!r} is not an electrical or mechanical port or node"
            )

        if name is None:
            if nodeA is not None and nodeB is not None:
                compA = nodeA.component.name
                compB = nodeB.component.name
                name = f"{compA}_{nodeA.name}__{compB}_{nodeB.name}"
            else:
                raise ValueError(
                    "Cannot create an unconnected wire without " "providing a name"
                )

        super().__init__(name)
        self.delay = delay
        if given_name is None:
            self._namespace = (".wires",)
        else:
            # Also put into main namespace if it has a specific name
            self._namespace = (".", ".wires")

        self.__nodeA = None
        self.__nodeB = None

        if nodeA is not None and nodeB is not None:
            self.connect(nodeA, nodeB)

    @property
    def nodeA(self):
        return self.__nodeA

    @property
    def nodeB(self):
        return self.__nodeB

    def _check_delay(self, value):
        if value < 0:
            raise ValueError("Delay of a wire must not be negative.")

        return value

    def connect(self, A, B):
        """Connects two signal nodes together. One must be an INPUT and the other and
        OUTPUT node. Or one or both might be BIDIRECTIONAL.

        Parameters
        ----------
        A : :class:`.SignalNode` or :class:`.Port`
            First signal node or Electrical port with a single node

        B : :class:`.SignalNode` or :class:`.Port`
            Second signal node or Electrical port with a single node
        """
        if self.nodeA is not None or self.nodeB is not None:
            raise FinesseException(
                f"{self!r} is already connecting {self.nodeA!r} to {self.nodeB!r}"
            )

        if isinstance(A, Port) and A.type == NodeType.ELECTRICAL:
            if len(A.nodes) != 1:
                raise FinesseException(
                    f"{A!r} has more than one port, please specify which to use"
                )
            else:
                A = A.nodes[0]

        if isinstance(B, Port) and B.type == NodeType.ELECTRICAL:
            if len(B.nodes) != 1:
                raise FinesseException(
                    f"{B!r} has more than one port, please specify which to use"
                )
            else:
                B = B.nodes[0]

        if not (isinstance(A, SignalNode) and isinstance(B, SignalNode)):
            raise FinesseException(
                f"Wires can only connect SignalNodes, not {A!r} to {B!r}"
            )

        self.__nodeA = A
        self.__nodeB = B

        pA = self._add_port("pA", self.nodeA.type)
        A = pA._add_node("A", None, self.nodeA)
        pB = self._add_port("pB", self.nodeB.type)
        B = pB._add_node("B", None, self.nodeB)

        if (
            A.direction
            in (
                NodeDirection.OUTPUT,
                NodeDirection.BIDIRECTIONAL,
            )
            and B.direction in (NodeDirection.INPUT, NodeDirection.BIDIRECTIONAL)
        ):
            self._register_node_coupling("WIRE", A, B)
        elif (
            B.direction
            in (
                NodeDirection.OUTPUT,
                NodeDirection.BIDIRECTIONAL,
            )
            and A.direction in (NodeDirection.INPUT, NodeDirection.BIDIRECTIONAL)
        ):
            self._register_node_coupling("WIRE", B, A)
        else:
            raise FinesseException(f"Cannot connect signal nodes {A!r} to {B!r}")

    def _get_workspace(self, sim):
        if sim.signal:
            self._eval_parameters()
            # Most wires are zero delay, so don't bother refilling them all the time
            refill = (
                (sim.model.fsig.f.is_changing or sim.signal.any_frequencies_changing)
                and self.delay.is_changing
                and self.delay != 0
            )
            ws = WireWorkspace(self, sim)
            ws.signal.add_fill_function(self.fill, refill)
            return ws
        else:
            return None

    def fill(self, ws):
        delay = np.exp(-1j * ws.values.delay * ws.sim.model_settings.fsig)
        key = (ws.owner_id, 0, 0, 0)
        if key in ws.sim.signal._submatrices:
            ws.sim.signal._submatrices[key][:] = delay
