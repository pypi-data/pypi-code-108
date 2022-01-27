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
import PySide2.QtCore as QtCore

from .types import ElementInterface, Type, PortManagerInterface
from .port import Port


class FlowIO(PortManagerInterface, ElementInterface):
    port_created = QtCore.Signal(Port)

    def __init__(self, *args, optional=False, source_parent=None,
                 **kwargs):
        self._port_definition = kwargs.pop('port_definition', None)
        super().__init__(*args, **kwargs)

        self._source_parent = source_parent
        self._parent_port = None
        self._size = QtCore.QSizeF(50.0, 50.0)
        self._port = None
        self._parent_port = None
        self._generics_map = {}
        # Distinguish between ports that should have a parent port but are on
        # the top-level and ports that should not have one.
        self._has_parent_port = False
        self._optional = optional

    def initialize(self):
        """
        Initializer to be called from outside (after the view has
        been created).
        """
        # Create port for IO-node.
        self._port = self._create_port(uuid=self._uuid)
        self.port_created.emit(self._port)

    def create_parent_port(self, pos=None, uuid=None):
        self._has_parent_port = True

        if self._parent_port is None:
            self._parent_port = self._create_parent_port(
                uuid=uuid, pos=pos)
            if self._parent_port is not None:
                self._parent_port.mirror_port = self._port
                self._port.mirror_port = self._parent_port

    def delete_parent_port(self):
        self._has_parent_port = False
        port = self._parent_port
        if port is not None:
            self._parent_port = None
            self._mirror_port = None
            self._delete_parent_port(port)

    def add_parent_port(self, port):
        self._has_parent_port = True
        self._parent_port = port
        self._mirror_port = port
        self._add_parent_port(port)

    def disarm(self, port):
        self._flow.disarm(port)

    def arm(self, port):
        self._flow.arm(port)

    @property
    def is_linked(self):
        return self._flow.is_linked

    @property
    def source_uuid(self):
        return self._flow.source_uuid

    @property
    def uuid(self):
        return self._flow.uuid

    @property
    def port_uuid(self):
        return self._port.uuid

    @property
    def name(self):
        # Port can be None while creating subflow from selection.
        # Avoid exception.
        res = ''
        if self.port:
            res = self.port.name
        return res

    @name.setter
    def name(self, value):
        self.port.name = value
        self.port.description = value
        if self._parent_port is not None:
            self._parent_port.description = value
            self._parent_port.name = value
        self.name_changed.emit(value)

    @property
    def description(self):
        return self._port.description

    @property
    def parent_port(self):
        """
        The parent_port is the output or input port of the sub-flow
        node in its parent flow.
        :return: Parent port.
        """
        return self._parent_port

    @parent_port.setter
    def parent_port(self, value):
        raise AssertionError('Cannot set ports!')
        self._parent_port = value
        self.uuid = value.uuid

    @property
    def has_parent_port(self):
        # Used, for example, for root level flows to be able to tell if they
        # should have parent ports when they are linked. Root level flows
        # cannot normally have parent_ports since it should be attached to
        # non-existant parent flow.
        return self._has_parent_port

    def default_parent_port(self):
        return self.flow.default_parent_port(self)

    @property
    def default(self):
        if not self.is_optional():
            return self.default_parent_port()
        elif self.is_linked:
            return self._source_parent
        else:
            return self.has_parent_port

    @default.setter
    def default(self, value):
        if not self.is_optional():
            return self.default_parent_port()
        elif self.is_linked:
            self._source_parent = value
        else:
            self._has_parent_port = value

    @property
    def port(self):
        return self._port

    @property
    def input(self):
        raise NotImplementedError()

    @property
    def output(self):
        raise NotImplementedError()

    @property
    def outputs(self):
        raise NotImplementedError()

    @property
    def inputs(self):
        raise NotImplementedError()

    def add_input(self, port):
        raise NotImplementedError()

    def add_output(self, port):
        raise NotImplementedError()

    def port_viewer(self, port):
        raise NotImplementedError()

    def available_indices(self):
        raise NotImplementedError()

    @property
    def index(self):
        index_ = self._flow.port_index(self)
        if index_ is None:
            return 0
        return index_

    def port_index(self, port):
        if port == self._port:
            return 0
        else:
            return -1

    def to_copy_dict(self):
        if self._parent_port is not None:
            uuid = self._parent_port.uuid
        else:
            uuid = self.port_uuid
        source_uuid = self.port_uuid

        type_ = str(self.port.datatype)
        desc = self.port.description
        scheme = self.port.scheme

        flowio_dict = {
            'index': self.index,
            'type': type_,
            'scheme': scheme,
            'description': desc,
            'x': self.position.x(),
            'y': self.position.y(),
            'width': self.size.width(),
            'height': self.size.height(),
            'uuid': uuid,
            'parent': self._has_parent_port,
            'source_parent': self._source_parent,
            'source_uuid': source_uuid,
            'requiresdata': False,
            'preview': False,
            'namespace_uuid': self.namespace_uuid()}
        flowio_dict.update(self.get_properties())
        return flowio_dict

    def to_dict(self, stub=False, execute=True):
        if execute:
            uuid = self._parent_port.full_uuid
            source_uuid = self.port_uuid
        elif stub:
            uuid = self._parent_port.uuid
            source_uuid = self.port_uuid
        else:
            uuid = self.port_uuid
            source_uuid = None

        type_ = str(self.port.datatype)
        desc = self.port.description
        scheme = self.port.scheme

        flowio_dict = {
            'index': self.index,
            'type': type_,
            'scheme': scheme,
            'description': desc,
            'x': self.position.x(),
            'y': self.position.y(),
            'width': self.size.width(),
            'height': self.size.height(),
            'uuid': uuid,
            'parent': self.default,
            'source_parent': self._source_parent,
            'requiresdata': False,
            'preview': False}

        if source_uuid is not None:
            flowio_dict['source_uuid'] = source_uuid
        flowio_dict.update(self.get_properties())
        return flowio_dict

    def add(self, flow=None):
        if flow is not None:
            self._flow = flow
        self._flow_add_io()
        self._port.add(self._flow)
        self.port_created.emit(self._port)
        if self._parent_port is not None:
            self._parent_port.add()
            self._add_io_to_subflow()
            self._flow_port_created.emit(self._parent_port)

    def remove(self):
        self._flow_remove_port()
        if self._parent_port is not None:
            self._flow_remove_parent_port()
            # self._parent_port = None
        self._flow_remove_flow_io()

    def is_initialized(self):
        return True

    def is_abortable(self):
        return False

    def validate(self):
        return

    def _add_io_to_subflow(self):
        """Add the parent port as an input/output port of the subflow node."""
        raise NotImplementedError("Not implemented in base class.")

    def _flow_add_io(self):
        """Add this flowIO to the flow."""
        raise NotImplementedError("Not implemented in base class.")

    def is_executable(self):
        return False

    def is_optional(self):
        return self.flow.flowio_optional(self, self._optional)

    def can_set_optional(self):
        return self._flow.can_set_optional(self)

    def can_set_default(self):
        return (self.flow.is_linked or
                self.flow.is_root_flow())

    def set_optional(self, value):
        self._optional = value

    def get_properties(self):
        return {
            'name': self.name,
            'optional': self._optional,
            'default': self.default,
        }

    def set_properties(self, properties):
        if 'name' in properties:
            self.name = properties['name']
        if 'optional' in properties:
            self.set_optional(properties['optional'])
        if 'default' in properties:
            self.default = properties['default']


