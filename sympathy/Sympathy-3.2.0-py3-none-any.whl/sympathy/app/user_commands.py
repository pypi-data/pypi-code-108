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
import json
import os.path
import itertools
import copy
import contextlib
import Qt.QtCore as QtCore
import Qt.QtWidgets as QtWidgets

from sympathy.utils import uuid_generator, log
from sympathy.utils.prim import uri_to_path, localuri, samefile
import sympathy.platform.exceptions as platform_exc
from sympathy.platform import workflow_converter

from . import library
from sympathy.app.flow.undo import UndoCommand, CommandFailed, MacroCommand
import sympathy.app.flow
import sympathy.app.util
import sympathy.app.common
import sympathy.app.flow_serialization
import sympathy.app.settings


__flow_factory = None


def _flow_factory(flowname):
    global __flow_factory
    if __flow_factory is None:
        __flow_factory = {flowtype.__name__: flowtype for flowtype in
                          [sympathy.app.flow.Flow, sympathy.app.flow.Lambda]}

    return __flow_factory[flowname]


core_logger = log.get_logger('core')


def copy_element_list_to_clipboard(flow_, element_list):
    """Helper for copying nodes without using the undo buffer."""
    flow_dict = sympathy.app.flow_serialization.partial_dict(
        flow_, element_list)
    data = json.dumps(flow_dict).encode('ascii')

    mime_data = QtCore.QMimeData()
    mime_data.setData(flow_.app_core.mime_type_flow(), data)
    QtWidgets.QApplication.clipboard().setMimeData(mime_data)

# TODO(erik): make pseudo commands in flow instead of
# implementing the logic here.


def propagate_flow_ctx(flow):
    @contextlib.contextmanager
    def inner():
        with flow.propagate_ctx():
            yield
    return inner


def propagate_flow_multi_ctx(flow):
    @contextlib.contextmanager
    def inner():
        with flow.propagate_ctx(), flow.infertype_ctx():
            yield
    return inner


def bulk_ctx(flow):
    @contextlib.contextmanager
    def inner():
        with flow.propagate_ctx(), \
                flow.infertype_ctx(), \
                sympathy.app.util.bulk_context(flow):
            yield
    return inner


def propagate_node_ctx(focus):
    @contextlib.contextmanager
    def inner():
        with focus.flow.propagate_ctx(focus), focus.flow.infertype_ctx():
            yield
    return inner


class CreateNodeCommand(UndoCommand):
    def __init__(self, node_id=None, library_node=None, flow=None, **kwargs):
        super().__init__(flow=flow)
        self._node_id = node_id
        self._node = None
        self._kwargs = kwargs

        if library_node is None:
            library_node = self._flow.app_core.library_node(node_id)
        self._library_node = library_node
        name = library_node.name
        self.set_text('Creating node {}'.format(name))

    def _first_redo(self):
        self._node = self._flow.create_node(
            node_id=self._node_id,
            library_node=self._library_node, **self._kwargs)

    def _redo(self):
        self._node.add(self._flow)

    def _undo(self):
        self._node.remove()

    def element_uuid(self):
        return self._node.uuid

    def created_element(self):
        return self._node


class CreateLibraryElementCommand(UndoCommand):
    def __init__(self, flow=None, node_id=None, library_node=None, **kwargs):
        super().__init__(flow=flow)
        self.set_text('Creating library element')

        if library_node is None:
            library_node = self._flow.app_core.library_node(node_id)

        if library_node.type == 'flow':
            self._cmd = InsertSubflowLinkCommand(
                flow=flow, node_id=node_id, library_node=library_node,
                **kwargs)
        else:
            self._cmd = CreateNodeCommand(
                flow=flow, node_id=node_id, library_node=library_node,
                **kwargs)

    def _redo(self):
        self._cmd.redo()

    def _undo(self):
        self._cmd.undo()

    def created_element(self):
        return self._cmd.created_element()

    def affected_flows(self):
        return self._cmd.affected_flows()


class DuplicateInputPortCommand(UndoCommand):
    def __init__(self, port):
        super().__init__(
            flow=port.node.flow, context=propagate_node_ctx(focus=port.node))
        self._port = port
        self._new_port = None
        self._index = None
        self.set_text('Creating node port')

    def _first_redo(self):
        self._new_port = self._port.node.create_named_input(
            self._port.name)
        self._index = self._new_port.index

    def _redo(self):
        self._flow.add_input_port(self._new_port)
        self._port.node.insert_named_input(self._index, self._new_port)

    def _undo(self):
        self._new_port.node.delete_input(self._new_port)

    def created_element(self):
        return self._new_port


class DuplicateOutputPortCommand(UndoCommand):
    def __init__(self, port):
        super().__init__(
            flow=port.node.flow, context=propagate_node_ctx(focus=port.node))
        self._port = port
        self._new_port = None
        self._index = None
        self.set_text('Creating node port')

    def _first_redo(self):
        self._new_port = self._port.node.create_named_output(
            self._port.name)
        self._index = self._new_port.index

    def _redo(self):
        self._flow.add_output_port(self._new_port)
        self._port.node.insert_named_output(self._index, self._new_port)

    def _undo(self):
        self._new_port.node.delete_output(self._new_port)

    def created_element(self):
        return self._new_port


class CreateNamedInputPortCommand(UndoCommand):
    def __init__(self, node, name):
        super().__init__(
            flow=node.flow, context=propagate_node_ctx(focus=node))
        self._node = node
        self._name = name
        self._new_port = None
        self._index = None
        self.set_text('Creating node port')

    def _first_redo(self):
        self._new_port = self._node.create_named_input(
            self._name)
        self._index = self._new_port.index

    def _redo(self):
        self._flow.add_input_port(self._new_port)
        self._new_port.node.insert_named_input(self._index, self._new_port)

    def _undo(self):
        self._node.delete_input(self._new_port)

    def created_element(self):
        return self._new_port


class CreateNamedOutputPortCommand(UndoCommand):
    def __init__(self, node, name):
        super().__init__(
            flow=node.flow, context=propagate_node_ctx(focus=node))
        self._node = node
        self._name = name
        self._new_port = None
        self.set_text('Creating node port')

    def _first_redo(self):
        self._new_port = self._node.create_named_output(
            self._name)
        self._index = self._new_port.index

    def _redo(self):
        self._flow.add_output_port(self._new_port)
        self._new_port.node.insert_named_output(
            self._index, self._new_port)

    def _undo(self):
        self._node.delete_output(self._new_port)

    def created_element(self):
        return self._new_port


