"""Top-level objects which specific optical, and otherwise, components should inherit
from."""

from copy import copy
from collections import OrderedDict
import enum
import logging
import numbers

import numpy as np

from finesse.components.node import NodeType, Port
from finesse.components.modal.variable import VariableWorkspace
from finesse.exceptions import ComponentNotConnected
from finesse.parameter import float_parameter
from finesse.utilities import check_name, is_iterable
from finesse.element import ModelElement

from collections import namedtuple

# DOFDefinition name should be the full-name of the
# definition for a particular element, e.g. m1.dofs.z
# if this is wrong, then unparsing will not work correctly
DOFDefinition = namedtuple("DOFDefinition", ("name", "DC", "AC", "DC_2_AC_scaling"))

LOGGER = logging.getLogger(__name__)


def unique_element():
    """Flags that this element type is unique in a model.

    In other words, only one of these element types can be in a single model.
    """

    def func(cls):
        cls._unique_element = True
        return cls

    return func


def borrows_nodes():
    """Flags that a ModelElement will be making references to nodes owner by other
    elements, or borrows a reference."""

    def func(cls):
        cls._borrows_nodes = True
        return cls

    return func


@enum.unique
class CouplingType(enum.Enum):
    """An enum describing the type of coupling between two nodes."""

    OPTICAL_TO_OPTICAL = 0
    OPTICAL_TO_ELECTRICAL = 1
    OPTICAL_TO_MECHANICAL = 2
    ELECTRICAL_TO_ELECTRICAL = 3
    ELECTRICAL_TO_OPTICAL = 4
    ELETRICAL_TO_MECHANICAL = 5
    MECHANICAL_TO_MECHANICAL = 6
    MECHANICAL_TO_OPTICAL = 7
    MECHANICAL_TO_ELECTRICAL = 8


@enum.unique
class NoiseType(enum.Enum):
    """An enum describing the type of noise a component generates."""

    QUANTUM = 0


def determine_coupling_type(from_node, to_node):
    """Retrieves the type of coupling (see :class:`.CouplingType`) between two nodes.

    Parameters
    ----------
    from_node : :class:`.Node`
        Node which couples into `to_node`.

    to_node : :class:`.Node`
        Node which has a coupling from `from_node`.

    Returns
    -------
    coupling_t : :class:`.CouplingType`
        The type of coupling between the two given nodes.
    """
    convert = {
        (NodeType.OPTICAL, NodeType.OPTICAL): CouplingType.OPTICAL_TO_OPTICAL,
        (NodeType.OPTICAL, NodeType.ELECTRICAL): CouplingType.OPTICAL_TO_ELECTRICAL,
        (NodeType.OPTICAL, NodeType.MECHANICAL): CouplingType.OPTICAL_TO_MECHANICAL,
        (
            NodeType.ELECTRICAL,
            NodeType.ELECTRICAL,
        ): CouplingType.ELECTRICAL_TO_ELECTRICAL,
        (NodeType.ELECTRICAL, NodeType.OPTICAL): CouplingType.ELECTRICAL_TO_OPTICAL,
        (
            NodeType.ELECTRICAL,
            NodeType.MECHANICAL,
        ): CouplingType.ELETRICAL_TO_MECHANICAL,
        (
            NodeType.MECHANICAL,
            NodeType.MECHANICAL,
        ): CouplingType.MECHANICAL_TO_MECHANICAL,
        (NodeType.MECHANICAL, NodeType.OPTICAL): CouplingType.MECHANICAL_TO_OPTICAL,
        (
            NodeType.MECHANICAL,
            NodeType.ELECTRICAL,
        ): CouplingType.MECHANICAL_TO_ELECTRICAL,
    }
    return convert[(from_node.type, to_node.type)]


@enum.unique
class InteractionType(enum.Enum):
    """An enum describing the type of interaction between two nodes."""

    REFLECTION = 0
    TRANSMISSION = 1


