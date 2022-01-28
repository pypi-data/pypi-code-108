"""Objects for connecting and registering connections between components."""

import enum
import logging
import weakref
from collections import OrderedDict
from copy import deepcopy

from .gauss import Gauss
from .. import components
from ..env import warn
from ..exceptions import ComponentNotConnected, FinesseException
from ..freeze import Freezable
from ..utilities import check_name, is_iterable


LOGGER = logging.getLogger(__name__)


@enum.unique
class NodeType(enum.Enum):
    """Enum describing the physical connection type of a :class:`.Node`"""

    OPTICAL = 0
    ELECTRICAL = 1
    MECHANICAL = 2


@enum.unique
class NodeDirection(enum.Enum):
    """Enum describing the direction that information at a :class:`.Node` flows.

    This is largely a description to help understand how external information
    flows in and out of a component. Inside a component all nodes will
    couple to one another in more complex ways.

    Input nodes are those going into a component, whereas output
    describe those leaving. For example incident and reflected light fields.

    Bidrectional takes information either direction. For example a mechanical
    degree of freedom, external forces can be applied to it, or
    its motion can be coupled to some external system.
    """

    INPUT = 0
    OUTPUT = 1
    BIDIRECTIONAL = 2


class Port(Freezable):
    """A collection of all the nodes at a specific point/surface of a component.

    Parameters
    ----------
    name : str
        Name of newly created node.

    component : Sub-class of :class:`.Connector`
        The component that this node belongs to.

    node_type : :class:`.NodeType`
        Physical node type.
    """

    def __init__(self, name, component, node_type):
        self._unfreeze()
        self.__component = weakref.ref(component)
        self.__name = check_name(name)
        self.__full_name = "{}.{}".format(component.name, name)
        self.__type = node_type
        self.__nodes = OrderedDict()
        self.__enabled = True
        self._freeze()

    def __deepcopy__(self, memo):
        new = object.__new__(type(self))
        memo[id(self)] = new
        new.__dict__.update(deepcopy(self.__dict__, memo))
        # Manually update the weakrefs to be correct
        new.__component = weakref.ref(memo[id(self.component)])
        return new

    def _add_node(self, name, direction=None, node=None, **kwargs):
        """Adds a new node to this port. Once called the new node can be access with:

            obj.port.name

        Parameters
        ----------
        name : str
            Name of the new node
        dof_parameter : ModelParameter
            A model parameter to be associated with this node

        Returns
        -------
        Node object added
        """
        if name in self.__nodes:
            raise Exception("Node already added to this component")

        if node is None:
            if self.__type == NodeType.OPTICAL:
                if direction is None:
                    raise Exception(
                        "Node direction must be specified for optical nodes"
                    )
                node = OpticalNode(name, self, direction, **kwargs)
            elif (
                self.__type == NodeType.MECHANICAL or self.__type == NodeType.ELECTRICAL
            ):
                node = SignalNode(name, self, direction, self.__type, **kwargs)
            else:
                raise Exception("Unexpected node type")
        elif len(kwargs) != 0:
            raise Exception(f"Cannot use kwargs when node ({node!r}) is not None")

        if node is None:
            raise RuntimeError("Node unexpectedly None")

        if node.type == NodeType.OPTICAL or self.type == NodeType.OPTICAL:
            if node.type != self.type:
                raise Exception(
                    f"Node ({node.type}) and port type ({self.type}) must be the same ({node!r}, {self!r})"
                )

        self.__nodes[name] = node
        # Update Elements node dict so it doesn't have to keep checking
        # it's ports about what nodes it has
        self.__component()._Connector__nodes[node.full_name] = node
        self._unfreeze()
        assert not hasattr(self, name)
        setattr(self, name, node)
        self._freeze()
        return node

    def _replace_node(self, name, new_node):
        """Replaces a node at this port with a new one.

        This can be used to change connections between elements but care must be taken.
        This does not update any states of the elements beyond simply changing the node.
        This should only be used when an element is borrowing a node from another
        element, and you want to change which node it is borrowing.
        """
        old_node = self.__nodes[name]
        if name not in self.__nodes:
            raise FinesseException(f"{self!r} does not have a node called `{name}`")
        if new_node.type != self.type:
            raise FinesseException("Node and port type must be the same")
        self.__nodes[name] = new_node
        # Update Elements node dict so it doesn't have to keep checking
        # it's ports about what nodes it has
        del self.__component()._Connector__nodes[old_node.full_name]
        self.__component()._Connector__nodes[new_node.full_name] = new_node
        self._unfreeze()
        setattr(self, name, new_node)
        self._freeze()

    def __repr__(self):
        return f"<Port {self.component.name}.{self.name} Type={self.__type} @ {hex(id(self))}>"

    @property
    def full_name(self):
        """
        :getter: Returns a full name of the port: {component name}.{port name}
        """
        return self.__full_name

    @property
    def enabled(self):
        return self.__enabled

    @property
    def type(self):
        """:class:`.NodeType` of the port object.

        :getter: Returns the node-type of the port (read-only).
        """
        return self.__type

    @property
    def name(self):
        """Name of the port object.

        :getter: Returns the name of the port (read-only).
        """
        return self.__name

    @property
    def _model(self):
        return self.component._model

    @property
    def component(self):
        """The component which has ownership of this port.

        :getter: Returns the component that this port belongs to (read-only).
        """
        return self.__component()

    @property
    def is_connected(self):
        """Flag indicating whether the port is attached to another component.

        :getter: Returns true if this port is attached to another component (read-only).
        """
        first = self.nodes[0].connection
        if first is None:
            return False
        else:
            return all(first is n.connection for n in self.nodes)

    @property
    def attached_to(self):
        """Component that the port is attached to.

        :getter: Returns the component this port is attached to, or returns None
                 if no such connected component exists (read-only).
        """
        if self.type == NodeType.OPTICAL:
            spaces = [_.space for _ in self.nodes]
            if all([spaces[0] == _ for _ in spaces]):
                return spaces[0]
            else:
                raise Exception(
                    "Nodes are somehow connected to different "
                    "spaces which should not happen"
                )
        else:
            raise NotImplementedError()

    @property
    def space(self):
        """Space that the port is attached to. Equivalent to :attr:`Port.attached_to`.

        :getter: Returns the space that this port is attached to (read-only).
        """
        if self.type != NodeType.OPTICAL:
            raise Exception("Port type is not optical, cannot retrieve attached space.")
        return self.attached_to

    @property
    def nodes(self):
        """Nodes associated with the port.

        :getter: Returns a tuple of the associated nodes at this port (read-only).
        """
        return tuple(self.__nodes.values())

    def node(self, name):
        """Get a node at this port by its name."""
        return self.__nodes[name]

    def get_unique_node(self, predicate: callable):
        """Returns the unique node at this port that satisfies the provided predicate.
        If multiple nodes satisfy this predicate then a RuntimeError is raised.

        Parameters
        ----------
        predicate : callable(components.Node) -> bool
            A callable that accepts a Node and returns a boolean value

        Examples
        --------
        Selecting a unique output node:
            port.get_unique_node(lambda node: not node.is_input)
        """
        is_node = tuple(predicate(_) for _ in self.nodes)
        if is_node.count(True) == 1:
            idx = is_node.index(True)
            return self.nodes[idx]
        else:
            raise RuntimeError(
                f"Port {repr(self)} does not have a single node that satisfies the predicate"
            )