class DeleteInputPortCommand(UndoCommand):
    def __init__(self, port):
        super().__init__(
            flow=port.node.flow, context=propagate_node_ctx(focus=port.node))
        self._port = port
        self._node = port.node
        self._index = port.index
        self._element_list = self._flow.connected_port_connections(
            [self._port])
        self.set_text('Deleting node port')

    def _redo(self):
        for element in self._element_list:
            element.remove()
        self._port.node.delete_input(self._port)

    def _undo(self):
        self._flow.add_input_port(self._port)
        self._node.insert_named_input(self._index, self._port)
        for element in reversed(self._element_list):
            element.add(self._flow)


class DeleteOutputPortCommand(UndoCommand):
    def __init__(self, port):
        super().__init__(
            flow=port.node.flow, context=propagate_node_ctx(focus=port.node))
        self._port = port
        self._node = port.node
        self._index = port.index
        self._element_list = self._flow.connected_port_connections(
            [self._port])
        self.set_text('Deleting node port')

    def _redo(self):
        for element in self._element_list:
            element.remove()
        self._port.node.delete_output(self._port)

    def _undo(self):
        self._flow.add_output_port(self._port)
        self._node.insert_named_output(self._index, self._port)
        for element in reversed(self._element_list):
            element.add(self._flow)


class DeleteFlowPortCommandBase(UndoCommand):
    def __init__(self, flowio, port):
        subflow = port.node
        super().__init__(
            flow=subflow.flow, context=propagate_node_ctx(focus=subflow))
        self._subflow = subflow
        self._flowio = flowio
        self._port = port
        self._element_list = self._flow.connected_port_connections(
            [self._port])

    def _redo(self):
        for element in self._element_list:
            element.remove()
        self._subflow.delete_parent_port(self._flowio)

    def _undo(self):
        self._subflow.add_parent_port(self._flowio, self._port)
        for element in reversed(self._element_list):
            element.add(self._flow)


class DeleteFlowInputPortCommand(DeleteFlowPortCommandBase):
    def __init__(self, port):
        flowio = port.mirror_port.node
        super().__init__(flowio, port)
        self.set_text('Deleting input port')


class DeleteFlowOutputPortCommand(DeleteFlowPortCommandBase):
    def __init__(self, port):
        flowio = port.mirror_port.node
        super().__init__(flowio, port)
        self.set_text('Deleting output port')


class CreateParentPortCommandBase(UndoCommand):
    def __init__(self, flowio):
        subflow = flowio.flow
        super().__init__(
            flow=subflow.flow, context=propagate_node_ctx(focus=subflow))
        self._flowio = flowio
        self._subflow = flowio.flow
        self._port = None

    def _first_redo(self):
        self._subflow.create_parent_port(self._flowio)
        self._port = self._flowio.parent_port

    def _redo(self):
        self._subflow.add_parent_port(
            self._flowio, self._port)

    def _undo(self):
        self._flowio.delete_parent_port()


class CreateParentInputPortCommand(CreateParentPortCommandBase):
    def __init__(self, flowio):
        super().__init__(flowio)
        self.set_text('Creating input port')


class CreateParentOutputPortCommand(CreateParentPortCommandBase):
    def __init__(self, flowio):
        super().__init__(flowio)
        self.set_text('Creating output port')


class CreateSubflowCommand(UndoCommand):
    def __init__(self, flow=None, cls=None, **kwargs):
        super().__init__(flow=flow)
        self._subflow = None
        self._factory = _flow_factory(cls) if cls else sympathy.app.flow.Flow
        self.set_text('Creating subflow')
        self._kwargs = kwargs

    def _first_redo(self):
        self._subflow = self._flow.create_function(
            self._factory, **self._kwargs)

    def _redo(self):
        self._subflow.add(self._flow)

    def _undo(self):
        self._subflow.remove()

    def element_uuid(self):
        return self._subflow.uuid

    def created_element(self):
        return self._subflow


class CreateFunction(UndoCommand):
    def __init__(self, factory, flow=None, **kwargs):
        super().__init__(flow=flow)
        self._factory = factory
        self._kwargs = kwargs
        self._subflow = None
        self.set_text('Creating function')

    def _first_redo(self):
        self._subflow = self._flow.create_function(
            self._factory, **self._kwargs)

    def _redo(self):
        self._subflow.add(self._flow)

    def _undo(self):
        self._subflow.remove()

    def element_uuid(self):
        return self._subflow.uuid

    def created_element(self):
        return self._subflow


class CreateLambdaCommand(CreateFunction):
    def __init__(self, **kwargs):
        super().__init__(sympathy.app.flow.Lambda, **kwargs)
        self.set_text('Creating lambda')


class CreateSubflowFromSelectionCommand(UndoCommand):

    def __init__(self, position, elements, flow_, **kwargs):
        super().__init__(flow=flow_, context=propagate_flow_multi_ctx(flow_))
        self._position = position
        self._elements = elements
        self._subflow = None
        self._external_connections = None
        self.set_text('Creating subflow from selection')

    def _first_redo(self):
        # Create stuff and store it as members
        self._subflow = self._flow.create_subflow(self._position)
        fixed_position = (self._position - QtCore.QPointF(
            self._subflow.size.width() / 2.0,
            self._subflow.size.height() / 2.0))
        self._subflow.position = fixed_position
        self._incoming, self._outgoing = (
            self._flow.external_connections_from_elements(self._elements))

        # Add/remove/move stuff storing subflow/parent connections
        for clist in itertools.chain(
                self._incoming.values(), self._outgoing.values()):
            for c in clist:
                c.remove(emit=False)
        self._flow.move_elements_to_flow(self._elements, self._subflow)
        self._subflow_connections, self._parent_connections = (
            self._flow.create_external_subflow_connections(
                self._subflow, self._incoming, self._outgoing))
        if self._flow.in_cycle(self._subflow):
            self._flow.app_core.display_custom_node_message(
                self._flow,
                warning=('Could not create subflow from selection which '
                         'would have become part of a cycle in the flow.'))
            self._undo()
            raise CommandFailed()

    def _redo(self):
        # Add/remove/move stuff
        self._subflow.add(self._flow)
        for clist in itertools.chain(self._incoming.values(),
                                     self._outgoing.values()):
            for c in clist:
                c.remove(emit=False)
        self._flow.move_elements_to_flow(
            self._elements, self._subflow)

        for c in self._subflow_connections:
            c.add(self._subflow, emit=False)
        for c in self._parent_connections:
            c.add(self._flow, emit=False)

    def _undo(self):
        # Add/remove/move stuff in reverse order
        for c in itertools.chain(self._subflow_connections,
                                 self._parent_connections):
            c.remove(emit=False)
        self._subflow.move_elements_to_flow(self._elements, self._flow)
        for clist in itertools.chain(
                self._incoming.values(), self._outgoing.values()):
            for c in clist:
                c.add(self._flow, emit=False)
        self._subflow.remove()

    def element_uuid(self):
        return self._subflow.uuid

    def created_element(self):
        return self._subflow