class FrequencyGenerator:
    """The base class for components which generate optical frequencies.

    A component inheriting from this class will allow the model to query the component
    to ask what frequencies it wants to use. Frequency generation comes in the form of
    either a laser or something that modulates.
    """

    def _couples_frequency(self, ws, connection, frequency_in, frequency_out):
        """This method returns whether this element is coupling frequencies for a
        particular connection.

        For example, a modulator would modulator frequencies when a field
        passes through it. Or a suspended mirror would couple the upper and
        lower sidebands on reflection due to radiation pressure effects.

        Parameters
        ----------
        ws : :class:`.ElementWorkspace`
            Workspace for this particular component
        connection : str
            Name of the connection being queried
        frequency_in : :class:`.Frequency`
            Input frequency
        frequency_out : :class:`.Frequency`
            Output frequency

        Returns
        -------
        bool
            True if frequencies couple at this element
        """
        return False

    def _modulation_frequencies(self):
        return []

    def _source_frequencies(self):
        return []

    def _on_response(self, freqWeakRef):
        """Callback function that model calls to say whether requested frequency was
        granted or not. If so a weak reference to the frequency object is returned.

        Parameters
        ----------
        freqWeakRef: Weakref.ref
            Weak reference to the assigned Frequency object

        Raises
        ------
        Exception
            If passed a name to a frequency this element did not
            ask for originally.
        """
        # if freqWeakRef() in self.__requested_frequencies:
        self.__frequencies.append(freqWeakRef)
        # else:
        #    raise Exception(f"{self} never requested a frequency {freqWeakRef()}")


class NoiseGenerator:
    """The base class for components which generate some kind of noise.

    A component inheriting from this class will allow the model to query the component
    to ask what noise it generates.
    """

    def __init__(self):
        self.__noises = {}

    def _register_noise_output(
        self,
        name,
        node,
        noise_type,
    ):
        if noise_type not in self.__noises.keys():
            self.__noises[noise_type] = []

        self.__noises[noise_type].append((name, node))

    def _couples_noise(self, ws, node, noise_type, frequency_in, frequency_out):
        """This method returns whether the noise sidebands this element produces are
        covariant for the specified frequencies at this node.

        Parameters
        ----------
        ws : :class:`.ElementWorkspace`
            Workspace for this particular component
        node : :class:`.Node`
            Node to check.
        noise_type : :class:`.NoiseType`
            NoiseType to check.
        frequency_in : :class:`.Frequency`
            Input frequency
        frequency_out : :class:`.Frequency`
            Output frequency

        Returns
        -------
        bool
            True if the specified sidebands are covariant.
        """
        return frequency_in.index == frequency_out.index

    @property
    def noises(self):
        return self.__noises


