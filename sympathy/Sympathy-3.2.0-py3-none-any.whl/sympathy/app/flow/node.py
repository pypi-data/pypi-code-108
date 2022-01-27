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
import collections
import itertools
import enum

import PySide2.QtCore as QtCore

from sympathy.platform import port as port_platform
from sympathy.utils import log
from sympathy.platform.migrations import epoch_version
from . types import NodeStatusInterface, Type, NodeInterface, Executors
from .. library import PortDefinition
from . import flowlib
from .. import datatypes
from . import exceptions
from .. import migrations


core_logger = log.get_logger('core')
factories = collections.defaultdict(lambda: Node)

# TODO: Improve visual handling of ports so that limit can be removed.
max_nports = 6


class StateMachine(QtCore.QObject):

    def __init__(self, parent):
        super().__init__(parent)
        self._running = False
        self._containers = []

    def addContainer(self, container):
        if container in self._containers:
            raise Exception(
                'Multiple calls to addContainer with same container.')

        self._containers.append(container)

    def configuration(self):
        return [container.state for container in self._containers]

    def start(self):
        self._running = True
        for container in self._containers:
            container.entered.emit(container._state)

    def isRunning(self):
        return self._running


class StateContainer(QtCore.QObject):

    entered = QtCore.Signal(object)
    exited = QtCore.Signal(object)

    def __init__(self, state_machine, transitions, start):
        super().__init__(state_machine)
        self._state = start
        self._states = []
        self._state_machine = state_machine
        self._transitions = transitions

        assert start in transitions

        state_machine.addContainer(self)

    def transit(self, event):
        from_state = self._state
        to_state = self._transitions.get(from_state, {}).get(event)

        if to_state:
            self.exited.emit(from_state)
            self._state = to_state
            self.entered.emit(to_state)

    @property
    def state(self):
        return self._state


class TitleMixin:
    def __str__(self):
        return ' '.join([x.capitalize() for x in self.name.split('_')])


# How 'bout ready and waiting or just a bool!?
class PendingStates(TitleMixin, enum.Enum):
    idle = enum.auto()
    pending = enum.auto()


class States(TitleMixin, enum.Enum):
    armed = enum.auto()
    done = enum.auto()
    done_locked = enum.auto()
    error = enum.auto()
    executing = enum.auto()
    invalid = enum.auto()
    queued = enum.auto()
    valid = enum.auto()


class TransitionStates(TitleMixin, enum.Enum):
    aborting = enum.auto()
    aborting_valid = enum.auto()
    aborting_invalid = enum.auto()
    initializing = enum.auto()
    validating = enum.auto()


class Events(TitleMixin, enum.Enum):
    node_error_occured = enum.auto()
    node_execution_finished = enum.auto()
    node_has_aborted = enum.auto()
    node_is_aborting = enum.auto()
    node_is_armed = enum.auto()
    node_is_disarmed = enum.auto()
    node_is_executing = enum.auto()
    node_is_queued = enum.auto()
    node_locked_execution_finished = enum.auto()
    parameters_are_being_validated = enum.auto()
    parameters_are_invalid = enum.auto()
    parameters_are_valid = enum.auto()
    inputs_are_available = enum.auto()
    inputs_are_processing = enum.auto()
    inputs_are_ready = enum.auto()
    inputs_are_unavailable = enum.auto()


class PendingEvents(TitleMixin, enum.Enum):
    pending_call_sent = enum.auto()
    pending_call_returned = enum.auto()


# Extra states were added to accommodate lambdas, jumping directly between
# valid and invalid, etc., without going through validating. In fact, this
# may be a better way to handle all internal validates in the future.

_state_transitions = {
    TransitionStates.initializing: {
        Events.parameters_are_being_validated: TransitionStates.validating,
    },
    TransitionStates.validating: {
        Events.parameters_are_invalid: States.invalid,
        Events.parameters_are_valid: States.valid,
    },
    States.invalid: {
        Events.parameters_are_being_validated: TransitionStates.validating,
        Events.parameters_are_valid: States.valid,
    },
    States.valid: {
        Events.parameters_are_being_validated: TransitionStates.validating,
        Events.inputs_are_ready: States.armed,
        Events.inputs_are_processing: States.armed,
        Events.inputs_are_available: States.armed,
        Events.parameters_are_invalid: States.invalid,
    },
    States.armed: {
        Events.node_is_queued: States.queued,
        Events.node_is_executing: States.executing,
        Events.parameters_are_being_validated: TransitionStates.validating,
        Events.node_is_disarmed: States.valid,
        Events.inputs_are_unavailable: States.valid,
        Events.parameters_are_invalid: States.invalid,
    },
    States.queued: {
        Events.node_is_aborting: TransitionStates.aborting,
        Events.node_is_executing: States.executing,
        Events.node_is_armed: TransitionStates.aborting,
        Events.node_is_disarmed: TransitionStates.aborting_valid,
        Events.inputs_are_ready: TransitionStates.aborting,
        Events.inputs_are_unavailable: TransitionStates.aborting_valid,
    },
    States.executing: {
        Events.node_is_aborting: TransitionStates.aborting,
        Events.node_is_armed: TransitionStates.aborting,
        Events.node_is_disarmed: TransitionStates.aborting_valid,
        Events.node_execution_finished: States.done,
        Events.node_locked_execution_finished: States.done_locked,
        Events.node_error_occured: States.error,
        Events.inputs_are_ready: TransitionStates.aborting,
        # Allowed for the case where a locked flow sets several nodes,
        # even in series, in executed state. It is not strictly right
        # but SHOULD not cause problems if there are no transitions
        # back to queued or executing.
        # Events.inputs_are_processing: TransitionStates.aborting,
        Events.inputs_are_unavailable: TransitionStates.aborting_valid,
        Events.parameters_are_invalid: TransitionStates.aborting_invalid,
    },
    States.done: {
        Events.parameters_are_being_validated: TransitionStates.validating,
        # Events.node_is_queued: States.queued,
        # Events.node_is_executing: States.executing,
        Events.node_is_armed: States.armed,
        Events.node_is_disarmed: States.valid,
        Events.inputs_are_unavailable: States.valid,
        Events.inputs_are_ready: States.armed,
        Events.inputs_are_processing: States.armed,
        Events.parameters_are_invalid: States.invalid,
    },
    States.done_locked: {
        Events.parameters_are_being_validated: TransitionStates.validating,
        # Events.node_is_queued: States.queued,
        # Events.node_is_executing: States.executing,
        Events.node_is_armed: States.armed,
        Events.node_is_disarmed: States.valid,
        Events.node_execution_finished: States.done,
        Events.inputs_are_unavailable: States.valid,
        Events.inputs_are_ready: States.armed,
        Events.inputs_are_processing: States.armed,
        Events.parameters_are_invalid: States.invalid,
    },
    TransitionStates.aborting: {
        Events.node_has_aborted: States.armed,
        Events.inputs_are_unavailable: TransitionStates.aborting_valid,
        Events.parameters_are_invalid: TransitionStates.aborting_invalid,
    },
    TransitionStates.aborting_valid: {
        Events.node_has_aborted: States.valid,
        Events.inputs_are_available: TransitionStates.aborting,
        Events.inputs_are_ready: TransitionStates.aborting,
        Events.inputs_are_processing: States.armed,
        Events.parameters_are_invalid: TransitionStates.aborting_invalid,
    },
    TransitionStates.aborting_invalid: {
        Events.node_has_aborted: States.invalid,
        Events.parameters_are_valid: TransitionStates.aborting_valid,
    },
    States.error: {
        Events.parameters_are_being_validated: TransitionStates.validating,
        Events.node_is_armed: States.armed,
        Events.node_is_disarmed: States.valid,
        Events.inputs_are_unavailable: States.valid,
        Events.inputs_are_ready: States.armed,
        Events.inputs_are_processing: States.armed,
        Events.parameters_are_invalid: States.invalid,
    }
}


