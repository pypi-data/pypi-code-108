# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import os

import PySide2.QtCore as QtCore

from sympathy.utils import uuid_generator
from .. import filename_manager as fileman
from .. util import make_enum


_Types = make_enum(
    'Types', 'Flow', 'Node', 'Connection', 'InputPort', 'OutputPort',
    'FlowInput', 'FlowOutput', 'TextField', 'RoutePoint')

Executors = make_enum(
    'Executors', 'Node', 'Flow', 'Port', 'Lambda')


class Type(object):
    """Types handles the different types of flow elements."""

    Flow = _Types.Flow
    Node = _Types.Node
    Connection = _Types.Connection
    InputPort = _Types.InputPort
    OutputPort = _Types.OutputPort
    FlowInput = _Types.FlowInput
    FlowOutput = _Types.FlowOutput
    TextField = _Types.TextField
    RoutePoint = _Types.RoutePoint

    main_types = {Flow, Node, FlowInput, FlowOutput, TextField, RoutePoint}
    port_types = {InputPort, OutputPort}
    element_types = {Flow, Node, Connection, InputPort, OutputPort,
                     FlowInput, FlowOutput, TextField}

    @staticmethod
    def filter_nodes(element_list):
        """Returns the nodes in the element_list."""
        return [
            element for element in element_list
            if Type.is_port_manager(element)]

    @staticmethod
    def filter_nodes_and_flows(element_list):
        """Returns nodes and flows in an element_list."""
        return [
            element for element in element_list
            if element.type in (Type.Node, Type.Flow)]

    @staticmethod
    def filter_main_elements(element_list):
        return [
            element for element in element_list
            if element.type in [Type.Node, Type.FlowInput, Type.FlowOutput,
                                Type.Flow, Type.TextField]]

    @staticmethod
    def filter_connections(element_list):
        """Returns the connections in element_list"""
        return [
            element for element in element_list
            if element.type == Type.Connection]

    @staticmethod
    def filter_flow_io_nodes(element_list):
        """Returns all flow IO-nodes"""
        return [
            element for element in element_list
            if element.type in (Type.FlowInput, Type.FlowOutput)
        ]

    @staticmethod
    def comparison_key(element):
        """Key for sorting element lists."""
        return element.type.index

    def is_element(element):
        return isinstance(element, ElementInterface)

    @staticmethod
    def is_port_manager(element):
        return isinstance(element, PortManagerInterface)

    @staticmethod
    def is_node(element):
        return isinstance(element, NodeInterface)

    def is_flow(element):
        return element.type == Type.Flow

    @staticmethod
    def is_port(element):
        return element.type in Type.port_types