class UnlinkSubflowCommand(UndoCommand):
    """
    Unlink subflow.
    Implemented by trying to follow the same steps as you would when using the
    GUI:

    1. Create a new subflow.
    2. Edit the old subflow and copy everything.
    3. Paste into the new subflow.
    4. Redraw connections to the new subflow.
    5. Remove the old subflow.

    The clipboard is actually not used, instead the data is copied by
    serializing and deserializing which makes it pretty close.
    """
    def __init__(self, subflow):
        super().__init__(flow=subflow.flow)
        self._linked_subflow = subflow
        self._unlinked_subflow = None
        self._linked_connections = []
        self._unlinked_connections = []

        linked_info = self._linked_subflow.get_properties()
        # TODO: make handling of fields associated with the link handled by the
        # flow. An unlinked flow should not be able to have source_label
        # identifier.
        self._unlinked_info = dict(linked_info)
        self._unlinked_info.pop('source_label', None)
        self._unlinked_info['identifier'] = None
        self._unlinked_info['icon_filename'] = None
        self._unlinked_info['tag'] = None
        self.set_text('Unlinking subflow')

    def created_element(self):
        return self._unlinked_subflow

    def _first_redo(self):
        create_subflow_cmd = CreateSubflowCommand(
            position=self._linked_subflow.position, flow=self._flow,
            uuid=uuid_generator.generate_uuid())
        create_subflow_cmd.redo()

        subflow = create_subflow_cmd.created_element()
        element_list = list(itertools.chain(
            (e for e in self._linked_subflow.elements()
                if e.type not in sympathy.app.flow.Type.port_types),
            self._linked_subflow.shallow_text_fields()))

        flow_dict = copy.deepcopy(sympathy.app.flow_serialization.partial_dict(
            self._linked_subflow, element_list))
        deserializer = (
            sympathy.app.flow_serialization.FlowDeserializer.from_dict(
                flow_dict, self._flow.app_core))

        with self._flow.app_core.no_validate():
            deserializer.build_paste_flow(
                subflow, center=False,
                warn_on_errors=[platform_exc.LibraryError],
                parent_flow=self._flow)

        subflow.set_properties(self._unlinked_info)
        subflow.name = self._linked_subflow.name

        if self._linked_subflow.aggregation_settings:
            aggregation_settings = {}
            conf_view = self._linked_subflow.aggregation_settings.get(
                'conf_view')
            if conf_view is not None:
                aggregation_settings['conf_view'] = conf_view
            old_nodes = self._linked_subflow.shallow_nodes()
            new_nodes = subflow.shallow_nodes()
            old_selected_uuids = set(
                self._linked_subflow.aggregation_settings.get(
                    'selected_uuids', []))
            # Copying of selected uuids relies on the exact same ordering
            # of nodes and subflows.
            if len(old_nodes) != len(new_nodes):
                core_logger.critical(
                    'Cannot set selected nodes for aggregation.')
            elif old_selected_uuids:
                new_selected_uuids = aggregation_settings.setdefault(
                    'selected_uuids', [])
                for old_node, new_node in zip(old_nodes, new_nodes):
                    old_uuid = old_node.uuid
                    if old_uuid in old_selected_uuids:
                        new_selected_uuids.append(new_node.uuid)
            subflow.aggregation_settings = aggregation_settings

        self._unlinked_subflow = subflow

        incoming, outgoing = self._flow.external_connections_from_elements(
            [self._linked_subflow])

        incoming = incoming.get(self._linked_subflow, [])
        outgoing = outgoing.get(self._linked_subflow, [])

        self._linked_connections = list(
            itertools.chain(incoming, outgoing))

        for connection in incoming:
            new_connection = self._flow.create_connection(
                connection.source,
                self._unlinked_subflow.input(connection.destination.index))
            self._unlinked_connections.append(new_connection)

        for connection in outgoing:
            new_connection = self._flow.create_connection(
                self._unlinked_subflow.output(connection.source.index),
                connection.destination)
            self._unlinked_connections.append(new_connection)

        for connection in self._linked_connections:
            connection.remove()

        self._linked_subflow.remove()
        subflow.validate()

    def _redo(self):
        for connection in self._linked_connections:
            connection.remove()
        self._linked_subflow.remove()

        self._unlinked_subflow.add(self._flow)
        for connection in self._unlinked_connections:
            connection.add(self._flow)

    def _undo(self):
        for connection in self._unlinked_connections:
            connection.remove()
        self._unlinked_subflow.remove()

        self._linked_subflow.add(self._flow)
        for connection in self._linked_connections:
            connection.add(self._flow)

    def added_removed_flows(self):
        return [self._linked_subflow]