class FlowInput(FlowIO):

    _type = Type.FlowInput

    """FlowInput (input within a subflow)"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_port_created = super().port_created
        self._flow_port_created = self._flow.input_port_created

        self._name = 'FlowInput'

    def _add_io_to_subflow(self):
        self._flow.add_input(self._parent_port)

    def _flow_add_io(self):
        return self._flow.add_flow_input(self)

    def _create_port(self, uuid=None):
        return self._flow.create_output_port(
            self, generics_map=self._generics_map, uuid=uuid,
            port_definition=self._port_definition)

    def _create_parent_port(self, uuid=None, pos=None):

        if self._flow.is_subflow():
            # Only outside port on subflow flow.
            return self._flow.create_input(
                generics_map=self._generics_map, pos=pos,
                uuid=uuid, port_definition=self._port_definition)

    def _delete_parent_port(self, port):
        self.flow.remove_input(port)
        self.flow.input_port_removed.emit(port)

    def _add_parent_port(self, port):
        self._flow.input_port_created.emit(port)

    def _flow_remove_port(self):
        self._flow.remove_output_port(self._port)

    def _flow_remove_parent_port(self):
        self._flow.remove_input(self._parent_port)

    def _flow_remove_flow_io(self):
        return self._flow.remove_flow_input(self)

    @property
    def output(self):
        return self._port

    @property
    def outputs(self):
        return [self._port]

    @property
    def inputs(self):
        return []

    def add_output(self, port):
        self._port = port
        self._port.position = QtCore.QPointF(
            self._size.width(),
            self._size.height() / 2.0 - port.size.height() / 2.0)

    def port_viewer(self, port):
        source = self._parent_port._flow.source_port(self._parent_port)
        if source is not None:
            self._flow.app_core.port_viewer(source)

    def available_indices(self):
        return self._flow.available_flow_input_indices(self)

    def is_deletable(self):
        return self._flow.can_remove_flow_input(self)

    def can_reorder(self):
        return self._flow.can_reorder_flow_input(self)


class FlowOutput(FlowIO):
    """FlowOutput (output within a subflow)"""

    _type = Type.FlowOutput

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.input_port_created = super().port_created
        self._flow_port_created = self._flow.output_port_created
        self._name = 'FlowOutput'

    def _add_io_to_subflow(self):
        self._flow.add_output(self._parent_port)

    def _flow_add_io(self):
        return self._flow.add_flow_output(self)

    def _create_port(self, uuid=None):
        return self._flow.create_input_port(
            self, generics_map=self._generics_map, uuid=uuid,
            port_definition=self._port_definition)

    def _create_parent_port(self, uuid=None, pos=None):
        if self._flow.is_subflow():
            # Only outside port on subflow flow.
            return self._flow.create_output(
                generics_map=self._generics_map, uuid=uuid,
                port_definition=self._port_definition, pos=pos)

    def _delete_parent_port(self, port):
        self.flow.remove_output(port)
        self.flow.output_port_removed.emit(port)

    def _add_parent_port(self, port):
        self._flow.output_port_created.emit(port)

    def _flow_remove_port(self):
        return self._flow.remove_input_port(self._port)

    def _flow_remove_parent_port(self):
        return self._flow.remove_output(self._parent_port)

    def _flow_remove_flow_io(self):
        return self._flow.remove_flow_output(self)

    @property
    def input(self):
        return self._port

    @property
    def outputs(self):
        return []

    @property
    def inputs(self):
        return [self._port]

    def add_input(self, port):
        self._port = port
        self._port.position = QtCore.QPointF(
            -8.0, self._size.height() / 2.0 - port.size.height() / 2.0)

    def available_indices(self):
        return self._flow.available_flow_output_indices(self)

    def is_deletable(self):
        return self._flow.can_remove_flow_output(self)

    def can_reorder(self):
        return self._flow.can_reorder_flow_output(self)