class ElementInterface(QtCore.QObject):
    """Interface and base class for all kinds of graph elements."""

    position_changed = QtCore.Signal(QtCore.QPointF)
    size_changed = QtCore.Signal(QtCore.QSizeF)
    name_changed = QtCore.Signal(str)

    _type = None

    def __init__(self, flow=None, uuid=None, **kwargs):
        self._flow = flow
        self._uuid = uuid or uuid_generator.generate_uuid()
        super().__init__(**kwargs)
        self._position = None
        self._size = None
        self._name = None
        self._was_in_subflow = False

    @property
    def was_in_subflow(self):
        return self._was_in_subflow

    @was_in_subflow.setter
    def was_in_subflow(self, value):
        self._was_in_subflow = value

    def parent_flows(self):
        """
        Iterator over all parent flows starting at the immediate parent flow and
        ending at the root flow (last parent).
        """
        parent = self._flow
        while parent:
            yield parent
            parent = parent._flow

    def root_flow(self):
        root = None
        for root in self.parent_flows():
            pass
        return root

    @property
    def type(self):
        return self._type

    def namespace_uuid(self):
        """Namespace UUID to avoid collisions."""
        if self._flow is not None:
            return self._flow.namespace_uuid()
        raise RuntimeError('Root flow not found.')

    @property
    def uuid(self):
        """Returns this element's UUID."""
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        """Set this element's UUID."""
        if value is None:
            return

        if self._uuid != value:
            # TODO: child elements should never switch UUID. For example,
            # nodes or subflows that are added to a flow.
            # This can instead be handled on creation. If implementations
            # requires a change of UUID, then the child can be removed
            # before updating it and adding it back to the parent.
            self._update_uuid(self._uuid, value)

    def _update_uuid(self, old_uuid, new_uuid):
        self._uuid = new_uuid

    @property
    def full_uuid(self):
        return uuid_generator.join_uuid(self.namespace_uuid(), self.uuid)

    @property
    def position(self):
        """The current position as QtCore.QPointF"""
        return self._position

    @position.setter
    def position(self, value):
        """Assigns the current position from a QtCore.QPointF"""
        if self._position != value:
            self._position = value
            self.position_changed.emit(value)

    @property
    def size(self):
        """The size as QtCore.QSizeF."""
        return self._size

    @size.setter
    def size(self, value):
        """Assign the size from a QtCore.QSizeF."""
        if isinstance(value, QtCore.QSize):
            # TODO: Check why CreateTextFieldCommands passes regular QSize.
            value = QtCore.QSizeF(value)

        if self._size != value:
            self._size = value
            self.size_changed.emit(value)

    def add(self, flow=None):
        """Add this element to flow (or the last used flow)."""
        raise NotImplementedError('Not implemented for interface')

    def remove(self):
        """Remove this element from it's flow."""
        raise NotImplementedError('Not implemented for interface')

    @property
    def flow(self):
        """Flow (or subflow) which this element belongs to."""
        return self._flow

    @flow.setter
    def flow(self, value):
        self._flow = value

    def to_dict(self):
        """Returns the dictionary representation of this element."""
        raise NotImplementedError('Not implemented for interface')

    @property
    def name(self):
        """Returns the name."""
        return self._name

    @name.setter
    def name(self, value):
        """Sets the element name, emits name_changed."""
        if self._name != value:
            self._name = value
            self.name_changed.emit(value)

    def __str__(self):
        """String for printing."""
        return '{}:{}:0x{:x}'.format(
            self.type.name, self.name, id(self))

    def is_deletable(self):
        return True