class InsertSubflowLinkCommand(UndoCommand):
    def __init__(self, flow=None, position=None, library_node=None,
                 filename=None, uuid=None, **kwargs):
        super().__init__(flow=flow)
        self.set_text('Inserting subflow as link')
        self._library_node = library_node
        self.create_subflow_cmd = None

        def flow_filenames(flow_):
            """Filename of flow and its parent flows."""

            while flow_:
                filename = flow_.filename
                if filename:
                    yield filename
                flow_ = flow_.flow

        def contains_same_filename(filename, filenames):
            """
            Returns True if any element of filenames refers to the
            same file as filename and False otherwise.
            """
            for flow_filename in filenames:
                if samefile(filename, flow_filename):
                    return True
            return False

        def flow_dict_filenames(flow_dict):
            """
            Return all flow filenames from flow dictionary.
            """
            def inner(flow_dict):
                filename = flow_dict.get('filename')
                if filename:
                    yield filename
                for child_flow_dict in flow_dict.get('flows', []):
                    for filename in inner(child_flow_dict):
                        yield filename

            res = list(inner(flow_dict))
            return res

        source_uri = None
        flow_filename = self._flow.root_or_linked_flow_filename

        if library_node:
            source_uri = uri_to_path(library_node.source_uri)
            filename = source_uri
        else:
            source_uri = filename

        if source_uri:
            if flow_filename:
                try:
                    source_uri = os.path.relpath(
                        filename, os.path.dirname(flow_filename))
                except ValueError:
                    # Path can't be made relative. Perhaps this flow and
                    # subflow are on different drives. Fall back to absolute
                    # path.
                    pass

            deserializer = sympathy.app.flow_serialization.FlowDeserializer(
                self._flow.app_core)
            deserializer.load_xml_file(filename)
            if not deserializer.is_valid():
                core_logger.critical('Failed to load %s', filename)

            loaded_flow_filenames = [filename] + flow_dict_filenames(
                deserializer.to_dict())
            flow_parent_filenames = flow_filenames(self._flow)

            # Ensure that insertion does not cause self referencing loops.
            # Exit early, without inserting, in such cases.
            for filename_ in loaded_flow_filenames:
                if contains_same_filename(
                        filename_, flow_parent_filenames):
                    core_logger.critical(
                        'Failed to insert "%s", because it would link to '
                        '"%s", its own parent.', filename, filename_)
                    return

            loaded_flow_filenames = [filename] + flow_dict_filenames(
                deserializer.to_dict())
            flow_parent_filenames = flow_filenames(self._flow)

            # Ensure that insertion does not cause self referencing loops.
            # Exit early, without inserting, in such cases.
            for filename_ in loaded_flow_filenames:
                if contains_same_filename(
                        filename_, flow_parent_filenames):
                    core_logger.critical(
                        'Failed to insert "%s", because it would link to '
                        '"%s", its own parent.', filename, filename_)
                    return

            self.create_subflow_cmd = CreateSubflowCommand(
                position=position, flow=self._flow,
                uuid=uuid_generator.generate_uuid(),
                library_node=library_node)

            self._deserializer = deserializer
            self._filename = source_uri
            flow_dict = deserializer.to_dict()
            self._source_uuid = flow_dict['uuid']
            self._source_label = flow_dict['label']
            self.flow_dict = flow_dict

    def _first_redo(self):
        if self.create_subflow_cmd is None:
            raise CommandFailed()
        self.create_subflow_cmd.redo()
        new_flow = self.created_element()
        filename = os.path.normpath(os.path.join(
            os.path.dirname(new_flow.flow.root_or_linked_flow_filename),
            self._filename))

        try:
            sympathy.app.common.load_flow_action(
                self._flow.app_core, new_flow, filename,
                self._deserializer,
                is_linked=True,
                warn_on_errors=[
                    platform_exc.ConflictingFlowLibrariesError],
                parent_flow=self._flow)
        except platform_exc.LibraryError:
            self.create_subflow_cmd.undo()
            raise CommandFailed()

        new_flow.source_uuid = self._source_uuid
        for port in itertools.chain(new_flow.inputs, new_flow.outputs):
            port.uuid = uuid_generator.generate_uuid()
        new_flow.set_linked(True)
        new_flow.source_uri = self._filename
        new_flow.source_label = self._source_label
        new_flow.library_node = self._library_node
        new_flow.name = ''

    def _redo(self):
        self.create_subflow_cmd.redo()

    def _undo(self):
        self.create_subflow_cmd.undo()

    def element_uuid(self):
        return self.created_element().uuid

    def created_element(self):
        return self.create_subflow_cmd.created_element()

    def added_removed_flows(self):
        return [self.created_element()]


class CreateFlowInputCommand(UndoCommand):
    def __init__(self, flow=None, port_definition_tuple=None, **kwargs):
        super().__init__(flow=flow)
        self._kwargs = kwargs
        if port_definition_tuple is not None:
            self._port_definition = library.PortDefinition(
                *port_definition_tuple)
        else:
            self._port_definition = None
        self._flow_input = None
        self.set_text('Creating flow input')

    def _first_redo(self):
        self._flow_input = self._flow.create_flow_input(
            port_definition=self._port_definition, **self._kwargs)

    def _redo(self):
        self._flow_input.add(self._flow)

    def _undo(self):
        self._flow_input.remove()

    def element_uuid(self):
        return self._flow_input.uuid

    def created_element(self):
        return self._flow_input


class CreateFlowOutputCommand(UndoCommand):

    def __init__(self, flow=None, port_definition_tuple=None, **kwargs):
        super().__init__(flow=flow)
        self._kwargs = kwargs
        if port_definition_tuple is not None:
            self._port_definition = library.PortDefinition(
                *port_definition_tuple)
        else:
            self._port_definition = None
        self._flow_output = None
        self.set_text('Creating flow output')

    def _first_redo(self):
        self._flow_output = self._flow.create_flow_output(
            port_definition=self._port_definition,
            **self._kwargs)

    def _redo(self):
        self._flow_output.add(self._flow)

    def _undo(self):
        self._flow_output.remove()

    def element_uuid(self):
        return self._flow_output.uuid

    def created_element(self):
        return self._flow_output


class ChangeFlowIOOrderInterface(UndoCommand):
    def __init__(self, flow_, new_order):
        super().__init__(flow=flow_)
        self.set_text("Changing port order")
        self._to_new_order = tuple(new_order)
        # Calculate the order for the reverse port ordering operation:
        # E.g. if new_order = [2,0,1,3,4], the order for the reverse operation
        # is [1,2,0,3,4]. In other words, when moving index 2 to position 0 the
        # reverse is to move index 0 to position 2.
        self._to_old_order = list(zip(*sorted(
            zip(new_order, range(len(new_order))))))[1]

    def _redo(self):
        raise NotImplementedError('Not implemented for interface')

    def _undo(self):
        raise NotImplementedError('Not implemented for interface')


class ChangeFlowInputOrderCommand(ChangeFlowIOOrderInterface):
    def _redo(self):
        self._flow.reorder_inputs(self._to_new_order)

    def _undo(self):
        self._flow.reorder_inputs(self._to_old_order)


class ChangeFlowOutputOrderCommand(ChangeFlowIOOrderInterface):
    def _redo(self):
        self._flow.reorder_outputs(self._to_new_order)

    def _undo(self):
        self._flow.reorder_outputs(self._to_old_order)


