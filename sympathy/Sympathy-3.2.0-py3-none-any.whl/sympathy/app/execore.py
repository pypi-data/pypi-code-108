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
import json
import warnings
import traceback
import collections
import functools
import datetime
import Qt.QtCore as QtCore

from sympathy.platform import node_result
from sympathy.platform import os_support
from sympathy.platform.message import Message
from sympathy.platform import message as msgmod
from sympathy.utils import log

from sympathy.app.environment_variables import expanded_node_dict
from . import flow
from . util import OrderedSet, result_messages, node_messages
from . messages import DisplayMessage, ResultMessage
from . tasks import task_worker
from . tasks import task_worker2
from . flow.types import Type
from . import settings

working_dir = os.getcwd()
core_logger = log.get_logger('core')

# Avoid creating too many processes.
THREAD_COUNT = os_support.limited_thread_count()

LOCALHOST = '127.0.0.1'

_type_aliases = {}


def flow_environ(flow):
    if flow.flow is not None:
        parent_environ = flow_environ(flow.flow)
    else:
        parent_environ = {}
    parent_environ.update(flow.root_or_linked_flow().parameters['environment'])
    return parent_environ


def node_settings(node):
    try:
        # Perhaps node is a flow?
        res = node.node_settings()
    except AttributeError:
        # node is a "proper" node
        res = node.flow.node_settings()
    return res


def node_directory(node):
    result = None
    try:
        # Perhaps node is a flow?
        result = os.path.dirname(
            node.root_flow().filename)
    except AttributeError:
        # node is a "proper" node
        result = os.path.dirname(
            node.flow.root_flow().filename)

    if not result:
        result = settings.instance()['default_folder']
    return result


class TaskError(Exception):
    pass


class Status(object):
    """
    Responsible for keeping track of the status of a task in progress
    abstracting away the details of taskids and queues, etc. from the user.
    """

    def __init__(self, node, task, child_nodes=None):
        self._task = task
        self._taskid = next(task)
        self._node = node
        self._child_nodes = None
        if child_nodes:
            self._child_nodes = {c.full_uuid: c for c in child_nodes}

    @property
    def taskid(self):
        return self._taskid

    @property
    def node(self):
        return self._node

    @property
    def child_nodes(self):
        return self._child_nodes

    def start(self):
        for _ in self._task:
            pass

    def abort(self):
        task_worker.abort_task(self._taskid)

    def put_messages(self, messages):
        for message in messages:
            task_worker.update_task(self.taskid, message.to_dict())

    def wait(self):
        with task_worker.await_done(self._taskid) as (done_msg, update_msgs):
            result = node_result.from_dict(done_msg[2])
        return result