class Node:
    """Represents a specific connection at a component.

    Mathematically a node represents a single equation in the interferometer matrix.

    A node can only be owned by a single component instance - with weak references stored by the
    connected components.

    Parameters
    ----------
    name : str
        Name of newly created node.

    component : :class:`.Port`
        The port that this node belongs to.

    node_type : :class:`.NodeType`
        Physical node type.
    """

    def __init__(self, name, port, node_type, direction):
        self.__port = weakref.ref(port)
        # self.__component = weakref.ref(port.component)
        self.__name = check_name(name)
        self.__type = node_type
        self.__direction = direction
        self.__full_name = "{}.{}.{}".format(port.component.name, port.name, name)
        self.__port_name = "{}.{}".format(port.name, name)
        self.__tag_name = None
        self.__connection = None
        self.used_in_detector_output = []
        self.has_signal_injection = False

    def __deepcopy__(self, memo):
        new = object.__new__(type(self))
        memo[id(self)] = new
        new.__dict__.update(deepcopy(self.__dict__, memo))
        id_port = id(self.port)
        # Manually update the weakrefs to be correct
        if id_port in memo:
            new.__port = weakref.ref(memo[id_port])
        else:
            # We need to update this reference later on
            # This will be called when the port property
            # is accessed. When this happens we'll peak back
            # at the memo once it has been filled and get
            # the new port reference. After this the refcount
            # for this function should goto zero and be garbage
            # collected
            def update_later():
                new.__port = weakref.ref(memo[id_port])

            new.__port = update_later  # just in case something calls
            # this weakref in the meantime
            memo[id(self._model)].after_deepcopy.append(update_later)

        # new.__component = weakref.ref(memo[id(self.component)])
        return new

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.full_name} @ {hex(id(self))}>"

    @property
    def is_input(self):
        """Flag indicating whether this node is an input to the associated component.

        :getter: Returns `True` if the field at this node
                 goes into `self.component` (read-only).
        """
        return self.direction == NodeDirection.INPUT

    @property
    def full_name(self):
        """Full name.

        :getter: Returns a full name of the node: {component name}.{port name}.{node name}
        """
        return self.__full_name

    @property
    def port_name(self):
        """Port name.

        :getter: Returns a shortened name of the node: {port name}.{node name}
        """
        return self.__port_name

    @property
    def type(self):
        """:class:`.NodeType` of the node object.

        :getter: Returns the node-type of the node (read-only).
        """
        return self.__type

    @property
    def direction(self):
        """
        :class:`.NodeDirection` of this node. This is largely a
        description to help understand how external information flow
        in and out of a component. Inside a component all nodes will
        couple to one another in more complex ways.

        Input nodes are those going into a component, whereas output
        describe those leaving. For example incident and reflected light fields.

        Bidrectional takes information either direction. For example a mechanical
        degree of freedom, external forces can be applied to it, or
        its motion can be coupled to some external system.

        :getter: Returns the directionality of the node (read-only).
        """
        return self.__direction

    @property
    def port(self):
        """:class:`.Port` this node is attached to.

        :getter: Returns the port of this node (read-only).
        """
        return self.__port()

    @property
    def name(self):
        """Name of the node object.

        :getter: Returns the name of the node (read-only).
        """
        return self.__name

    @property
    def tag(self):
        """Tagged name of the node object.

        :getter: Returns the tagged (user-defined) name of the node (read-only).
        """
        return self.__tag_name

    def _set_tag(self, tag):
        self.__tag_name = tag

    @property
    def _model(self):
        return self.component._model

    @property
    def component(self):
        """The component which has ownership of this node.

        :getter: Returns the component that this node belongs to (read-only).
        """
        return self.port.component

    def is_neighbour(self, node):
        """Checks if `node` is a connected by an edge to this node.

        Parameters
        ----------
        node : :class:`.Node`
            Node with which to check connection.

        Returns
        -------
        flag : bool
            True if `node` is connected to this node, False otherwise.
        """
        # if not associated with a model yet, check registered connections directly
        try:
            a = self._model.network.has_node(self.full_name)
            b = node.full_name in self._model.network.neighbors(self.full_name)
            return a and b
        except ComponentNotConnected:
            return (
                self.full_name,
                node.full_name,
            ) in self.component._registered_connections.values()

        # if not self.has_model():
        #     return (self, node) in self.__component()._registered_connections.values()
        # return (self._model.network.has_node(self) and
        #         node in self._model.network.neighbors(self))

    @property
    def connection(self):
        """A reference to the :class:`.Space` or :class:`.Wire` object attached to this
        node.

        :getter: Returns a reference to the :class:`.Space` or :class:`.Wire`
                object attached to the node (read-only).
        """
        # if self.__connection is not None:
        #    return self.__connection()

        try:
            if self.direction == NodeDirection.INPUT:
                edges = self._model.network.in_edges(self.full_name)
            elif self.direction == NodeDirection.OUTPUT:
                edges = self._model.network.out_edges(self.full_name)
            else:
                raise NotImplementedError(f"{self}, {self.direction}")

            for edge in edges:
                edge_data = self._model.network.get_edge_data(*edge)
                owner = edge_data["owner"]()
                if isinstance(
                    owner,
                    (
                        components.Space,
                        components.Wire,
                        components.DegreeOfFreedom,
                    ),
                ):
                    # self.__connection = edge_data["owner"]
                    return owner
        except ComponentNotConnected:
            pass

        return None