class CreateConnectionCommand(UndoCommand):
    def __init__(self, source_port, destination_port, flow_, uuid=None,
                 route_points=None, check_cycle=False, **kwargs):
        super().__init__(
            flow=source_port.node.flow,
            context=propagate_node_ctx(focus=source_port.node))
        self._uuid = uuid
        self._source_port = source_port
        self._destination_port = destination_port
        self._connection = None
        self._route_points = route_points
        self._check_cycle = check_cycle
        self.set_text('Creating connection')

    def _first_redo(self):
        self._connection = self._flow.create_connection(
            self._source_port, self._destination_port,
            uuid=self._uuid,
            route_points=self._route_points)

        if self._check_cycle:
            if (self._flow.in_cycle(self._source_port) or
                    self._flow.in_cycle(self._destination_port)):
                self._flow.app_core.display_custom_node_message(
                    self._flow,
                    warning=('Could not create connection which '
                             'would have formed a cycle in the flow.'))
                self._undo()
                raise CommandFailed()

    def _redo(self):
        self._connection.add(self._flow)

    def _undo(self):
        self._connection.remove()

    def element_uuid(self):
        return self._connection.uuid

    def created_element(self):
        return self._connection


class CreateTextFieldCommand(UndoCommand):
    def __init__(self, rectangle, flow_, uuid=None):
        super().__init__(flow=flow_)
        self._rectangle = rectangle
        self._uuid = uuid
        self._text_field = None
        self.set_text('Creating text field')

    def _first_redo(self):
        self._text_field = self._flow.create_text_field(
            self._rectangle, self._uuid)

    def _redo(self):
        self._text_field.add(self._flow)

    def _undo(self):
        self._text_field.remove()

    def element_uuid(self):
        return self._text_field.uuid

    def created_element(self):
        return self._text_field


class PasteElementListCommand(UndoCommand):

    def __init__(self, flow_, encoded_mime_data, mouse_anchor, app_core):
        super().__init__(flow=flow_, context=bulk_ctx(flow_))
        flow_dict = json.loads(encoded_mime_data)
        ports = flow_dict.get('flow', []).get('ports', {})

        if not flow_.can_create_flow_input():
            ports.pop('inputs')

        if not flow_.can_create_flow_output():
            ports.pop('outputs')

        self._deserializer = (
            sympathy.app.flow_serialization.FlowDeserializer.from_dict(
                flow_dict, app_core))

        self._mouse_anchor = mouse_anchor
        self.set_text('Pasting')
        self._top_level_created_elements = []
        self._top_level_created_connections = []
        self._element_list = []
        self._added_removed_flows = []

    def created_top_level_elements(self):
        return self._top_level_created_elements

    def _first_redo(self):
        with self._flow.app_core.no_validate():
            try:
                self._deserializer.build_paste_flow(
                    self._flow, self._mouse_anchor,
                    warn_on_errors=[
                        platform_exc.ConflictingFlowLibrariesError],
                    parent_flow=self._flow)
            except platform_exc.LibraryError:
                raise CommandFailed()

        self._top_level_created_elements = [
            cmd.created_element()
            for cmd in self._deserializer.created_nodes()
            if cmd.created_element().flow is self._flow]

        for node in self._top_level_created_elements:
            if node.type in {sympathy.app.flow.Type.Node,
                             sympathy.app.flow.Type.Flow}:
                node.validate()

        top_level_connections = [
            cmd.created_element()
            for cmd in itertools.chain(
                    self._deserializer.created_connections())
            if cmd.created_element().flow is self._flow]

        self._element_list = (self._top_level_created_elements +
                              top_level_connections)
        self._top_level_created_elements.extend(
            [r for c in top_level_connections for r in c.route_points])

        self._added_removed_flows.extend([
            cmd.created_element()
            for cmd in self._deserializer.created_nodes()
            if cmd.created_element().type == sympathy.app.flow.Type.Flow
            and cmd.created_element().is_linked])

    def _redo(self):
        for element in self._element_list:
            element.add(self._flow)

    def _undo(self):
        for element in reversed(self._element_list):
            element.remove()

    def added_removed_flows(self):
        return self._added_removed_flows


class RemoveElementCommand(UndoCommand):
    def __init__(self, element):
        super().__init__(
            flow=element.flow, context=propagate_flow_ctx(element.flow))
        self._element = element
        self.set_text('Removing item')
        self._remove_file = (
            sympathy.app.settings.instance().get('session_temp_files') ==
            sympathy.app.settings.session_temp_files_remove_unused)

        self._added_removed_flows = []
        if sympathy.app.flow.Type.is_flow(self._element):
            for subflow in itertools.chain(
                    [self._element], self._element.all_subflows()):
                if subflow.is_linked:
                    self._added_removed_flows.append(subflow)

    def element(self):
        return self._element

    def _first_redo(self):
        if not self._element.is_deletable():
            raise CommandFailed()
        self._redo()

    def _redo(self):
        if sympathy.app.flow.Type.is_node(self._element):
            if self._element.is_executing():
                self._element.abort()
            elif self._element.is_queued():
                self._element.disarm()

            if self._remove_file:
                if self._element.is_done():
                    self._element.disarm()
                self._element.remove_files()
        self._element.remove()

    def _undo(self):
        self._element.add(self._flow)

    def added_removed_flows(self):
        return self._added_removed_flows


class RemoveElementListCommand(MacroCommand):
    def __init__(self, flow_, element_list):
        self._connections = (
            sympathy.app.flow.Type.filter_connections(element_list))
        self._element_list = [
            e for e in element_list if e not in self._connections]

        # First connections, then everything else
        cmds = []
        element_set = set()
        for element in (
                self._connections +
                flow_.connected_connections(self._element_list,
                                            search_parent_flow=True) +
                self._element_list):

            if element not in element_set:
                element_set.add(element)
                cmd = RemoveElementCommand(element)
                cmds.append(cmd)

        super().__init__(commands=cmds, context=bulk_ctx(flow_))
        self.set_text('Removing {} elements'.format(len(element_list)))


class CutElementListCommand(RemoveElementListCommand):
    def __init__(self, flow_, element_list):
        super().__init__(flow_, element_list)
        copy_element_list_to_clipboard(flow_, element_list)


class MoveElementCommand(UndoCommand):
    def __init__(self, element, old_position, new_position):
        super().__init__(flow=element.flow)
        self._element = element
        self._old_position = old_position
        self._new_position = new_position
        self.set_text('Moving element')

    def _redo(self):
        self._element.position = self._new_position

    def _undo(self):
        self._element.position = self._old_position


class ResizeElementCommand(UndoCommand):
    def __init__(self, element, old_rect, new_rect):
        super().__init__(flow=element.flow)
        self._element = element
        self._old_rect = old_rect
        self._new_rect = new_rect
        self.set_text('Resizing element')

    def _redo(self):
        self._element.position = self._new_rect.topLeft()
        self._element.size = self._new_rect.size()

    def _undo(self):
        self._element.position = self._old_rect.topLeft()
        self._element.size = self._old_rect.size()