_pending_transitions = {
    PendingStates.idle: {
        PendingEvents.pending_call_sent: PendingStates.pending,
    },

    PendingStates.pending: {
        PendingEvents.pending_call_returned: PendingStates.idle,
    },
}


class NodeStateMachine(NodeStatusInterface, QtCore.QObject):
    """Implementation of the state machine for a regular executable Node."""
    state_changed = QtCore.Signal()
    node_state_entered = QtCore.Signal(object)
    node_state_exited = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        parent = kwargs.get('parent')
        super().__init__(*args, **kwargs)
        self._parent = parent

        self._state_machine = StateMachine(self)

        self._node_state_container = StateContainer(
            self._state_machine, _state_transitions,
            TransitionStates.initializing)
        self._pending_state_container = StateContainer(
            self._state_machine, _pending_transitions, PendingStates.idle)

        self._node_state_container.entered.connect(self._state_changed)
        self._pending_state_container.entered.connect(self._state_changed)
        self._node_state_container.entered.connect(self.node_state_entered)
        self._node_state_container.exited.connect(self.node_state_exited)

        self._state_machine.start()
        self._conf = self._state_machine.configuration()

    def _state_changed(self):
        self._conf = self._state_machine.configuration()
        self.state_changed.emit()
        # core_logger.debug('NEW STATE {}'.format(str(self)))

    def __str__(self):
        current_states = []
        configuration = self.configuration()

        if not self._state_machine.isRunning():
            current_states.append('State Machine is not running!')

        if TransitionStates.initializing in configuration:
            current_states.append('Initialized')

        if TransitionStates.validating in configuration:
            current_states.append('Validating')

        if States.error in configuration:
            current_states.append('Error')

        if States.invalid in configuration:
            current_states.append('Invalid')

        if States.valid in configuration:
            current_states.append('Valid')

        if States.armed in configuration:
            current_states.append('Armed')

        if States.queued in configuration:
            current_states.append('Queued')

        if States.executing in configuration:
            current_states.append('Executing')

        if (TransitionStates.aborting in configuration or
                TransitionStates.aborting_valid in configuration):
            current_states.append('Aborting')

        if States.done_locked in configuration:
            current_states.append('Done-Locked')

        if States.done in configuration:
            current_states.append('Done')

        if PendingStates.idle in configuration:
            current_states.append('Idle')

        if PendingStates.pending in configuration:
            current_states.append('Pending')

        return 'States: ' + ', '.join(current_states)

    def configuration(self):
        return self._conf

    def state(self):
        return self._node_state_container.state

    def is_executing_or_queued_or_done(self):
        s = self.configuration()
        return States.executing in s or States.queued in s or self.is_done()

    def is_configurable(self):
        s = self.configuration()
        return PendingStates.idle in s and (
            States.error in s or
            States.valid in s or
            States.invalid in s or
            States.armed in s or
            self.is_done())

    def is_executable(self):
        s = self.configuration()
        return PendingStates.idle in s and States.armed in s

    def is_debuggable(self):
        return self.is_executable()

    def is_profileable(self):
        return self.is_executable()

    def is_abortable(self):
        s = self.configuration()
        return PendingStates.idle in s and (
            States.queued in s or States.executing in s)

    def is_reloadable(self):
        s = self.configuration()
        return PendingStates.idle in s and (
            States.error in s or
            States.valid in s or
            States.invalid in s or
            States.armed in s or
            States.done_locked in s or
            States.done in s)

    def is_armable(self):
        c = self.configuration()
        return PendingStates.idle in c and any(
            s in c for s in
            (States.done,
             States.done_locked,
             States.valid,
             States.error))

    def is_disarmable(self):
        c = self.configuration()
        return PendingStates.idle in c and any(
            s in c for s in
            (States.done,
             States.done_locked,
             States.armed,
             States.error))

    def is_deletable(self):
        return True

    def is_queueable(self):
        s = self.configuration()
        return PendingStates.idle in s and (
            States.armed in s or self.is_done())

    def is_armed(self):
        return States.armed in self.configuration()

    def is_queued(self):
        return States.queued in self.configuration()

    def is_executing(self):
        return States.executing in self.configuration()

    def has_pending_request(self):
        return PendingStates.pending in self.configuration()

    def is_successfully_executed(self):
        return self.is_done()

    def in_error_state(self):
        return States.error in self.configuration()

    def is_configuration_valid(self):
        s = self.configuration()
        return self.is_initialized() and (States.invalid not in s and
                                          TransitionStates.validating not in s)

    def is_initialized(self):
        s = self.configuration()
        return (self._state_machine.isRunning() and
                TransitionStates.initializing not in s)

    def is_valid(self):
        return States.valid in self.configuration()

    def is_done(self):
        s = self.configuration()
        return States.done in s or States.done_locked in s

    def is_done_locked(self):
        s = self.configuration()
        return States.done_locked in s

    def is_error(self):
        s = self.configuration()
        return States.error in s

    def validate(self, external_validate=True):
        core_logger.debug("node.NodeStateMachine.validate called for node %s",
                          self._parent.uuid)
        if external_validate:
            self.change_pending_state(PendingEvents.pending_call_sent)
        self.change_node_state(Events.parameters_are_being_validated)

    def validate_done(self, result, external_validate=True):
        core_logger.debug(
            "node.NodeStateMachine.validate_done called for node %s",
            self._parent.uuid)
        if external_validate:
            self.change_pending_state(PendingEvents.pending_call_returned)

        if result and result > 0:
            self.change_node_state(Events.parameters_are_valid)
        else:
            self.change_node_state(Events.parameters_are_invalid)

    def execute(self):
        self.change_pending_state(PendingEvents.pending_call_sent)
        self.change_node_state(Events.node_is_executing)

    def execute_done(self, result, locked):
        core_logger.debug(
            'execute_done %s with result %s', self._parent.uuid, result)
        self.change_pending_state(PendingEvents.pending_call_returned)
        if result > 0:
            if locked:
                self.change_node_state(Events.node_locked_execution_finished)
            else:
                self.change_node_state(Events.node_execution_finished)
        else:
            self.change_node_state(Events.node_error_occured)

    def abort(self):
        self.change_pending_state(PendingEvents.pending_call_sent)
        self.change_node_state(Events.node_is_aborting)

    def abort_done(self):
        self.change_pending_state(PendingEvents.pending_call_returned)
        self.change_node_state(Events.node_has_aborted)

    def change_node_state(self, event):
        self._node_state_container.transit(event)

    def change_pending_state(self, event):
        self._pending_state_container.transit(event)