class Connector(ModelElement):
    """Base class for any component which connects nodes together.

    Internally it stores the nodes and the connections associated with the component. During the
    matrix build this class will then ensure that the matrix elements for each coupling requested
    are allocated and and the required matrix view for editing their values is retrieved.

    The inheriting class should call ``_register_node`` and ``_register_coupling`` to define the
    connections it wants to use.

    Parameters
    ----------
    name : str
        Name of the new `Connector` instance.
    """

    _borrows_nodes = False

    def __init__(self, name):
        super().__init__(name)

        self.__connections = OrderedDict()
        self.__enabled_checks = OrderedDict()
        self.__ports = OrderedDict()
        self.__interaction_types = {}
        self.__nodes = OrderedDict()
        self._abcd_matrices = {}
        self.__abcds_symbolised = False

    def __nodes_of(self, *node_types):
        return tuple([node for node in self.nodes.values() if node.type in node_types])

    @property
    def borrows_nodes(self):
        """Whether this element borrows node references from another.

        When this is True the element may not create all of its own nodes and just link
        into one that already exists and is owned by another element.
        """
        return self._borrows_nodes

    @property
    def optical_nodes(self):
        """The optical nodes stored by the connector.

        :getter: Returns a list of the stored optical nodes (read-only).
        """
        return self.__nodes_of(NodeType.OPTICAL)

    @property
    def signal_nodes(self):
        """The signal nodes stored by the connector.

        :getter: Returns a list of the stored signal nodes (read-only).
        """
        return self.__nodes_of(NodeType.ELECTRICAL, NodeType.MECHANICAL)

    @property
    def ports(self):
        """Retrieves the ports available at the object.

        Returns
        -------
        tuple
            Read-only tuple of the ports available at this object.
        """
        return tuple(self.__ports.values())

    def _add_port(self, name, type):
        """Creates either an electrical, mechanical, or optical port for this component.

        Each port can then have multiple different nodes associated with - each node
        being an equation to solve for in the linear system.

        For example, the input and output optical field at one part of a component
        would be one port, i.e. reflection from one side of a mirror.

        The port is added to the component object directly to be referenced at a later
        time when the users is connecting components or definining couplings in a component.

        Parameters
        ----------
        name : str
            Name of the port
        type : NodeType
            Type of nodes this port holds

        Returns
        -------
        Port object added
        """
        check_name(name)

        if name in self.ports:
            raise Exception("Port %s already exists for this object" % name)

        if hasattr(self, name):
            raise Exception(
                "Port name %s already exists as an attribute in of this object" % name
            )

        p = Port(name, self, type)
        self.__ports[name] = p

        # self._unfreeze()
        assert not hasattr(self, name)
        setattr(self, name, p)
        # self._freeze()
        return p

    @property
    def _enabled_checks(self):
        return copy(self.__enabled_checks)

    @property
    def _registered_connections(self):
        return copy(self.__connections)

    @property
    def all_internal_optical_connections(self):
        """A dictionary of all the optical connections this element is making between
        its nodes."""
        return {
            k: (self.nodes[v[0]], self.nodes[v[1]])
            for k, v in self.__connections.items()
            if (
                self.coupling_type(self.nodes[v[0]], self.nodes[v[1]])
                == CouplingType.OPTICAL_TO_OPTICAL
            )
        }

    @property
    def all_internal_connections(self):
        """A dictionary of all the connections this element is making between its
        nodes."""
        return {
            k: (self.nodes[v[0]], self.nodes[v[1]])
            for k, v in self.__connections.items()
        }

    def coupling_type(self, from_node, to_node):
        """Obtains the type of coupling (see :class:`.CouplingType`) between the two
        specified nodes at this component.

        Parameters
        ----------
        from_node : :class:`.Node`
            Node which has a forwards coupling to `to_node`.

        to_node : :class:`.Node`
            Node which has a backwards coupling from `from_node`.

        Returns
        -------
        coupling_t : :class:`.CouplingType`
            The type of coupling between the specified nodes.
        """
        try:
            return determine_coupling_type(from_node, to_node)
        except KeyError:
            return None

    def interaction_type(self, from_node, to_node):
        """Obtains the type of interaction (see :class:`.InteractionType`) between the
        two specified nodes at this component.

        Parameters
        ----------
        from_node : :class:`.Node`
            Node which has a forwards coupling to `to_node`.

        to_node : :class:`.Node`
            Node which has a backwards coupling from `from_node`.

        Returns
        -------
        interaction_t : :class:`.InteractionType`
            The type of interaction between the specified nodes.
        """
        try:
            return self.__interaction_types[(from_node.full_name, to_node.full_name)]
        except KeyError:
            return None

    @property
    def nodes(self):
        """All the nodes of all the ports at this component. Order is likely to be the
        order in which the ports and nodes were created, but this is not guaranteed.

        Returns
        -------
        nodes : tuple(:class:`.Node`)
        """
        return self.__nodes

    def _register_node_coupling(
        self,
        connection_id: int,
        from_node,
        to_node,
        interaction_type=None,
        forced_name=None,
        enabled_check=None,
    ):
        """Registers that this element will connect the output of one of its nodes to
        the input of another.

        Each element is responsible for requesting connections
        to be made within a Model. In practice this means the
        model will allocate the required matrix elements for
        this element to fill in.

        Parameters
        ----------
        connection_id : str
            A unique string ID for this element which is used to identify this connection.

        from_node : :class:`.Node`
            The input node

        to_node : :class:`.Node`
            The output node

        interaction_type : :class:`.InteractionType`, optional
            The type of interaction between the nodes if applicable.

        forced_name : str, optional
            Can force the name of a connection. Used by spaces/wires for
            using the correct name as it doesn't own the node

        enabled_check : function, optional
            A function that returns a True/False if this connection should be enabled
            when a simulation is built from a model. The default value None means True.
        """
        from finesse.components import Space, Wire

        if forced_name is None:
            name = "{}->{}".format(from_node.full_name, to_node.full_name)
        else:
            name = forced_name

        try:
            if self._model is not None:
                raise Exception("Component has already been added to a model")
        except ComponentNotConnected:
            pass

        if name in self.__connections:
            raise Exception(
                "Connection called {} already set at component {}".format(
                    self.name, name
                )
            )

        # TODO: decide whether we actually need this - shouldn't be possible
        #       to connect non-existing ports without python complaining about
        #       an undefined parameter first anyway
        if isinstance(self, Space) or isinstance(self, Wire):
            if from_node.port not in from_node.port.component.ports:
                raise Exception()
            if to_node.port not in to_node.port.component.ports:
                raise Exception()
        else:
            if from_node.full_name not in self.nodes:
                raise Exception(
                    "Node {}.{} is not available at component `{}`".format(
                        from_node.port.name, from_node.name, self.name
                    )
                )
            if to_node.full_name not in self.nodes:
                raise Exception(
                    "Node {}.{} is not available at component `{}`".format(
                        to_node.port.name, to_node.name, self.name
                    )
                )
        if (from_node.full_name, to_node.full_name) in self.__connections.values():
            raise Exception(
                f"Connection between {(from_node.full_name, to_node.full_name)} already exists"
            )

        self.__connections[connection_id] = (from_node.full_name, to_node.full_name)
        if enabled_check:
            self.__enabled_checks[connection_id] = enabled_check

        if interaction_type is not None:
            self.__interaction_types[
                (from_node.full_name, to_node.full_name)
            ] = interaction_type

    def is_valid_coupling(self, from_node, to_node):
        """Flags whether the provided node coupling exists at this connector."""
        return (from_node.full_name, to_node.full_name) in self.__connections.values()

    def check_coupling(self, from_node, to_node):
        """Checks that a coupling exists between `from_node` -> `to_node` and raises a
        ``ValueError`` if not."""
        fname, tname = from_node.full_name, to_node.full_name
        if (fname, tname) not in self.__connections.values():
            raise ValueError(f"No coupling exists between {fname} -> {tname}")

    def _parse_from_to_nodes(self, from_node, to_node):
        if isinstance(from_node, numbers.Integral):
            from_node = getattr(self, f"p{from_node}")
        if isinstance(to_node, numbers.Integral):
            to_node = getattr(self, f"p{to_node}")

        if isinstance(from_node, Port):
            from_node = from_node.i
        if isinstance(to_node, Port):
            to_node = to_node.o

        return from_node, to_node

    def _resymbolise_ABCDs(self):
        # By default components will not have to resymbolise optical ABCD matrices
        pass

    def register_abcd_matrix(self, M_sym, *couplings):
        """Register an ABCD matrix of the given symbolic form for a sequence of
        coupling(s).

        Specifying several couplings for one `M_sym` means that all these
        node couplings will point to the same reference ABCDs --- i.e. the
        matrices kept in the underlying ABCD matrix store will be the same
        blocks of memory.

        .. warning::

            This should only be used in the ``_resymbolise_ABCDs`` method of Connectors,
            when implementing a new component.

        Parameters
        ----------
        M_sym : :class:`numpy.ndarray`
            A 2x2 matrix of symbolic elements describing the analytic form of
            the ABCD matrix for the given coupling(s).

        couplings : sequence of tuples
            Arguments of tuples giving the node couplings which are described by
            the given symbolic ABCD matrix `M_sym`.

            These tuples can be of size two or three, with the first two elements
            always as the `from_node` -> `to_node` instances. The former case implies that
            both the tangential and sagittal plane ABCD matrix couplings are equal
            and so both directions 'x' and 'y' in the underlying matrices store will
            be set to the same values. Whilst the latter case, where the third element is
            either 'x' or 'y', sets just these direction keys to this matrix.
        """
        M_num = np.array(M_sym, dtype=np.float64)

        for coupling in couplings:
            if not is_iterable(coupling) or len(coupling) < 2 or len(coupling) > 3:
                raise ValueError(
                    f"Expected coupling {coupling} passed to _register_abcd_matrix "
                    "to be an iterable of length two (from_node, to_node) or "
                    "length three (from_node, to_node, direction)."
                )

            # No plane given, so same matrix will be used for
            # both planes at this given node coupling
            if len(coupling) == 2:
                from_node, to_node = coupling
                direction = ("x", "y")
            # Otherwise use the specified plane
            else:
                from_node, to_node, direction = coupling
                if direction != "x" and direction != "y":
                    raise ValueError(
                        f"Expected direction argument of coupling {coupling} to "
                        f"be either 'x' or 'y' but got {direction}."
                    )

                direction = (direction,)

            # Check that the node coupling actually exists on this connector
            self.check_coupling(from_node, to_node)

            for d in direction:
                key = (from_node, to_node, d)
                if key in self._abcd_matrices:
                    raise ValueError(
                        f"There is already an ABCD matrix defined for the coupling "
                        f"{from_node.full_name} -> {to_node.full_name} in the "
                        f"plane '{d}'!"
                    )

                LOGGER.debug(
                    "For node coupling %s -> %s, in plane %s, registered "
                    "ABCD matrix:\n Symbolic: %s, Current Numeric: %s",
                    from_node.full_name,
                    to_node.full_name,
                    d,
                    M_sym.tolist(),
                    M_num.tolist(),
                )
                self._abcd_matrices[(from_node, to_node, d)] = M_sym, M_num

    def _re_eval_abcds(self):
        for M_sym, M_num in self._abcd_matrices.values():
            M_num[:] = np.array(M_sym, dtype=np.float64)

    def ABCD(
        self,
        from_node,
        to_node,
        direction="x",
        symbolic=False,
        copy=True,
        retboth=False,
    ):
        """
        Parameters
        ----------
        from_node : :class:`.OpticalNode` or :class:`.Port` or str or int
            Input node. If a port, or string repr of a port, is given then
            the *input* optical node of that port will be used.

        to_node : :class:`.OpticalNode` or :class:`.Port` or str or int
            Output node. If a port, or string repr of a port, is given then
            the *output* optical node of that port will be used.

        direction : str, optional; default: 'x'
            Direction of ABCD matrix computation, default is 'x' for tangential plane.

        symbolic : bool, optional; default: False
            Whether to return the symbolic matrix (as given by equations above). Defaults
            to False such that the numeric matrix is returned.

        copy : bool, optional; default: True
            Whether to return a copy of ABCD matrix (or matrices if `retboth` is true). Defaults
            to True so that the internal matrix cannot be accidentally altered. Use caution
            if switching this flag off.

        retboth : bool, optional; default: False
            Whether to return both the symbolic and numeric matrices as a tuple
            in that order.

        Returns
        -------
        M : :class:`numpy.ndarray`
            The ABCD matrix of the specified coupling for the mirror. This is symbolic
            if either of `symbolic` or `retboth` flags are True.

        M2 : :class:`numpy.ndarray`
            Only returned if `retboth` is True, otherwise just `M` above is returned. This
            will always be the numeric matrix.

        Raises
        ------
        err : :class:`ValueError`
            If no coupling exists between `from_node` and `to_node`.
        """
        from_node, to_node = self._parse_from_to_nodes(from_node, to_node)
        self.check_coupling(from_node, to_node)

        if not self.__abcds_symbolised:
            self._resymbolise_ABCDs()
            self.__abcds_symbolised = True

        key = (from_node, to_node, direction)

        if key not in self._abcd_matrices:
            # If an optical coupling exists and no abcd has been specfied
            # then we can assume it is an identity transformation
            M_sym = np.eye(2, dtype=object)
            M_num = np.eye(2)
        else:
            M_sym, M_num = self._abcd_matrices[key]
            if M_sym is None:
                # Symbolic M is None if an error occurred during the tracing
                # In such a case M_num is a TotalReflectionError or
                # some other exception instance
                raise M_num

            # Evaluate M_sym and assign to memory of M_num so that
            # M_num always corresponds to current parameter state
            M_num[:] = np.array(M_sym, dtype=np.float64)

        return _conn_abcd_return(M_sym, M_num, symbolic, copy, retboth)


def _conn_abcd_return(M_sym, M_num, symbolic: bool, copy: bool, retboth: bool):
    """Helper function for handling symbolic and numeric ABCD matrices in functions."""
    if copy:
        Ms = M_sym.copy()
        Mn = M_num.copy()
    else:
        Ms = M_sym
        Mn = M_num

    if retboth:
        return Ms, Mn

    if symbolic:
        return Ms

    return Mn


@float_parameter("value", "Value", is_default=True)
class Variable(ModelElement):
    def __init__(self, name, value):
        super().__init__(name)
        self.value = value

    def _get_workspace(self, sim):
        return VariableWorkspace(self)

    def __float__(self):
        return float(self.value)

    def __int__(self):
        return int(self.value)

    def __complex__(self):
        return complex(self.value)