class EditNodeLabelCommand(UndoCommand):
    def __init__(self, element, old_label, new_label):
        super().__init__(flow=element.flow)
        self._element = element
        self._old_label = old_label
        self._new_label = new_label
        if not new_label:
            self.set_text('Clearing node label')
        else:
            self.set_text('Changing node label to {}'.format(new_label))

    def _redo(self):
        self._element.name = self._new_label

    def _undo(self):
        self._element.name = self._old_label


class EditTextFieldCommand(UndoCommand):
    def __init__(self, element, old_text, new_text):
        super().__init__(flow=element.flow)
        self._element = element
        self._old_text = old_text
        self._new_text = new_text
        self.set_text('Editing text field')

    def _redo(self):
        self._element.set_text(self._new_text)

    def _undo(self):
        self._element.set_text(self._old_text)


class EditTextFieldColorCommand(UndoCommand):
    def __init__(self, element, old_color, new_color):
        super().__init__(flow=element.flow)
        self._element = element
        self._old_color = old_color
        self._new_color = new_color
        self.set_text('Changing text field color')

    def _redo(self):
        self._element.set_color(self._new_color)

    def _undo(self):
        self._element.set_color(self._old_color)


class TextFieldOrderCommand(UndoCommand):
    def __init__(self, flow, current_model, direction):
        super().__init__(flow=flow)
        self._current_model = current_model
        self._direction = direction
        self._old_models = self._flow._text_fields[:]
        self.set_text('Changing text field order')

    def _redo(self):
        self._flow.change_text_field_order(
            self._current_model, self._direction)

    def _undo(self):
        self._flow.set_text_field_order(self._old_models)


class ExpandSubflowCommand(UndoCommand):
    def __init__(self, subflow):
        super().__init__(
            flow=subflow.flow, context=propagate_flow_multi_ctx(subflow.flow))
        self._subflow = subflow
        self.set_text('Expanding subflow {}'.format(subflow.display_name))
        self._elements = None
        self._subflow_connections = None
        self._parent_connections = None
        self._flat_connections = None
        self._unlink_cmd = None

    def _first_redo(self):
        subflow = self._subflow
        if self._subflow.is_linked:
            self._unlink_cmd = UnlinkSubflowCommand(self._subflow)
            self._unlink_cmd.redo_no_context()

            subflow = self._unlink_cmd.created_element()

        self._elements = [
            e for e in subflow.elements()
            if e.type in sympathy.app.flow.Type.main_types - {
                    sympathy.app.flow.Type.FlowInput,
                    sympathy.app.flow.Type.FlowOutput}]

        for e in self._elements:
            e.was_in_subflow = True

        for c in subflow.connections():
            for p in c.route_points:
                p.was_in_subflow = True
        self.__redo_nonlinked()

    def _redo(self):
        if self._subflow.is_linked:
            self._unlink_cmd.redo_no_context()
        self.__redo_nonlinked()

    def __redo_nonlinked(self):
        subflow = self._subflow
        if self._subflow.is_linked:
            subflow = self._unlink_cmd.created_element()

        if self._subflow_connections is None:
            self._subflow_connections, self._parent_connections = (
                self._flow.external_connections_from_subflow(subflow))
            self._flat_connections = (
                self._flow.external_connections_convert_to_flat(
                    subflow, self._subflow_connections,
                    self._parent_connections))

        emit = self._subflow.is_linked

        # Add/remove/move stuff in reverse order
        for c in self._subflow_connections + self._parent_connections:
            c.remove(emit=emit)
        subflow.move_elements_to_flow(self._elements, self._flow)
        for c in self._flat_connections:
            c.add(self._flow, emit=emit)
        subflow.remove()

    def _undo(self):
        # Add/remove/move stuff
        subflow = self._subflow
        if self._subflow.is_linked:
            subflow = self._unlink_cmd.created_element()

        subflow.add(self._flow)
        for c in self._flat_connections:
            c.remove(emit=False)
        self._flow.move_elements_to_flow(self._elements, subflow)

        for c in self._subflow_connections:
            c.add(subflow, emit=False)
        for c in self._parent_connections:
            c.add(self._flow, emit=False)

        if self._subflow.is_linked:
            self._unlink_cmd.undo_no_context()

    def added_removed_flows(self):
        if self._unlink_cmd is not None:
            return self._unlink_cmd.added_removed_flows()
        return []


class EditNodeBaseParameters(UndoCommand):
    def __init__(self, node, new_params_model, new_version=None):
        super().__init__(
            flow=node.flow, context=propagate_node_ctx(focus=node))
        self._flow = node.flow
        self._old_version = node.version
        self._new_version = new_version or node.version
        self._old_params = node.base_parameter_model
        self._new_params = new_params_model
        self._node = node
        self.set_text('Editing base parameters for node {}'.format(node.name))

    def _redo(self):
        self._node.version = self._new_version
        self._node.base_parameter_model = self._new_params
        self._node.validate()

    def _undo(self):
        self._node.version = self._old_version
        self._node.base_parameter_model = self._old_params
        self._node.validate()


class EditNodeParameters(UndoCommand):
    """Should not be used when the node has active overrides."""

    def __init__(self, node, new_params_model):
        super().__init__(
            flow=node.flow, context=propagate_node_ctx(focus=node))
        assert not node.has_overrides()
        self._old_params = node.parameter_model
        self._new_params = new_params_model
        self._node = node
        self.set_text('Editing parameters for node {}'.format(node.name))

    def _redo(self):
        self._node.parameter_model = self._new_params
        self._node.validate()

    def _undo(self):
        self._node.parameter_model = self._old_params
        self._node.validate()


class ChangeNodeOriginalNodeID(UndoCommand):
    def __init__(self, node, original_nodeid):
        super().__init__(flow=node.flow)
        self._node = node
        self._new_original_nodeid = original_nodeid
        self._old_original_nodeid = self._node.original_nodeid
        self.set_text('Setting original_nodeid for node {} to {}'.format(
            node.name, self._new_original_nodeid))

    def _redo(self):
        self._node.original_nodeid = self._new_original_nodeid

    def _undo(self):
        self._node.original_nodeid = self._old_original_nodeid


class EditWorkflowEnvironment(UndoCommand):
    def __init__(self, flow_, new_env, old_env):
        super().__init__(flow=flow_)
        self.set_text("Edit environment variables for workflow {}".format(
            flow_.display_name))
        self._new_env = new_env
        self._old_env = old_env

    def _redo(self):
        self._flow.environment = self._new_env

    def _undo(self):
        self._flow.environment = self._old_env