def node_factory(node_id=None, **kwargs):
    cls = factories[node_id]
    return cls(identifier=node_id, **kwargs)


class StatefulNodeMixin(object):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_state_machine_()
        self._ok = True

    def _node_state_entered(self, state):
        handler = self._node_state_entered_handlers.get(state)
        if handler:
            handler()

    def _node_state_exited(self, state):
        handler = self._node_state_exited_handlers.get(state)
        if handler:
            handler()

    def _init_state_machine_(self):
        # Start the state machine and propagate the signals
        self._state_machine = NodeStateMachine(parent=self)

        self._node_state_entered_handlers = {
            TransitionStates.validating: self.on_state_validating,
            States.error: self.on_state_error,
            States.invalid: self.on_state_invalid,
            States.valid: self.on_state_valid,
            States.armed: self.on_state_armed,
            States.queued: self.on_state_queued,
            States.executing: self.on_state_executing,
            TransitionStates.aborting: self.on_state_aborting,
            TransitionStates.aborting_valid: self.on_state_aborting,
            States.done: self.on_state_done,
            States.done_locked: self.on_state_done,
        }

        self._node_state_exited_handlers = {
            States.executing: self.on_exited_executing,
        }

        self._state_machine.node_state_entered.connect(
            self._node_state_entered)
        self._state_machine.node_state_exited.connect(self._node_state_exited)

        self._state_machine.state_changed.connect(self._state_changed)

    # Transfer NodeStatusInterface functions

    def is_armed(self):
        return self._state_machine.is_armed()

    def is_queued(self):
        return self._state_machine.is_queued()

    def is_executing(self):
        return self._state_machine.is_executing()

    def has_pending_request(self):
        return self._state_machine.has_pending_request()

    def is_successfully_executed(self):
        return self._state_machine.is_successfully_executed()

    def in_error_state(self):
        return self._state_machine.in_error_state() or not self._ok

    def is_configuration_valid(self):
        return self._state_machine.is_configuration_valid()

    def is_done(self):
        return self._state_machine.is_done()

    def is_done_locked(self):
        return self._state_machine.is_done_locked()

    def is_configurable(self):
        return (self._state_machine.is_configurable() and
                self._ok)

    def is_executing_or_queued_or_done(self):
        return self._state_machine.is_executing_or_queued_or_done()

    def is_executable(self):
        return (self._state_machine.is_executable() and self._ok)

    def is_armable(self):
        return self._state_machine.is_armable() and self._ok

    def is_debuggable(self):
        return self._state_machine.is_debuggable()

    def is_profileable(self):
        return self._state_machine.is_executable()

    def is_abortable(self):
        return self._state_machine.is_abortable()

    def is_reloadable(self):
        return (self._state_machine.is_reloadable() and self._ok)

    def is_valid(self):
        return self._state_machine.is_valid()

    def is_state_deletable(self):
        return self._state_machine.is_deletable()

    def is_queueable(self):
        return (self._state_machine.is_queueable() and
                self._inputs_are_connected() and self._ok)

    def is_deletable(self):
        # A node is deletable if the state-machine says so
        # and if the node is not involved in any execution chain.
        state_ok = self.is_state_deletable()
        outgoing = self._outgoing_nodes()
        outgoing_ok = all([node.is_state_deletable() for node in outgoing])

        return state_ok and outgoing_ok

    def state(self):
        return self._state_machine.state()

    def _state_changed(self):
        self.state_changed.emit()

    def _input_event(self):
        def node_event(node):
            done = False
            event = Events.inputs_are_available
            if node.state() == States.armed:
                event = Events.inputs_are_ready
            elif node.state() in [
                    States.queued, States.executing]:
                event = Events.inputs_are_processing
            elif node.state() not in [
                    States.done, States.done_locked]:
                event = Events.inputs_are_unavailable
                done = True
            return (done, event)

        events = set([Events.inputs_are_available])

        for input_ in self.inputs:
            source_port = None
            if self.flow:
                source_port = self.flow.source_port(input_, True, True)

            if source_port:
                if source_port.type == Type.OutputPort:
                    source_node = source_port.node
                    if source_node.type == Type.Node:
                        done, event = node_event(source_node)
                        events.add(event)
                        if done:
                            break
                    elif (source_node.type == Type.FlowInput and not
                          source_node.flow.flow_input_available(source_node)):
                        events.add(Events.inputs_are_unavailable)
                        break
                    elif (source_node.type == Type.Flow and
                          source_node.is_atom()):
                        done, event = node_event(source_node)
                        events.add(event)
                        if done:
                            break
                else:
                    events.add(Events.inputs_are_unavailable)
                    break
            else:
                events.add(Events.inputs_are_unavailable)
                break

        for event in [
                Events.inputs_are_unavailable,
                Events.inputs_are_ready,
                Events.inputs_are_processing,
                Events.inputs_are_available]:

            if event in events:
                return event

        return Events.inputs_are_available

    def update_input_state(self):
        event = self._input_event()
        self._state_machine.change_node_state(event)

    def state_string(self):
        return str(self._state_machine)

    def _incoming_nodes(self):
        incoming = []
        for port in self.get_operative_inputs(True):
            source = self._flow.source_port(port)
            if source is None:
                incoming.append(None)
            elif source.node.type in (Type.Node, Type.Flow):
                incoming.append(source.node)
        return incoming

    def _outgoing_nodes(self):
        return [dst.node for dst in self._outgoing_ports()]

    def _outgoing_ports(self):
        return [
            dst
            for port in self._outputs
            for dst in self._flow.destination_ports(port, atom=True)
            if dst is not None]

    def arm(self, port=None):
        if self._input_event() != Events.inputs_are_unavailable:
            self._state_machine.change_node_state(Events.node_is_armed)

    def disarm(self, port=None):
        self._state_machine.change_node_state(Events.node_is_disarmed)

    def clear_error(self):
        if self.in_error_state() and self._ok:
            self._state_machine.change_node_state(Events.node_is_armed)

    def clear_locked_done(self):
        if self._ok and self.in_error_state() or self.is_done_locked():
            self._state_machine.change_node_state(Events.node_is_armed)

    def all_incoming_nodes_are_successfully_executed(self):
        incoming = self._incoming_nodes()
        if None in incoming:
            return False
        else:
            for node in incoming:
                if not node.is_successfully_executed() or (
                        node.is_done_locked()):
                    return False
        return True

    def all_incoming_nodes_are_queued_or_executing_or_done(self):
        incoming = self._incoming_nodes()

        if None in incoming:
            return False
        else:
            for node in incoming:
                if not node.is_executing_or_queued_or_done():
                    return False
        return True

    def execution_allowed(self):
        return (
            self.all_incoming_nodes_are_successfully_executed() and
            not self.is_successfully_executed() and
            not self.is_queued())

    def update_progress(self, progress):
        if self.is_executing():
            p = int(progress)
            if p != self._progress:
                self._progress = p
                self.progress_changed.emit(p)

    def progress(self):
        return self._progress

    #
    # State change handlers
    #

    @QtCore.Slot()
    def on_state_validating(self):
        core_logger.debug(
            "Calling appcore.AppCore.validate_node for node %s",
            self.uuid)
        self._flow.app_core.validate_node(self)

    @QtCore.Slot()
    def on_state_error(self):
        pass

    @QtCore.Slot()
    def on_state_invalid(self):
        pass

    @QtCore.Slot()
    def on_state_valid(self):
        self.update_input_state()

    @QtCore.Slot()
    def on_state_armed(self):
        pass

    @QtCore.Slot()
    def on_state_queued(self):
        pass

    @QtCore.Slot()
    def on_state_executing(self):
        self._progress = 0
        # self._state_machine.execution_started.emit()

    @QtCore.Slot()
    def on_exited_executing(self):
        pass
        # self._state_machine.execution_finished.emit()

    @QtCore.Slot()
    def on_state_aborting(self):
        self._flow.abort_node(self)

    @QtCore.Slot()
    def on_state_done(self):
        pass

    def reload(self):
        self._flow.app_core.clear_node_messages(self)
        self._state_machine.change_node_state(Events.node_is_armed)

    @QtCore.Slot()
    def execute(self):
        core_logger.debug('execute %s', self.uuid)
        try:
            self._flow.execute_node(self)
        except exceptions.SyFloatingInputError:
            # TODO(Erik): Improve handling of node state in Lambdas.
            pass

    @QtCore.Slot()
    def debug(self):
        self._flow.debug_node(self)

    @QtCore.Slot()
    def profile(self):
        self._flow.profile_node(self)

    @QtCore.Slot()
    def abort(self):
        self._state_machine.abort()

    @QtCore.Slot()
    def set_aborting(self, child_nodes=None):
        self.abort()

    @QtCore.Slot()
    def set_queued(self):
        self._state_machine.change_node_state(Events.node_is_queued)

    @QtCore.Slot()
    def set_started(self):
        self._flow.app_core.clear_node_messages(self)
        self._state_machine.change_node_state(Events.node_is_executing)

    @QtCore.Slot(int)
    def set_done(self, result, locked=False):
        self._state_machine.execute_done(result, locked)

    @QtCore.Slot(int)
    def set_aborted(self, child_nodes=None):
        self._progress = 0
        self._state_machine.abort_done()

    @QtCore.Slot(int)
    def validate_done(self, result):
        self._progress = 0
        self._state_machine.validate_done(result, self.needs_validate)

    def is_initialized(self):
        return self._state_machine.is_initialized()

    def _inputs_are_connected(self):
        connected = [p.is_connected_to_node() for p in self.inputs]
        result = False
        if len(connected) == 0:
            result = True
        elif False not in connected:
            result = True

        return result

    def inputs_are_connected(self):
        return self._inputs_are_connected()

    @QtCore.Slot()
    def validate(self):
        if self._ok:
            self._state_machine.validate(self.needs_validate)

    def configure(self):
        self._flow.app_core.clear_node_messages(self)
        self._flow.app_core.execute_node_parameter_view(self)


