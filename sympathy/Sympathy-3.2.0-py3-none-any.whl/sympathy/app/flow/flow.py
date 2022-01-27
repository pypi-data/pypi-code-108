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
import itertools
import functools
import collections
import contextlib
import copy
import json
import os.path

from PySide2 import QtCore

from sympathy.utils import uuid_generator
from sympathy.utils.prim import absolute_paths, localuri, format_display_string
from sympathy.utils import prim, log
from sympathy.platform import version_support as vs
from sympathy.platform import node_result
from sympathy.utils.context import format_deprecated_warn
from . types import NodeStatusInterface, Type, NodeInterface, Executors
from . connection import Connection, RoutePoint
from . flowio import FlowInput, FlowOutput
from . textfield import TextField
from . node import node_factory, Node
from . node import States
from . port import InputPort, OutputPort
from . import flowlib
from . import exceptions
from .. import filename_manager
from .. import library
from .. import signals
from .. import settings
from .. import migrations
from .. import common
from .. import graph
from .. import util


core_logger = log.get_logger('core')


def connection_by_end_position(connection):
    return (connection.destination.node.position.y(),
            connection.destination.index)


def connection_by_start_position(connection):
    return (connection.source.node.position.y(), connection.source.index)


def default_flow_filename():
    return os.path.join(os.getcwd(), '<unsaved-flow>.syx')


class PropagateContext:

    def __init__(self, flow, focus=None, all=False):
        self._flow = flow
        self._all = all
        self._nodes = [focus]
        self._flows_changed = set()

    def add_changed_flow(self, flow):
        self._flows_changed.add(flow)

    def get_changed_flows(self):
        return self._flows_changed

    @property
    def delayed(self):
        return self._flow is not None


class InfertypeContext:

    def __init__(self, delayed):
        self._delayed = delayed
        self.edges = []
        self.errors = []
        self.removed = []
        self.replacements = {}

    @property
    def delayed(self):
        return self._delayed