class Executor(object):
    """
    Interface.

    Responsible for performing the actions on the node.
    All methods return Status instances.
    """

    def __init__(self, node, aliases):
        self._node = node
        self._aliases = aliases

    def validate(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def view(self):
        raise NotImplementedError


class NodeExecutor(Executor):

    def validate(self):
        node_dict = expanded_node_dict(
            self._node.to_dict(True), flow_environ(self._node.flow))

        return Status(
            self._node,
            task_worker.worker(
                ('validate_parameters',
                 self._node.source_file,
                 self._node.class_name,
                 self._node.full_uuid,
                 json.dumps(node_dict),
                 self._aliases,
                 node_directory(self._node),
                 node_settings(self._node)),
                None))

    def execute(self, mode):
        node_dict = expanded_node_dict(
            self._node.to_dict(True), flow_environ(self._node.flow))

        return Status(
            self._node,
            task_worker.worker(
                (mode,
                 self._node.source_file,
                 self._node.class_name,
                 self._node.full_uuid,
                 json.dumps(node_dict),
                 self._aliases,
                 node_directory(self._node),
                 node_settings(self._node)),
                self._node.log_filename,
                quit_after=self._node.quit_after_exec))

    def view(self):
        directory = node_directory(self._node)
        return Status(
            self._node,
            task_worker.worker(
                ('execute_parameter_view',
                 self._node.source_file,
                 self._node.class_name,
                 self._node.full_uuid,
                 json.dumps(self._node.to_dict(True)),
                 self._aliases,
                 directory, node_settings(self._node)),
                None,
                quit_after=True))


def flowdata(flow):
    all_nodes = flow.all_nodes(remove_invalid=False, atom=True)
    node_list = flow.node_set_list(remove_invalid=False, atom=True)
    # TODO(Erik): Proper handling of nodes that are not connected.
    order = [node.full_uuid for node in node_list
             if not hasattr(node, 'inputs_are_connected') or
             node.inputs_are_connected()]
    node_dependencies = [(src.full_uuid, dst.full_uuid)
                         for src, dst in flow.internal_node_dependencies()]
    bypass_ports = [
        src.node.index for src, dst in flow.bypass_ports()]
    input_ports = flow.ports_connected_to_input_ports(group=True)
    output_ports = flow.ports_connected_to_output_ports()
    input_nodes = [port.node.full_uuid for flowio_ports in input_ports
                   for port in flowio_ports]
    output_nodes = [port.node.full_uuid if port else None
                    for port in output_ports]
    input_ports = [[port.full_uuid for port in flowio_ports]
                   for flowio_ports in input_ports]
    output_ports = [port.full_uuid for port in output_ports]

    nodes = {}

    for node_ in all_nodes:
        try:
            atom = node_.is_atom()
        except AttributeError:
            atom = False

        if atom:
            node_dict = flowdata(node_)
            source_file = None
        else:
            node_dict = expanded_node_dict(
                node_.to_dict(execute=True),
                flow_environ(node_.flow))
            source_file = node_.source_file

        nodes[node_.full_uuid] = (
            source_file,
            node_.class_name,
            node_.full_uuid,
            json.dumps(node_dict))

    fnodes = sorted([node for node in nodes.items() if node[0] in order],
                    key=lambda x: order.index(x[0]))

    if len(fnodes) < len(nodes):
        # Workaround message since logging gsetup is, currently, not present
        # during extract.
        # nodes = sorted(set(nodes) - set(order))
        raise TaskError('Unconnected nodes in subflow')

    result = {'full_uuid': flow.full_uuid,
              'nodes': fnodes,
              'node_deps': node_dependencies,
              'input_nodes': input_nodes,
              'output_nodes': output_nodes,
              'input_ports': input_ports,
              'output_ports': output_ports,
              'bypass_ports': bypass_ports,
              'name': flow.name,
              'node_settings': node_settings(flow)}

    try:
        return flow.to_node_dict(result)
    except AttributeError:
        return result


class FlowExecutor(Executor):

    def execute(self, mode):
        return Status(
            self._node,
            task_worker.worker(
                (mode,
                 None,
                 self._node.class_name,
                 self._node.full_uuid,
                 json.dumps(flowdata(self._node)),
                 self._aliases,
                 node_directory(self._node),
                 node_settings(self._node)),
                self._node.log_filename),
            child_nodes=self._node.all_nodes(atom=True))

    def view(self, mode):

        def sort_groups(flow_):
            nodes = flow_.predecessor_node_depths()
            if nodes:
                res = [[sort_groups(n) if isinstance(n, flow.Flow) else n
                        for n in g]
                       for g in nodes]
                res[0].insert(0, flow_)
            else:
                res = [[flow_]]
            return res

        def enumerate_sorted(sorted_groups):
            """
            Depth sorting with ability to handle atom Flows, like locked
            subflows, including enumeration for both nodes and flows.
            """
            res = {}

            def inner(group, i):
                for j, group in enumerate(group):
                    depth = i + j
                    for item in group:
                        if isinstance(item, list):
                            inner(item, depth)
                        else:
                            # Assuming Node or Flow.
                            res[item.full_uuid] = depth
            inner(sorted_groups, 0)
            return res

        def sort_fcn(v1):
            uuid = v1['uuid']
            level = v1['level']
            return(level, uuid)

        def node_info(f, level_mapping):
            node_list = []

            for node in f.shallow_nodes():

                if node.type == Type.Node:
                    uuid = node.full_uuid
                    try:
                        level = level_mapping[uuid]
                    except KeyError:
                        # The typical reason is lambdas or locked subflows
                        # inside of the flow being configured.
                        core_logger.debug(
                            'Node uuid: %s was not found in mapping, '
                            'this can cause problems ordering '
                            'wizard configuration.', uuid)
                        level = 0

                    node_dict = {
                        'node_settings': node_settings(f),
                        'uuid': uuid,
                        'class_name': node.class_name,
                        'source_file': node.source_file,
                        'library': node.library,
                        'level': level,
                        'name': node.name,
                        'svg_icon_data': (
                            str(
                                node.svg_icon_data.toBase64())
                            if node.has_svg_icon else None),
                        'json_node_dict': json.dumps(
                            node.to_dict(True))}
                    node_list.append(node_dict)

            node_list.sort(key=sort_fcn)

            return node_list

        def subflow_info(f, level_mapping):
            return {'uuid': f.full_uuid,
                    'name': f.name,
                    'json_aggregation_settings': json.dumps(
                        f.aggregation_settings),
                    'is_linked': f.is_linked,
                    'nodes': node_info(f, level_mapping),
                    'flows': [subflow_info(flw, level_mapping)
                              for flw in f.shallow_subflows()]}

        # Acquire sorted node structure.
        uuid_to_group = enumerate_sorted(sort_groups(self._node))
        flow_info = subflow_info(self._node, uuid_to_group)

        return Status(
            self._node,
            task_worker.aggregated_parameter_view_worker(
                ('aggregated_parameter_view',
                 mode,
                 self._node.full_uuid,
                 json.dumps(flow_info),
                 self._aliases,
                 node_directory(self._node)),
                quit_after=True))


class LambdaExecutor(FlowExecutor):

    def execute(self, mode):

        return Status(
            self._node,
            task_worker.worker(
                (mode,
                 None,
                 self._node.class_name,
                 self._node.full_uuid,
                 json.dumps(flowdata(self._node)),
                 self._aliases,
                 node_directory(self._node),
                 node_settings(self._node)),
                self._node.log_filename))


class PortViewerExecutor(Executor):

    def view(self):
        return Status(
            self._node,
            task_worker.worker(
                ('execute_port_viewer',
                 self._node.node.source_file,
                 self._node.node.class_name,
                 self._node.full_uuid,
                 json.dumps([self._node.filename,
                             self._node.index,
                             self._node.node.name,
                             self._node.node.icon]),
                 self._aliases,
                 node_directory(self._node.node),
                 node_settings(self._node.node)), None,
                quit_after=True))


def executor(element, aliases):
    """
    Return new executor appropriate for element.

    One single manager may handle different executors, and this avoids
    repeating the if statement.
    """
    if element.executor == flow.Executors.Node:
        return NodeExecutor(element, aliases)
    elif element.executor == flow.Executors.Lambda:
        return LambdaExecutor(element, aliases)
    elif element.executor == flow.Executors.Flow:
        return FlowExecutor(element, aliases)
    elif element.executor == flow.Executors.Port:
        return PortViewerExecutor(element, aliases)
    else:
        assert(False)


class WarnOverwriteDict(collections.OrderedDict):
    def __setitem__(self, key, value):
        if key in self:
            warnings.warn('Overwrite key: {}.Stack:\n{}'.format(
                key, ''.join(traceback.format_stack())))
        return super(WarnOverwriteDict, self).__setitem__(key, value)


def not_reenterable(func):
    entries = collections.defaultdict(bool)

    @functools.wraps(func)
    def inner(*args, **kwargs):
        if entries[func]:
            return
        entries[func] = True
        try:
            ret = func(*args, **kwargs)
        finally:
            entries[func] = False
        return ret
    return inner


class NodeExecuteContext(object):
    """
    Keeps track of the kind of execute action to take, debug profile or
    execute.
    """

    def __init__(self, node, action):
        self.node = node
        self.action = action


class TaskManager(QtCore.QObject):
    message_output = QtCore.Signal(int, Message)

    def __init__(self, parent=None):
        super(TaskManager, self).__init__(parent)
        self._taskids = {}

    @property
    def tasks(self):
        return self._taskids

    def process(self):
        pass

    def done(self):
        raise NotImplementedError('Interface: override to use.')


class BaseTaskManager(TaskManager):
    def __init__(self, parent=None):
        super(BaseTaskManager, self).__init__(parent=parent)
        self._views = collections.OrderedDict()

    def done(self):
        return not self._views

    def _handle_task_done(self, taskid, elemid, task, result):
        pass

    def _handle_task_update(self, taskid, elemid, task, msg):
        pass

    def handle_message(self, message):
        taskid, cmd, data = message
        if cmd == task_worker2.DONE_TASK:
            full_uuid = self._taskids.pop(taskid, None)
            task = self._views.pop(full_uuid, None)
            result = None
            if full_uuid:
                result = node_result.from_dict(data)
            self._handle_task_done(taskid, full_uuid, task, result)

        elif cmd == task_worker2.UPDATE_TASK:
            full_uuid = self._taskids.get(taskid)
            task = self._views.get(full_uuid, None)
            msg = None
            if full_uuid:
                msg = msgmod.from_dict(data)
            self._handle_task_update(taskid, full_uuid, task, msg)

    def handle_message_reply(self, taskid, message):
        if taskid in self._taskids:
            full_uuid = self._taskids[taskid]
            view = self._views[full_uuid]
            view.put_messages([message])

        elif taskid == -1:
            for taskid, full_uuid in self._taskids.items():
                view = self._views[full_uuid]
                view.put_messages([message])


class NodeTaskManager(TaskManager):
    node_is_queued = QtCore.Signal(flow.NodeInterface)
    node_execution_started = QtCore.Signal(flow.NodeInterface)
    execute_node_done = QtCore.Signal(
        flow.NodeInterface, node_result.NodeResult)
    execute_child_node_done = QtCore.Signal(
        flow.NodeInterface, flow.NodeInterface,
        node_result.NodeResult, bool)
    port_done = QtCore.Signal(flow.Port)
    node_is_aborting = QtCore.Signal(flow.NodeInterface, list)
    node_has_aborted = QtCore.Signal(flow.NodeInterface, list)
    node_progress_changed = QtCore.Signal(flow.NodeInterface, float)
    child_node_progress_changed = QtCore.Signal(
        flow.NodeInterface, flow.NodeInterface, float)
    display_message = QtCore.Signal(DisplayMessage)

    all_nodes_finished = QtCore.Signal()
    profiling_finished = QtCore.Signal(set)

    def __init__(self, parent=None):
        super(NodeTaskManager, self).__init__(parent)

        self._waiting_nodes = collections.OrderedDict()
        self._ready_nodes = collections.OrderedDict()
        self._running_tasks = collections.OrderedDict()

        self._nodes_dict = {}
        self._modes_dict = {}

        self._profile_nodes_done = set()
        self._profile_nodes_dict = {}

    def profiling_done(self):
        return (not self._profile_nodes_dict and
                self._profile_nodes_done)

    def _complete_profiling(self):
        self.profiling_finished.emit(list(self._profile_nodes_done))
        self._profile_nodes_done = set()

    def handle_message(self, message):
        def get_child_node(child_full_uuid, parent_full_uuid=None, task=None):
            if not task:
                task = self._running_tasks[parent_full_uuid]
            child_nodes = task.child_nodes
            return child_nodes[child_full_uuid]

        taskid, cmd, data = message
        if cmd == task_worker2.DONE_TASK:
            full_uuid = self._taskids[taskid]
            task = self._running_tasks[full_uuid]
            profiling = full_uuid in self._profile_nodes_dict
            node = self._complete_task(full_uuid)
            result = node_result.from_dict(data)
            error = result.has_error()
            status = result.status

            child_results = result.child_results
            parent_done = status == 1

            if node and profiling and not error:
                self._profile_nodes_done.add(node)

            if child_results:
                for child_full_uuid, child_result in child_results:
                    child_node = get_child_node(child_full_uuid, task=task)
                    self.execute_child_node_done.emit(
                        node, child_node, child_result, parent_done)

            self.execute_node_done.emit(node, result)
            for node_message in node_messages(node, result):
                self.display_message.emit(node_message)

            if self.profiling_done():
                self._complete_profiling()

            if status and node:
                for port in node.outputs:
                    self.port_done.emit(port)

            self.process()

        elif cmd == task_worker2.UPDATE_TASK:
            msg = msgmod.from_dict(data)
            if msg.type == msgmod.ProgressMessage:
                full_uuid = self._taskids.get(taskid)
                if full_uuid:
                    node = self._get_node(full_uuid)
                    self.node_progress_changed.emit(node, msg.data)
            if msg.type == msgmod.ChildNodeProgressMessage:
                full_uuid = self._taskids.get(taskid)
                child_full_uuid, child_progress = msg.data

                if full_uuid and child_full_uuid:
                    node = self._get_node(full_uuid)
                    self.child_node_progress_changed.emit(
                        node, get_child_node(child_full_uuid, full_uuid),
                        child_progress)

            elif msg.type == msgmod.ChildNodeDoneMessage:
                full_uuid = self._taskids.get(taskid)
                child_full_uuid, node_result_dict = msg.data
                child_result = node_result.from_dict(node_result_dict)
                if full_uuid and child_full_uuid:
                    node = self._get_node(full_uuid)
                    self.execute_child_node_done.emit(
                        node, get_child_node(child_full_uuid, full_uuid),
                        child_result, False)
            else:
                full_uuid = self._taskids.get(taskid)
                if full_uuid:
                    self.message_output.emit(taskid, msg)

    def done(self):
        return len((self._waiting_nodes or
                    self._ready_nodes or self._running_tasks or {})) == 0

    def process(self):
        self._schedule_nodes()
        if self.done():
            self.all_nodes_finished.emit()

    def already_processing(self, full_uuid):
        try:
            return (
                full_uuid in self._waiting_nodes or
                full_uuid in self._ready_nodes or
                full_uuid in self._running_tasks)
        except KeyError:
            return False

    def add_node(self, node, mode):
        full_uuid = node.full_uuid

        if node in self._nodes_dict:
            return

        self._nodes_dict[full_uuid] = node
        self._modes_dict[full_uuid] = mode
        self._waiting_nodes[full_uuid] = node
        self.node_is_queued.emit(node)

    def add_nodes(self, nodes, mode):
        for node in nodes:
            self.add_node(node, mode)
        if mode == 'profile':
            # Only one profiling at a time.
            self._profile_nodes_dict = {node.full_uuid: node
                                        for node in nodes}
            self._profile_done = set()

    def abort_node(self, node):
        full_uuid = node.full_uuid
        task = self._running_tasks.pop(full_uuid, None)
        child_nodes = None

        if task:
            child_nodes = task.child_nodes
            if child_nodes is not None:
                child_nodes = [c for c in list(child_nodes.values())]
        else:
            try:
                locked = node.is_locked()
            except AttributeError:
                locked = False
            # TODO(Erik): Create a better solution! We do not track child nodes
            # unless executing, so these are not canceled properly unless
            # execution has started. Abort for subflows relies on the states of
            # child nodes. Overall state handling for locked flows becomes
            # difficult because its logic is shared with normal flow handling.
            if locked:
                child_nodes = list(node.all_nodes(atom=True))

        child_nodes = child_nodes or []
        self.node_is_aborting.emit(node, child_nodes)

        if task:
            self._taskids.pop(task.taskid, None)
            task.abort()

        self._remove_node(full_uuid)
        self.node_has_aborted.emit(node, child_nodes)

        if self.profiling_done():
            self._complete_profiling()

    def _remove_node(self, full_uuid):
        node = self._nodes_dict.pop(full_uuid, None)
        if node:
            self._waiting_nodes.pop(full_uuid, None)
            self._ready_nodes.pop(full_uuid, None)
            self._profile_nodes_dict.pop(full_uuid, None)
            self._modes_dict.pop(full_uuid, None)
            return node

    def _complete_task(self, full_uuid):
        task = self._running_tasks.pop(full_uuid, None)
        if task:
            self._taskids.pop(task.taskid, None)

        return self._remove_node(full_uuid)

    def _get_node(self, full_uuid):
        return self._nodes_dict.get(full_uuid)

    def _schedule_nodes(self):
        self._add_ready_nodes_to_task_queue()

        error_nodes = []

        for node in list(self._ready_nodes.values()):
            try:
                self._execute_node(node)
            except TaskError as e:
                error_nodes.append(node)
                result = node_result.NodeResult()
                result.stderr = 'Failed to schedule {} due to: {}.'.format(
                    node, e)
                for node_message in node_messages(node, result):
                    self.display_message.emit(node_message)

        for error_node in error_nodes:
            self.abort_node(error_node)

    def _add_ready_nodes_to_task_queue(self):
        abort_nodes = []
        execute_nodes = []

        def is_node_ready_to_execute(node):
            return (
                node.all_incoming_nodes_are_successfully_executed() and
                node.full_uuid in self._waiting_nodes)

        def should_node_abort(node):
            return (
                node.is_queued() and
                not node.all_incoming_nodes_are_queued_or_executing_or_done())

        for node in list(self._waiting_nodes.values()):
            if is_node_ready_to_execute(node):
                execute_nodes.append(node)
            elif should_node_abort(node):
                abort_nodes.append(node)
            elif not node.is_queued():
                try:
                    state_string = node.state_string()
                except AttributeError:
                    state_string = '-'
                core_logger.critical(
                    '%s INCONSISTENT EXECORE STATE %s',
                    datetime.datetime.now().isoformat(), state_string)

        for node in abort_nodes:
            self.abort_node(node)

        for node in execute_nodes:
            full_uuid = node.full_uuid
            del self._waiting_nodes[full_uuid]
            self._ready_nodes[full_uuid] = node

    def _execute_node(self, node):
        full_uuid = node.full_uuid
        mode = self._modes_dict[full_uuid]
        task = executor(node, _type_aliases).execute(mode)
        del self._ready_nodes[full_uuid]
        self._running_tasks[full_uuid] = task
        self._taskids[task.taskid] = full_uuid
        task.start()
        self.node_execution_started.emit(node)

    def handle_message_reply(self, taskid, message):
        if taskid in self._taskids:
            full_uuid = self._taskids[taskid]
            run = self._running_tasks[full_uuid]
            run.put_messages([message])


class ParameterViewTaskManager(BaseTaskManager):
    execute_node_parameter_view_done = QtCore.Signal(
        flow.NodeInterface, node_result.NodeResult)
    display_message = QtCore.Signal(DisplayMessage)
    help_requested = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(ParameterViewTaskManager, self).__init__(parent=parent)

    def _handle_task_done(self, taskid, full_uuid, task, result):
        if task:
            task._node.parameter_view_open = False
            self.execute_node_parameter_view_done.emit(
                task.node, result)
            for node_message in node_messages(task.node, result):
                self.display_message.emit(node_message)

    def _handle_task_update(self, taskid, full_uuid, task, msg):
        if msg.type == msgmod.RequestHelpMessage:
            help_entry = msg.data
            self.help_requested.emit(help_entry)
        elif full_uuid:
            self.message_output.emit(taskid, msg)

    def add_view(self, node):
        if node.full_uuid in self._views:
            view = self._views[node.full_uuid]
            msg = msgmod.RaiseWindowMessage(node.full_uuid)
            view.put_messages([msg])
        else:
            node.parameter_view_open = True
            task = executor(node, _type_aliases).view()
            self._views[node.full_uuid] = task
            self._taskids[task.taskid] = node.full_uuid
            task.start()

    def message_input(self, ident, message):
        if ident is None:
            for view in self._views.values():
                view.put_messages([message])
        try:
            self._views[ident].put_messages([message])
        except KeyError:
            pass


class AggregatedParameterViewTaskManager(ParameterViewTaskManager):
    execute_subflow_parameter_view_done = QtCore.Signal(
        flow.NodeInterface, node_result.NodeResult)

    def _handle_task_done(self, taskid, full_uuid, task, result):
        if task:
            task._node.parameter_view_open = False

        if result and result.valid:
            self.execute_subflow_parameter_view_done.emit(
                task.node, result)

        for node_message in node_messages(task.node, result):
            self.display_message.emit(node_message)

    def _handle_task_update(self, taskid, full_uuid, task, msg):
        if full_uuid:
            self.message_output.emit(taskid, msg)

    def add_view(self, node, mode):
        if node.full_uuid in self._views:
            view = self._views[node.full_uuid]
            msg = msgmod.RaiseWindowMessage(node.full_uuid)
            view.put_messages([msg])
        else:
            node.parameter_view_open = True
            task = executor(node, _type_aliases).view(mode)
            self._views[node.full_uuid] = task
            self._taskids[task.taskid] = node.full_uuid
            task.start()


class ValidateTaskManager(BaseTaskManager):
    validate_node_done = QtCore.Signal(
        flow.NodeInterface, node_result.NodeResult)
    display_message = QtCore.Signal(ResultMessage)

    def _handle_task_done(self, taskid, full_uuid, task, result):
        if full_uuid:
            self.validate_node_done.emit(task.node, result)
            for node_message in node_messages(task.node, result):
                self.display_message.emit(node_message)

    def _handle_task_update(self, taskid, full_uuid, task, msg):
        if full_uuid:
            self.message_output.emit(taskid, msg)

    def add_view(self, node):
        if node.full_uuid not in self._views:
            task = executor(node, _type_aliases).validate()
            self._views[node.full_uuid] = task
            self._taskids[task.taskid] = node.full_uuid
            task.start()


class PortViewerTaskManager(BaseTaskManager):
    execute_node_parameter_view_done = QtCore.Signal(
        flow.NodeInterface, node_result.NodeResult)
    display_message = QtCore.Signal(DisplayMessage)
    help_requested = QtCore.Signal(str)

    def _handle_task_done(self, taskid, full_uuid, task, result):
        if full_uuid and task:
            if task:
                try:
                    # TODO: This should ideally be handled via appcore.
                    task._node.port_viewer_open = False
                except Exception:
                    # Exception happens if node is already removed. Assignment
                    # is needed for port to get the right viewer state when
                    # remove is undone.
                    pass
        for msg in node_messages(task._node, result, title="Viewer"):
            self.display_message.emit(msg)

    def _handle_task_update(self, taskid, full_uuid, task, msg):
        if msg.type == msgmod.RequestHelpMessage:
            help_entry = msg.data
            self.help_requested.emit(help_entry)
        elif full_uuid:
            if isinstance(msg, msgmod.OutStreamMessage):
                ident, text = msg.data
                self.message_output.emit(taskid, type(msg)(
                    [full_uuid, text]))
            else:
                self.message_output.emit(full_uuid, msg)

    def add_view(self, port):
        if port.full_uuid in self._views:
            view = self._views[port.full_uuid]
            msg = msgmod.RaiseWindowMessage(port.full_uuid)
            view.put_messages([msg])
        else:
            port.port_viewer_open = True
            task = executor(port, _type_aliases).view()
            self._views[port.full_uuid] = task
            self._taskids[task.taskid] = port.full_uuid
            task.start()

    def handle_port_done(self, port):
        full_uuid = port.full_uuid
        view = self._views.get(full_uuid)
        if view:
            msg = msgmod.PortDataReadyMessage.init_args(
                port.filename, full_uuid, str(port.datatype))
            view.put_messages([msg])


class ExeCore(QtCore.QObject):
    execute_node_done = QtCore.Signal(
        flow.NodeInterface, node_result.NodeResult)
    execute_child_node_done = QtCore.Signal(
        flow.NodeInterface, flow.NodeInterface, node_result.NodeResult, bool)
    validate_node_done = QtCore.Signal(
        flow.NodeInterface, node_result.NodeResult)
    node_progress_changed = QtCore.Signal(flow.NodeInterface, float)
    child_node_progress_changed = QtCore.Signal(
        flow.NodeInterface, flow.NodeInterface, float)
    # node_status_changed = QtCore.Signal(flow.NodeInterface, str)
    message_output = QtCore.Signal(int, Message)

    all_nodes_finished = QtCore.Signal()
    profiling_finished = QtCore.Signal(set)
    node_is_queued = QtCore.Signal(flow.NodeInterface)
    node_execution_started = QtCore.Signal(flow.NodeInterface)
    node_has_aborted = QtCore.Signal(flow.NodeInterface, list)
    node_is_aborting = QtCore.Signal(flow.NodeInterface, list)
    node_allowed_to_execute_request = QtCore.Signal(flow.NodeInterface)
    display_message = QtCore.Signal(DisplayMessage)

    execute_node_parameter_view_done = QtCore.Signal(
        flow.NodeInterface, node_result.NodeResult)
    execute_subflow_parameter_view_done = QtCore.Signal(
        flow.NodeInterface, node_result.NodeResult)

    help_requested = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(ExeCore, self).__init__(parent)
        self._node_task_manager = NodeTaskManager(self)
        self._parameter_view_task_manager = ParameterViewTaskManager(self)
        self._aggregated_parameter_view_task_manager = (
            AggregatedParameterViewTaskManager(self))
        self._port_viewer_task_manager = PortViewerTaskManager(self)
        self._validate_task_manager = ValidateTaskManager(self)

        self._task_managers = (
            self._node_task_manager, self._parameter_view_task_manager,
            self._aggregated_parameter_view_task_manager,
            self._validate_task_manager, self._port_viewer_task_manager)

        self._connect()

    def _connect(self):
        self._node_task_manager.node_is_queued.connect(
            self.node_is_queued)
        self._node_task_manager.node_execution_started.connect(
            self.node_execution_started)
        self._node_task_manager.execute_node_done.connect(
            self.execute_node_done)
        self._node_task_manager.execute_child_node_done.connect(
            self.execute_child_node_done)
        self._node_task_manager.node_is_aborting.connect(
            self.node_is_aborting)
        self._node_task_manager.node_has_aborted.connect(
            self.node_has_aborted)

        self._node_task_manager.node_progress_changed.connect(
            self.node_progress_changed)
        self._node_task_manager.child_node_progress_changed.connect(
            self.child_node_progress_changed)
        # self._node_task_manager.node_status_changed.connect(
        #     self.node_status_changed)
        self._node_task_manager.display_message.connect(
            self.display_message)
        self._port_viewer_task_manager.display_message.connect(
            self.display_message)
        self._port_viewer_task_manager.help_requested.connect(
            self.help_requested)
        self._node_task_manager.all_nodes_finished.connect(
            self.all_nodes_finished)
        self._node_task_manager.profiling_finished.connect(
            self.profiling_finished)
        self._node_task_manager.port_done.connect(
            self._port_viewer_task_manager.handle_port_done)

        tm = self._parameter_view_task_manager
        tm.execute_node_parameter_view_done[
            flow.NodeInterface, node_result.NodeResult].connect(
                self.execute_node_parameter_view_done)
        tm.display_message.connect(self.display_message)
        tm.help_requested.connect(self.help_requested)

        agtm = self._aggregated_parameter_view_task_manager
        agtm.execute_subflow_parameter_view_done[
            flow.NodeInterface, node_result.NodeResult].connect(
                self.execute_subflow_parameter_view_done)
        agtm.display_message.connect(self.display_message)

        self._validate_task_manager.validate_node_done.connect(
            self.validate_node_done)
        self._validate_task_manager.display_message.connect(
            self.display_message)

        managers = [tm, agtm, self._validate_task_manager,
                    self._node_task_manager, self._port_viewer_task_manager]

        for manager in managers:
            manager.message_output.connect(self.message_output)

        task_worker.create_client().received.connect(
            self._messages_received)

    def _messages_received(self, messages):
        for message in messages:
            taskid, cmd, msg = message
            for task_manager in self._task_managers:
                if taskid in task_manager.tasks:
                    task_manager.handle_message(message)

    def message_input(self, ident, message):
        if message.type == msgmod.DataReadyMessage:
            self._aggregated_parameter_view_task_manager.handle_message_reply(
                ident, message)
        elif message.type == msgmod.DataBlockedMessage:
            self._aggregated_parameter_view_task_manager.handle_message_reply(
                ident, message)
        else:
            handled = False
            for task_manager in self._task_managers:
                if ident in task_manager.tasks:
                    task_manager.handle_message_reply(ident, message)
                    handled = True
                    break

            if not handled:
                core_logger.debug('Execore: ignoring message_input: %s',
                                  str(message.type.__name__))

    def set_type_aliases(self, type_aliases):
        global _type_aliases
        _type_aliases = type_aliases

    # @not_reenterable
    def process(self):
        not_finished_managers = (
            [task_manager for task_manager in self._task_managers
             if not task_manager.done()])
        # Check if any tasks are running.
        if not_finished_managers:
            for task_manager in not_finished_managers:
                task_manager.process()

    def _execute_nodes(self, node_set, mode='execute'):
        if len(node_set) == 0:
            return

        def already_executed_or_processing(node):
            return (
                node.is_successfully_executed() or
                self._node_task_manager.already_processing(node.full_uuid))

        node_set = [node for node in node_set
                    if not already_executed_or_processing(node)]
        self._node_task_manager.add_nodes(node_set, mode)

    @QtCore.Slot(OrderedSet)
    def execute_nodes(self, node_set):
        self._execute_nodes(node_set, 'execute')
        self.process()

    @QtCore.Slot(OrderedSet)
    def debug_nodes(self, node_set):
        node_set = list(node_set)

        node = node_set[-1:]
        if not node:
            return
        self.execute_nodes(node_set[:-1])
        node = node[0]

        node_dict = expanded_node_dict(
            node.to_dict(True), flow_environ(node.flow))

        task = task_worker.worker(
            ('debug',
             node.source_file,
             node.class_name,
             node.full_uuid,
             json.dumps(node_dict),
             _type_aliases,
             node_directory(node),
             node_settings(node)),
            None)
        for _ in task:
            pass

    @QtCore.Slot(OrderedSet, OrderedSet)
    def profile_nodes(self, node_set_execute, node_set_profile):
        self._execute_nodes(node_set_execute, 'execute')
        self._execute_nodes(node_set_profile, 'profile')
        self.process()

    @QtCore.Slot(flow.NodeInterface)
    def abort_node(self, node):
        self._node_task_manager.abort_node(node)
        # self.process()

    @QtCore.Slot(flow.Node)
    def validate_node(self, node):
        self._validate_task_manager.add_view(node)
        self.process()

    @QtCore.Slot(flow.Node)
    def execute_node_parameter_view(self, node):
        self._parameter_view_task_manager.add_view(node)
        self.process()

    @QtCore.Slot(flow.Flow, str)
    def execute_subflow_parameter_view(self, subflow, mode):
        self._aggregated_parameter_view_task_manager.add_view(
            subflow, mode)
        self.process()

    @QtCore.Slot(flow.Port)
    def execute_port_viewer(self, port):
        self._port_viewer_task_manager.add_view(port)
        self.process()

    @QtCore.Slot()
    def restart_all_task_workers(self):
        task_worker.set_workers(None)