class PortManagerInterface(object):
    # Port is imported here to avoid circular imports.
    from .port import Port
    input_port_created = QtCore.Signal(Port)
    output_port_created = QtCore.Signal(Port)
    input_port_removed = QtCore.Signal(Port)
    output_port_removed = QtCore.Signal(Port)
    ports_reordered = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._inputs = []
        self._outputs = []

    def input(self, index_or_uuid):
        """Returns the input port matching either an index (0-based) or
        UUID.
        """
        if isinstance(index_or_uuid, int):
            return self._inputs[index_or_uuid]
        elif isinstance(index_or_uuid, str):
            for port in self._inputs:
                if port.uuid == index_or_uuid:
                    return port
        return None

    def output(self, index_or_uuid):
        """Returns the output port matching either an index (0-based) or
        UUID.
        """
        if isinstance(index_or_uuid, int):
            return self._outputs[index_or_uuid]
        elif isinstance(index_or_uuid, str):
            for port in self._outputs:
                if port.uuid == index_or_uuid:
                    return port

    def create_input(self, port_definition=None, datatype=None,
                     generics_map=None, uuid=None, pos=None):
        """Create an input port."""
        port = self._flow.create_input_port(self, port_definition,
                                            generics_map, uuid, pos)

        self.input_port_created.emit(port)
        return port

    def create_output(self, port_definition=None, datatype=None,
                      generics_map=None, uuid=None, pos=None):
        """Create an output port."""
        port = self._flow.create_output_port(self, port_definition,
                                             generics_map, uuid, pos)
        self.output_port_created.emit(port)
        return port

    def add_input(self, port):
        """Add the Port to this subflow's list of input ports."""
        self._inputs.append(port)
        self._update_port_layout()

    def add_output(self, port):
        """Add the Port to this subflow's list of output ports."""
        self._outputs.append(port)
        self._update_port_layout()

    def insert_input(self, pos, port):
        """Insert the Port to this subflow's list of input ports."""
        self._inputs.insert(pos, port)
        self._update_port_layout()

    def insert_output(self, pos, port):
        """Insert the Port to this subflow's list of output ports."""
        self._outputs.insert(pos, port)
        self._update_port_layout()

    def remove_input(self, port):
        """Remove the Port to this subflow's list of input ports."""
        del self._inputs[self._inputs.index(port)]
        self.input_port_removed.emit(port)
        self._update_port_layout()

    def remove_output(self, port):
        """Remove the Port to this subflow's list of output ports."""
        del self._outputs[self._outputs.index(port)]
        self.output_port_removed.emit(port)
        self._update_port_layout()

    def _update_port_layout(self):
        self._set_port_positions(-8.0, self._inputs)
        self._set_port_positions(self.size.width() + 8.0, self._outputs)

    def _set_port_positions(self, x_position, ports):
        if len(ports) > 0:
            y = 0.0
            dy = self._size.height() / (len(ports) + 1)
            if len(ports) <= 2:
                y = dy
            else:
                height = (self._size.height() -
                          ports[0].size.height() / 2.0 -
                          ports[-1].size.height() / 2.0)
                dy = height / (len(ports) - 1)
                y = ports[0].size.height() / 2.0
            for port in ports:
                port.position = QtCore.QPointF(
                    x_position - port.size.width() / 2.0,
                    y - port.size.height() / 2.0)
                y += dy

    def reorder_inputs(self, new_order):
        """Change the order of the input ports according to new_order. Here,
        new_order is a list with the new positions (eg. to rotate three ports
        one step down, use new_order=[2, 0, 1]).
        """
        self._inputs = [self._inputs[i] for i in new_order]
        self._update_port_layout()
        self.ports_reordered.emit()

    def reorder_outputs(self, new_order):
        """Change the order of the output ports according to new_order."""
        self._outputs = [self._outputs[i] for i in new_order]
        self._update_port_layout()
        self.ports_reordered.emit()

    @property
    def inputs(self):
        """Returns all input ports (list(Port))."""
        return self._inputs

    @property
    def outputs(self):
        """Returns all output ports (list(Port))."""
        return self._outputs

    def get_operative_inputs(self, execute=False):
        return self._inputs

    def port_index(self, port):
        """Returns the index matching port."""
        for index, input_ in enumerate(self._inputs):
            if input_ == port:
                return index
        for index, output_ in enumerate(self._outputs):
            if output_ == port:
                return index
        return None

    def needs_filename(self, port):
        return False

    def can_create_input(self, name):
        return False

    def can_create_output(self, name):
        return False

    def can_delete_input(self, port):
        return False

    def can_delete_output(self, port):
        return False

    def remove_files(self):
        pass


