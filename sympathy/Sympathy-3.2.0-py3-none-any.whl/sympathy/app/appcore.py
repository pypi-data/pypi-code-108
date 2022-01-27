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
"""
The AppCore is the interface between the GUI application and the ExeCore (the
ExeCore handles all access to the nodes). AppCore also provides a bunch of
helper and interfaces between the library, documentation etc.
"""
import os
import json
import itertools
import contextlib

from Qt import QtCore

from sympathy.platform import node_result
from sympathy.platform.exceptions import SyNodeError
from sympathy.platform import message as msgmod
from sympathy.utils import uuid_generator, log
from sympathy.platform import parameter_types

from . import flow
from . import user_commands
from . import library
from . import flow_manager
from . import settings
from . import sy_profile
from . import message_manager
from . import util
from . import filename_manager as fileman
from . import user_statistics
from . credentials import credentials
from . import messages
from . import environment_variables
from .. utils import prim

core_logger = log.get_logger('core')
migr_logger = log.get_logger('core.migrations')


class AppCore(QtCore.QObject):
    """AppCore. The interface between the GUI and the execution engine."""
    execute_nodes_requested = QtCore.Signal(util.OrderedSet)
    debug_nodes_requested = QtCore.Signal(util.OrderedSet)
    profile_nodes_requested = QtCore.Signal(util.OrderedSet, util.OrderedSet)
    abort_node_requested = QtCore.Signal(flow.NodeInterface)
    validate_node_requested = QtCore.Signal(flow.Node)
    execute_node_parameter_view_requested = QtCore.Signal(flow.Node)
    execute_subflow_parameter_view_requested = QtCore.Signal(
        flow.Flow, str)
    execute_port_viewer = QtCore.Signal(flow.Port)
    all_execution_has_finished = QtCore.Signal()
    display_message_received = QtCore.Signal(messages.DisplayMessage)
    clear_node_messages_requested = QtCore.Signal(str)
    text_output_received = QtCore.Signal(str, node_result.NodeResult)
    node_progress = QtCore.Signal(flow.NodeInterface, float)
    restart_all_task_workers = QtCore.Signal()
    flow_libraries_changed = QtCore.Signal(flow.Flow)
    bulk_operation_requested = QtCore.Signal(flow.Flow)
    bulk_operation_finished = QtCore.Signal(flow.Flow)
    help_requested = QtCore.Signal(str)

    def __init__(self, args, parent=None):
        self._args = args
        super(AppCore, self).__init__(parent)
        self._library_manager = library.LibraryManager(self)
        self.node_library_added = self._library_manager.library_added
        self.node_library_output = self._library_manager.library_output
        self.node_library_aliases = self._library_manager.library_aliases
        self._flow_manager = flow_manager.FlowManager(self)
        self._validate_enabled = True
        self._reload_library_enabled = True
        self._message_manager = message_manager.MessageManager(self)
        self.message_output = self._message_manager.message_output
        self._credential_manager = credentials.instance()
        self._result_ids = set()
        if args and args.environment_credentials:
            self._credential_manager.set_environment_credentials(
                args.environment_credentials,
                environment_variables.instance().shell_variables(),
                case_sensitive=not prim.is_windows())
    #
    # File extensions and mime types information
    #
    @staticmethod
    def mime_type_node():
        """Returns the mime type used for nodes."""
        return 'application-x-sympathy-node'

    @staticmethod
    def mime_type_flow():
        """Returns the mime type used for flows."""
        return 'application-x-sympathy-flow'

    @staticmethod
    def flow_suffix():
        """Returns the flow file suffix."""
        return 'syx'

    #
    # General
    #

    def message_input(self, taskid, msg):
        stream_types = {
            msgmod.StdoutMessage: messages.Levels.notice,
            msgmod.StderrMessage: messages.Levels.warning,
        }

        if msg.type in stream_types:
            level = stream_types[msg.type]
            ident, text = msg.data
            if ident:
                node = None
                source = None
                title = None
                # Could be handled earlier, for example, when the viewer, etc.,
                # creates the message.
                if uuid_generator.is_joined_uuid(ident):
                    node = self.get_flode(ident)
                    if not node:
                        port = self.get_port(ident)
                        if port:
                            node = port.node
                            title = "Viewer"
                if not node:
                    # Workaround for problems using NodeMessage for non-node
                    # tasks or missing nodes.
                    # TODO: Remove NodeMessage as base for StreamMessage and
                    # make it safe to call for non-node tasks.
                    ident = str(ident or 'Unknown')
                    source = ident
                    title = ident
                self.display_message(
                    messages.StreamMessage(
                        level=level, id=(
                            taskid, ident, level),
                        brief=text, node=node, source=source, title=title))
        elif msg.type == msgmod.CredentialRequestMessage:
            data = msg.data
            connection_parameter = parameter_types.Connection.from_dict(data)
            ok, secrets = credentials.instance().request_connection(
                connection_parameter, True)
            if not ok:
                secrets = None
            self.message_reply(taskid, msg.reply(secrets))

        elif msg.type == msgmod.CredentialEditMessage:
            data, secrets = msg.data
            connection_parameter = parameter_types.Connection.from_dict(data)
            ok, secrets = credentials.instance().edit_connection(
                    connection_parameter, secrets)
            if not ok:
                secrets = None
            self.message_reply(taskid, msg.reply(secrets))

        elif msg.type == msgmod.CredentialConfigureMessage:
            data, kwargs = msg.data
            connection_parameter = parameter_types.Connection.from_dict(data)
            ok, secrets = credentials.instance().configure_connection(
                    connection_parameter, kwargs)
            if not ok:
                secrets = None
            self.message_reply(taskid, msg.reply(secrets))
        else:
            self._message_manager.message_input(taskid, msg)

    def message_reply(self, taskid, reply):
        self.message_output.emit(taskid, reply)

    #
    # Flow library
    #

    def opened_flows(self):
        return self._flow_manager.flows()

    def create_flow(self, flow_uuid=None):
        """Create a new flow, optionally with a given UUID."""
        flow_ = flow.Flow(app_core=self, uuid=flow_uuid,
                          undo_stack=flow.UndoStack())
        self._flow_manager.insert_flow(flow_)
        return flow_

    def remove_flow(self, flow_):
        """
        Remove top-level flow from available flows and perform relevant
        cleanup.
        """
        with flow_.reload_libraries_and_pythonpaths():
            self._flow_manager.remove_root_flow(flow_)
            flow_.remove_libraries_and_pythonpaths()

        if settings.instance().session_temp_files in [
               settings.session_temp_files_remove_flow,
               settings.session_temp_files_remove_unused]:

            fileman.instance().deallocate_namespace(flow_.namespace_uuid())

    #
    # Node library
    #

    def change_flow_libraries(self, flow):
        self.flow_libraries_changed.emit(flow)

    def clear_node_library(self):
        """Remove all nodes from the node library."""
        self._library_manager.clear()

    def set_reload_node_library_enabled(self, value):
        self._reload_library_enabled = value

    def reload_node_library(self):
        """Reload the node library."""
        if not self._reload_library_enabled:
            return

        self._library_manager.reload_library()
        self.node_library_added.emit()
        cache = {}
        for flow_ in self._flow_manager.flows():
            for node_ in flow_.all_nodes():
                flow_ = node_.flow
                libraries = cache.get(flow_)

                if libraries is None:
                    root = flow_.root_or_linked_flow()
                    libraries = [os.path.normcase(l)
                                 for l in util.library_paths(root)]
                    cache[flow_] = libraries
                node_.update_library_node(libraries)

    def reload_documentation(self, library=None, output_folder=None,
                             excluded_exts=None):
        """Reload the documentation."""
        self._library_manager.reload_documentation(
            library=library, output_folder=output_folder,
            excluded_exts=excluded_exts)

    def get_documentation_builder(self):
        """Reload the documentation."""
        return self._library_manager.get_documentation_builder()

    def library_node(self, node_identifier):
        """
        Returns the library information about a node given its identifier.
        """
        return self._library_manager.library_node(node_identifier)

    def is_node_in_library(self, node_identifier, libraries=None):
        """Returns True if the node is in the library."""
        if not self._reload_library_enabled:
            libraries = None
        return self._library_manager.is_in_library(node_identifier,
                                                   libraries=libraries)

    def library_node_from_definition(self, node_identifier, definition):
        """Add a single node to the library, used for when loading flows
        with nodes not in the library.
        """
        return self._library_manager.library_node_from_definition(
            node_identifier, definition)

    def register_node(self, node_identifier, node):
        self._library_manager.register_node(node_identifier, node)

    def library_root(self):
        """Returns the root of the library."""
        return self._library_manager.root()

    def json_type_alias_definitions(self):
        """Returns the type aliases defined in the library."""
        defs = self._library_manager.typealiases()
        return json.dumps(defs)

    def set_library_dict(self, data):
        self._library_manager.set_library_data(
            data['tags'], data['library'], data['aliases'])

    def get_library_dict(self, update=True):
        tags, lib, aliases = self._library_manager.get_library_data(
            update=update)
        return {'tags': tags, 'library': lib, 'aliases': aliases}

    def get_flow(self, full_uuid, parent_flow=None):
        if parent_flow:
            flow_ = parent_flow
        else:
            (namespace_uuid, _) = uuid_generator.split_uuid(full_uuid)
            flow_ = self._flow_manager.flow(namespace_uuid)

        if flow_.full_uuid == full_uuid:
            return flow_

        for subflow in flow_.all_subflows():
            if subflow.full_uuid == full_uuid:
                return subflow

    #
    # Node operations
    #
    def get_node(self, full_uuid, parent_flow=None):
        """Returns the flow.Node() given its full UUID."""
        (namespace_uuid, node_uuid) = uuid_generator.split_uuid(full_uuid)
        if parent_flow:
            flow_ = parent_flow
        else:
            flow_ = self._flow_manager.flow(namespace_uuid)
        return flow_.node(node_uuid, current_namespace=namespace_uuid,
                          search_namespace=namespace_uuid)

    def get_port(self, full_uuid, parent_flow=None):
        (namespace_uuid, port_uuid) = uuid_generator.split_uuid(full_uuid)
        if parent_flow:
            flow_ = parent_flow
        else:
            flow_ = self._flow_manager.flow(namespace_uuid)

        for node in flow_.all_nodes():
            for port in itertools.chain(node.inputs,
                                        node.outputs):
                if port.full_uuid == full_uuid:
                    return port
        return None

    def get_flode(self, full_uuid, parent_flow=None):
        """
        Get flow or node.
        ^^^ ^^   ^    ^^
        """
        node = self.get_node(full_uuid, parent_flow)
        if node is None:
            node = self.get_flow(full_uuid, parent_flow)
        return node

    # Do we have any merits towards using UUID at this point?
    def _extract_node_properties(self, node):
        return (
            node.uuid, node.class_name, node.source_file, node.library,
            node.node_identifier, json.dumps(node.to_dict()),
            self.json_type_alias_definitions())

    def execute_nodes(self, node_set):
        """Execute a set ofg nodes. node_set is a list of lists with nodes
        grouped according to their position in the graph. The elements are
        flow.Node() objects.
        """
        self.execute_nodes_requested.emit(util.OrderedSet(node_set))

    def debug_nodes(self, node_set):
        self.debug_nodes_requested.emit(util.OrderedSet(node_set))

    def profile_nodes(self, node_set_execute, node_set_profile):
        self.profile_nodes_requested.emit(util.OrderedSet(node_set_execute),
                                          util.OrderedSet(node_set_profile))

    def abort_node(self, node):
        """Abort node execution."""
        user_statistics.user_aborted_node(node)
        self.abort_node_requested.emit(node)

    def _log_unknown_uuid(self, full_uuid):
        core_logger.error("Uuid %s is neither a node nor a flow... "
                          "what is it?", full_uuid)

    @QtCore.Slot(flow.NodeInterface)
    def set_node_status_queued(self, flode):
        """Change the node's status to Queued."""
        if flode is not None:
            flode.execute_queued()

    @QtCore.Slot(flow.NodeInterface)
    def set_node_status_execution_started(self, flode):
        """Alert the flow.Node() that it is being executed."""
        if flode is not None:
            flode.execute_started()

    @QtCore.Slot(flow.NodeInterface, node_result.NodeResult)
    def execute_node_done(self, flode, result):
        """Alert the flow.Node() that it has finished executing."""
        if flode is not None:
            user_statistics.user_executed_node(flode, result)
            flode.flow.execute_node_done_action(flode, result.status)
            self._message_manager.execution_done(flode)

    @QtCore.Slot(flow.NodeInterface,
                 flow.NodeInterface,
                 node_result.NodeResult, bool)
    def execute_child_node_done(self, parent_flow, child_flode,
                                result, parent_done):
        """
        Alert the parent flow.Node() that its child has finished executing.
        """
        def get_flode_log(full_uuid):
            try:
                flode = self.get_flode(full_uuid, parent_flow)
            except KeyError:
                # Assuming that we are getting updates from extracted Lambda.
                # Reason for KeyError should be that namespace_uuid is unknown
                # to FlowManager.
                flode = None
            else:
                if flode is None:
                    self._log_unknown_uuid(full_uuid)
            return flode

        locked = None
        if not parent_done:
            locked = True

        new_res = result.id not in self._result_ids

        if new_res or parent_done:
            self._result_ids.add(result.id)
            # None for parent flow parent_flow indicates that the parent is a
            # *normal* node such as Map or Apply.
            if parent_flow is not None and child_flode is not None:

                if new_res:
                    user_statistics.user_executed_node(child_flode, result)

                error = 0 if result.has_error() else 1
                parent_flow.execute_child_node_done(
                    child_flode, error, locked=locked)
                if new_res:
                    for node_message in util.node_messages(
                            child_flode, result):
                        self.display_message(node_message)

    def display_custom_node_message(self, flode, output='', warning='',
                                    error='', error_details=''):
        result = node_result.NodeResult()
        if error:
            try:
                raise SyNodeError(error, error_details)
            except SyNodeError:
                result.store_current_exception()
        if warning:
            result.stderr = warning
        if output:
            result.stdout = output
        for node_message in util.node_messages(flode, result):
            self.display_message(node_message)

    def clear_node_messages(self, node):
        self.clear_node_messages_requested.emit(node.full_uuid)

    @QtCore.Slot(messages.DisplayMessage)
    def display_message(self, message):
        """Update the output related to the node."""
        self.display_message_received.emit(message)
        self._result_ids.add(message.id)

    def get_flodes(self, full_uuids, parent_flode):
        """
        Returns
        -------
        list of flode or None (if full_uuids is None)
        """
        flodes = None
        if full_uuids is not None:
            flodes = []
            for full_uuid in full_uuids:
                flode = self.get_flode(full_uuid, parent_flode)
                if flode is not None:
                    flodes.append(flode)
        return flodes

    @QtCore.Slot(flow.NodeInterface, list)
    def set_node_is_aborting(self, parent_flode, child_flodes):
        """Alert the node.Node() that is being aborted."""
        parent_flode.execute_aborting(child_flodes)

    @QtCore.Slot(flow.NodeInterface, list)
    def node_has_aborted(self, parent_flode, child_flodes):
        """Alert the node.Node() that has been aborted."""
        parent_flode.execute_aborted(child_flodes)

    @QtCore.Slot(flow.Node)
    def node_has_successfully_finished_execution(self, node):
        """Returns True if the node has been successfully executed."""
        return node.is_successfully_executed()

    def _node_session_filename(
            self, session_folder, full_uuid, class_name, ext):
        clean_identifier = ''.join(
            [c for c in full_uuid if c not in '{}'])
        return os.path.join(session_folder, '{}_{}.{}'.format(
            class_name, clean_identifier, ext))

    def profiling_finished(self, node_set):
        session_folder = settings.instance()['session_folder']

        node_stats = [
            (node, self._node_session_filename(
                session_folder,
                node.full_uuid,
                node.class_name,
                'stat'))
            for node in node_set]

        result = node_result.NodeResult()
        flow, report = sy_profile.report(node_stats)
        result.stdout = report
        result.stdout_clean = True
        title = f'Profile report ({flow.full_display_name})'
        for result_message in util.node_messages(
                flow, result, title=title):
            self.node_library_output.emit(result_message)

    def validate_enabled(self):
        return self._validate_enabled

    def set_validate_enabled(self, value):
        self._validate_enabled = value

    @contextlib.contextmanager
    def no_validate(self):
        old_validate_enabled = self.validate_enabled()
        try:
            self.set_validate_enabled(False)
            yield
        finally:
            self.set_validate_enabled(old_validate_enabled)

    @QtCore.Slot(flow.Node)
    def validate_node(self, node):
        """Ask ExeCore to validate the node."""
        if self._validate_enabled:
            core_logger.debug('validate %s', node.uuid)
            if node.needs_validate:
                self.validate_node_requested.emit(node)
            else:
                node.validate_done(node.internal_validate())
        else:
            node.validate_done(False)

    @QtCore.Slot(flow.Node, node_result.NodeResult)
    def validate_node_done(self, node, result):
        """Alert node.Node() that the validation is finished."""

        try:
            status = 0 if not result.output else 1
        except Exception:
            status = 0

        if node is not None:
            if node.flow is not None:
                node.flow.validate_node_done_action(node, status)
            else:
                node.validate_done(status)

    @QtCore.Slot(flow.NodeInterface, float)
    def update_node_progress(self, flode, progress):
        """Update the progress (percentage) of the flode."""
        self.node_progress.emit(flode, progress)
        if flode is not None:
            flode.update_progress(progress)

    @QtCore.Slot(flow.Flow, flow.NodeInterface, float)
    def update_child_node_progress(self, parent_flow, child_flode,
                                   progress):
        """Update the progress (percentage) of the child flode."""
        if parent_flow is not None and child_flode is not None:
            parent_flow.update_child_progress(child_flode, progress)

    def execute_node_parameter_view(self, node):
        """Ask ExeCore to open up the parameter configuration GUI."""
        self.execute_node_parameter_view_requested.emit(node)

    @QtCore.Slot(flow.Node, node_result.NodeResult)
    def execute_node_parameter_view_done(self, node_, result):
        """Updates the node with the result of the configuration."""
        adjusted_parameters = result.output
        if not adjusted_parameters:
            return

        if node_ is not None:
            user_statistics.user_configured_node(node_, result)
            adjusted_parameters = json.loads(adjusted_parameters)
            if adjusted_parameters is None:
                return

            old_params = node_.parameter_model
            new_params = library.ParameterModel.from_dict(
                adjusted_parameters['parameters'])

            if not old_params.equal_to(new_params):
                # Auto migrate node if needed
                if node_.can_auto_migrate():
                    migr_logger.info(
                        "Auto migrating node %s", node_.identifier)
                    cmd = user_commands.MigrateNode(node_, auto_only=True)
                    node_.flow.undo_stack().push(cmd)

                # Store parameters
                if node_.has_overrides():
                    new_params = library.OverridesModel.from_dict(
                        adjusted_parameters['parameters'])
                    overrides_flow = node_.get_overrides_flow()
                    new_params.set_version(node_.version)
                    new_params.set_nodeid(node_.identifier)
                    cmd = user_commands.EditNodeOverrideParameters(
                        overrides_flow, node_, new_params)
                    overrides_flow.flow.undo_stack().push(cmd)
                else:
                    cmd = user_commands.EditNodeParameters(
                        node_, new_params)
                    node_.flow.undo_stack().push(cmd)

    def execute_subflow_parameter_view(self, subflow, mode='configure'):
        """Ask ExeCore to open up an aggregated sub-flow configuration GUI."""
        self.execute_subflow_parameter_view_requested.emit(subflow, mode)

    @QtCore.Slot(str, str)
    def execute_subflow_parameter_view_done(self, full_uuid, result):
        """Updates all involved nodes with new result of configuration."""
        json_flow_info = result.output
        if json_flow_info is None or json_flow_info == '':
            core_logger.warning(
                'Invalid response from subflow parameter view.')
            return

        flow_info = json.loads(json_flow_info)
        if flow_info['configure']:
            changed_item_list = self.handle_subflow_parameter_view_done(
                full_uuid, flow_info)
            for node in changed_item_list:
                user_statistics.user_configured_node(node, result)
        else:
            self.handle_subflow_settings_view_done(full_uuid, flow_info)

    def handle_subflow_parameter_view_done(self, full_uuid, flow_info_dict):
        """
        Updates all involved nodes with new result of configuration.

        Returns
        -------
        list of [Node]
            Nodes changed by configuration.
        """
        def get_top_flow(flow1, flow2):
            """
            Return whichever flow is "higher" in the subflow hierarchy or None
            if the two flows are unrelated.

            If one of the flows is None, return the other flow. If both flows
            are None, return None.
            """
            if flow1 is None:
                return flow2
            elif flow2 is None:
                return flow1

            flow_ = flow2
            while flow_ is not None:
                if flow_ is flow1:
                    return flow1
                flow_ = flow_.flow

            flow_ = flow1
            while flow_ is not None:
                if flow_ is flow2:
                    return flow2
                flow_ = flow_.flow

            return None

        def changed_nodes(subflow, flow_info, override_flow=None):
            """
            Return a list of changes to nodes.

            Parameters
            ----------
            subflow : flow.Flow
                The subflow that is being configured.
            flow_info : dict
                Dictionary structure with all nodes and subflows in the
                configured subflow.
            override_flow : flow.Flow or None
                Flow where overrides should be saved. Defaults to subflow.

            Returns
            -------
            list of tuples
                A list of tuples each with three elements: the changed node,
                the new parameter model and the flow where the overrides should
                be stored. The last element will be None if the node should be
                modified directly.

            """
            # Check if this subflow should be set as the new override_flow.
            if override_flow is None and subflow.is_linked:
                override_flow = subflow

            # Find nodes whose parameters have changed.
            nodes = []
            for node_info in flow_info['nodes']:
                node_dict = json.loads(node_info['json_node_dict'])
                node = self.get_node(node_info['uuid'])
                node_override_flow = node.get_overrides_flow()

                if override_flow or node_override_flow:
                    param_model = library.OverridesModel.from_dict(
                        node_dict['parameters'])
                    param_model.set_version(node.auto_migrated_version())
                    param_model.set_nodeid(node.identifier)
                else:
                    param_model = library.ParameterModel.from_dict(
                        node_dict['parameters'])

                equal = node.parameter_model.equal_to(param_model)

                if not equal:
                    # Overrides should be put in either the active overrides
                    # flow (node.get_overrides_flow()) or the flow found by the
                    # code above (override_flow). Whichever is the top flow.
                    # This is because configuring a subflow when there are
                    # overrides "above" that subflow should only edit the
                    # active overrides, but whether there are overrides "below"
                    # the configured subflow doesn't matter.
                    top_override_flow = get_top_flow(
                        node_override_flow, override_flow)
                    nodes.append((node, param_model, top_override_flow))

            # Recursively search through any subflows.
            for subflow_info in flow_info['flows']:
                subflow = self.get_flow(subflow_info['uuid'])
                nodes.extend(changed_nodes(
                    subflow, subflow_info, override_flow))
            return nodes

        subflow = self.get_flow(flow_info_dict['uuid'])
        if subflow is None:
            core_logger.warning(
                "Can't find the subflow which was just configured.")
            return []

        changed_item_list = changed_nodes(subflow, flow_info_dict)
        core_logger.debug('Changes detected for subflow parameter view.')
        top_flow = subflow.flow

        cmds = []
        for node, param_model, override_flow in changed_item_list:
            # Auto migrate node if needed
            if node.can_auto_migrate():
                migr_logger.info("Auto migrating node %s", node.identifier)
                cmd = user_commands.MigrateNode(node, auto_only=True)
                node.flow.undo_stack().push(cmd)

            if override_flow is None:
                core_logger.debug('Changed parameters for node %s', node)
                # TODO: Isn't param_model an OverridesModel here?
                # Now: only if the subflow should have overrides!
                cmd = user_commands.EditNodeParameters(node, param_model)
            else:
                assert override_flow.is_linked
                core_logger.debug(
                    'Changed override parameters for node %s', node)
                cmd = user_commands.EditNodeOverrideParameters(
                    override_flow, node, param_model)
            cmds.append(cmd)
        macro = user_commands.MacroCommand(
            text=f"Editing parameters for flow {top_flow.name}",
            commands=cmds,
            context=user_commands.propagate_flow_ctx(top_flow))

        top_flow.undo_stack().push(macro)
        return [node for node, param_model, override_flow in changed_item_list]

    def handle_subflow_settings_view_done(self, full_uuid, flow_info_dict):
        """Updates the subflow settings."""
        def get_deep_selected_nodes(subflow):
            """
            Return a list of all selected nodes in all subflows below subflow.
            """
            aggregation_settings = subflow.aggregation_settings
            try:
                selected_uuids = aggregation_settings['selected_uuids']
            except KeyError:
                selected_uuids = aggregation_settings.get('uuid_selected', [])
            except TypeError:
                selected_uuids = []

            shallow_flodes = subflow.shallow_nodes()
            shallow_flows = set([n for n in shallow_flodes
                                 if n.type == flow.types.Type.Flow])
            shallow_nodes = set([n for n in shallow_flodes
                                 if n.type == flow.types.Type.Node])

            nodes = []
            for node_ in shallow_nodes:
                if node_.uuid in selected_uuids:
                    nodes.append(node_)

            for subsubflow in shallow_flows:
                if subsubflow.uuid in selected_uuids:
                    nodes.extend(get_deep_selected_nodes(subsubflow))
            return nodes

        def get_deselected_nodes(flow_info, subflow):
            """
            Return a list of nodes that have been deselected from the
            aggregation settings, including all selected nodes in deselected
            subflows.
            If the override setting has been turned off all nodes that were
            selected before will be treated as having been deselected.
            """
            new_aggregation_settings = json.loads(
                flow_info['json_aggregation_settings'])
            old_aggregation_settings = subflow.aggregation_settings
            if old_aggregation_settings is None:
                return []

            # Support older settings formats
            try:
                old_selected = old_aggregation_settings['selected_uuids']
            except KeyError:
                old_selected = old_aggregation_settings.get(
                    'uuid_selected', [])

            new_selected = new_aggregation_settings['selected_uuids']
            deselected_uuids = set(old_selected) - set(new_selected)
            shallow_flodes = subflow.shallow_nodes()
            shallow_flows = {n for n in shallow_flodes
                             if n.type == flow.types.Type.Flow}
            shallow_nodes = {n for n in shallow_flodes
                             if n.type == flow.types.Type.Node}

            # Add deselected shallow nodes
            result = [n for n in shallow_nodes
                      if n.uuid in deselected_uuids]

            # Add deselected shallow nodes
            for subsubflow in shallow_flows:
                if subsubflow.uuid in deselected_uuids:
                    result.extend(get_deep_selected_nodes(subsubflow))
            return result

        def get_deleted_uuids(subflow):
            """
            Return a list of hierarchical uuids for nodes that have overrides
            registered in subflow, but that have since been deleted.
            """
            # The "tree uuids" (joined uuids of all subflows leading to a node)
            # of all the nodes that have overrides stored in this subflow.
            tree_uuids = subflow.override_parameters.keys()
            deleted_tree_uuids = []

            for tree_uuid in tree_uuids:
                flow_ = subflow
                uuid_parts = uuid_generator.split_uuid(tree_uuid)

                for i, uuid_part in enumerate(uuid_parts):
                    shallow_flodes = {n.uuid: n for n in flow_.shallow_nodes()}

                    if uuid_part in shallow_flodes:
                        flow_ = shallow_flodes[uuid_part]
                        last_part = i == len(uuid_parts) - 1
                        is_node = flow_.type == flow.types.Type.Node

                        # The last uuid part should always be a node, and all
                        # other parts should be flows:
                        if last_part != is_node:
                            deleted_tree_uuids.append(tree_uuid)
                            break
                    else:
                        # This uuid_part doesn't exist in flow_
                        deleted_tree_uuids.append(tree_uuid)
                        break
            return deleted_tree_uuids

        confflow = self.get_flow(flow_info_dict['uuid'])
        if confflow is None:
            core_logger.warning(
                "Can't find the flow which was just configured.")
            return

        # Delete lingering overrides for deleted nodes/flows.
        deleted_uuids = get_deleted_uuids(confflow)

        # Remove overrides for this subflow level for nodes which have been
        # deselected in the settings.
        deselected_nodes = get_deselected_nodes(flow_info_dict, confflow)
        deselected_override_nodes = [
            n for n in deselected_nodes
            if n.get_override_parameter_model(confflow) is not None]

        settings = json.loads(flow_info_dict['json_aggregation_settings'])

        # Update the actual aggregation settings.
        cmd = user_commands.EditFlowSettingsCommand(
            confflow, settings, deleted_uuids, deselected_override_nodes)
        if deleted_uuids or deselected_override_nodes or (
                not cmd.aggregation_settings_are_equal()):
            confflow.undo_stack().push(cmd)

    def port_viewer(self, port):
        """Open the port viewer that matches the given node and port."""
        self.execute_port_viewer.emit(port)

    #
    # Misc
    #
    def restart_workers(self):
        """Restart all task workers, effectively reloading all node related
        python code.
        """
        self.restart_all_task_workers.emit()

    def interface_started(self):
        """
        Called after interface (cli/gui) is operational to allow for feedback
        about the platform status, perform cleanup, etc.
        """
        brief_session = (
            'The temporary files folder could not be created, please make '
            'sure that the selected folder exists and '
            'that you have write access to it and then RESTART the '
            'APPLICATION.\n'
            'The setting is found in: "Preferences -> Temporary Files -> '
            'Temporary Files".')

        if not os.path.exists(settings.instance().sessions_folder):
            self.display_message(
                messages.DisplayMessage(
                    level=messages.Levels.error,
                    title='Startup failed',
                    brief=brief_session))