class EditNodeExecutionConfig(UndoCommand):
    def __init__(self, node, value):
        super().__init__(flow=node.flow)
        self.set_text(
            'Editing execution config for node {}'.format(node.name))
        self._node = node
        self._old_value = self._node.exec_conf_only
        self._new_value = value

    def _redo(self):
        self._node.exec_conf_only = self._new_value

    def _undo(self):
        self._node.exec_conf_only = self._old_value


class DeleteOverrideParametersForUUID(UndoCommand):
    """
    Intended to be used when the node associated with a certain uuid can't be
    found.
    """

    def __init__(self, subflow, uuid):
        super().__init__(flow=subflow.flow)
        self._subflow = subflow
        self._old_overrides = subflow.override_parameters.get(uuid)
        self._uuid = uuid
        self.set_text(
            'Removing override parameters for uuid {}'.format(uuid))

    def _redo(self):
        # Node doesn't exist so it should be enough to modify the subflows
        # override parameters directly.
        self._subflow.override_parameters.pop(self._uuid, None)

    def _undo(self):
        # Node doesn't exist so it should be enough to modify the subflows
        # override parameters directly.
        self._subflow.override_parameters[self._uuid] = self._old_overrides


class EditNodeOverrideParameters(UndoCommand):
    def __init__(self, subflow, node, new_params_model):
        super().__init__(
            flow=subflow.flow, context=propagate_node_ctx(focus=node))
        self._subflow = subflow
        self._old_overrides = node.get_override_parameter_model(subflow)
        self._new_overrides = new_params_model
        self._node = node
        self.set_text(
            'Editing override parameters for node {}'.format(node.name))

    def _redo(self):
        self._subflow.set_node_override_parameters(
            self._node, self._new_overrides)
        self._node.validate()

    def _undo(self):
        self._subflow.set_node_override_parameters(
            self._node, self._old_overrides)
        self._node.validate()


class CreateRoutePoint(UndoCommand):
    def __init__(self, flow_, conn, pos, src_pos, dst_pos):
        super().__init__(flow=flow_)
        self._conn = conn
        self._pos = pos
        self._src_pos = src_pos
        self._dst_pos = dst_pos

        self._route_point = None
        self.set_text('Adding connection route point')

    def _first_redo(self):
        self._route_point = self._conn.create_route_point(
            self._pos, self._src_pos, self._dst_pos)

    def _redo(self):
        self._route_point.add()

    def _undo(self):
        self._route_point.remove()


class EditSubflowLockStateCommand(UndoCommand):
    def __init__(self, subflow, new_locked_state):
        super().__init__(flow=subflow)
        self._new_state = new_locked_state
        self._old_state = subflow.is_locked()
        if new_locked_state:
            self.set_text('Locking subflow {}'.format(subflow.display_name))
        else:
            self.set_text('Unlocking subflow {}'.format(subflow.display_name))

    def _redo(self):
        self._flow.set_locked(self._new_state)

    def _undo(self):
        self._flow.set_locked(self._old_state)


class EditFlowSettingsCommand(UndoCommand):
    def __init__(self, top_flow, settings, deleted_uuids, deselected_nodes):
        """
        Constructor is called from appcore::execute_subflow_parameter_view_done
        """
        super().__init__(flow=top_flow, context=propagate_flow_ctx(top_flow))
        self.set_text(f'Editing settings for flow {self._flow.display_name}')
        self._flow = top_flow
        self._new_aggregation_settings = settings
        self._old_aggregation_settings = self._flow.aggregation_settings
        self._cmds = []

        for uuid in deleted_uuids:
            core_logger.debug(
                'Removing override parameters for deleted uuid %s', uuid)
            cmd = DeleteOverrideParametersForUUID(top_flow, uuid)
            self._cmds.append(cmd)

        for node in deselected_nodes:
            core_logger.debug('Removing override parameters for node %s', node)
            cmd = EditNodeOverrideParameters(top_flow, node, None)
            self._cmds.append(cmd)

    def aggregation_settings_are_equal(self):
        return self._new_aggregation_settings == self._old_aggregation_settings

    def _redo(self):
        for cmd in self._cmds:
            cmd.redo_no_context()
        self._flow.aggregation_settings = self._new_aggregation_settings

    def _undo(self):
        self._flow.aggregation_settings = self._old_aggregation_settings
        for cmd in reversed(self._cmds):
            cmd.undo_no_context()

    def affected_flows(self):
        affected_flows = super().affected_flows()
        for cmd in self._cmds:
            affected_flows.extend(cmd.affected_flows())
        return affected_flows


class LinkSubflowCommand(UndoCommand):
    def __init__(self, subflow, filename):
        super().__init__(flow=subflow.flow)
        self.set_text('Linking subflow to file {}'.format(filename))
        self._subflow = subflow
        self._old_is_linked = subflow.is_linked
        self._library_node = self._subflow.library_node

        parent_flow_path = os.path.dirname(
            subflow.flow.root_or_linked_flow_filename)
        try:
            subflow_relative_path = os.path.relpath(filename,
                                                    parent_flow_path)
        except ValueError:
            # Path can't be made relative. Perhaps this flow and parent are on
            # different drives. Fall back to absolute path.
            subflow_relative_path = filename

        self._old_source = subflow.source_uri
        self._new_source = subflow_relative_path
        self._old_source_uuid = subflow.source_uuid
        self._new_source_uuid = uuid_generator.generate_uuid()
        self._old_in, self._new_in = self._make_uuids(
            subflow.inputs)
        self._old_out, self._new_out = self._make_uuids(
            subflow.outputs)
        self._old_filename = subflow.filename
        self._new_filename = filename

    def _make_uuids(self, ports):
        old = []
        new = []
        for port in ports:
            old.append(port.uuid)
            new.append(uuid_generator.generate_uuid())
        return old, new

    def _set_uuids(self, ports, uuids):
        for port, uuid in zip(ports, uuids):
            self._flow.set_port_uuid(port, uuid)

    def _redo(self):
        self._subflow.set_linked(True)
        self._subflow.source_uri = self._new_source
        self._subflow.source_uuid = self._new_source_uuid
        self._subflow.filename = self._new_filename
        self._set_uuids(self._subflow.inputs, self._new_in)
        self._set_uuids(self._subflow.outputs, self._new_out)
        self._subflow.library_node = None

    def _undo(self):
        self._subflow.set_linked(self._old_is_linked)
        self._subflow.filename = self._old_filename
        self._subflow.source_uri = self._old_source
        self._subflow.source_uuid = self._old_source_uuid
        self._set_uuids(self._subflow.inputs, self._old_in)
        self._set_uuids(self._subflow.outputs, self._old_out)
        self._subflow.library_node = self._library_node

    def added_removed_flows(self):
        return [self._subflow]