class NodeInterface(PortManagerInterface, ElementInterface):
    """Interface/base class for Node type (executable) elements."""

    state_changed = QtCore.Signal()
    progress_changed = QtCore.Signal(int)
    name_changed = QtCore.Signal(str)
    parameter_viewer_changed = QtCore.Signal(bool)
    parameters_changed = QtCore.Signal()
    migration_status_changed = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._size = QtCore.QSizeF(50, 50)
        self._parameter_view_open = False
        self._migration_status = None

    def initialize(self):
        """
        Initialize this node, should be performed after the NodeView has
        been created and the node is added to a flow.
        """
        self._log_filename = fileman.instance().allocate_filename(
            self.flow.root_flow().namespace_uuid(),
            self.full_uuid, '', 'log')

    @QtCore.Slot()
    def execute(self):
        """Execute the node."""
        raise NotImplementedError('Not implemented for interface')

    @QtCore.Slot()
    def abort(self):
        """Stop the execution of this node."""
        raise NotImplementedError('Not implemented for interface')

    def progress(self):
        """Progress of execution (0-100 %)."""
        raise NotImplementedError('Not implemented for interface')

    def reload(self):
        raise NotImplementedError('Not implemented for interface')

    @property
    def ok(self):
        """
        Returns the status of the node.
        """
        # TODO: Confusing name for what mostly means is available.
        return self._ok

    @property
    def needs_validate(self):
        return True

    @property
    def parameter_view_open(self):
        return self._parameter_view_open

    @parameter_view_open.setter
    def parameter_view_open(self, state):
        self._parameter_view_open = state
        self.parameter_viewer_changed.emit(state)

    @property
    def migration_status(self):
        return self._migration_status

    @migration_status.setter
    def migration_status(self, status):
        old = self._migration_status
        self._migration_status = status
        if status != old:
            self.migration_status_changed.emit()

    def internal_validate(self):
        if not self.needs_validate:
            return self.ok
        raise ValueError('Only used when needs_validate is False.')

    @property
    def log_filename(self):
        return self._log_filename

    def remove_files(self):
        try:
            os.remove(self._log_filename)
        except (OSError, IOError):
            pass

    def set_started(self):
        raise NotImplementedError('Not implemented for interface')

    def execute_started(self):
        self.set_started()

    def execute_queued(self):
        self.set_queued()

    def set_done(self, status):
        raise NotImplementedError('Not implemented for interface')

    def execute_done(self, status):
        self.set_done(status)

    def set_aborting(self, child_nodes=None):
        raise NotImplementedError('Not implemented for interface')

    def execute_aborting(self, child_nodes=None):
        self.set_aborting(child_nodes)

    def set_aborted(self, child_nodes=None):
        raise NotImplementedError('Not implemented for interface')

    def execute_aborted(self, child_nodes=None):
        self.set_aborted(child_nodes)


class NodeStatusInterface(object):
    """Interface for the different states an executable node can have."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def is_configurable(self):
        """The node can be configured (all inputs are connected if they are
        needed).
        """
        raise NotImplementedError('Not implemented for interface')

    def is_executable(self):
        """The node can be executed (inputs are connected)."""
        raise NotImplementedError('Not implemented for interface')

    def is_abortable(self):
        """The node can be aborted."""
        raise NotImplementedError('Not implemented for interface')

    def is_reloadable(self):
        """The node can be reloaded."""
        raise NotImplementedError('Not implemented for interface')

    def is_deletable(self):
        """The node can be removed."""
        raise NotImplementedError('Not implemented for interface')

    def is_debuggable(self):
        """The node can be debugged (not used)."""
        raise NotImplementedError('Not implemented for interface')

    def is_profileable(self):
        """The node can be profiled (not used)."""
        raise NotImplementedError('Not implemented for interface')

    def is_queueable(self):
        """The node can be put in the execution queue."""
        raise NotImplementedError('Not implemented for interface')

    def is_armed(self):
        """The node is armed (ready to be validated)."""
        raise NotImplementedError('Not implemented for interface')

    def is_queued(self):
        """The node is in the execution queue."""
        raise NotImplementedError('Not implemented for interface')

    def is_executing(self):
        """The node is currently executing."""
        raise NotImplementedError('Not implemented for interface')

    def has_pending_request(self):
        """The execore is performing an action on the node."""
        raise NotImplementedError('Not implemented for interface')

    def is_successfully_executed(self):
        """The node has been successfully executed"""
        raise NotImplementedError('Not implemented for interface')

    def in_error_state(self):
        """The node has some kind of error."""
        raise NotImplementedError('Not implemented for interface')

    def is_configuration_valid(self):
        """The node configuration is valid."""
        # TODO(erik): Currently a misnomer, does not actually include the valid
        # state.
        raise NotImplementedError('Not implemented for interface')

    def is_initialized(self):
        """The node has been initialized."""
        raise NotImplementedError('Not implemented for interface')