class Node(StatefulNodeMixin, NodeStatusInterface, NodeInterface):

    initialized = QtCore.Signal()
    parameters_are_valid = QtCore.Signal()
    parameters_are_invalid = QtCore.Signal()
    parameters_are_being_validated = QtCore.Signal()
    node_is_aborting = QtCore.Signal()
    node_has_aborted = QtCore.Signal()
    node_is_queued = QtCore.Signal()
    node_is_executing = QtCore.Signal()
    node_error_occured = QtCore.Signal()
    node_execution_finished = QtCore.Signal()
    node_is_armed = QtCore.Signal()
    pending_call_sent = QtCore.Signal()
    pending_call_returned = QtCore.Signal()

    _type = Type.Node
    executor = Executors.Node
    _conf_port_name = '__sy_conf__'
    _out_port_name = '__sy_out__'
    _err_port_name = '__sy_err__'
    _both_port_name = '__sy_both__'

    def __init__(self, identifier=None, ports=None,
                 port_format=None, library_node=None, only_conf=None,
                 version=None, name=None, original_nodeid=None, **kwargs):
        assert(identifier)
        super().__init__(**kwargs)
        self._identifier = identifier
        self._name = 'No name'
        self._output = ''
        self._progress = 0
        self._generics_map = {}
        if library_node is None:
            library_node = self._flow.app_core.library_node(identifier)
        self._node = library_node
        self._ok = self._node.ok
        self._name = name or self._node.name
        self._version = version
        if version is None:
            if library_node is not None:
                self._version = library_node.version
            else:
                self._version = epoch_version
        self._base_parameter_model = self._node.parameter_model
        self._override_parameter_models = []
        self.original_nodeid = original_nodeid
        self._ports = ports
        self._port_format = port_format or '1.0'
        self._only_conf_output = only_conf
        self._update_migrations()

    def initialize(self):
        """Initialize this node, should be performed after the NodeView has
        been created."""
        super().initialize()

        def get_def(port_dict, index):
            port_dict = dict(port_dict)
            port_dict['index'] = index
            port_dict['type'] = port_dict['type_base']
            return PortDefinition.from_definition(port_dict)

        if self._ports and self._port_format == '1.1':
            # Build ports from instances.
            for i, input_ in enumerate(self._ports.get('inputs', [])):
                self.create_input(
                    get_def(input_, i), generics_map=self._generics_map)

            for i, output_ in enumerate(self._ports.get('outputs', [])):
                self.create_output(
                    get_def(output_, i), generics_map=self._generics_map)
        else:
            # Build ports from node definition.
            for input_ in self._node.inputs:
                self.create_input(input_, generics_map=self._generics_map)
            for output_ in self._node.outputs:
                self.create_output(output_, generics_map=self._generics_map)

    def update_library_node(self, libraries=None):
        if self._ok:
            if not self._flow.app_core.is_node_in_library(
                    self._identifier, libraries=libraries):
                self._ok = False
                self._update_ports()
                self._state_machine.state_changed.emit()
        else:
            if self._flow.app_core.is_node_in_library(
                    self._identifier, libraries=libraries):
                self._node = self._flow.app_core.library_node(self._identifier)
                self._ok = self._node.ok
                if self._ok:
                    self._update_ports()
                    self.validate()
                    self._state_machine.state_changed.emit()
        self._update_migrations()

    def get_operative_inputs(self, execute=False):
        res = list(self.inputs)
        if execute:
            conf_port = self.flow.get_operative_config_port(self)
            if conf_port:
                if res and self.is_config_port_name(res[-1].name):
                    res[-1] = conf_port
                else:
                    res.append(conf_port)
        return res

    def to_copy_dict(self, base_params=False):
        node_dict = self.to_dict()
        node_dict['full_uuid'] = self.full_uuid
        node_dict['original_nodeid'] = None
        if base_params:
            parameters = self._base_parameter_model.to_ordered_dict()
        else:
            parameters = self.parameter_model.to_dict()
        node_dict['parameters'] = {'data': parameters, 'type': 'json'}
        return node_dict

    def to_dict(self, execute=False):
        inputs = []
        for input_ in self.get_operative_inputs(execute=execute):
            inputs.append(input_.to_dict(execute))
        outputs = []
        for output_ in self._outputs:
            outputs.append(output_.to_dict(execute))

        if execute:
            parameters = self._execute_parameter_model().to_dict()
        else:
            parameters = self._base_parameter_model.to_ordered_dict()

        if execute and self.get_overrides_flow() is not None:
            version = self.get_override_parameter_model(
                self.get_overrides_flow()).get_version()
        else:
            version = self.version

        result = {
            'id': self.node_identifier,
            'version': str(version),
            'description': self.description,
            'copyright': self.copyright,
            'library': self.library,
            'author': self.author,
            'uuid': self.uuid,
            'x': self.position.x(),
            'y': self.position.y(),
            'width': self.size.width(),
            'height': self.size.height(),
            'label': self.name,
            'parameters': {'data': parameters, 'type': 'json'},
            'ports': {'inputs': inputs,
                      'outputs': outputs},
            'source_file': self.source_file,
            'original_nodeid': self.original_nodeid,
        }

        if execute:
            result['__hierarchical_uuid'] = self._hierarchical_uuid
            result['update_parameters'] = not self._node.migrations

        if self._only_conf_output:
            result['only_conf'] = True

        port_format = self._current_port_format()
        if port_format != '1.0':
            result['port_format'] = port_format

        if self.icon:
            result['icon'] = self.icon
        result['source_file'] = self.source_file
        return result

    @property
    def _hierarchical_uuid(self):
        uuids = [self.uuid]
        for parent in self.flow.parent_flows():
            uuids.append(parent.uuid)
        return '.'.join(reversed(uuids))

    def _update_uuid(self, old_uuid, new_uuid):
        super()._update_uuid(old_uuid, new_uuid)
        if self.flow:
            self.flow.update_node_uuid(old_uuid, new_uuid)

    @property
    def identifier(self):
        """Returns the node identifier (from the node class)."""
        return self.node_identifier

    def add(self, flow=None):
        if flow is not None:
            self._flow = flow
        self._flow.add_node(self)
        for port in self._inputs:
            port.add(flow)
        for port in self._outputs:
            port.add(flow)

    def remove(self):
        # TODO: Remove any overrides for this node?
        self._flow.remove_node(self)

    def remove_files(self):
        super().remove_files()

        for port in self._outputs:
            port.remove_files()

    def needs_filename(self, port):
        return port.node is self and port.type == Type.OutputPort

    def port_viewer(self, port):
        self._flow.app_core.port_viewer(port)

    @property
    def exec_conf_only(self):
        return self._only_conf_output or False

    @exec_conf_only.setter
    def exec_conf_only(self, value):
        self._only_conf_output = value
        self.arm()

    @property
    def base_parameter_model(self):
        return self._base_parameter_model

    @base_parameter_model.setter
    def base_parameter_model(self, new_model):
        self._base_parameter_model = new_model
        self._update_migrations()

    def _verify_overrides(self):
        """Verify overrides and remove any invalid overrides."""
        pass

    def has_overrides(self):
        self._verify_overrides()
        return bool(len(self._override_parameter_models))

    def get_overrides_flow(self):
        self._verify_overrides()
        if not self.has_overrides():
            return None

        uuid = self._override_parameter_models[-1][1]

        for flow_ in self.flow.parent_flows():
            if uuid == flow_.uuid:
                return flow_
        return None

    def get_override_parameter_model(self, flow):
        self._verify_overrides()
        for m, uuid in self._override_parameter_models:
            if uuid == flow.uuid:
                return m
        return None

    def set_override_parameter_model(self, parameter_model, flow):
        self._verify_overrides()

        uuids = []

        for flow_ in self.flow.parent_flows():
            uuids.append(flow_.uuid)
        old_full_indexes = [uuids.index(uuid)
                            for m, uuid in self._override_parameter_models]
        new_full_index = uuids.index(flow.uuid)

        # new_index is the index of the new override parameters in the existing
        # list of overrides.
        new_index = sorted(set(old_full_indexes + [new_full_index])).index(
            new_full_index)

        if parameter_model is None:
            # Delete override parameters
            if new_full_index in old_full_indexes:
                # Delete one of the old overrides.
                del self._override_parameter_models[new_index]
            else:
                # Trying to delete override parameters that don't exist.
                return
                # raise Exception(
                #     "Trying to delete override parameters that don't exist.")
        else:
            # Add or update override parameters
            if new_full_index in old_full_indexes:
                # Update one of the old overrides.
                self._override_parameter_models[new_index] = (
                    parameter_model, flow.uuid)
            elif new_index >= len(self._override_parameter_models):
                # Append a new layer of overrides.
                self._override_parameter_models.append(
                    (parameter_model, flow.uuid))
            else:
                # Insert a new layer of overrides.
                self._override_parameter_models.insert(
                    new_index, (parameter_model, flow.uuid))
        self.parameters_changed.emit()

    def _port_definition_name_lookup(self, defs):
        return {d.get('name'): d for d in defs}

    def _port_name_group(self, ports, name):
        return [port for port in ports if port.port_definition.name == name]

    def _any_connection_is_connected(self):
        return any(itertools.chain(
            (self.flow.source_port(p, False, True)
             for p in self._inputs),
            (self.flow.destination_ports(p, False, False)
             for p in self._outputs)))

    def _infertype_replace(self, replacements):
        flowlib.infertype_flow(self.flow, check=True, replace=replacements)

    def _create_port_type_replacements(self, kind, name):
        res = {}

        inputs = self._port_definition.get('inputs', [])
        outputs = self._port_definition.get('outputs', [])
        ns = self._enumerate_port_names({kind[:-1]: {name: 1}})
        inputs, outputs = port_platform.instantiate(inputs, outputs, ns)

        # Drop the extra definition.
        i = None
        ports_ = {'inputs': inputs, 'outputs': outputs}[kind]
        for j, port in enumerate(ports_):
            if port.get('name', '') == name:
                i = j
        del ports_[i]

        mapping = {}
        for pdef, port in itertools.chain(zip(inputs, self._inputs),
                                          zip(outputs, self._outputs)):

            dtype = datatypes.DataType.from_str(pdef['type'])
            dtype.identify(mapping)
            res[port] = dtype

        return res

    def _delete_port_type_replacements(self, kind, name):
        res = {}
        inputs = self._port_definition.get('inputs', [])
        outputs = self._port_definition.get('outputs', [])

        ns = self._enumerate_port_names()

        i = None
        node_ports = {'inputs': self._inputs, 'outputs': self._outputs}[kind]
        for j, port in enumerate(node_ports):
            if port.name == name:
                i = j

        ns[kind[:-1]][name] -= 1
        inputs, outputs = port_platform.instantiate(inputs, outputs, ns)

        mapping = {}
        for inst_port_group in [inputs, outputs]:
            for port in inst_port_group:
                dtype = datatypes.DataType.from_str(port['type'])
                dtype.identify(mapping)

        inst_port_group = {'inputs': inputs, 'outputs': outputs}[kind]
        dtype = datatypes.DataType.from_str('<a>')
        dtype.identify({})
        inst_port_group.insert(i, {'type': dtype})

        for pdef, port in itertools.chain(zip(inputs, self._inputs),
                                          zip(outputs, self._outputs)):
            dtype = datatypes.DataType.from_str(pdef['type'])
            dtype.identify(mapping)
            res[port] = dtype

        return res

    def is_config_port_name(self, name):
        return name == self._conf_port_name

    def _can_create_port(self, kind, ports, name):
        res = False
        lookup = self._port_definition_name_lookup(
            self._port_definition.get(kind, []))
        if name:
            try:
                def_ = lookup[name]
            except KeyError:
                return False
            maxn = port_platform.maxno(def_.get('n', 1))
            if len(self._port_name_group(ports, name)) < maxn:
                try:
                    self._infertype_replace(
                        self._create_port_type_replacements(kind, name))
                    res = True
                except exceptions.SyInferTypeError:
                    pass
                except KeyError:
                    return False
        return res

    def _can_delete_port(self, kind, ports, port):
        res = False

        lookup = self._port_definition_name_lookup(
            self._port_definition.get(kind, []))
        name = port.name
        if name:
            def_ = lookup[name]
            minn = port_platform.minno(def_.get('n', 1))
            ok = len(self._port_name_group(ports, name)) > minn
            if ok:
                try:
                    self._infertype_replace(
                        self._delete_port_type_replacements(kind, name))
                    res = True
                except exceptions.SyInferTypeError:
                    pass
                except KeyError:
                    return False
        return res

    def can_create_input(self, name):
        return len(self._inputs) < max_nports and self._can_create_port(
            'inputs', self._inputs, name)

    def can_delete_input(self, port):
        return self._can_delete_port('inputs', self._inputs, port)

    def can_create_output(self, name):
        output_names = set([output.name for output in self._outputs])

        ok = True
        if name in {self._out_port_name, self._err_port_name}:
            ok = self._both_port_name not in output_names
        elif name == self._both_port_name:
            ok = all(p not in output_names
                     for p in [self._out_port_name, self._err_port_name])
        return ok and (
            len(self._outputs) < max_nports and self._can_create_port(
                'outputs', self._outputs, name))

    def can_delete_output(self, port):
        return self._can_delete_port('outputs', self._outputs, port)

    def _enumerate_port_names(self, ns=None):
        ns = dict(ns or {})
        pdefs = self._port_definition

        inputs = ns.setdefault('input', {})
        outputs = ns.setdefault('output', {})

        for pdef in pdefs['inputs']:
            name_ = pdef.get('name')
            if name_ and name_ not in inputs:
                inputs.setdefault(name_, 0)

        for pdef in pdefs['outputs']:
            name_ = pdef.get('name')
            if name_ and name_ not in outputs:
                outputs.setdefault(name_, 0)

        for kind, group in [('input', self._inputs),
                            ('output', self._outputs)]:
            ns_kind = ns.setdefault(kind, {})
            for p in group:
                name_ = p.name
                if name_:
                    ns_kind.setdefault(name_, 0)
                    ns_kind[name_] += 1
        return ns

    def _update_ports(self):
        inputs = self._port_definition.get('inputs', [])
        outputs = self._port_definition.get('outputs', [])
        ns = self._enumerate_port_names()
        inputs, outputs = port_platform.instantiate(inputs, outputs, ns)
        self._update_port_types(inputs, outputs)

    def _update_port_types(self, inputs, outputs):
        self._generics_map.clear()
        for def_, p in itertools.chain(zip(inputs, self._inputs),
                                       zip(outputs, self._outputs)):
            p.datatype_base = datatypes.DataType.from_str(def_['type'])
        flowlib.infertype_flow(self.flow)

    def _create_named_port(self, name, kind, ports_fn, create_fn):
        ns = self._enumerate_port_names({kind: {name: 1}})

        inputs = self._port_definition.get('inputs', [])
        outputs = self._port_definition.get('outputs', [])
        inputs, outputs = port_platform.instantiate(inputs, outputs, ns)

        pos = 0
        pc = None
        for i, p in enumerate(ports_fn(inputs, outputs)):
            if p.get('name') == name:
                pos = i
                pc = p

        port = create_fn(
            self,
            port_definition=PortDefinition.from_definition(pc),
            generics_map=self._generics_map, pos=pos)

        self._update_port_types(inputs, outputs)
        return port

    def _delete_port(self, port):
        inputs = self._port_definition.get('inputs', [])
        outputs = self._port_definition.get('outputs', [])
        ns = self._enumerate_port_names()
        inputs, outputs = port_platform.instantiate(inputs, outputs, ns)
        self._update_port_types(inputs, outputs)

    def delete_input(self, port):
        self.remove_input(port)
        self.flow.remove_input_port(port)
        self._delete_port(port)
        self.arm()

    def delete_output(self, port):
        self.remove_output(port)
        self.flow.remove_output_port(port)
        self._delete_port(port)

    def create_named_output(self, name):
        port = self._create_named_port(
            name, 'output', lambda i, o: o, self._flow.create_output_port)
        self.output_port_created.emit(port)
        self.arm()
        return port

    def create_named_input(self, name):
        port = self._create_named_port(
            name, 'input', lambda i, o: i, self._flow.create_input_port)
        self.input_port_created.emit(port)
        self.disarm()
        return port

    def insert_named_input(self, pos, port):
        self.insert_input(pos, port)
        self._delete_port(port)
        self.input_port_created.emit(port)

    def insert_named_output(self, pos, port):
        self.insert_output(pos, port)
        self._delete_port(port)
        self.output_port_created.emit(port)
        self.arm()

    def _creatable_port_defs(self, defs):
        return [def_ for def_ in defs if (
            port_platform.maxno(def_.get('n', 1)) >
            port_platform.minno(def_.get('n', 1)))]

    def creatable_input_defs(self):
        return self._creatable_port_defs(
            self._port_definition.get('inputs', []))

    def creatable_output_defs(self):
        return self._creatable_port_defs(
            self._port_definition.get('outputs', []))

    def _current_port_format(self):
        # Any numbered ports in use.
        ns = self._enumerate_port_names()
        ns_default = {}
        for kind in ['input', 'output']:
            ns_kind = ns_default.setdefault(kind, {})
            for def_ in self._port_definition.get(kind + 's', []):
                name = def_.get('name')
                if name:
                    defno = port_platform.defno(def_.get('n'))
                    if defno > 0:
                        ns_kind[name] = defno

        return '1.0' if ns == ns_default else '1.1'

    @property
    def author(self):
        return self._node.author

    @property
    def maintainer(self):
        return self._node.maintainer

    @property
    def description(self):
        return self._node.description

    @property
    def copyright(self):
        return self._node.copyright

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, version):
        self._version = version

    @property
    def library_node_name(self):
        return self._node.name

    @property
    def library_node(self):
        return self._node

    @property
    def library(self):
        return self._node.library

    @property
    def has_svg_icon(self):
        return self._node.has_svg_icon

    @property
    def has_docs(self):
        return self._node.has_docs

    @property
    def html_docs(self):
        return self._node.html_docs

    @property
    def html_base_uri(self):
        return self._node.html_base_uri

    @property
    def svg_icon_data(self):
        return self._node.svg_icon_data

    @property
    def node_identifier(self):
        return self._node.node_identifier

    @property
    def icon(self):
        return self._node.icon

    @property
    def has_conf_output(self):
        for port in self.outputs:
            if self.is_config_port_name(port.name):
                return True
        return False

    @property
    def _port_definition(self):
        inputs = self._node.port_definition.get('inputs', [])
        outputs = self._node.port_definition.get('outputs', [])
        parameter_model = self._node.parameter_model
        bdefs_in = []
        bdefs_out = [
            {
                'name': name,
                'description': desc,
                'n': (0, 1, 0),
                'scheme': 'hdf5',
                'type': 'text'
            }
            for (name, desc) in [('__sy_out__', 'Output Text'),
                                 ('__sy_err__', 'Warning Text'),
                                 ('__sy_both__', 'Output and Warning Text')]]
        if not (parameter_model and
                parameter_model.is_empty(ignore_group=True)):
            for conf_type, bdefs in [('<z>', bdefs_in), ('json', bdefs_out)]:
                bdefs.append({
                    'name': self._conf_port_name,
                    'description': 'Configuration port',
                    'n': (0, 1, 0),
                    'scheme': 'hdf5',
                    'type': conf_type})

        return {'inputs': inputs + bdefs_in,
                'outputs': outputs + bdefs_out}

    def _get_parameter_model(self):
        self._verify_overrides()
        if len(self._override_parameter_models):
            return self._override_parameter_models[-1][0]
        return self._base_parameter_model

    def _set_parameter_model(self, new_model):
        self._verify_overrides()
        if len(self._override_parameter_models):
            flow_uuid = self._override_parameter_models[-1][1]
            self._override_parameter_models[-1] = (new_model, flow_uuid)
        self._base_parameter_model = new_model
        self.parameters_changed.emit()
        self._update_migrations()

    @property
    def parameter_model(self):
        return self._get_parameter_model().to_parameter_model()

    @parameter_model.setter
    def parameter_model(self, value):
        return self._set_parameter_model(value)

    def _execute_parameter_model(self):
        """
        Return the parameter model that should be used for execute,
        configure etc. Either base parameters or active overrides. Possibly
        also auto migrated to current version of the node.
        """
        overrides_flow = self.get_overrides_flow()
        if overrides_flow is None:
            return self._migrations.auto_migrated_parameters
        else:
            tree_uuid = overrides_flow.tree_uuid(self)
            migrations = overrides_flow._get_overrides_migration_chain(
                tree_uuid)
            return migrations.auto_migrated_parameters

    def auto_migrated_version(self):
        overrides_flow = self.get_overrides_flow()
        if overrides_flow is None:
            return self._migrations.auto_migrated_version()
        else:
            tree_uuid = overrides_flow.tree_uuid(self)
            migrations = overrides_flow._get_overrides_migration_chain(
                tree_uuid)
            return migrations.auto_migrated_version()

    def auto_migrated_base_version(self):
        return self._migrations.auto_migrated_version()

    def can_auto_migrate(self):
        return self.auto_migrated_version() > self.version

    def migrations_debug_info(self):
        return self._migrations.debug_dict()

    def _update_migrations(self):
        self._migrations = migrations.MigrationChain(node=self)
        if self._ok:
            self.migration_status = self._migrations.gui_status()
        else:
            self.migration_status = None

    def migrate_node(self, macro_cmd, auto_only=False):
        self._migrations.forward(macro_cmd, auto_only=auto_only)

    @property
    def parent(self):
        return self._node.parent

    @property
    def tags(self):
        return self._node.tags

    @property
    def source_file(self):
        return self._node.source_uri

    @property
    def class_name(self):
        return self._node.class_name

    @property
    def needs_validate(self):
        return self._node.needs_validate

    @property
    def quit_after_exec(self):
        return False


class BuiltinNode(Node):

    @property
    def needs_validate(self):
        return False