class LinkSubflowToLibraryCommand(UndoCommand):

    def __init__(self, subflow, flow_info, filename, library_path):
        super().__init__(flow=subflow.flow)
        self._subflow = subflow
        self._filename = filename
        self._library_path = library_path
        self.set_text('Linking subflow to library node {}'.format(filename))
        self._set_properties_cmd = SetElementProperties(
            self._subflow, self._subflow, flow_info)
        self._link_subflow_cmd = None
        self._old_library_node = self._subflow.library_node
        self._library_node = None

    def _first_redo(self):
        filename = self._filename
        library_path = self._library_path

        try:
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError:
                pass

            try:
                # Set flow properties while saving to file.
                self._set_properties_cmd.redo()
                saved = sympathy.app.common.save_flow_to_file(
                    self._subflow, filename)
            finally:
                self._set_properties_cmd.undo()

            if not saved:
                raise Exception('Failed to save library flow')

            flow_data = workflow_converter.get_flow_data(filename)

            if flow_data:
                # Normally set by library_creator/library_manager.
                flow_data['library'] = localuri(library_path)
            else:
                raise Exception('Failed to open library flow')
        except Exception as e:
            core_logger.error(
                "Exception when linking subflow to library: %s", e)
            raise CommandFailed()

        library_node = self._subflow.app_core.library_node_from_definition(
            flow_data['id'], flow_data)
        self._subflow.app_core.register_node(
            library_node.node_identifier, library_node)

        self._library_node = library_node
        self._link_subflow_cmd = LinkSubflowCommand(
            self._subflow, filename)

        self._redo()

    def _redo(self):
        self._link_subflow_cmd.redo()
        self._set_properties_cmd.redo()
        self._subflow.library_node = self._library_node

    def _undo(self):
        self._link_subflow_cmd.undo()
        self._subflow.library_node = self._old_library_node
        self._set_properties_cmd.undo()

    def affected_flows(self):
        return (self._link_subflow_cmd.affected_flows()
                + self._set_properties_cmd.affected_flows())

    def added_removed_flows(self):
        return self._link_subflow_cmd.added_removed_flows()


class SetElementProperties(UndoCommand):
    def __init__(self, flow, element, new_properties):
        super().__init__(flow=flow)
        self.set_text(f'Changing properties for element: {element.name}')
        self._element = element
        self._new_properties = new_properties
        self._old_properties = element.get_properties()

    def _redo(self):
        self._element.set_properties(self._new_properties)

    def _undo(self):
        self._element.set_properties(self._old_properties)


class SetFlowLibraries(UndoCommand):
    def __init__(self, flow, new_libraries, new_pythonpaths):
        super().__init__(flow=flow)
        self.set_text('Changing flow libraries')
        self._new_libraries = new_libraries
        self._old_libraries = flow.library_paths()
        self._new_pythonpaths = new_pythonpaths
        self._old_pythonpaths = flow.python_paths()

    def _redo(self):
        old_conflicts = sympathy.app.util.library_conflicts(
            sympathy.app.util.library_paths())

        self._flow.set_libraries_and_pythonpaths(
            libraries=self._new_libraries, pythonpaths=self._new_pythonpaths)

        new_conflicts = sympathy.app.util.library_conflicts(
            sympathy.app.util.library_paths())

        if sympathy.app.util.library_conflicts_worse(old_conflicts,
                                                     new_conflicts):
            self._flow.app_core.display_custom_node_message(
                self._flow,
                warning=('Library change introduced new conflicts and was '
                         'therefore ignored. Using previous setting.'))
            self._undo()
            raise CommandFailed()

    def _undo(self):
        self._flow.set_libraries_and_pythonpaths(
            libraries=self._old_libraries, pythonpaths=self._old_pythonpaths)


class MigrateNode(MacroCommand):
    def __init__(self, node, auto_only=False):
        super().__init__(
            commands=[], flow=node.flow, context=propagate_flow_ctx(node.flow))
        self._node = node
        self._new_node = None
        self._auto_only = auto_only
        self._push_allowed = True

    def _update_migrations(self):
        if self._node.flow is not None:
            self._node._update_migrations()

    def push(self, cmd):
        if not self._push_allowed:
            raise CommandFailed()
        cmd.redo_no_context()
        self._cmds.append(cmd)

    def _first_redo(self):
        with self._flow.app_core.no_validate():
            try:
                self._node.migrate_node(self, auto_only=self._auto_only)
            except Exception:
                self._undo()
                import traceback
                self.flow().app_core.display_custom_node_message(
                    self._node, error="Failed to migrate node",
                    error_details=traceback.format_exc())
                raise

            for flow_ in self.flow().parent_flows():
                if not flow_.is_root_flow():
                    try:
                        self.push(MigrateNodeOverrides(self._node, flow=flow_))
                    except CommandFailed:
                        pass

        self._new_node = self._flow.node(self._node.uuid)
        self._new_node.validate()

        self._push_allowed = False

        if not self._cmds:
            raise CommandFailed()

        self._update_migrations()

    def _redo(self):
        with self._flow.app_core.no_validate():
            super()._redo()
        self._new_node.validate()
        self._update_migrations()

    def _undo(self):
        with self._flow.app_core.no_validate():
            super()._undo()
        self._node.validate()
        self._update_migrations()

    def text(self):
        # If there is only one subcommand, MacroCommand.text() will show the
        # text for that subcommand instead of this text. That is not desired
        # for this command.
        return f"Migrating node {self._node.name}"


class MigrateNodeOverrides(MacroCommand):
    def __init__(self, node, flow):
        super().__init__(
            commands=[], flow=flow, context=propagate_node_ctx(node))
        self._node = node
        self._subflow = flow
        self._flow = flow.flow
        self._tree_uuid = flow.tree_uuid(node)
        self._push_allowed = True

    def push(self, cmd):
        if not self._push_allowed:
            raise CommandFailed()
        cmd.redo_no_context()
        self._cmds.append(cmd)

    def _first_redo(self):
        try:
            self._subflow.migrate_overrides(self._tree_uuid, self)
        except CommandFailed:
            self._undo()
            raise
        else:
            self._push_allowed = False

        if not self._cmds:
            raise CommandFailed()

    def text(self):
        # If there is only one subcommand, MacroCommand.text() will show the
        # text for that subcommand instead of this text. That is not desired
        # for this command.
        return f"Migrating overrides for node {self._node.name}"