# TODO: ensure consistency. For example, source_uuid or identifier should not
# be set for a normal subflow (is_linked == False), identifier.
class Flow(NodeStatusInterface, NodeInterface):
    """
    A Flow is a node which contains other nodes. If it has no parent (None),
    it is the root flow.
    """
    # Flows have a few different configurations which determine the behavior.
    #
    # - Root flows, are flows that are connected to a file.
    #   - Linked flows:
    #     - File linked flows.
    #     - Library linked flows.
    #   - Library flows.
    #   - The current top flow.
    # - Non root flows.
    # - Sub flows.
    # - Locked flows.
    #
    # A root flow can, for example, contain environment variables.
    # File and library linked flows should be considered linked.
    # Library flows must be root flows.
    #
    # Linked flows can have overrides.
    # Locked flows will execute differently.
    # Etc.
    #
    # As a consequence it is easy to represent inconsistent states. For example
    # by changing the library link state without also changing the link state.
    # TODO: refactor representation to avoid accidentally ending up in
    # inconsistent states.

    node_created = QtCore.Signal(NodeInterface)
    node_removed = QtCore.Signal(NodeInterface)
    subflow_created = QtCore.Signal(NodeInterface)
    subflow_removed = QtCore.Signal(NodeInterface)
    connection_created = QtCore.Signal(Connection)
    connection_removed = QtCore.Signal(Connection)
    route_point_added = QtCore.Signal(RoutePoint)
    route_point_removed = QtCore.Signal(RoutePoint)
    flow_input_created = QtCore.Signal(FlowInput)
    flow_input_removed = QtCore.Signal(FlowInput)
    flow_output_created = QtCore.Signal(FlowOutput)
    flow_output_removed = QtCore.Signal(FlowOutput)
    text_field_created = QtCore.Signal(TextField)
    text_field_removed = QtCore.Signal(TextField)
    node_output_updated = QtCore.Signal(Node)
    overrides_changed = QtCore.Signal()
    icon_changed = QtCore.Signal()
    flow_updated = QtCore.Signal()
    before_remove = QtCore.Signal()
    description_changed = QtCore.Signal(str)
    execution_status_changed = QtCore.Signal()

    _base_name = 'Subflow'
    executor = Executors.Flow
    _type = Type.Flow
    class_name = 'Flow'
    _in_reload_ctx = False
    _propagate_ctx = PropagateContext(None)
    _infertype_ctx = InfertypeContext(False)

    _conf_port_name = '__sy_conf__'

    def __init__(self, app_core=None, library_node=None, identifier=None,
                 tag=None, undo_stack=None, **kwargs):
        super().__init__(**kwargs)
        self.app_core = app_core or self._flow.app_core
        self.unsaved_name = "Untitled flow"
        self.source_uuid = None
        self._source_label = None

        # We need to have one instance ID per root flow to be able to have
        # several instances open of the same flow simultaneously.
        self._namespace_uuid = None
        if self._flow is None:
            # Top level flow.
            self._namespace_uuid = uuid_generator.generate_uuid()
        self._conf_port = None
        self._flow_inputs = []
        self._flow_outputs = []
        self._graph = graph.DocumentGraph()
        self._nodes = {}
        self._subflows = {}
        self._connections = []
        self._text_fields = []
        self._filename = ''
        self._source_uri = ''
        self._name = ''
        self._node = library_node
        self._identifier = identifier
        self._tag = tag
        self._position = QtCore.QPointF()
        self._node_signals = {}
        self._progress = None
        self._name_counters = {}
        self._inputs = []
        self._outputs = []
        self._version = ''
        self._author = ''
        self._description = ''
        self._documentation = ''
        self._copyright = ''
        self._icon_filename = None
        self._parameters = {}
        self._override_parameters = {}
        self._is_linked = False
        self._aggregation_settings = None
        self._libraries = []
        self._pythonpaths = []
        self._locked = False
        self._broken_link = False
        self._state = None
        self._in_state_done = set()
        self._in_state_done_locked = set()
        self._in_state_armed = set()
        self._in_state_valid = set()
        self._in_state_invalid = set()
        self._in_state_queued = set()
        self._in_state_executing = set()
        self._in_state_error = set()
        self._locked_nodes = set()
        self._locked_operation = False
        self._signals = signals.SignalHandler()
        self._undo_stack = undo_stack
        self.update_state()
        self._update_migration_status()

    @property
    def name(self):
        return self.display_name

    @name.setter
    def name(self, value):
        self._name = value
        self.name_changed.emit(self.display_name)

    @property
    def source_label(self):
        return self._source_label

    @source_label.setter
    def source_label(self, value):
        self._source_label = value
        self.name_changed.emit(self.display_name)

    @property
    def link_label(self):
        return self._name

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if self._description != value:
            self._description = value
            self.description_changed.emit(value)

    @property
    def documentation(self):
        return self._documentation

    @documentation.setter
    def documentation(self, value):
        if self._documentation != value:
            self._documentation = value

    @property
    def copyright(self):
        if self._copyright:
            return self._copyright
        elif self._node:
            return self._node.copyright
        return ''

    @property
    def maintainer(self):
        if self._node:
            return self._node.maintainer
        return ''

    @property
    def node_identifier(self):
        if self._node:
            return self._node.node_identifier
        else:
            return None

    @property
    def library_node(self):
        return self._node

    @library_node.setter
    def library_node(self, value):
        old_library_node = self._node
        self._node = value
        if old_library_node is not value:
            self.icon_changed.emit()
        if value:
            self._is_linked = True

    @property
    def library(self):
        return self._node.library

    @property
    def identifier(self):
        return self._identifier or ''

    @identifier.setter
    def identifier(self, value):
        self._identifier = value

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, value):
        self._tag = value

    def _get_aggregated_nodes(self, uuids=None):
        res = []
        if uuids is None:
            uuids = self._aggregation_selected_uuids()
        for uuid in uuids:
            if uuid in self._nodes:
                res.append(self._nodes[uuid])
            elif uuid in self._subflows:
                res.extend(self._subflows[uuid]._get_aggregated_nodes())
        return res

    @property
    def aggregation_settings(self):
        return self._aggregation_settings

    @aggregation_settings.setter
    def aggregation_settings(self, value):
        org_uuids = self._aggregation_selected_uuids()
        self._aggregation_settings = value

        if (self._conf_port or self.flow and
                self.flow.get_operative_config_port(self)):
            # Get configured nodes.
            new_uuids = self._aggregation_selected_uuids()
            changed_uuids = sorted(
                set(new_uuids).symmetric_difference(org_uuids))
            aggregated_nodes = self._get_aggregated_nodes(changed_uuids)
            for node in aggregated_nodes:
                node.arm()

    def _aggregation_selected_uuids(self):
        res = []
        if self.aggregation_settings:
            res = self.aggregation_settings.get('selected_uuids') or res
        return res

    def _is_aggregating(self, node):
        return node.uuid in self._aggregation_selected_uuids()

    def get_operative_config_port(self, node):
        flow_ = self
        conf_port = None

        for flow_ in self.parent_flows():
            if flow_._is_aggregating(node):
                conf_port = flow_._conf_port or conf_port
            else:
                break
            node = flow_
        return conf_port

    def _paths(self, paths, abspath=False):
        if paths is None:
            return
        res = paths
        if abspath:
            res = absolute_paths(os.path.dirname(
                self.root_or_linked_flow_filename), paths)
        return res

    def library_paths(self, abspath=False):
        return self._paths(self._libraries, abspath=abspath)

    def python_paths(self, abspath=False):
        return self._paths(self._pythonpaths, abspath=abspath)

    def get_infertype_ctx(self):
        return self._infertype_ctx

    @contextlib.contextmanager
    def infertype_ctx(self):
        """
        Sets the type inference context.

        The context ensures that type inference will be deferred.

        Yields
        ------
        InfertypeContext
            Context recording changes relevant to type inference.

        """
        ctx = Flow._infertype_ctx
        if ctx.delayed:
            yield ctx
        else:
            ctx = InfertypeContext(True)
            Flow._infertype_ctx = ctx
            try:
                yield ctx
                if ctx.delayed:
                    flowlib.infertype_flow(self)
            finally:
                Flow._infertype_ctx = InfertypeContext(False)

    @contextlib.contextmanager
    def propagate_ctx(self, focus=None):
        """
        Sets the propagation context.

        The context ensures that state propagation will trigger on exit.

        When there is an existing propagate_ctx that context will be returned
        and no new context will be created. TO ENSURE PROPER PROPAGATION the
        context must be setup so that all nodes with changes to propagate are
        covered. This can be achieved by creating the first context as early as
        possible.

        For actions with a single node effect, the node context should normally
        be the affected node and for multiple of unknown effects the context
        should normally be the closest parent flow that contain all direct
        effects.

        Some actions may be directly handled or may for some reason not require
        propagation. For example, execute_done. In such cases, no
        propagate_ctx needs to be created.

        Parameters
        ----------
        focus : Node or Flow or None
            Propagate focus, when None all content of self becomes the focus.

        Yields
        ------
        PropagateContext
            Records the propagation flow and focus.
        """

        ctx = Flow._propagate_ctx
        if ctx.delayed:
            yield ctx
        else:
            ctx = PropagateContext(self, focus=focus)
            Flow._propagate_ctx = ctx
            try:
                yield ctx
                if focus:
                    if Type.is_node(focus):
                        focus.update_input_state()
                    self._propagate_state_change_from_node(focus)
                else:
                    self._propagate_state_change_for_all_nodes()
            finally:
                for subflow in ctx.get_changed_flows():
                    subflow.execution_status_changed.emit()
                Flow._propagate_ctx = PropagateContext(None)

    @contextlib.contextmanager
    def reload_libraries_and_pythonpaths(self, force=False):
        outer_reload = force or not Flow._in_reload_ctx
        Flow._in_reload_ctx = True
        try:
            python_paths = util.python_paths()
            library_paths = util.library_paths()
            yield
        finally:
            if outer_reload:
                Flow._in_reload_ctx = False
                if (set(util.python_paths()) != set(python_paths) or
                        set(util.library_paths()) != set(library_paths)):
                    self.app_core.reload_node_library()

    def update_flow_uuid(self, old_uuid, new_uuid):
        subflow = self.flow._subflows.pop(old_uuid)
        self.flow._subflows[new_uuid] = subflow

    def update_node_uuid(self, old_uuid, new_uuid):
        node = self.flow._nodes.pop(old_uuid)
        self.flow._nodes[new_uuid] = node
        core_logger.warning('Changing existing node: {node.uuid}')

    def _update_uuid(self, old_uuid, new_uuid):
        super()._update_uuid(old_uuid, new_uuid)
        if self.flow:
            self.update_flow_uuid(old_uuid, new_uuid)

    def set_libraries_and_pythonpaths(self, libraries=None, pythonpaths=None):
        libraries_changed = libraries != self._libraries

        self._libraries = libraries
        self._pythonpaths = pythonpaths

        with self.reload_libraries_and_pythonpaths(force=True):
            self.add_libraries_and_pythonpaths()

        if libraries_changed:
            self.app_core.change_flow_libraries(self)

    def _set_workflow_path_setting(self, key, value):
        """Helper method for setting workflow libraries or python paths."""
        # Only actual file flows should have settings.
        if not self.root_or_linked_flow() is self or not self._namespace_uuid:
            return
        settings_ = settings.instance()
        try:
            paths = settings_[key]
        except KeyError:
            paths = {}
        if value is None:
            try:
                del paths[self.namespace_uuid()]
            except KeyError:
                pass
        else:
            paths[self.namespace_uuid()] = value
        settings_[key] = paths

    def add_libraries_and_pythonpaths(self):
        self._set_workflow_path_setting('Python/workflow_library_paths',
                                        self.library_paths(abspath=True))
        self._set_workflow_path_setting('Python/workflow_python_paths',
                                        self.python_paths(abspath=True))
        for subflow in self._subflows.values():
            subflow.add_libraries_and_pythonpaths()

    def remove_libraries_and_pythonpaths(self):
        self._set_workflow_path_setting('Python/workflow_library_paths', None)
        self._set_workflow_path_setting('Python/workflow_python_paths', None)
        for subflow in self._subflows.values():
            subflow.remove_libraries_and_pythonpaths()

    @property
    def full_link_uuid(self):
        """
        Full uuid of the link for a linked subflow.

        If subflow is not linked use normal full_uuid.
        """
        if self.is_linked and self._flow is not None:
            return uuid_generator.join_uuid(
                self._flow.namespace_uuid(), self.uuid)
        else:
            return self.full_uuid

    def namespace_uuid(self):
        if self._flow is None or self._is_linked:
            res = self._namespace_uuid
            if res is None:
                # This indicates that the flow has been deleted! That is bad!
                core_logger.warning(
                    "Asked for full_uuid for deleted flow %s.", self.uuid)
                return '{00000000-0000-0000-0000-000000000000}'
            return res
        else:
            return super().namespace_uuid()

    #
    # Node type methods
    #

    def initialize(self):
        super().initialize()

    def reorder_inputs(self, new_order):
        # Only reorder ports if this is not a top level flow.
        if self.flow is not None:
            super().reorder_inputs(new_order)

        # Always reorder flow inputs.
        self._flow_inputs = [self._flow_inputs[i] for i in new_order]

    def reorder_outputs(self, new_order):
        # Only reorder ports if this is not a top level flow.
        if self.flow is not None:
            super().reorder_outputs(new_order)

        # Always reorder flow outputs.
        self._flow_outputs = [self._flow_outputs[i] for i in new_order]

    def _overrides_to_syx_format(self, overrides):
        res = {'__extra_info__': {}}
        for uuid, node_overrides in overrides.items():
            res[uuid] = node_overrides['data']
            res['__extra_info__'][uuid] = {
                'version': node_overrides['version'],
                'nodeid': node_overrides['nodeid'],
            }
        return res

    def _common_dict(self, stub=False):
        common_dict = {
            'id': self.identifier,
            'node_id': self.node_identifier,
            'label': self._name,
            'uuid': self.uuid,
            'x': self.position.x(),
            'y': self.position.y(),
            'width': self.size.width(),
            'height': self.size.height(),
            'is_linked': self._is_linked,
            'is_subflow': self.is_subflow(),
            'is_locked': self._locked,
            'icon': self._icon_filename,
            'broken_link': self._broken_link,
            'cls': type(self).__name__,
            'parameters': self._parameters,
            'environment': self.get_stored_environment(),
            'source': self._source_uri}
        if not (stub and self.is_linked):
            text_fields = sorted(
                self._text_fields, key=lambda field: field.order())
            text_fields = [
                textfield.to_dict() for textfield in text_fields]
            libraries = [prim.unipath(lib) for lib in self._libraries]
            pythonpaths = [prim.unipath(path) for path in self._pythonpaths]
            common_dict.update({
                'textfields': text_fields,
                'aggregation_settings': self._aggregation_settings,
                'libraries': libraries,
                'pythonpaths': pythonpaths,
                'version': self._version,
                'author': self._author,
                'description': self._description,
                'documentation': self._documentation,
                'copyright': self._copyright})

            tag = self.tag
            if tag:
                common_dict['tag'] = tag
        else:
            overrides = self._overrides_to_syx_format(self.override_parameters)
            common_dict.update({
                'overrides': overrides})

        return common_dict

    def _basic_input_ports(self, execute=False):
        res = []
        if self._conf_port:
            res.append(self._conf_port.to_dict(
                execute=execute))
        return res

    def to_copy_dict(self, base_node_params=True):
        flow_dict = self._common_dict()
        nodes = [node.to_copy_dict(base_params=base_node_params)
                 for node in self._nodes.values()
                 if node.type == Type.Node]
        flows = [subflow.to_copy_dict()
                 for subflow in self._subflows.values()]
        connections = [connection.to_copy_dict()
                       for connection in self._connections]

        # Choose the right uuids and labels depending on whether flow is
        # linked or not.
        full_uuid = self.full_uuid
        source_uuid = None
        source_label = None
        if self.is_linked:
            source_uuid = self.source_uuid
            full_uuid = self.full_link_uuid
            source_label = self.source_label

        flow_dict.update({
            'source_label': source_label,
            'label': self._name,
            'source_uuid': source_uuid,
            'full_uuid': full_uuid,
            'filename': self.filename,
            'overrides': self._overrides_to_syx_format(
                self.override_parameters),
            'nodes': nodes,
            'flows': flows,
            'ports': {
                'inputs': [port.to_copy_dict()
                           for port in self._flow_inputs],
                'outputs': [port.to_copy_dict()
                            for port in self._flow_outputs]},
            'basic_ports': {
                'inputs': self._basic_input_ports(),
                'outputs': [],
            },
            'connections': connections})
        return flow_dict

    def to_dict(self, execute=False, stub=False):
        flow_dict = self._common_dict(stub)
        if stub and self.is_linked:
            flow_dict.update({
                'source_uuid': self.source_uuid,
                'ports': {
                    'inputs': [port.to_dict(stub=True, execute=execute)
                               for port in self._flow_inputs
                               if not stub or port.parent_port],
                    'outputs': [port.to_dict(stub=True, execute=execute)
                                for port in self._flow_outputs
                                if not stub or port.parent_port]},
                'basic_ports': {
                    'inputs': self._basic_input_ports(
                        execute=execute),
                    'outputs': [],
                },
            })
        else:
            nodes = [node.to_dict(execute=execute)
                     for node in self._nodes.values()
                     if node.type == Type.Node]
            flows = [subflow.to_dict(execute, stub=True)
                     for subflow in self._subflows.values()]
            connections = [connection.to_dict(execute)
                           for connection in self._connections]

            label = self._name
            if execute:
                uuid = self.full_uuid
            elif self.is_linked:
                uuid = self.source_uuid
                label = self.source_label
            else:
                uuid = self.uuid

            flow_dict.update({
                'uuid': uuid,
                'label': label,
                'nodes': nodes,
                'flows': flows,
                'ports': {
                    'inputs': [port.to_dict(execute=execute)
                               for port in self._flow_inputs],
                    'outputs': [port.to_dict(execute=execute)
                                for port in self._flow_outputs]},
                'basic_ports': {
                    'inputs': self._basic_input_ports(execute=execute),
                    'outputs': [],
                },
                'connections': connections})
        return flow_dict

    def to_node_dict(self, data):
        """For builtins that want to execute as a specific flow."""
        # Could be done with parameter_helper but that could add some
        # dependencies.
        return {
            'parameters': {'data': {'type': 'group', 'flow':
                                    {'type': 'string', 'value':
                                     json.dumps(data)}},
                           'type': 'json'},
            'ports': {
                'inputs': (
                    [port.port.to_dict(execute=True)
                     for port in self._flow_inputs] +
                    self._basic_input_ports(execute=True)),
                'outputs': [port.port.to_dict(execute=True)
                            for port in self._flow_outputs]}}

    def is_subflow(self):
        return self._flow is not None

    def parent_flows(self):
        """
        Iterator over all parent flows starting in (and including) self to
        the root (last parent).
        """
        yield self
        for parent in super().parent_flows():
            yield parent

    def is_root_flow(self):
        return self._flow is None

    def root_or_linked_flow(self):
        for root in self.parent_flows():
            if root._is_linked:
                return root
        return root

    def add(self, flow=None):
        with self.reload_libraries_and_pythonpaths():
            self.add_libraries_and_pythonpaths()
            if flow is not None:
                self._flow = flow
            self._flow.add_subflow(self, emit=False)
            for port in self._inputs + self._outputs:
                port.add(self._flow)

            self._flow.subflow_created.emit(self)

    def remove(self):
        with self.reload_libraries_and_pythonpaths():
            self.before_remove.emit()
            if self._flow is not None:
                try:
                    self._flow.remove_subflow(self)
                except AttributeError:
                    pass
            self.remove_libraries_and_pythonpaths()

    def remove_files(self):
        super().remove_files()

        for node in self._nodes_and_subflows():
            node.remove_files()

    #
    # Flow type methods
    #

    def _change_connection_state(self, connection):
        if self._in_state_done_locked:
            destination = connection.destination
            if destination:
                node = destination.node
                if node and node.type == Type.FlowOutput:
                    self.update_state()

    def _add_node_state(self, node, changed_done=True):
        abort = False
        if self._locked_operation and node in self._locked_nodes:
            if node.is_queued() or node.is_executing():
                pass
            elif node.is_done_locked():
                pass
            elif node.is_done():
                self._locked_nodes.remove(node)
            elif node.in_error_state():
                self._locked_nodes.remove(node)
            else:
                self._locked_nodes = set()
                abort = True

        changed_done = self.__remove_node_state(node) or changed_done
        if node.is_done_locked():
            changed_done = True
            self._in_state_done_locked.add(node)
        elif node.is_done():
            changed_done = True
            self._in_state_done.add(node)
        elif node.in_error_state():
            self._in_state_error.add(node)
        elif node.is_executing():
            self._in_state_executing.add(node)
        elif node.is_queued():
            self._in_state_queued.add(node)
        elif node.is_armed():
            self._in_state_armed.add(node)
        else:
            if node.is_configuration_valid():
                self._in_state_valid.add(node)
            else:
                self._in_state_invalid.add(node)
        self.update_state(changed_done)
        if abort:
            self.abort_node(self)

    def __remove_node_state(self, node):
        changed_done = False
        if node in self._in_state_done:
            self._in_state_done.remove(node)
            return True
        if node in self._in_state_done_locked:
            self._in_state_done_locked.remove(node)
            return True

        for in_state in [self._in_state_armed,
                         self._in_state_valid,
                         self._in_state_invalid,
                         self._in_state_queued,
                         self._in_state_executing,
                         self._in_state_error]:
            if node in in_state:
                in_state.remove(node)
                break
        return changed_done

    def _remove_node_state(self, node, changed_done=True):
        self.update_state(self.__remove_node_state(node) or changed_done)

    def _add_node_signals(self, node):
        self._signals.connect_reference(node, [
            (node.state_changed, functools.partial(
                self.on_node_state_changed, node)),
            (node.progress_changed, functools.partial(
                self.on_node_progress_changed, node)),
            (node.parameters_changed, self.parameters_changed),
            (node.migration_status_changed, self._update_migration_status),
        ])

    def _add_node(self, node):
        self._existing_node_guard(node)
        self._graph.add_node(node)
        if node.uuid in self._nodes:
            core_logger.critical('Re-adding existing node: {node.uuid}')
        self._nodes[node.uuid] = node
        node.flow = self

    def add_node(self, node, emit=True):
        """Add a previously created node."""
        self._add_node(node)
        self._add_node_signals(node)
        if emit:
            self.node_created.emit(node)
        self._add_node_state(node)
        self._update_migration_status()

    def _remove_node_signals(self, node):
        # Disconnect all signals
        self._signals.disconnect_all(node)

    def remove_node(self, node):
        self.node_removed.emit(node)
        for port in node.inputs + node.outputs:
            port.remove()

        self._graph.remove_node(node)
        del self._nodes[node.uuid]
        node.flow = None
        self._remove_node_signals(node)
        self._remove_node_state(node)
        self._update_migration_status()

    def create_node(self, position=None, **kwargs):
        node = node_factory(**kwargs)
        node.position = position
        self.add_node(node, emit=True)
        # Handle special special signals during creation
        node.initialize()
        node.validate()
        deprecated = node.library_node.deprecated
        if deprecated and settings.instance()['deprecated_warning']:
            result = node_result.NodeResult()
            msg = format_deprecated_warn(*deprecated, help=True) + '\n'
            result.stderr = result.stderr_details = msg
            result.stderr_clean = True
            for node_message in util.node_messages(node, result):
                self.app_core.display_message(node_message)
        return node

    def _add_subflow(self, subflow):
        self._existing_subflow_guard(subflow)
        self._graph.add_node(subflow)
        if subflow.uuid in self._subflows:
            core_logger.critical('Re-adding existing subflow: {subflow.uuid}')
        self._subflows[subflow.uuid] = subflow

    def add_subflow(self, subflow, emit=True):
        self._add_subflow(subflow)
        self._add_node_signals(subflow)

        if emit:
            self.subflow_created.emit(subflow)
        self._add_node_state(subflow)
        self._update_migration_status()

    def remove_subflow(self, subflow):
        self.subflow_removed.emit(subflow)

        for port in subflow.inputs + subflow.outputs:
            port.remove()

        self._graph.remove_node(subflow)
        del self._subflows[subflow.uuid]
        subflow.flow = None
        self._remove_node_signals(subflow)
        self._signals.disconnect_all(subflow)
        self._remove_node_state(subflow)
        self._update_migration_status()

    def name_subflow(self, subflow):
        base_name = subflow._base_name
        counter = self._name_counters.get(base_name, 0)
        name = '{} {}'.format(base_name, counter)
        self._name_counters[base_name] = counter + 1
        subflow.name = name

    def create_function(self, factory, position=None, uuid=None, flow=None,
                        **kwargs):
        subflow = factory(uuid=uuid, parent=self, flow=self, **kwargs)
        subflow.position = position
        self.add_subflow(subflow, emit=False)
        self.name_subflow(subflow)
        self.subflow_created.emit(subflow)
        subflow.initialize()  # Correct here?
        if subflow.is_atom():
            subflow.validate()

        # Create ports in this method too?
        return subflow

    @QtCore.Slot(QtCore.QPointF)
    def create_subflow(self, position, uuid=None):
        return self.create_function(Flow, position, uuid)

    def external_connections_from_elements(self, elements):
        """Return external connections for a list of elements in this flow."""
        node_list = sorted(Type.filter_nodes(elements),
                           key=lambda n: n.position.y())
        inputs = set([port for node in node_list for port in node.inputs])
        outputs = set([port for node in node_list for port in node.outputs])

        #
        # Flow outputs
        #
        outgoing_connections = {}
        for connection in self._connections:
            source = connection.source
            if source in outputs and connection.destination not in inputs:
                connection_list = outgoing_connections.get(source.node, [])
                connection_list.append(connection)
                connection_list = sorted(
                    connection_list, key=connection_by_end_position)
                outgoing_connections[source.node] = connection_list

        #
        # Flow inputs
        #
        incoming_connections = {}
        for connection in self._connections:
            destination = connection.destination
            if destination in inputs and connection.source not in outputs:
                connection_list = incoming_connections.get(
                    destination.node, [])
                connection_list.append(connection)
                connection_list = sorted(
                    connection_list, key=connection_by_start_position)
                incoming_connections[destination.node] = connection_list

        return incoming_connections, outgoing_connections

    def external_connections_from_subflow(self, subflow):
        """Return external connections for a subflow."""
        connections = subflow.connections()
        subflow_connections = []
        for c in connections:
            src_type = c.source.node.type
            dst_type = c.destination.node.type
            if src_type == Type.FlowInput or dst_type == Type.FlowOutput:
                subflow_connections.append(c)

        parent_connections = [c for c in self.connections()
                              if (c.destination in subflow.inputs or
                                  c.source in subflow.outputs)]

        return subflow_connections, parent_connections

    def external_connections_convert_to_flat(
            self, subflow, subflow_connections, parent_connections):
        """Return flat external connections"""
        res = []

        def connect(src, dst):
            res.append(Connection(src, dst, self))

        by_src = collections.defaultdict(list)
        by_dst = collections.defaultdict(list)

        for parent_c in parent_connections:
            if parent_c.source.node is subflow:
                by_src[parent_c.source].append(parent_c)
            if parent_c.destination.node is subflow:
                by_dst[parent_c.destination].append(parent_c)

        for subflow_c in subflow_connections:
            src_port = subflow_c.source
            src_node = src_port.node
            src_type = src_node.type
            dst_port = subflow_c.destination
            dst_node = dst_port.node
            dst_type = dst_node.type

            if src_type == Type.FlowInput and dst_type == Type.FlowOutput:
                for parent_c0 in by_dst[src_node.parent_port]:
                    for parent_c1 in by_src[dst_node.parent_port]:
                        connect(parent_c0.source, parent_c1.destination)
            elif src_type == Type.FlowInput:
                for parent_c in by_dst[src_node.parent_port]:
                    connect(parent_c.source, dst_port)
            elif dst_type == Type.FlowOutput:
                for parent_c in by_src[dst_node.parent_port]:
                    connect(src_port, parent_c.destination)
            else:
                core_logger.critical(
                    'Unexpected internal connection in parent_connections.')
        return res

    def create_external_subflow_connections(
            self, subflow, incoming_connections, outgoing_connections):
        """
        Recreate connections that were broken when a subflow was created.
        Creates flow IOs as bridges between parent flow and subflow.
        Returns a list of connections
        """
        source_to_output = {}
        created_subflow_connections = []
        created_parent_connections = []
        created_port_pair_set = set()

        for outgoing in outgoing_connections.values():
            num_ports = len(outgoing)
            for (port_nr, connection) in enumerate(outgoing):
                source = connection.source
                if source in source_to_output:
                    flow_output = source_to_output[source]
                else:
                    flow_output = subflow.create_flow_output()
                    source_to_output[source] = flow_output

                port_pair = (source, flow_output.input)
                if port_pair not in created_port_pair_set:
                    created_subflow_connections.append(
                        subflow.create_connection(
                            source, flow_output.input, emit=False))

                    created_port_pair_set.add(port_pair)

                pos = source.node.position
                height_separation = flow_output.size.height() * 1.5
                flow_output.position = QtCore.QPointF(
                    pos.x() + flow_output.size.width() * 2.0,
                    pos.y() - (num_ports - 1) * height_separation / 2.0 +
                    height_separation * port_nr)
                connection.remove()
                created_parent_connections.append(self.create_connection(
                    flow_output.parent_port, connection.destination,
                    emit=False))

        source_to_input = {}
        created_input_connections = []
        for incoming in incoming_connections.values():
            num_ports = len(incoming)
            for port_nr, connection in enumerate(incoming):

                if connection.source in source_to_input:
                    new_input = False
                    flow_input = source_to_input[connection.source]
                else:
                    new_input = True
                    flow_input = subflow.create_flow_input()
                    source_to_input[connection.source] = flow_input

                port_pair = (flow_input.output, connection.destination)
                if port_pair not in created_port_pair_set:
                    created_subflow_connections.append(subflow.create_connection(
                        flow_input.output, connection.destination, emit=False))

                    created_port_pair_set.add(port_pair)

                pos = connection.destination.node.position
                height_separation = flow_input.size.height() * 1.5
                flow_input.position = QtCore.QPointF(
                    pos.x() - flow_input.size.width() * 2.0,
                    pos.y() - (num_ports - 1) * height_separation / 2.0 +
                    height_separation * port_nr)
                connection.remove(emit=False)
                if new_input:
                    new_connection = self.create_connection(
                        connection.source, flow_input.parent_port, emit=False)
                    created_input_connections.append(new_connection)
                    created_parent_connections.append(new_connection)

        # Fix connection/port order
        created_input_connections.sort(key=connection_by_start_position)
        new_port_order = [
            connection.destination.index
            for connection in created_input_connections]
        subflow.reorder_inputs(new_port_order)

        return created_subflow_connections, created_parent_connections

    def move_elements_to_flow(self, element_list, flow):
        """Move elements and internal connections to flow."""
        node_list = sorted(Type.filter_nodes(element_list),
                           key=lambda n: n.position.y())
        inputs = set([port for node in node_list for port in node.inputs])
        outputs = set([port for node in node_list for port in node.outputs])
        internal_connections = [connection for connection in self._connections
                                if (connection.source in outputs and
                                    connection.destination in inputs)]

        flow.import_(element_list, internal_connections)
        flow._state_changed()

    def connected_connections(self, node_list, search_parent_flow=False):
        """
        Returns (unique) connections stat start or end in a node in the
        node list.
        """
        all_ports = set([
            port for node in node_list
            if Type.is_port_manager(node)
            for port in node.inputs + node.outputs])

        # Add involved ports for parent node if an IO-node in a sub-flow
        # is in the node list.
        flow_io_nodes = Type.filter_flow_io_nodes(node_list)
        io_ports = {node.parent_port for node in flow_io_nodes}

        connections = self.connected_port_connections(all_ports)

        # Find connections to port in parent flow if possible.
        if search_parent_flow and self.flow:
            connections.extend(self.flow.connected_port_connections(io_ports))

        return connections

    def connected_port_connections(self, ports):
        return list(set([connection for connection in self.connections()
                         if (connection.source in ports or
                             connection.destination in ports)]))

    def add_input_port(self, port):
        self._graph.add_node(port)
        self._graph.add_edge(port, port.node)

    def create_input_port(self, node, port_definition=None,
                          generics_map=None, uuid=None, pos=None):
        if not port_definition:
            port_definition = library.AnyTypePortDefinition()

        port = InputPort(
            node, port_definition, generics_map,
            flow=self, uuid=uuid, parent=node)

        self._graph.add_node(port)
        self._graph.add_edge(port, node)
        if pos is None:
            node.add_input(port)
        else:
            node.insert_input(pos, port)
        return port

    def remove_input_port(self, port):
        if port in self._graph:
            self._graph.remove_node(port)

    def add_output_port(self, port):
        self._graph.add_node(port)
        self._graph.add_edge(port.node, port)

    def create_output_port(self, node, port_definition=None,
                           generics_map=None, uuid=None, pos=None):
        """Create an output port and attach it to node."""
        if not port_definition:
            port_definition = library.AnyTypePortDefinition()

        port = OutputPort(
            node, port_definition, generics_map,
            flow=self, uuid=uuid, parent=node)

        self._graph.add_node(port)
        self._graph.add_edge(node, port)

        if pos is None:
            node.add_output(port)
        else:
            node.insert_output(pos, port)

        port.filename = filename_manager.instance().allocate_filename(
            node.flow.root_flow().namespace_uuid(),
            node.full_uuid, port.index, 'sydata')
        return port

    def remove_output_port(self, port):
        if port in self._graph:
            self._graph.remove_node(port)

    def _add_flow_input(self, flow_input):
        self._existing_flow_input_guard(flow_input)
        self._graph.add_node(flow_input)
        self._flow_inputs.append(flow_input)

    def add_flow_input(self, flow_input, emit=True):
        self._add_flow_input(flow_input)
        if emit:
            self.flow_input_created.emit(flow_input)

    def remove_flow_input(self, input_):
        if input_ in self._graph:
            self._graph.remove_node(input_)
        if input_ in self._flow_inputs:
            del self._flow_inputs[self._flow_inputs.index(input_)]
        self.flow_input_removed.emit(input_)
        parent_port = input_.parent_port
        if parent_port is not None:
            self.input_port_removed.emit(parent_port)

    def _new_parent_port_uuid(self, flowio, uuid):
        if self.is_linked:
            if not uuid:
                uuid = uuid_generator.generate_uuid()
        else:
            uuid = flowio.port_uuid
        return uuid

    def _create_flowio(self,
                       flowio_cls,
                       add_flowio_func,
                       signal_flowio_created,
                       port_definition=None,
                       generics_map=None,
                       uuid=None, position=QtCore.QPointF(0, 0),
                       create_parent_port=True,
                       parent_port_uuid=None, **kwargs):

        if create_parent_port is None:
            create_parent_port = True

        flowio = flowio_cls(flow=self, parent=self,
                            port_definition=port_definition,
                            uuid=uuid, **kwargs)

        flowio.position = position
        add_flowio_func(flowio, emit=False)
        flowio.initialize()

        parent_port_uuid = self._new_parent_port_uuid(flowio, parent_port_uuid)

        if create_parent_port:
            flowio.create_parent_port(uuid=parent_port_uuid)
            if flowio.parent_port:
                self._infertype(flowio.parent_port, None)

        signal_flowio_created.emit(flowio)
        return flowio

    def create_flow_input(self, *args, **kwargs):
        return self._create_flowio(
            FlowInput,
            self.add_flow_input,
            self.flow_input_created,
            *args,
            **kwargs)

    def flow_input(self, uuid):
        for input_ in self._flow_inputs:
            if input_.port_uuid == uuid:
                return input_
        return None

    def flow_inputs(self):
        return list(self._flow_inputs)

    def flow_input_available(self, flow_input):
        """
        Used when scanning backwards to check if node inputs are connected
        in update_input_state. If source_port returned a flow_input this
        means that the parent_port is either optional or not connected.
        """
        assert flow_input in self._flow_inputs
        return flow_input.parent_port is None

    def remove_input(self, input_):
        if self._flow:
            self._flow.remove_input_port(input_)
        del self._inputs[self._inputs.index(input_)]
        self._update_port_layout()

        if self.is_config_port_name(input_.name):
            self._conf_port = None

    def remove_output(self, output_):
        if self._flow:
            self._flow.remove_output_port(output_)
            self._update_port_layout()
        del self._outputs[self._outputs.index(output_)]
        self._update_port_layout()

    def _add_flow_output(self, flow_output):
        self._existing_flow_output_guard(flow_output)
        self._graph.add_node(flow_output)
        self._flow_outputs.append(flow_output)

    def add_flow_output(self, flow_output, emit=True):
        self._add_flow_output(flow_output)
        if emit:
            self.flow_output_created.emit(flow_output)

    def remove_flow_output(self, output_):
        if output_ in self._graph:
            self._graph.remove_node(output_)
        if output_ in self._flow_outputs:
            del self._flow_outputs[self._flow_outputs.index(output_)]
        self.flow_output_removed.emit(output_)
        self.output_port_removed.emit(output_.parent_port)

    def create_flow_output(self, *args, **kwargs):
        return self._create_flowio(
            FlowOutput,
            self.add_flow_output,
            self.flow_output_created,
            *args,
            **kwargs)

    def flow_output(self, uuid):
        for output_ in self._flow_outputs:
            if output_.port_uuid == uuid:
                return output_
        return None

    def flow_outputs(self):
        return list(self._flow_outputs)

    def remove_route_point(self, route_point, emit=True):
        if emit:
            pass
        self.route_point_removed.emit(route_point)

    def add_route_point(self, route_point, emit=True):
        if emit:
            self.route_point_added.emit(route_point)

    def set_port_uuid(self, port, uuid):
        connections = self.connected_port_connections([port])

        for connection in connections:
            self._remove_connection(connection)
            self.connection_removed.emit(connection)
        port.uuid = uuid
        for connection in connections:
            self._add_connection(connection)
            self.connection_created.emit(connection)

    def _remove_connection(self, connection):
        del self._connections[self._connections.index(connection)]
        self._graph.remove_edge(connection.source, connection.destination)
        self._change_connection_state(connection)

    def _consistency_guard(self, ok, msg, *objs):
        # Here to ensure consistency. If it never triggers, we might be able to
        # remove it, but should rather extend and move the logic to
        # unit-tests. For example, each user command test might check that the
        # state is always consistent.
        if not ok:
            core_logger.critical(msg, *objs)

    def _existing_check_contained(self, obj, objs):
        return obj in objs

    def _existing_check_uuid_contained(self, obj, objs):
        return obj.uuid in set([o.uuid for o in objs])

    def _existing_object_guard(self, obj, objs=None, uuids=True):
        self._consistency_guard(
            not self._existing_check_contained(obj, self._graph),
            'Duplicating existing object %s', obj)
        if objs:
            self._consistency_guard(
                not self._existing_check_contained(obj, objs),
                'Duplicating existing object %s', obj)
            if uuids:
                self._consistency_guard(
                    not self._existing_check_uuid_contained(obj, objs),
                    'Duplicating existing uuid %s', obj)

    def _existing_connection_guard(self, connection):
        existing = set()
        existing_uuids = set()
        for c in self._connections:
            existing.add((c.source, c.destination))
            existing_uuids.add((c.source.uuid, c.destination.uuid))
        current = (connection.source, connection.destination)

        self._consistency_guard(
            not self._graph.has_edge(connection.source, connection.destination),
            'Duplicating edge in graph from %s to %s',
            connection.source.uuid, connection.destination.uuid)

        self._consistency_guard(
            not self._existing_check_contained(current, existing),
            'Duplicating connection object %s', connection)
        current = (connection.source.uuid, connection.destination.uuid)
        self._consistency_guard(
            not self._existing_check_contained(current, existing_uuids),
            'Duplication connection %s, by uuid pair %s', connection, current)

    def _existing_node_guard(self, node):
        self._existing_object_guard(node, list(self._nodes.values()))

    def _existing_subflow_guard(self, subflow):
        self._existing_object_guard(subflow, self.shallow_subflows())

    def _existing_flow_input_guard(self, flow_input):
        # TODO(erik): Ignoring uuid check since flow inputs do not have unique
        # uuids. Investigate if this can be changed.
        self._existing_object_guard(flow_input, self._flow_inputs, uuids=False)

    def _existing_flow_output_guard(self, flow_output):
        # TODO(erik): Ignoring uuid check since flow outputs do not have unique
        # uuids. Investigate if this can be changed.
        self._existing_object_guard(flow_output, self._flow_outputs,
                                    uuids=False)

    def _existing_text_field_guard(self, text_field):
        self._existing_object_guard(text_field, self._text_fields)

    def _add_connection(self, connection):
        self._existing_connection_guard(connection)

        self._graph.add_edge(
            connection.source,
            connection.destination, connection=connection)
        self._connections.append(connection)
        self._change_connection_state(connection)

    def add_connection(self, connection, emit=True):
        self._infertype(connection.source, connection.destination)

        connection.destination.filename = connection.source.filename
        self._add_connection(connection)
        self.connection_created.emit(connection)

    def remove_connection(self, connection, emit=True):
        if self._graph.has_edge(connection.source, connection.destination):
            self._remove_connection(connection)
            self.connection_removed.emit(connection)

            for port in (connection.source, connection.destination):
                self._infertype(connection.source, connection.destination,
                                disconnect=True)

            connection.destination.filename = ''
            return True
        else:
            return False

    def create_connection(self, src, dst, uuid=None, emit=True,
                          route_points=None):
        connection = Connection(src, dst, self, uuid, parent=self,
                                route_points=route_points)

        self._infertype(src, dst)

        dst.filename = src.filename
        self._add_connection(connection)
        self.connection_created.emit(connection)
        return connection

    def in_cycle(self, element):
        return self._graph.in_cycle(element)

    def remove_cycles(self):
        res = []
        while self.in_cycle(None):
            edges_in_cycles = list(self._graph.edges_in_cycles())
            # Slightly weird 2-level break construct.
            for src, dst in edges_in_cycles:
                if src.type == Type.OutputPort and dst.type == Type.InputPort:
                    for connection in self._connections:
                        if (connection.source is src and
                                connection.destination is dst):
                            self.remove_connection(connection)
                            res.append(connection)
                            break
                    else:
                        continue
                    break
        return res

    def _add_text_field(self, text_field):
        self._existing_text_field_guard(text_field)
        self._graph.add_node(text_field)
        self._text_fields.insert(0, text_field)

    def add_text_field(self, text_field):
        self._add_text_field(text_field)
        self.text_field_created.emit(text_field)

    def create_text_field(self, rectangle, uuid=None):
        text_field = TextField(self, uuid, parent=self)
        text_field.position = rectangle.topLeft()
        text_field.size = rectangle.size()
        self.add_text_field(text_field)
        return text_field

    def remove_text_field(self, text_field):
        self._graph.remove_node(text_field)
        if text_field in self._text_fields:
            del self._text_fields[self._text_fields.index(text_field)]
        self.text_field_removed.emit(text_field)

    def change_text_field_order(self, field, direction):
        def _reorder(direction, l, i):
            if direction == common.FRONT:
                e = l.pop(i)
                l.insert(0, e)
            elif direction == common.FORWARD and i != 0:
                e = l.pop(i)
                l.insert(i - 1, e)
            elif direction == common.BACKWARD:
                e = l.pop(i)
                l.insert(i + 1, e)
            elif direction == common.BACK:
                e = l.pop(i)
                l.append(e)
            return l

        i = self._text_fields.index(field)
        self._text_fields = _reorder(direction, self._text_fields, i)
        self.reorder_text_fields()

    def set_text_field_order(self, fields):
        self._text_fields = fields[:]
        self.reorder_text_fields()

    def reorder_text_fields(self):
        interval = 0.99 / len(self._text_fields)
        for j, model in enumerate(self._text_fields):
            order = 0.99 - float(j) * interval
            model.set_order(order)

    def import_(self, elements, connections):
        for c in connections:
            c.remove(emit=False)
        for element in sorted(elements, key=Type.comparison_key):
            element.remove()
            element.add(self)
        for c in connections:
            c.add(self, emit=False)

    def node(self, uuid, current_namespace=None, search_namespace=None):
        if current_namespace is None:
            current_namespace = self.namespace_uuid()
        current_namespace = (self._namespace_uuid or current_namespace)

        node = None
        if search_namespace is None or current_namespace == search_namespace:
            node = self._nodes.get(uuid, None)

        if node is None:
            for subflow in self._subflows.values():
                node = subflow.node(uuid, current_namespace=current_namespace,
                                    search_namespace=search_namespace)
                if node is not None:
                    break
        return node

    def elements(self):
        return self._graph.nodes()

    def can_edit(self):
        return not self.is_broken_link()

    def can_unlink(self):
        return True

    def can_expand(self):
        return True

    def can_save_as(self):
        return True

    def can_self_lock(self):
        return True

    def _in_parent_atom(self):
        flows = self.parent_flows()
        next(flows)
        return any(flow.is_self_atom() for flow in flows)

    def can_lock(self):
        return not self._in_parent_atom() and self.can_self_lock()

    def is_locked(self):
        """
        A locked flow is to be regarded more like an indivisible node. It
        will be fully executed on execution and will not produce
        intermediate data.

        Flows below a locked flow will never be locked.
        """
        return not self._in_parent_atom() and self.is_self_atom()

    def set_locked(self, checked):
        curr_locked = self._locked
        self._locked = checked

        if curr_locked and not checked:
            # Unlock and validate.
            self.arm()

        self._state_changed()
        self.icon_changed.emit()

    def all_nodes(self, remove_invalid=False, atom=False):
        node_list = [node for node in self._nodes.values()
                     if node.type == Type.Node]
        for subflow in self._subflows.values():
            if atom and subflow.is_atom():
                node_list.append(subflow)
            else:
                node_list.extend(
                    subflow.all_nodes(
                        remove_invalid=remove_invalid, atom=atom))
        if remove_invalid:
            node_list = [
                node for node in node_list if node.is_armed()]
        return node_list

    def shallow_nodes(self):
        return list(self._nodes_and_subflows())

    def shallow_subflows(self):
        return list(self._subflows.values())

    def shallow_text_fields(self):
        return list(self._text_fields)

    def connections(self):
        return list(self._connections)

    def connection_is_allowed(self, source, destination):
        """
        Check if a connection between the source and destination ports
        is allowed
        """
        if source.type != Type.OutputPort:
            return False
        if destination.type != Type.InputPort:
            return False
        if source.node == destination.node:
            return False
        if not source.matches(destination):
            return False
        if destination in [connection.destination
                           for connection in self._connections]:
            return False
        return True

    def is_connected(self, port):
        if port not in self._graph:
            return False

        # Check if this is an input port
        connected = False

        for pred in self._graph.predecessors(port):
            if pred.type == Type.OutputPort:
                connected = True
                break

        if not connected:
            for succ in self._graph.successors(port):
                if succ.type == Type.InputPort:
                    connected = True
                    break
        return connected

    def input_connection_to_port(self, input_port):
        """Returns the connection which has input_port as destination"""
        connections = [
            connections for connections in self._connections
            if connections.destination == input_port]
        if connections:
            return connections[0]
        else:
            return None

    def output_connections_from_port(self, output_port):
        """Returns a list of connections with output_port as source"""
        connections = [
            connections for connections in self._connections
            if connections.source == output_port]
        return connections

    def _source_element(self, element, atom=False):
        if element is None:
            return None

        if element not in self._graph:
            return None

        for pred in self._graph.predecessors(element):
            return pred

    def _source_element_cross(self, element, atom=False):
        res = None

        if element.type == Type.InputPort:
            res = self._source_element(element, atom=atom)

        elif element.type == Type.OutputPort:
            if element.node.type == Type.Node:
                res = None
            elif element.node.type == Type.Flow:
                if atom and element.node.is_atom():
                    res = None
                else:
                    res = element.mirror_port
            elif element.node.type == Type.FlowInput:
                res = element.node.parent_port
        else:
            assert False
        return res

    def source_port_traverse(self, element, previous=None, atom=False):
        if element is not None and element.type == Type.Node:
            return previous
        else:
            if element.type in [Type.FlowInput, Type.FlowOutput]:
                element = element.parent_port
                if element is None and previous:
                    return previous

            elif element.type == Type.FlowOutput:
                element = element.parent_port

            elif element.type == Type.Flow:
                if previous and element.is_atom():
                    if atom or previous.mirror_port is None:
                        return previous
                element = previous.mirror_port

            if element is None:
                return None

            next_elem = None
            flow = element.flow
            if flow:
                next_elem = flow._source_element(element, atom=atom)

            if next_elem is not None:
                return self.source_port_traverse(
                    next_elem, element, atom)
            else:
                if previous and element.type == Type.FlowOutput:
                    return element
        return None

    def source_port_no_traverse(self, element, previous=None):
        if element is not None and element.type in (
                Type.Node, Type.Flow, Type.FlowInput, Type.FlowOutput):
            return previous
        else:
            next_elem = self._source_element(element)
            if next_elem is not None:
                return self.source_port_no_traverse(next_elem, element)
        return None

    def source_port(self, element, traverse_subflows=True, atom=False):
        # TODO(erik): make the graph easier to query directly. Offering better
        # control and less built-in decisions. Queries should be done from
        # the flow anyway - without relying on recursion.
        if traverse_subflows:
            return self.source_port_traverse(element, atom=atom)
        else:
            return self.source_port_no_traverse(element)

    def has_source_port(self, element, traverse_subflows=True):
        return self.source_port(element, traverse_subflows) is not None

    def destination_ports(self, element, traverse_subflows=True, both=False,
                          atom=False):
        """
        Follows all output edges of element to input ports.

        Returns a list of all ports traversed. When traverse_subflows is True,
        the traversal will continue inside subflows, otherwise it will stop.

        If both is True, then both input ports and output ports will be added
        to the output, otherwise only input ports will be added.
        """
        # TODO(erik): make the graph easier to query directly. Offering better
        # control and less built-in decisions. Queries should be done from
        # the flow anyway - without relying on recursion.

        return_ports = []
        if element is None:
            return []

        if not any(self._graph.successors(element)):
            return return_ports

        if element.type == Type.InputPort:
            if element.node.type == Type.Node:
                return_ports.append(element)
            elif element.node.type == Type.FlowOutput:
                if traverse_subflows:
                    # If self._flow is None there is no destination port for
                    # this FlowOutput
                    if both:
                        return_ports.append(element)

                    if self._flow:
                        if element.node.parent_port:
                            return_ports.extend(self._flow.destination_ports(
                                element.node.parent_port, both=both,
                                atom=atom))
                else:
                    return_ports.append(element)
            elif element.node.type == Type.Flow:
                if atom and element.node.is_atom():
                    return_ports.append(element)

                elif traverse_subflows:
                    if both:
                        return_ports.append(element)

                    if element.mirror_port:
                        return_ports.extend(element.node.destination_ports(
                            element.mirror_port, both=both, atom=atom))
                    else:
                        if self.is_config_port_name(element.name):
                            for node_ in element.node._get_aggregated_nodes():
                                p = InputPort(
                                    node_, definition=element.port_definition)
                                return_ports.append(p)
                else:
                    return_ports.append(element)
        elif element.type == Type.OutputPort:
            if both:
                return_ports.append(element)
            for destination in self._graph.successors(element):
                element = destination
                try:
                    return_ports.extend(self.destination_ports(
                        element, traverse_subflows, both, atom=atom))
                except KeyError:
                    # For unconnected nodes.
                    pass
        else:
            assert(False)

        return return_ports

    def has_destination_port(self, element, traverse_subflows=True):
        return len(self.destination_ports(element, traverse_subflows)) > 0

    def connection_is_complete(self, source, destination):
        return (self.has_source_port(source) and
                self.has_destination_port(destination))

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, value):
        old_filename = self._filename

        self._filename = value
        if not self._name:
            # If name is empty, filename is used as display_name.
            # Time to emit name_changed.
            self.name_changed.emit(self.display_name)
        if old_filename != value:
            self.icon_changed.emit()

    @property
    def root_or_linked_flow_filename(self):
        """
        Read-only property containing the filename of the first parent workflow
        with a defined filename, including this workflow.
        """
        return self.root_or_linked_flow().filename or ''

    def state_string(self):
        return 'States: ' + str(self._state)

    @property
    def display_name(self):
        """Display name for the linked flow"""
        if self._name:
            return self._name
        else:
            return self.source_display_name

    @property
    def source_display_name(self):
        """Display name for the source flow"""
        if self.is_linked and self.source_label:
            return self.source_label
        elif self._filename:
            return vs.fs_decode(
                os.path.splitext(os.path.basename(self._filename))[0])
        else:
            return self.unsaved_name

    @property
    def full_display_name(self):
        if self._flow is None:
            return self.display_name
        else:
            if self._is_linked:
                return '{} \u26ad {}'.format(self._flow.full_display_name,
                                             self.display_name)
            else:
                return '{} > {}'.format(self._flow.full_display_name,
                                        self.display_name)

    @property
    def full_display_name_tuple(self):
        if self._flow is None:
            return (self.display_name,)
        else:
            return tuple(
                list(self._flow.full_display_name_tuple) +
                [format_display_string(self.display_name)])

    def reload(self):
        for node in self._topological_nodes():
            if node.type in [Type.Flow, Type.Node]:
                node.reload()

    def arm(self, port=None):
        if port and port.node.type in [Type.FlowInput, Type.FlowOutput]:
            return

        if self.is_executing() or self.is_queued():
            self.abort()
        self.reload()

    def disarm(self, port=None):
        if port and port.node.type in [Type.FlowInput, Type.FlowOutput]:
            return

        if self.is_executing() or self.is_queued():
            self.abort()

        starts = self._start_nodes(all_subflows_as_atom=True)
        for node in starts:
            node.disarm()

        for subflow in self._subflows.values():
            # Only reload subflows that have not been reloaded yet
            if subflow not in starts:
                subflow.disarm()

    def clear_error(self):
        for node_ in self.shallow_nodes():
            node_.clear_error()
        for flow_ in self.shallow_subflows():
            flow_.clear_error()

    def clear_locked_done(self, force=False):
        if force or self.is_locked():
            for flow_ in self.shallow_subflows():
                flow_.clear_locked_done()

            for node_ in self.shallow_nodes():
                node_.clear_locked_done()

    def _start_nodes(self, all_subflows_as_atom=False):
        def inner(elements):
            output = set()
            for element in elements:
                if element is not None and element.type in (Type.Flow, Type.Node):
                    if element.type == Type.Node:
                        output.add(element)
                    else:
                        if (all_subflows_as_atom or element.is_atom()):
                            output.add(element)
                        else:
                            output.update(element._start_nodes(
                                all_subflows_as_atom=all_subflows_as_atom))
                else:
                    output.update(inner(self._graph.successors(element)))
            return output

        return inner(self._graph.entry_nodes())

    def _end_nodes(self):
        """Returns a list of end nodes (nodes connected to the graph exit)"""
        # Rewind until output ports
        end_nodes = []
        for element in self._graph.exit_nodes():
            found = False
            while not found:
                if element is None:
                    found = True
                elif element.type == Type.Flow:
                    if element.is_atom():
                        end_nodes.append(element)
                    else:
                        end_nodes.extend(element._end_nodes())
                    found = True
                elif element.type == Type.Node:
                    end_nodes.append(element)
                    found = True
                if not found:
                    element = next(iter(self._graph.predecessors(element)), None)
                else:
                    found = True
        return end_nodes

    def _predecessor_node_edges(self, dsts, traversed_nodes=None, atom=True):
        """
        Returns a set of edges (with Node objects) that contains the
        graph up until 'dst'. Used for node execution.
        """
        if traversed_nodes is None:
            traversed_nodes = set()
        edge_set = util.OrderedSet()
        work = collections.deque(dsts)

        while work:
            dst = work.popleft()

            if dst and dst not in traversed_nodes:
                source_nodes = []

                if dst.type in (Type.Node, Type.FlowInput, Type.FlowOutput,
                                Type.Flow):
                    for p in dst.get_operative_inputs(execute=True):
                        source = p.flow.source_port(p, True, atom=atom)
                        if source:
                            source_nodes.append(source.node)
                traversed_nodes.add(dst)
                for src in source_nodes:
                    edge_set.update([(src, dst)])
                    work.append(src)

                # A single node without connections.
                if not source_nodes:
                    edge_set.update([(dst, dst)])

        return edge_set

    def _predecessor_node_graph(self, node=None, atom=True, starts=None):
        """
        Transforms the internal graph (of nodes, ports, flow i/o, subflows)
        to a flat (no subflow hierarchy) graph with only nodes and connections
        between them.

        Parameters
        ----------
        node
            Marks the end of graph. Set node to None to use all exit nodes!
            (caveat: the exit has to be in this).
        atom
            When True, such flows are considered as 1 node.
        starts
            Can be used to limit the beginning of the graph, when a start is
            reached, that branch of predecessor search ends.
        """
        if starts is not None:
            starts = set(starts)

        if node is None:
            # Find the end nodes
            edge_set = util.OrderedSet()
            edge_set.update(self._predecessor_node_edges(
                self._end_nodes(), atom=atom, traversed_nodes=starts))
        else:
            edge_set = node.flow._predecessor_node_edges(
                [node], atom=atom, traversed_nodes=starts)
        return self._node_edges_to_graph(list(edge_set), node)

    def _node_graph(self):
        return self._limited_node_graph(self._graph.nodes())

    def _limited_node_graph(self, nodes):

        def inplace_nodegraph(graph):
            ports = set()
            nodes = set(graph.nodes())
            for src, dst in list(graph.edges()):
                if src.type == Type.OutputPort and dst.type == Type.InputPort:
                    if src.node in nodes and dst.node in nodes:
                        graph.add_edge(src.node, dst.node)
                    graph.remove_edge(src, dst)
                    ports.add(src)
                    ports.add(dst)
                elif src.type == Type.InputPort:
                    graph.remove_edge(src, dst)
                    ports.add(src)
                elif dst.type == Type.OutputPort:
                    graph.remove_edge(src, dst)
                    ports.add(dst)

            for port in ports:
                graph.remove_node(port)

        subgraph = self._graph.subgraph(nodes, as_view=False)
        inplace_nodegraph(subgraph)
        return subgraph

    def _topological_nodes(self):
        nodes = self._graph.entry_descendants()
        return [n for n in self._limited_node_graph(nodes).topological_sort()
                if n.type in [Type.Node, Type.Flow]]

    def _propagate_state_change_for_all_nodes(self):
        """
        Returns a set of edges (with Node objects) that contains the
        graph up until 'node'. Used for node execution.
        """
        node_graph = self._limited_node_graph(self._graph.entry_descendants())
        self._propagate_state_change_from_graph(node_graph)

    def _propagate_state_change_from_node(self, node):
        """
        Returns a set of edges (with Node objects) that contains the
        graph up until 'node'. Used for node execution.
        """
        node_graph = self._limited_node_graph(self._graph.descendants(node))
        self._propagate_state_change_from_graph(node_graph)

    def update_input_state(self):
        # As it is, the state is already re-computed after each internal
        # change. Perhaps locked flows could do something here.
        # This would require looking at the actual input, like nodes do
        # by use of _input_event.
        pass

    def _propagate_state_change_from_graph(self, graph):
        # Might need to revisit this to avoid excessive waste, for example,
        # when a chain of nodes become done, one at a time.
        #
        # As a future next development, one could track if the nodes changed
        # their state and only for such cases process the successors. However
        # this would require first recording all changes state changes that
        # take place.
        visiting = set()

        def inner(flow, graph):
            visiting.add(flow)

            for node in graph.topological_sort():
                if node.type == Type.Node:
                    node.update_input_state()
                elif node.type == Type.Flow:
                    subgraph = node._node_graph()
                    inner(node, subgraph)
                    node.update_input_state()
                elif node.type == Type.FlowInput:
                    pass
                elif node.type == Type.FlowOutput:
                    pass

            flow.update_input_state()

            if flow.flow and flow.flow not in visiting:
                parent_descendants = set()
                parent_descendants.update(flow.flow._graph.descendants(flow))
                for port in flow.outputs:
                    parent_descendants.remove(port)

                subgraph = flow.flow._limited_node_graph(parent_descendants)
                inner(flow.flow, subgraph)

        return inner(self, graph)

    def _node_edges_to_graph(self, edges, node=None):
        sources = [edge[0] for edge in edges]
        sinks = [edge[1] for edge in edges]
        all_nodes = set(sources).union(set(sinks))
        if len(all_nodes) == 0 and (node is not None):
            all_nodes = set([node])

        edges = [(src, dst) for src, dst in edges if src is not dst]
        return graph.DocumentGraph(nodes=all_nodes, edges=edges)

    def _predecessor_node_graph_and_depths(self, node=None,
                                           remove_invalid=False, atom=True):
        g = self._predecessor_node_graph(node, atom=atom)
        node_depths = g.node_depths()

        levels = []

        def level(kv):
            return kv[1]

        for _, group in itertools.groupby(
                sorted(node_depths.items(), key=level), level):
            levels.append([n for n, l in group])

        if remove_invalid:
            reduced = []
            for group in levels:
                new_group = []
                for node in group:
                    if node.type == Type.FlowInput:
                        pass
                    elif node.is_armed():
                        new_group.append(node)
                reduced.append(new_group)
            levels = reduced

        nodes = [level for level in levels if len(level) > 0]
        return nodes, g

    def predecessor_node_depths(self, node=None, remove_invalid=False, atom=True):
        return self._predecessor_node_graph_and_depths(node, remove_invalid, atom)[0]

    def all_incoming_nodes_are_successfully_executed(self):
        def check(port):
            if port:
                node = port.node
                return (node.is_successfully_executed() and
                        not node.is_done_locked())
            else:
                if self._locked:
                    return True

                return False

        return all(
            check(self.flow.source_port(input)) for input in self.inputs)

    def all_incoming_nodes_are_queued_or_executing_or_done(self):
        def check(port):
            if port:
                return port.node.is_executing_or_queued_or_done()
            else:
                if self._locked:
                    return

                return False

        return all(
            check(self.flow.source_port(input)) for input in self.inputs)

    def node_set_list(self, node=None, remove_invalid=True, atom=True):
        """Helper function to get a set of all nodes below node as a list."""
        node_list = self.predecessor_node_depths(
            node, remove_invalid=remove_invalid, atom=atom)
        return {}.fromkeys(
            [node_ for level in node_list for node_ in level]).keys()

    def execute_node(self, node=None):
        self.app_core.execute_nodes(self.node_set_list(node))

    def debug_node(self, node=None):
        self.app_core.debug_nodes(list(self.node_set_list(node)))

    def profile_node(self, node=None):
        node_list = list(self.node_set_list(node, atom=True))
        self.app_core.profile_nodes(node_list[:-1], node_list[-1:])

    @QtCore.Slot()
    def execute_all_nodes(self):
        self.app_core.execute_nodes(
            self.node_set_list(None, remove_invalid=True))

    @QtCore.Slot()
    def profile_all_nodes(self):
        profile_node_list = self.all_nodes(remove_invalid=True, atom=True)
        all_node_list = self.node_set_list(None, atom=True)

        self.app_core.profile_nodes([node for node in all_node_list
                                     if node not in profile_node_list],
                                    profile_node_list)

    def is_atom(self):
        return self.is_locked()

    def is_self_atom(self):
        return self._locked

    def execute(self):
        try:
            if self.is_atom():
                self.execute_node(self)
            else:
                self.execute_all_nodes()
        except exceptions.SyFloatingInputError:
            # TODO(Erik): Improve handling of node state in Lambdas.
            pass

    def debug(self):
        pass

    def profile(self):
        if self.is_atom():
            self.profile_node(self)
        else:
            self.profile_all_nodes()

    def abort_node(self, node):
        self.app_core.abort_node(node)

    def abort(self):
        """
        Stop execution of a flow.

        Traverse graph breadth-first from entry to exit and abort the first
        nodes in each branch that are executing or queued.
        Only proceed from one node to another if no abort is performed.
        """
        if self.is_atom():
            self.abort_node(self)
        else:
            for node in reversed(self._topological_nodes()):
                if node.type in [Type.Flow, Type.Node]:
                    if node.is_queued() or node.is_executing():
                        node.abort()

    #
    # NodeStatusInterface
    #

    def configure_node_action(self, node):
        with self.propagate_ctx(node):
            node.clear_error()
        node.configure()

    def configure_action(self):
        with self.propagate_ctx():
            self.clear_error()
        self.app_core.execute_subflow_parameter_view(self, 'configure')

    def configure_with_wizard_action(self):
        with self.propagate_ctx():
            self.clear_error()
        self.app_core.execute_subflow_parameter_view(
            self, 'configure_with_wizard')

    def configure_with_tabbed_action(self):
        with self.propagate_ctx():
            self.clear_error()
        self.app_core.execute_subflow_parameter_view(
            self, 'configure_with_tabbed')

    def settings(self):
        self.app_core.execute_subflow_parameter_view(self, 'settings')

    @property
    def is_configured_with_wizard(self):
        return (self.aggregation_settings or {}).get(
            'conf_view') == 'WizardBuilder'

    @QtCore.Slot()
    def validate(self):
        for node in self._topological_nodes():
            if node.type in [Type.Flow, Type.Node]:
                core_logger.debug("Calling flow.node.Node.validate for node %s",
                                  node.uuid)
                node.validate()

    def _nodes_and_subflows(self):
        return itertools.chain(self._nodes.values(), self._subflows.values())

    def state(self):
        return self._state

    def _state_changed(self):
        self.state_changed.emit()
        if self._defer_update_execution_status():
            self._record_execution_status_changed()
        else:
            self.execution_status_changed.emit()

    def is_configurable(self):
        return not (self.is_queued() or self.is_executing())

    def is_executable(self):
        return self._state == States.armed

    def is_debuggable(self):
        return False

    def is_profileable(self):
        return self.is_executable()

    def is_abortable(self):
        return self.is_queued() or self.is_executing()

    def is_reloadable(self):
        return not self.is_abortable()

    def is_state_deletable(self):
        return not (self.is_executing() or self.is_queued())

    def is_deletable(self):
        return True

    def is_queueable(self):
        return self.states in (States.armed, States.done)

    def is_armed(self):
        return self._state == States.armed

    def is_queued(self):
        return self._state == States.queued

    def is_valid(self):
        return self._state == States.valid

    def is_executing(self):
        return self._state == States.executing

    def has_pending_request(self):
        for node in self._nodes_and_subflows():
            if node.has_pending_request():
                return True
        return False

    def is_successfully_executed(self):
        """
        Return True if all nodes are successfully executed. Return False if
        there are nodes that haven't been successfully executed. Return None if
        there are no nodes in the flow.

        Subflows without nodes are ignored.
        """
        return self.is_done()

    def in_error_state(self):
        return self._state == States.error

    def is_configuration_valid(self):
        return self._state != States.invalid

    def is_initialized(self):
        return True

    def is_done(self):
        return self._state in [States.done, States.done_locked]

    def is_done_locked(self):
        return self._state == States.done_locked

    def _atom_nodes(self):
        nodes = []
        if self.is_atom():
            nodes = _all_nodes_set_list(self, False, True)
        return nodes

    def _set_recursive_status(self, setter):
        atom_nodes = self._atom_nodes()
        if self.is_locked():
            self._locked_nodes = set(atom_nodes)

        for node in atom_nodes:
            setter(node)

    def set_queued(self):
        self._set_recursive_status(lambda node: node.set_queued())

    def execute_queued(self):
        self._locked_operation = True
        self.set_queued()

    def set_started(self):
        self._set_recursive_status(lambda node: node.set_started())

    def execute_started(self):
        self._locked_operation = True
        self.set_started()

    def execute_done(self, status):
        self._locked_operation = False
        self.set_done(status)
        self.update_state()

    def _output_node_set(self):
        res = set()
        for output in self.outputs:
            source_port = self.source_port(output)
            node = None
            if source_port:
                node = source_port.node
                if node:
                    res.add(node)
        return res

    def _contained_output_node_set(self):
        """
        Return set of nodes connected to the output ports
        that are contained within the flow.

        This eliminates output nodes that are in fact before
        self.
        """
        contained_flows = {self}
        contained_output_nodes = set()

        for node in self._output_node_set():
            parent_flows = set()
            flow = node.flow

            while flow is not None and flow not in contained_flows:
                parent_flows.add(flow)
                flow = flow.flow
            if flow in contained_flows:
                contained_flows.update(parent_flows)
                contained_output_nodes.add(node)

        return contained_output_nodes

    def set_child_done(self, node, result, locked=None):
        org_locked = locked
        if locked is None:
            locked = self.is_locked()

        if org_locked or (
                locked and node not in self._contained_output_node_set()):
            node.set_done(result, locked=locked)
        else:
            node.set_done(result)

    def set_done(self, result, locked=None):
        def set_locked_done(flow, locked):
            for subflow in flow.shallow_subflows():
                set_locked_done(subflow, locked)

        if locked is None:
            locked = True

        output_node_set = self._contained_output_node_set()

        for subflow in self.shallow_subflows():
            set_locked_done(subflow, locked)

        for node in self._atom_nodes():
            node.set_done(
                result, locked=locked and node not in output_node_set)

    def _arg_or_all_nodes(self, nodes):
        nodes = nodes
        if nodes is None:
            nodes = self._atom_nodes()
        return nodes

    def set_aborting(self, child_nodes=None):
        for node in self._arg_or_all_nodes(child_nodes):
            node.set_aborting()

    def set_aborted(self, child_nodes=None):
        for node in self._arg_or_all_nodes(child_nodes):
            node.set_aborted()

    def execute_aborting(self, child_nodes=None):
        self.set_aborting(child_nodes)
        self.update_state()

        for node in reversed(self._topological_nodes()):
            if node.type in [Type.Flow, Type.Node]:
                if node.is_queued() or node.is_executing():
                    node.abort()

    def execute_aborted(self, child_nodes=None):
        def visit_predecessors(graph, work, ignore):
            visited = set()
            while work:
                element = work.pop()
                if element not in visited:
                    visited.add(element)
                    if element not in ignore:
                        yield element
                        work.extend(graph.predecessors(element))

        self.set_aborted(child_nodes)
        if self._locked_operation:
            # Avoid searching previous flows.
            starts = {self.flow.source_port(input, atom=False).node
                      for input in self.inputs}
            graph = self._predecessor_node_graph(atom=False, starts=starts)
            lock_nodes = set()
            keep_starts = []

            for element in visit_predecessors(
                    graph, list(graph.exit_nodes()), starts):
                if element.type in [Type.Flow, Type.Node]:
                    state = element.state()
                    if state in [States.error, States.done]:
                        keep_starts.append(element)
                    elif state == States.done_locked:
                        lock_nodes.add(element)

            keep_nodes = set(visit_predecessors(graph, keep_starts, starts))

            for element in lock_nodes.difference(keep_nodes):
                element.arm()

        self._locked_operation = False

    @QtCore.Slot(NodeInterface)
    def on_node_is_executing(self, node):
        pass

    def _count_progress(self):
        total_number_of_nodes = 0
        total_progress = 0.0
        for node in self._nodes.values():
            if node.is_queued():
                total_number_of_nodes += 1
            elif node.is_successfully_executed():
                total_progress += 100.0
                total_number_of_nodes += 1
            elif node.is_executing():
                total_progress += node.progress()
                total_number_of_nodes += 1

        for subflow in self._subflows.values():
            number_of_nodes, progress = subflow._count_progress()
            total_number_of_nodes += number_of_nodes
            total_progress += progress

        return total_number_of_nodes, total_progress

    def _is_empty(self):
        if len(self._nodes):
            return False
        for subflow in self._subflows.values():
            if not subflow._is_empty():
                return False
        return True

    def _new_state(self):
        if self._broken_link:
            new_state = States.error
        elif self._is_empty():
            # Empty flows are ARMED, but are ignored when calculating the state
            # of their parent flows.
            new_state = States.done
        else:
            new_state = 0
            if self._in_state_error:
                new_state = States.error
            elif self._in_state_executing:
                new_state = States.executing
            elif self._in_state_queued:
                new_state = States.queued
            elif self._in_state_invalid:
                new_state = States.invalid
            elif self._in_state_valid:
                new_state = States.valid
            elif self._in_state_armed:
                new_state = States.armed
            elif self._in_state_done_locked:
                output_node_set = self._output_node_set()
                # TODO(erik): Implement cheaper test checking nodes as they
                # change state instead of all output nodes after each change.
                locked_state = (States.executing
                                if self._locked_operation
                                else States.done_locked)
                new_state = (locked_state if
                             any(n for n in output_node_set
                                 if n.is_done_locked()) else States.done)
            elif self._in_state_done:
                new_state = States.done
            else:
                new_state = States.armed
        return new_state

    def update_state(self, emit=True):
        """
        Loop through child nodes/subflows to determine the current state of
        this flow.
        """
        old_state = self._state
        new_state = self._new_state()
        changed = new_state != old_state
        self._state = new_state
        if emit or changed:
            self._state_changed()
            if new_state == States.executing and old_state != States.queued:
                self._progress = None

    def _update_progress(self):
        total_number_of_nodes, total_progress = self._count_progress()
        new_progress = int(
            total_progress / total_number_of_nodes
            if total_number_of_nodes > 0 else 1)
        self.update_progress(new_progress)

    def update_progress(self, value):
        new_progress = int(value)
        if new_progress != self._progress:
            self._progress = new_progress
            self.progress_changed.emit(new_progress)

    def update_child_progress(self, node, progress):
        node.update_progress(progress)

    @QtCore.Slot(NodeInterface)
    def on_node_state_changed(self, node):
        self._add_node_state(node)
        if node.is_successfully_executed():
            self._update_progress()

    @QtCore.Slot(NodeInterface, float)
    def on_node_progress_changed(self, node, progress=0):
        self._update_progress()

    def progress(self):
        return self._progress

    @property
    def ok(self):
        return not self._broken_link

    def _update_migration_status(self):
        migration_statuses = set()
        for node in itertools.chain(
                self._nodes.values(), self.shallow_subflows()):
            migration_statuses.add(node.migration_status)

        migration_statuses.update(self._overrides_migration_status())

        if 'red' in migration_statuses:
            status = 'red'
        elif 'yellow' in migration_statuses:
            status = 'yellow'
        elif 'green' in migration_statuses:
            status = 'green'
        else:
            status = None
        self.migration_status = status

    def _overrides_migration_status(self):
        migration_statuses = set()
        for tree_uuid in self.override_parameters.keys():
            migration_chain = self._get_overrides_migration_chain(
                tree_uuid=tree_uuid)
            if migration_chain is None:
                continue
            migration_statuses.add(migration_chain.gui_status())
        return migration_statuses

    def can_migrate_overrides(self):
        statuses = self._overrides_migration_status()
        return 'yellow' in statuses or 'green' in statuses

    def execution_status(self):
        """Returns the number of finished and the total number of nodes"""
        if self.is_atom():
            return 1, 1 if self.is_done() else 0

        total_nodes = len(self._nodes)
        subflow_set = set(self.shallow_subflows())
        total_finished = len({node for node in itertools.chain(
            self._in_state_done,
            self._in_state_done_locked)
                              if node not in subflow_set})
        for subflow in self._subflows.values():
            nodes, finished = subflow.execution_status()
            total_nodes += nodes
            total_finished += finished

        return total_nodes, total_finished

    def port_viewer(self, port):
        origin_port = self.flow.source_port(port)
        origin_port.node.port_viewer(origin_port)

    def print_graph(self):
        output = []

        all_names = set([])
        element_names = dict()

        obj_ids = {}
        count = itertools.count()

        def get_id(obj):
            if obj in obj_ids:
                return obj_ids[obj]
            i = next(count)
            obj_ids[obj] = i
            return i

        def name(element):
            if element in element_names:
                return element_names[element]

            if element.type == Type.InputPort:
                name_ = '{}<{}'.format(element.description, element.node.name)
            elif element.type == Type.OutputPort:
                name_ = '{}>{}'.format(element.node.name, element.description)
            else:
                name_ = element.name
            while name_ in all_names:
                name_ += '_'
            name_ = name_.replace('"', '_')
            all_names.add(name_)
            element_names[element] = name_
            return name_

        edges = self._graph.edges()
        output.append('digraph flow {')
        output.append('  rankdir="LR";')
        for src, dst in edges:
            src_id = get_id(src)
            dst_id = get_id(dst)

            output.append('  "{} ({})"->"{} ({})";'.format(
                name(src),
                src_id,
                name(dst),
                dst_id))

        output.append('}')
        return '\n'.join(output)

    def _get_default_environment(self):

        flows = list(self.parent_flows())
        library_flow = None
        start_flow = self

        for flow in reversed(flows):
            if flow.library_node:
                library_flow = flow
                if flow.flow is not None:
                    start_flow = flow.flow
                else:
                    start_flow = flow
                    core_logger.debug('Library flow missing parent flow')
                break

        flow_filename = start_flow.root_or_linked_flow_filename
        parent_flow_filename = ''
        if start_flow.flow is not None:
            parent_flow_filename = start_flow.flow.root_or_linked_flow_filename

        if flow_filename:
            dirname = os.path.dirname(flow_filename)
        else:
            dirname = os.getcwd()
            flow_filename = default_flow_filename()

        # Get dirname of flow.

        res = {
            'SY_FLOW_FILEPATH': flow_filename,
            'SY_PARENT_FLOW_FILEPATH': parent_flow_filename,
            'SY_FLOW_DIR': dirname}

        if library_flow:
            res['SY_LIBRARY_DIR'] = (
                library_flow.library_node.library)
        return res

    def node_settings(self):
        env = self._get_default_environment()
        res = {
            'node/flow_filename': env['SY_FLOW_FILEPATH'],
            'node/flow_dir': env['SY_FLOW_DIR'],
        }

        lib_dir = env.get('SY_LIBRARY_DIR')
        if lib_dir:
            res['node/lib_dir'] = lib_dir
        return res

    @property
    def parameters(self):
        """
        Get a copy of the parameters dict including default environment
        variables.

        Setter sets the parameter dictionary instance.
        """
        if self._parameters is None:
            params = {}
        else:
            params = copy.deepcopy(self._parameters)

        # Add some flow meta data environment variables
        env = params.get('environment', {}) or {}
        env.update(self._get_default_environment())
        params['environment'] = env

        return params

    @parameters.setter
    def parameters(self, value):
        self._parameters = value
        self.set_environment(value.get('environment', {}))

    @property
    def environment(self):
        return self.parameters['environment']

    @environment.setter
    def environment(self, value):
        self.set_environment(value)

    def set_environment(self, env):
        new_env = copy.deepcopy(env)
        default_env = self._get_default_environment()
        for key in default_env.keys():
            if key in new_env:
                del new_env[key]
        self._parameters['environment'] = new_env

    def get_stored_environment(self):
        env = copy.deepcopy(self.parameters['environment'])
        default_env = self._get_default_environment()
        for key in default_env.keys():
            env.pop(key, None)
        return env

    def set_node_override_parameters(self, node, parameter_model):
        if not isinstance(parameter_model,
                          (library.OverridesModel, type(None))):
            raise TypeError("Overrides must be OverridesModel, not",
                            type(parameter_model))
        overrides = self.override_parameters

        tree_uuid = self.tree_uuid(node)

        # Add or remove the overrides for this tree_uuid
        if parameter_model is None:
            overrides.pop(tree_uuid, None)
        else:
            overrides[tree_uuid] = parameter_model.to_dict()
        node.set_override_parameter_model(parameter_model, flow=self)

        self._update_migration_status()
        self.overrides_changed.emit()

    def tree_uuid(self, node):
        """Return a hierarchical "tree uuid" for a node in the flow."""
        uuid_parts = [node.uuid]
        for flow_ in node.parent_flows():
            if flow_ is self:
                break
            uuid_parts.append(flow_.uuid)
        return uuid_generator.join_uuids(reversed(uuid_parts))

    @property
    def override_parameters(self):
        return self._override_parameters

    def override_nodes(self):
        nodes = []
        for tree_uuid in self.override_parameters.keys():
            node, _subflow = self._get_node_and_subflow_from_tree_uuid(
                tree_uuid)
            if node is not None:
                nodes.append(node)
        return nodes

    def _get_node_and_subflow_from_tree_uuid(self, tree_uuid):
        """
        Returns a tuple with node and subflow if found.
        Can return the subflow without the node or just (None, None) if
        neither is found.
        """
        from . import types

        flow_ = self
        uuid_parts = uuid_generator.split_uuid(tree_uuid)

        for i, uuid_part in enumerate(uuid_parts):
            shallow_flodes = {n.uuid: n for n in flow_.shallow_nodes()}

            last_part = i == len(uuid_parts) - 1
            if uuid_part in shallow_flodes:
                subflow_ = shallow_flodes[uuid_part]
                is_node = subflow_.type == types.Type.Node
                if last_part and is_node:
                    return subflow_, flow_
                flow_ = subflow_
            elif last_part:
                return None, flow_
            else:
                return None, None
        return None, None

    def _get_overrides_migration_chain(self, tree_uuid):
        # 1. Check if overrides need to be migrated
        node, subflow = self._get_node_and_subflow_from_tree_uuid(tree_uuid)
        if node is None or subflow is None:
            # The node (and possibly subflow) seems to have been deleted
            return None
        if not self.app_core.is_node_in_library(node._identifier):
            return None

        try:
            params = self.override_parameters[tree_uuid]
        except KeyError:
            return None
        overrides_model = library.OverridesModel.from_dict(params)

        # 2. Find correct migration(s)
        migration_chain = migrations.OverridesMigrationChain(
            node, overrides_model, self)

        return migration_chain

    def migrate_overrides(self, tree_uuid, macro_cmd):
        migration_chain = self._get_overrides_migration_chain(
            tree_uuid=tree_uuid)
        if (migration_chain is not None
                and migration_chain.gui_status() is not None):
            migration_chain.forward(macro_cmd)

    def get_properties(self):
        """
        Return a dictionary with the following workflow attributes: 'label',
        'description', 'author', 'copyright', 'version', 'icon_filename'.
        """
        properties = {
            'label': self._name,
            'version': self._version,
            'author': self._author,
            'description': self._description,
            'documentation': self._documentation,
            'copyright': self.copyright,
            'icon_filename': self.icon_filename,
            'tag': self.tag,
            'identifier': self.identifier}

        if self.is_linked:
            properties.update({
                'source_label': self.source_label})
        return properties

    def set_properties(self, properties):
        """
        Use the values in dictionary properties to set some workflow
        attributes.

        The following keys are used if present: 'label', 'description',
        'author', 'copyright', 'version'.
        """
        if 'label' in properties:
            self.name = properties['label']
        if 'source_label' in properties:
            self.source_label = properties['source_label']
        if 'description' in properties:
            self.description = properties['description']
        if 'documentation' in properties:
            self.documentation = properties['documentation']
        if 'author' in properties:
            self._author = properties['author']
        if 'copyright' in properties:
            self._copyright = properties['copyright']
        if 'version' in properties:
            self._version = properties['version']
        if 'icon_filename' in properties:
            self.icon_filename = properties['icon_filename']
        if 'tag' in properties:
            self._tag = properties['tag']
        if 'identifier' in properties:
            self._identifier = properties['identifier']

    @property
    def is_linked(self):
        """Get/Set is_linked."""
        return self._is_linked

    def is_broken_link(self):
        return self._broken_link

    def set_broken_link(self, value):
        icon = self.icon
        self._broken_link = value
        self.update_state()
        if self.icon != icon:
            self.icon_changed.emit()

    def set_linked(self, value):
        was_linked = self._is_linked
        if value and not was_linked:
            # Subflow wasn't linked before, but is being linked now. Add to
            # flow_manager
            self._is_linked = value
            self._namespace_uuid = uuid_generator.generate_uuid()
            self.app_core._flow_manager.insert_flow(self)
        elif not value and was_linked:
            # Subflow was linked before, but is unlinked now
            self.app_core._flow_manager.remove_flow(self)
            self._is_linked = value
            self._namespace_uuid = None
        self.icon_changed.emit()

    @property
    def source_uri(self):
        """Get/Set source_uri."""
        return self._source_uri

    @source_uri.setter
    def source_uri(self, value):
        # source_uri should use forward slash as separator.
        self._source_uri = '/'.join(value.split(os.path.sep))

    @property
    def has_svg_icon(self):
        return True

    @property
    def icon(self):
        if self._node and self._node.icon:
            return self._node.icon

        if self._icon_filename:
            root_filename = self.root_or_linked_flow_filename
            if root_filename:
                try:
                    res = os.path.normpath(os.path.join(os.path.dirname(
                        self.root_or_linked_flow_filename),
                        self._icon_filename))
                except Exception:
                    res = self._icon_filename
                return localuri(res)

        if self.is_linked:
            icon_path = 'linked-file.svg'
            if self.is_broken_link():
                icon_path = 'broken-link.svg'
            res = os.path.join(util.icon_path('actions'), icon_path)
        elif self._locked:
            res = util.icon_path('actions/action-unavailable-symbolic.svg')
        else:
            res = util.icon_path('sub_application.svg')
        return localuri(res)

    @property
    def background(self):
        res = None

        if self._locked:
            svg_path = 'actions/action-unavailable-symbolic.svg'
            res = localuri(util.icon_path(svg_path))
        return res

    @property
    def icon_filename(self):
        if self._icon_filename:
            return prim.nativepath(self._icon_filename)
        return ''

    @icon_filename.setter
    def icon_filename(self, value):
        # icon_filename should use forward slash as separator.
        if value:
            self._icon_filename = prim.unipath(value)
        else:
            self._icon_filename = None
        self.icon_changed.emit()

    def all_subflows(self):
        subflows = self.shallow_subflows()
        for subflow in subflows:
            subflows.extend(subflow.all_subflows())
        return subflows

    def save(self, prompt_for_filename=False, propagate_cancelled=False):
        """Save flow"""
        if prompt_for_filename:
            try:
                filename = common.ask_for_filename(self)
            except common.SaveCancelled:
                if propagate_cancelled:
                    raise
                else:
                    return
            self.filename = filename
        try:
            common.persistent_save_flow_to_file(self, self.filename)
        except common.SaveCancelled:
            if propagate_cancelled:
                raise
            else:
                return

        # Now see if any subflows need saving.
        try:
            common.ask_about_saving_flows([self], include_root=False)
        except common.SaveCancelled:
            if propagate_cancelled:
                raise
            else:
                return

    def undo_stack(self):
        return self.root_flow()._undo_stack

    def is_clean(self):
        return self.undo_stack().is_clean(self)

    def set_clean(self, clean=True):
        self.undo_stack().set_clean(self, clean=clean)

    def subflows_are_clean(self):
        """Return True if this flow and all its subflows are clean."""
        dirty_flows = self.undo_stack().get_dirty_flows()
        dirty_subflows = any(flow for flow in dirty_flows
                             if self in flow.parent_flows())
        return not dirty_subflows

    def output_nodes(self):
        """
        Return all nodes connected to the flow's outputs.

        These must be written when running a subflow and all its child nodes
        including subflows as a single process.
        """
        nodes = []

        def inner(node):
            if node.type == Type.Flow:
                for output in node.outputs:
                    port = node.source_port(output)
                    if port is not None:
                        inner(port.node)
            elif node.type == Type.Node:
                nodes.append(node)

        inner(self)
        return nodes

    def input_nodes(self):
        """
        Return all nodes connected to the flow's inputs.

        These must be written before running a flow including subflows as
        a single process.
        """
        nodes = []

        def inner(node):
            if node.type == Type.Flow:
                for input in node.inputs:
                    connects = node.output_connections_from_port(
                        input.mirror_port)
                    for connect in connects:
                        inner(connect.destination.node)
            elif node.type == Type.Node:
                nodes.append(node)
            elif node.type == Type.FlowOutput:
                pass
            else:
                assert(False)

        inner(self)
        return nodes

    def ports_connected_to_output_ports(self):
        ports = []
        for flow_output in self._flow_outputs:
            ports.append(
                self.source_port_traverse(flow_output.port))
        return ports

    def ports_connected_to_input_ports(self, group=False):
        ports = []
        if group:
            addfunc = ports.append
        else:
            addfunc = ports.extend

        for flow_input in self._flow_inputs:
            addfunc(self.destination_ports(
                flow_input.port, traverse_subflows=True))
        return ports

    def bypass_ports(self):
        """
        Return pairs of ports that are belonging to flow_inputs and
        flow_outputs that are connected to eachother directly or indirectly.
        """
        in_ports = {flow_input.port for flow_input in
                    self._flow_inputs}
        ports = []

        for flow_output in self._flow_outputs:
            out = flow_output.port
            inp = out
            curr = inp
            prev = None
            while curr and prev is not curr and curr not in in_ports:
                if curr and curr.type == Type.OutputPort:
                    inp = curr
                prev = curr
                curr = self._source_element_cross(prev)

            if curr and curr.type == Type.OutputPort:
                inp = curr

            if inp in in_ports:
                ports.append((inp, out))
        return ports

    def port_index(self, port):
        if port.type in [Type.InputPort, Type.OutputPort]:
            return super().port_index(port)
        elif port.type in [Type.FlowInput, Type.FlowOutput]:
            # If the flowio has a parent_port, that should determine ordering.
            # For flowios in top level flows we fall back to the ordering in
            # self._flow_inputs/self._flow_outputs.
            if port.parent_port is not None:
                return super().port_index(port.parent_port)
            elif port.type == Type.FlowInput:
                return self._flow_inputs.index(port)
            elif port.type == Type.FlowOutput:
                return self._flow_outputs.index(port)

    def internal_node_dependencies(self):
        edge_set = util.OrderedSet()
        traversed_nodes = set()
        external_input_nodes = set()

        for fio in self._flow_inputs:
            source = self.source_port(fio, atom=True)
            if source and source.node and source.node.type in [
                    Type.Node, Type.Flow]:
                external_input_nodes.add(source.node)

        traversed_nodes.update(external_input_nodes)
        external_input_nodes.add(None)

        edge_set.update(self._predecessor_node_edges(
            self._end_nodes(), traversed_nodes=traversed_nodes, atom=True))
        return [e for e in edge_set if e[0] not in external_input_nodes
                and e[0] is not e[1]]

    def _parent_port_index(self, flowio):
        if flowio.type == Type.FlowInput:
            flowios = self._flow_inputs
            ios = self.inputs
        elif flowio.type == Type.FlowOutput:
            flowios = self._flow_outputs
            ios = self.outputs

        return [
            input_ for input_ in flowios
            if (input_.parent_port in ios or
                input_ == flowio)].index(flowio)

    def create_parent_port(self, flowio):
        index = self._parent_port_index(flowio)
        uuid = self._new_parent_port_uuid(flowio, None)
        flowio.create_parent_port(pos=index, uuid=uuid)
        if flowio.parent_port:
            self.flow._infertype(flowio.parent_port, None)
        self.disarm()

    def add_parent_port(self, flowio, port):
        index = self._parent_port_index(flowio)
        if flowio.type == Type.FlowInput:
            add_port = self._flow.add_input_port
            insert_port = self.insert_input
        elif flowio.type == Type.FlowOutput:
            add_port = self._flow.add_output_port
            insert_port = self.insert_output
        else:
            assert False

        add_port(port)
        flowio.add_parent_port(port)
        insert_port(index, port)
        self.disarm()

    def delete_parent_port(self, flowio):
        flowio.delete_parent_port()
        self.arm()

    def delete_input(self, port):
        if port is self._conf_port:
            self._conf_port = None

        self.remove_input(port)
        self.input_port_removed.emit(port)
        self.arm()

    def delete_output(self, port):
        self.remove_output(port)
        self.output_port_removed.emit(port)

    def create_named_input(self, name):
        assert self.is_config_port_name(name)
        pdef = library.PortDefinition(
            self._conf_port_name, 'Configuration port', '<z>', 'hdf5', 0, False)
        mapping = {}
        port = self._flow.create_input_port(self, pdef, mapping)
        self._conf_port = port
        port.datatype_instantiate(mapping)
        self.input_port_created.emit(port)
        return port

    def add_input(self, port):
        if self.is_config_port_name(port.name):
            self._conf_port = port
            super().add_input(port)
        else:
            if self._conf_port in self._inputs:
                # Ensure config port is always last.
                super().insert_input(len(self._inputs) - 1, port)
            else:
                super().add_input(port)

    def insert_input(self, pos, port):
        super().insert_input(pos, port)
        if self.is_config_port_name(port.name):
            self._conf_port = port

    def insert_named_input(self, pos, port):
        self.insert_input(pos, port)
        self.input_port_created.emit(port)

    def insert_named_output(self, pos, port):
        self.insert_output(pos, port)
        self.output_port_created.emit(port)
        self.arm()

    def create_named_output(self, name):
        raise NotImplementedError()

    def available_flow_input_indices(self, flow_input):
        return range(len(self._flow_inputs))

    def available_flow_output_indices(self, flow_output):
        return range(len(self._flow_outputs))

    def can_create_flow_input(self):
        return True

    def can_create_flow_output(self):
        return True

    def can_remove_flow_input(self, flowinput):
        return True

    def can_remove_flow_output(self, flowoutput):
        return True

    def can_reorder_flow_input(self, flowinfo):
        return True

    def can_reorder_flow_output(self, flowoutput):
        return True

    def can_set_optional(self, flowio):
        return True

    def default_parent_port(self, flowio):
        return True

    def flowio_optional(self, flowio, optional):
        return optional

    def _can_create_parent_flowio(self, flowio):
        return flowio.is_optional() and flowio.parent_port is None

    def can_create_input(self, obj):
        res = False
        if self.is_config_port_name(obj):
            res = self._conf_port is None
        elif obj in self._flow_inputs:
            res = self._can_create_parent_flowio(obj)
        return res

    def can_create_output(self, obj):
        res = False
        if obj in self._flow_outputs:
            res = self._can_create_parent_flowio(obj)
        return res

    def _can_delete_port(self, flowio_group, port):
        res = False
        if port in flowio_group:
            res = port.is_optional() and port.parent_port is not None
        else:
            for flowio in flowio_group:
                if (flowio.is_optional()
                        and flowio.parent_port is port and port is not None):
                    res = True
                    break
        return res

    def can_delete_input(self, port):
        if port is None:
            return False
        elif port is self._conf_port:
            res = True
        elif self.is_config_port_name(port):
            res = self._conf_port is not None
        else:
            res = self._can_delete_port(self._flow_inputs, port)
        return res

    def can_delete_output(self, port):
        return self._can_delete_port(self._flow_outputs, port)

    def _creatable_parent_flowios(self, flowio_group):
        return [flowio for flowio in flowio_group
                if flowio.is_optional()]

    def creatable_parent_flow_inputs(self):
        return self._creatable_parent_flowios(self._flow_inputs)

    def creatable_parent_flow_outputs(self):
        return self._creatable_parent_flowios(self._flow_outputs)

    def is_config_port_name(self, name):
        return name == self._conf_port_name

    def creatable_input_ports(self):
        return [(self._conf_port,
                 {
                     'name': self._conf_port_name,
                     'description': 'Configuration port',
                     'n': (0, 1, 0),
                     'scheme': 'hdf5',
                     'type': '<z>'
                 })]

    def creatable_output_ports(self):
        return []

    def infertype_constraints(self):
        input_constraints = [
            (flow_input.parent_port, flow_input.port)
            for flow_input in self._flow_inputs
            if flow_input.parent_port is not None]

        output_constraints = [
            (flow_output.port, flow_output.parent_port)
            for flow_output in self._flow_outputs
            if flow_output.parent_port is not None]

        return input_constraints + output_constraints

    def _infertype(self, port0, port1, disconnect=False,
                   check=False):
        infertype_ctx = self._infertype_ctx
        if not infertype_ctx.delayed:
            flowlib.infertype_connect(
                port0, port1, disconnect, check)
        else:
            infertype_ctx.edges.append((port0, port1, disconnect))

    # Actions. Triggered by the user or event such as validation finish.
    # Responsible for setting up the propagate_ctx when necessary.

    def _defer_update_execution_status(self):
        return self._propagate_ctx.delayed

    def _record_execution_status_changed(self):
        self._propagate_ctx.add_changed_flow(self)

    def reload_node_action(self, node):
        with self.propagate_ctx(node):
            node.reload()

    def reload_action(self):
        with self.propagate_ctx():
            self.reload()

    def abort_action(self):
        with self.propagate_ctx():
            self.abort()

    def abort_node_action(self, node):
        with self.propagate_ctx():
            node.abort()

    def validate_action(self):
        with self.propagate_ctx():
            self.validate()

    def validate_node_done_action(self, node, status):
        with self.propagate_ctx(node):
            node.validate_done(status)

    def execute_action(self):
        self.execute_all_nodes()

    def execute_node_action(self, node):
        node.execute()

    def profile_action(self):
        self.profile_all_nodes()

    def profile_node_action(self, node):
        node.profile()

    def execute_node_done_action(self, node, status):
        # TODO: integrate with general propagation: optimization to avoid
        # excessive propagate on execution, should only be needed on error.
        if status > 0:
            node.execute_done(status)
        else:
            with self.propagate_ctx(node):
                node.execute_done(status)

    def execute_child_node_done(self, node, status, locked=None):
        # TODO: integrate with general propagation: optimization to avoid
        # excessive propagate on execution, should only be needed on error.
        if status > 0:
            self.set_child_done(node, status, locked=locked)
        else:
            with self.propagate_ctx():
                self.set_child_done(node, status, locked=locked)


def _all_nodes_set_list(flow, remove_invalid=True, atom=False):
    node_set = flow.all_nodes(remove_invalid=remove_invalid, atom=atom)
    return [n for n in flow.node_set_list(
        remove_invalid=remove_invalid, atom=atom) if n in node_set]
