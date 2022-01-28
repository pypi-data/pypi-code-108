"""Signal-type electrical component for producing signal inputs."""
from finesse.components.node import NodeType, Node, Port, SignalNode
from finesse.components.general import Connector
from finesse.parameter import float_parameter, info_parameter
from finesse.components.modal.signal import siggen_fill_rhs, SignalGeneratorWorkspace
from finesse.components.dof import DegreeOfFreedom
from finesse.exceptions import FinesseException


@float_parameter("amplitude", "Amplitude", units="arb")
@float_parameter("phase", "Phase", units="degrees")
@info_parameter("f", "Frequency", units="Hz")
class SignalGenerator(Connector):
    """Represents a signal generator which produces a signal with a given amplitude and
    phase.

    Parameters
    ----------
    name : str
        Name of newly created signal generator.

    node : .class:`finesse.components.node.Node`
        A node to inject a signal into.

    amplitude : float, optional
        Amplitude of the signal in volts.

    phase : float, optional
        Phase-offset of the signal from the default in degrees, defaults to zero.
    """

    def __init__(self, name, node, amplitude=1, phase=0):
        Connector.__init__(self, name)
        node = self._input_to_node(node)
        self._add_port("port", node.type)
        self.port._add_node("o", None, node)
        node.has_signal_injection = True

        self.amplitude = amplitude
        self.phase = phase

    def _input_to_node(self, node):
        if isinstance(node, str) and self._model is not None:
            node = self._model.get(node)

        if isinstance(node, DegreeOfFreedom):
            node = node.AC.i
        elif isinstance(node, Port):
            port = node
            if len(port.nodes) == 1:
                # single node ports, just use the only one we have
                node = port.nodes[0]
            else:
                # Else try and get a singular input node.
                is_input_node = tuple(_.is_input for _ in port.nodes)
                if is_input_node.count(True) == 1:
                    idx = is_input_node.index(True)
                    node = port.nodes[idx]
                else:
                    raise Exception(
                        f"Signal generator ({self.name}): Port `{port}` has more than 1 input node, please specify which to use."
                    )
        elif not isinstance(node, Node):
            raise Exception(
                f"Signal generator ({self.name}) input `{node!r}` should be a SignalNode not {type(node)}"
            )

        if not isinstance(node, SignalNode):
            raise FinesseException(f"{node!r} is not a SignalNode")

        return node

    def _on_add(self, model):
        if model is not self.node._model:
            raise Exception(
                f"{repr(self)} is using a node {self.node} from a different model"
            )

    @property
    def node(self):
        """Change the node the signal generator injects into.

        :setter: Change the node the signal generator injects into.
        """
        return self.port.o

    @node.setter
    def node(self, value):
        """Set which signal node this generator should inject into."""
        if self._model.is_built:
            raise FinesseException("Cannot change whilst the model is being run.")
        # Get new node object and change it over
        new_node = self._input_to_node(value)
        self.port._replace_node("o", new_node)
        new_node.has_signal_injection = True

    @property
    def f(self):
        """Signal frequency being injected, is always the `fsig` of the model."""
        return self._model.fsig.f

    def _get_workspace(self, sim):
        if sim.signal:
            ws = SignalGeneratorWorkspace(self, sim)
            ws.rhs_idx = ws.sim.signal.field(self.port.o, 0, 0)
            ws.signal.set_fill_rhs_fn(siggen_fill_rhs)

            if self.port.o.type is NodeType.MECHANICAL:
                ws.scaling = 1 / sim.model_settings.x_scale
            else:
                ws.scaling = 1

            return ws
        else:
            return None