class SignalNode(Node):
    """Represents a specific small signal degree of freedom. A signal is some small AC
    oscillation in some property, such as longitudinal motion, voltage, laser amplitude,
    etc.

    Parameters
    ----------
    name : str
        Name of the mechanical motion.

    port : :class:`.Port`
        The port that this node belongs to.

    num_frequencies : int
        Number of mechanical frequencies to model
    """

    def __init__(self, name, port, direction, node_type):
        super().__init__(name, port, node_type, direction)
        self.__frequencies = None
        self.__num_frequencies = 1

    @property
    def num_frequencies(self):
        return self.__num_frequencies

    @property
    def frequencies(self):
        if self.__frequencies is None:
            return (self.component._model.fsig.f.ref,)
        else:
            return self.__frequencies

    @frequencies.setter
    def frequencies(self, value):
        self.__frequencies = value
        self.__num_frequencies = len(value)


class OpticalNode(Node):
    """Represents a specific optical port connection at a component.

    OpticalNodes also have additional physical properties such as the beam parameter (of type
    :class:`.BeamParam`) at the nodes' position within the interferometer.

    Parameters
    ----------
    name : str
        Name of the optical node.
    port : :class:`.Port`
        The port that this node belongs to.
    direction : :class:`.NodeDirection`
        True if the field at this node is going into the component.
    """

    def __init__(self, name, port, direction):
        super().__init__(name, port, NodeType.OPTICAL, direction)

        self.__space = None

    def __deepcopy__(self, memo):
        new = super().__deepcopy__(memo)
        # Manually update the weakrefs to be correct
        if self.__space is not None:
            id_space = id(self.__space())
            if id_space in memo:
                new.__space = weakref.ref(memo[id_space])
            else:
                # We need to update this reference later on
                # This will be called when the port property
                # is accessed. When this happens we'll peak back
                # at the memo once it has been filled and get
                # the new port reference. After this the refcount
                # for this function should goto zero and be garbage
                # collected
                def update_later():
                    new.__space = weakref.ref(memo[id_space])

                new.__space = update_later  # just in case something calls
                # this weakref in the meantime
                memo[id(self._model)].after_deepcopy.append(update_later)

        return new

    @property
    def opposite(self):
        """The opposite direction node.

        :getter: Returns the opposite direction node to this one.
        """
        return getattr(self.port, "o" if self.is_input else "i")

    @property
    def q(self):
        """Beam parameter value at this node.

        :getter: Returns the beam parameter at this node. If the beam
                 parameters in the tangential and sagittal planes are
                 different then it returns a tuple of the two parameters.
        :setter: Sets the beam parameter at this node. If the argument
                 provided is a 2-tuple then the parameter is set astigmatically
                 for the node.
        """
        return self.qx, self.qy

    @q.setter
    def q(self, value):
        if is_iterable(value):  # both qx and qy specified
            self.qx = value[0]
            self.qy = value[1]
        else:  # only one q specified
            if self in self._model.gausses:
                self._model.update_gauss(self, qx=value, qy=value)

            else:
                node_name = self.full_name.replace(".", "_")
                name = f"g{node_name}"
                self._model.add(Gauss(name, self, qx=value, qy=value))

    @property
    def qx(self):
        """Beam parameter value in the tangential plane.

        :getter: Returns the beam parameter at the node in the
                 tangential plane.
        :setter: Sets the beam parameter at the node in the
                 tangential plane.
        """
        trace = self._model.last_trace
        if trace is None:
            gauss = self._model.gausses.get(self)
            # TODO (sjr) Also check in model.cavities for this node as source
            if gauss is None:
                raise RuntimeError(
                    f"No stored beam trace yet performed on model and {self.full_name} "
                    "does not have correspond to any Gauss or Cavity object - unable to "
                    "access any beam parameter at this node."
                )

            warn(
                "No beam trace solution yet stored in the model. Returning "
                "qx based on Gauss object entry."
            )
            qx = gauss.qx
        else:
            qx, _ = trace.get(self, (None, None))
            if qx is None:
                raise RuntimeError(
                    f"Bug encountered! Could not find entry for {self.full_name} "
                    "in last stored beam trace solution of the model."
                )

        return qx

    @qx.setter
    def qx(self, value):
        if self in self._model.gausses:
            self._model.update_gauss(self, qx=value)

        else:
            node_name = self.full_name.replace(".", "_")
            name = f"g{node_name}"
            self._model.add(Gauss(name, self, q=value))

    @property
    def qy(self):
        """Beam parameter value in the sagittal plane.

        :getter: Returns the beam parameter at the node in the
                 sagittal plane.
        :setter: Sets the beam parameter at the node in the
                 sagittal plane.
        """
        trace = self._model.last_trace
        if trace is None:
            gauss = self._model.gausses.get(self)
            # TODO (sjr) Also check in model.cavities for this node as source
            if gauss is None:
                raise RuntimeError(
                    f"No stored beam trace yet performed on model and {self.full_name} "
                    "does not have correspond to any Gauss or Cavity object - unable to "
                    "access any beam parameter at this node."
                )

            warn(
                "No beam trace solution yet stored in the model. Returning "
                "qy based on Gauss object entry."
            )
            qy = gauss.qy
        else:
            _, qy = trace.get(self, (None, None))
            if qy is None:
                raise RuntimeError(
                    f"Bug encountered! Could not find entry for {self.full_name} "
                    "in last stored beam trace solution of the model."
                )

        return qy

    @qy.setter
    def qy(self, value):
        if self in self._model.gausses:
            self._model.update_gauss(self, qy=value)

        else:
            node_name = self.full_name.replace(".", "_")
            name = f"g{node_name}"
            self._model.add(Gauss(name, self, q=value))

    @property
    def space(self):
        """A reference to the :class:`.Space` object attached to this node.

        :getter: Returns a reference to the :class:`.Space`
                 object attached to the node (read-only).
        """
        if self.__space is not None:
            return self.__space()

        try:
            if self.is_input:
                edges = self._model.network.in_edges(self.full_name)
            else:
                edges = self._model.network.out_edges(self.full_name)

            for edge in edges:
                edge_data = self._model.network.get_edge_data(*edge)
                owner = edge_data["owner"]()

                if isinstance(owner, components.Space):
                    self.__space = weakref.ref(owner)
                    return owner
        except ComponentNotConnected:
            pass

        return None
