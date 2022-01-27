# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
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
Part of the sympathy package.
"""
import copy
import functools
import sys
import numpy as np
import re
import io
from typing import Callable, Optional

from . import message
from . import os_support
# from . import qt_compat2
from . import settings
from . exceptions import sywarn, SyDataError
from . import widget_library as sywidgets
from . editors import config
from .. utils.context import with_files, original
from .. utils import port as port_util
from .. utils.prim import uri_to_path, format_display_string
from . parameter_helper import ParameterRoot
from . import parameter_helper_gui
from . parameter_helper_gui import (
    ParameterView, WidgetBuildingVisitor, sy_parameters)
from .. utils.context import InputPortDummy
from .. utils import preview
from .. utils import network
from .. utils import log
from .. utils.parameters import update_parameters as default_update_parameters

import Qt.QtCore as QtCore
import Qt.QtWidgets as QtWidgets
import Qt.QtGui as QtGui

# QtCore = qt_compat2.QtCore
# QtGui = qt_compat2.QtGui


migr_logger = log.get_logger('core.migrations')


def void(*args):
    pass


class BindingDataError(SyDataError):
    pass


def _raise_if_exception(res):
    if isinstance(res, Exception):
        raise res
    return res


class NodeContext(object):
    def __init__(self, input, output, definition, parameters, typealiases,
                 objects=None, own_objects=None):
        self.input = input
        self.output = output
        self.definition = definition
        self.parameters = parameters
        self.typealiases = typealiases
        self._objects = {} if objects is None else objects
        # Will allow you to check if the port was opened directly by this node
        # (context).  or if it came from another node (in case of locked flow,
        # Map, etc).
        # TODO(erik): create an appropriate API for this.
        self._own_objects = set() if own_objects is None else own_objects

    def __iter__(self):
        return iter((self.input, self.output, self.definition, self.parameters,
                    self.typealiases))

    def __len__(self):
        return sum(1 for _ in self)

    def manage_input(self, filename, fileobj):
        """
        Let the lifetime of fileobj be decided outside of the node.
        Normally, it will be more long-lived than regular inputs
        and outputs, making it possible to add inputs that need to be
        live when writeback takes place.
        """
        self._objects[filename] = fileobj

    def __enter__(self):
        return self

    def __exit__(self, *args):
        for output_ in self.output:
            output_.close()

        for obj in self._objects.values():
            try:
                obj.close()
            except Exception:
                pass

        for input_ in self.input:
            input_.close()

        self._objects.clear()


def managed_context(function):
    """
    Decorator function used to provide automatic management of node_context
    input and output fields.

    When using a managed context the input and output fields will contain the
    value yielded by the generator instead of the generator itself.
    """
    def adapt(self, node_context, managers, **kwargs):
        """Adapter for running node function using 'with_files'."""
        # Splitting inputs and outputs.
        length = len(node_context.input)
        inputs = managers[:length]
        outputs = managers[length:]

        managed_node_context = self.update_node_context(
            node_context, inputs, outputs,
            sy_parameters(node_context.parameters, node=self))

        managed_node_context._objects = node_context._objects

        return function(
            self,
            managed_node_context,
            **kwargs)

    def wrapper(self, node_context, **kwargs):
        """
        The managers list argument contain both input and output, in the
        same list. The reason for this is the interface of with_files.
        The input elements will be first and the output elements last.
        """
        def runner(managers):
            return adapt(self, node_context, managers, **kwargs)

        result = with_files(runner,
                            list(node_context.input) +
                            list(node_context.output))
        node_context.__exit__()
        return result

    wrapper.function = function
    return wrapper


def update_parameters(node, old_params):
    """
    Update parameters of old nodes using new node definition from library.

    This should only be used for nodes that are not managed by migrations.
    """
    # Node specific parameter updating if applicable.
    try:
        old_params = _raise_if_exception(
            node.update_parameters_basic(old_params))
    except NotImplementedError:
        pass

    try:
        definition_params = node.parameters
    except AttributeError:
        definition_params = {}

    # And then default parameter updating.
    default_update_parameters(old_params, definition_params)


def update_bindings(params, definition, inputs, outputs, conf_type):

    warn_attr = (
        'Data attribute: "{key}", required for binding is missing in input. ')

    warn_item = (
        'Data item: "{key}", required for binding is missing in input. ')

    warn_rest = (
        'Either the configuration data used is of different type than the '
        'data used to setup the binding or the input lacks the required '
        'content.')

    warn_attr = warn_attr + warn_rest
    warn_item = warn_item + warn_rest

    def update_internal(param, data):
        if param:
            if param['type'] in ['group', 'page']:
                for k, v in param.items():
                    param_ = param.get(k)
                    if param_ and isinstance(param_, dict):
                        update_internal(param_, data)
            else:
                binding = param.get('binding')
                value = data
                if binding is not None:
                    for seg in binding:
                        op = seg[0]
                        try:
                            key = seg[1]
                        except Exception:
                            key = None

                        if op == '.':
                            try:
                                value = getattr(value, seg[1])
                            except Exception:
                                raise BindingDataError(
                                    warn_attr.format(key=key))
                        elif op == '[]':
                            try:
                                value = value.__getitem__(seg[1])
                            except Exception:
                                raise BindingDataError(
                                    warn_item.format(key=key))
                        elif op == '()':
                            sywarn('Binding operator call is not implemented.')
                        else:
                            sywarn(f'Unknown binding operator: {op}.')

                    if isinstance(value, np.generic):
                        value = value.tolist()
                    elif isinstance(value, np.ndarray):
                        value = value.tolist()

                    if param['type'] == 'list':
                        list_param = param.get('list', [])
                        param['value_names'] = value
                        try:
                            # Try to set value based on value_names, primarily
                            # to avoid some warnings about inconsistent
                            # parameters.
                            param['value'] = [
                                list_param.index(v) for v in value]
                        except Exception:
                            pass
                    else:
                        param['value'] = value

    def update_external(param, data):
        if param:
            if param['type'] in ['group', 'page']:
                for k, v in data.items():
                    param_ = param.get(k)
                    if param_ and isinstance(param_, dict):
                        update_external(param_, v)
            else:
                for k, v in data.items():
                    if k not in ['type', 'order', 'label', 'description',
                                 'binding']:
                        param[k] = v

    def prune(param):
        def prune_names(param):
            return set(param).difference(
                ['editor', 'order', 'description'])

        if not isinstance(param, dict):
            return param
        elif param['type'] in ['group', 'page']:
            return {k: prune(param[k]) for k in prune_names(param.keys())}
        else:
            return {k: param[k] for k in prune_names(param.keys())}

    idefs = definition['ports'].get('inputs', [])
    if (idefs and len(idefs) == len(inputs) and
            idefs[-1].get('name') == '__sy_conf__'):
        conf_type = idefs[-1].get('type')
        binding_mode = params.get('binding_mode')

        if binding_mode is None:
            if conf_type == 'json':
                binding_mode = ParameterRoot._binding_mode_external
            else:
                binding_mode = ParameterRoot._binding_mode_internal

        if binding_mode == ParameterRoot._binding_mode_external:
            try:
                update_external(params, inputs[-1].get())
            except Exception:
                sywarn('Could not update parameters with configuration data.')

        elif binding_mode == ParameterRoot._binding_mode_internal:
            try:
                update_internal(params, inputs[-1])
            except Exception:
                raise
                sywarn('Could not update parameters with configuration data.')
        else:
            sywarn(f'Unknown binding mode: {binding_mode}')

    odefs = definition['ports'].get('outputs', [])
    if (odefs and len(odefs) == len(outputs) and
            odefs[-1].get('name') == '__sy_conf__'):
        try:
            outputs[-1].set(prune(params))
        except Exception:
            sywarn('Could not write parameters as configuration data.')


def _build_mem_port(port_dict):
    return port_util.port_mem_maker(port_dict)


def _build_mem_ports(port_dicts):
    return [
        _build_mem_port(port_dict)
        for port_dict in port_dicts]


class BaseContextBuilder(object):
    def build(self, node, parameters, typealiases, exclude_output=False,
              exclude_input=False, read_only=False, bind=False):
        """Build node context object."""
        # Creates a dictionary of typealiases with inter-references expanded.
        node_typealiases = port_util.typealiases_parser(typealiases)

        # Take input port definitions and convert to the required
        # structure for the node context object.
        input_ports = parameters['ports'].get('inputs', [])
        if exclude_input:
            node_input = _build_mem_ports(input_ports)
        else:
            node_input = node._build_file_ports_or_dummys(
                port_util.dummy_input_port_maker, input_ports, 'r')

        # Do the same for the output port. In some cases we are not
        # allowed to access the output port and this is when we set
        # the structure to None.
        output_ports = parameters['ports'].get('outputs', [])
        if exclude_output:
            node_output = _build_mem_ports(output_ports)
        else:
            # Generate output port object structure.
            node_output = node._build_file_ports_or_dummys(
                port_util.dummy_output_port_maker, output_ports,
                'r' if read_only else 'w')

        # Users should not really need to have access to the node definition?
        node_definition = parameters

        # Copy parameter structure
        node_parameters = parameters['parameters'].get('data', {})
        if parameters.get('update_parameters', True):
            migr_logger.debug("Running update_parameters for node: %s", node)
            update_parameters(node, node_parameters)
        else:
            migr_logger.debug("Skipping update_parameters for node: %s", node)
        if bind:
            update_bindings(
                node_parameters, node_definition, node_input, node_output,
                node._conf_in_port_type(node_definition))

        # Initialize instance of NodeContext.
        return node.create_node_context(
            node_input,
            node_output,
            node_definition,
            node_parameters,
            node_typealiases.values(),
            own_objects=set([id(o) for o in node_input + node_output]))


class ManualContextBuilder(object):
    """
    Build node context object with the ability to supply inputs that override
    the ones provided by the parameters.  The resulting inputs and outputs are
    available for access and closing through public fields.
    """

    def __init__(self, inputs, outputs, is_output_node, port_dummies=False,
                 objects=None, check_fns=True):
        self.inputs = inputs
        self.outputs = outputs
        self.input_fileobjs = {}
        self.output_fileobjs = {}
        self.objects = {} if objects is None else objects
        self._port_dummies = port_dummies
        self._is_output_node = is_output_node
        self._check_fns = check_fns

    def build(self, node, parameters, typealiases, exclude_output=False,
              exclude_input=False, read_only=False, bind=False):
        """Build node context object."""
        # Creates a dictionary of typealiases with inter-references expanded.
        node_typealiases = port_util.typealiases_parser(typealiases)

        # Take input port definitions and convert to the required
        # structure for the node context object.
        input_ports = parameters['ports'].get('inputs', [])
        if exclude_input:
            node_input = _build_mem_ports(input_ports)
        else:
            node_input = []
            for input_port in input_ports:
                # requires_deepcopy = input_port.get('requires_deepcopy', True)
                requires_deepcopy = True
                filename = input_port['file']
                data = self.inputs.get(filename)

                if not filename:
                    data = _build_mem_port(input_port)

                elif data is None:
                    try:
                        data = port_util.port_maker(input_port, 'r',
                                                    external=False,
                                                    expanded=node._expanded,
                                                    managed=node._managed)
                        if requires_deepcopy:
                            data = data.__deepcopy__()
                    except (IOError, OSError) as e:
                        # E.g. the file doesn't exist yet.
                        if self._port_dummies:
                            data = InputPortDummy(e)
                        else:
                            raise
                    self.input_fileobjs[filename] = data
                    self.inputs[filename] = data
                    self.objects[filename] = data
                else:
                    if requires_deepcopy:
                        data = data.__deepcopy__()

                node_input.append(data)

        # Do the same for the output port. In some cases we are not
        # allowed to access the output port and this is when we set
        # the structure to None.
        output_ports = parameters['ports'].get('outputs', [])
        if exclude_output:
            node_output = _build_mem_ports(output_ports)
        else:
            # Generate output port object structure.
            node_output = []
            for output_port in output_ports:
                filename = output_port['file']
                data = self.outputs.get(filename)

                if not filename:
                    data = _build_mem_port(input_port)

                elif data is None:
                    if self._is_output_node:
                        data = port_util.port_maker(
                            output_port, 'r' if read_only else 'w',
                            external=False,
                            expanded=node._expanded,
                            managed=node._managed)
                        self.output_fileobjs[filename] = data
                    else:
                        data = port_util.port_maker(output_port, None,
                                                    external=None,
                                                    no_datasource=True)
                    self.outputs[filename] = data
                    self.objects[filename] = data

                node_output.append(data)

        # Users should not really need to have access to the node definition?
        node_definition = parameters

        # Copy parameter structure
        node_parameters = parameters['parameters'].get('data', {})
        if parameters.get('update_parameters', True):
            migr_logger.debug("Running update_parameters for node: %s", node)
            update_parameters(node, node_parameters)
        else:
            migr_logger.debug("Skipping update_parameters for node: %s", node)
        if bind:
            update_bindings(
                node_parameters, node_definition, node_input, node_output,
                node._conf_in_port_type(node_definition))

        own_objects = dict(self.output_fileobjs)
        own_objects.update(self.input_fileobjs)

        # Initialize instance of NodeContext.
        node_context = node.create_node_context(
            node_input,
            node_output,
            node_definition,
            node_parameters,
            node_typealiases.values(),
            self.objects,
            set([id(o) for o in own_objects.values()]))
        node_context.__exit__ = void
        return node_context


class ConfirmChangesDialogMixin(object):
    """
    Add this mixin class as a parent class to any configuration QDialog where
    you want a confirmation dialog when pressing cancel.

    There are two requirements on subclasses:
    1. ConfirmChangesDialogMixin must come before the QDialog in the list of
       parent classes. Otherwise keyPressEvent, reject, and done will not be
       called.
    2. Subclasses must override parameters_changed and cleanup.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._use_dialog = settings.settings()['Gui/nodeconfig_confirm_cancel']

    def parameters_changed(self):
        raise NotImplementedError

    def cleanup(self):
        raise NotImplementedError

    def keyPressEvent(self, event):
        # Only accept Ctrl+Enter as Ok and Esc as Cancel.
        # This is to avoid closing the dialog by accident.
        if ((event.key() == QtCore.Qt.Key_Return or
                event.key() == QtCore.Qt.Key_Enter) and
                event.modifiers() & QtCore.Qt.ControlModifier):
            self.accept()
        elif event.key() == QtCore.Qt.Key_Escape:
            self.reject()

    def reject(self):
        """
        Ask the user if the dialog should be closed.
        Reject/accept the dialog as appropriate.
        """
        # For a QDialog reject is the place to modify closing behavior, not
        # closeEvent.
        if not self._use_dialog:
            self._reject_immediately()
        elif self.parameters_changed():
            res = self._confirm_cancel_dialog()
            if res is None:
                return
            else:
                if res:
                    self.accept()
                else:
                    self._reject_immediately()
        else:
            self._reject_immediately()

    def done(self, r):
        # At this point we know that the dialog will close, so this is a good
        # place to do cleanup.
        self.cleanup()
        super().done(r)

    def _reject_immediately(self):
        super().reject()

    def _confirm_cancel_dialog(self):
        """
        Ask the user if the parameter dialog should be closed.

        Returns True if the parameters were accepted, False if they were
        rejected and None if the user cancels.
        """
        choice = QtWidgets.QMessageBox.question(
            self, 'Save changes to configuration',
            "The node's configuration has changed. Save changes in node?",
            QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard |
            QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.Cancel)

        if choice == QtWidgets.QMessageBox.Discard:
            return False
        elif choice == QtWidgets.QMessageBox.Save:
            return True
        else:
            return None


class NullParametersWidgetMixin(parameter_helper_gui.ParameterViewBase):
    valid_changed = QtCore.Signal()


class ParametersWidgetMixin(parameter_helper_gui.ProxyParameterViewBase):
    valid_changed = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._widget = None
        self._message_widget = None
        self._parameters_changed = None
        self._valid = False

    def set_configuration_widget(self, widget):
        self._widget = widget
        self._set_child(widget)

    def set_message_widget(self, widget):
        self._message_widget = widget

    def set_changed_checker(self, func):
        self._parameters_changed = func

    def parameters_changed(self):
        if self._parameters_changed is None:
            return None
        else:
            # First notify the widget that it should save its parameters so
            # that they can be compared.
            self.save_parameters()
            return self._parameters_changed()

    def save_parameters(self):
        try:
            super().save_parameters()
        except Exception:
            import traceback
            sywarn("The following exception happened while trying to save "
                   "configuration:\n\n{}".format(traceback.format_exc()))

    def update_status(self):
        status = self._widget.valid
        self._valid = status
        # set ok button status
        if self._message_widget is not None:
            message = self._widget.status
            color_state = (not status) + (message != '')

            self._message_widget.set_state(color_state)
            self._message_widget.set_message(str(message))
        self.valid_changed.emit()


class ParametersWidget(ParametersWidgetMixin, QtWidgets.QWidget):
    pass


class ParametersDialog(ParametersWidgetMixin, ConfirmChangesDialogMixin,
                       QtWidgets.QDialog):
    help_requested = QtCore.Signal()

    def __init__(self, widget, name, socket_bundle,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._input_comm = socket_bundle
        self._input_reader = socket_bundle.reader
        self._input_reader.received.connect(self.handle_input)

        layout = QtWidgets.QVBoxLayout()
        button_box = QtWidgets.QDialogButtonBox()
        self._help_button = button_box.addButton(
            QtWidgets.QDialogButtonBox.Help)

        has_preview = widget.has_preview()

        if has_preview:
            self._preview_button = sywidgets.PreviewButton()
            self._preview_button.toggled.connect(widget.set_preview_active)

            button_box.addButton(self._preview_button,
                                 QtWidgets.QDialogButtonBox.ActionRole)

        self._ok_button = button_box.addButton(QtWidgets.QDialogButtonBox.Ok)
        self._cancel_button = button_box.addButton(
            QtWidgets.QDialogButtonBox.Cancel)
        self._ok_button.setDefault(False)

        # Reducing white space around widgets
        widget.setContentsMargins(0, 0, 0, 0)
        widgetlayout = widget.layout()
        if widgetlayout:
            widget.layout().setContentsMargins(0, 0, 0, 0)

        # Message area
        message_area = MessageArea(widget, parent=self)
        layout.addWidget(message_area)
        layout.addWidget(widget)
        layout.addWidget(button_box)
        self.setLayout(layout)
        self.set_configuration_widget(widget)
        self.set_message_widget(message_area)
        self.setWindowFlags(QtCore.Qt.Window)

        self._help_button.clicked.connect(self.help_requested)
        self._ok_button.clicked.connect(self.accept)
        self._cancel_button.clicked.connect(self.reject)
        self.accepted.connect(self.save_parameters)

        widget.status_changed.connect(self.update_status)

        self.setWindowTitle(name)
        self.show()
        self.raise_()
        self.activateWindow()
        self.update_status()
        QtCore.QTimer.singleShot(0, focus_widget(self))

    def handle_input(self, msgs):
        for msg in msgs:
            if msg.type == message.RaiseWindowMessage:
                self.raise_window()
            elif msg.type == message.NotifyWindowMessage:
                self.notify_in_taskbar()

    def raise_window(self):
        if not self.isActiveWindow():
            os_support.raise_window(self)

    def notify_in_taskbar(self):
        QtWidgets.QApplication.alert(self, 2000)

    def update_status(self):
        status = self._widget.valid
        # set ok button status
        if self._ok_button is not None:
            self._ok_button.setEnabled(status)

        super().update_status()


class MessageArea(QtWidgets.QLabel):
    """
    Widget showing messages in the ParametersDialog.

    The messages allow html formatting and hyperlinks are opened in an
    external browser. The background color can be set with `set_state`.
    The MessageArea can be set to disappear after a given timeout interval.
    """
    _white_line_re = re.compile('[\\r\\n\\f]+')
    _white_multi_re = re.compile('\\s+')

    _white_re = re.compile('\\s')
    _middle_dot = '\u00b7'

    _after_first = 'After first message'

    def __init__(self, view, parent=None):
        self._message = ''
        self._show_mode = 'Automatic'
        self._doc = QtGui.QTextDocument()
        super().__init__(parent)
        self._init_gui()
        self.hide()
        self._set_view(view)

    def _init_gui(self):
        self.setFrameStyle(QtWidgets.QFrame.Box)
        self._context_menu = QtWidgets.QMenu(parent=self)
        self._show_always_action = QtWidgets.QAction(
            'Always show', self)
        self._show_auto_action = QtWidgets.QAction(
            'Show automatically', self)
        self._hide_always_action = QtWidgets.QAction(
            'Hide always', self)

        show_group = QtWidgets.QActionGroup(self)

        show_group.addAction(self._show_always_action)
        show_group.addAction(self._show_auto_action)
        show_group.addAction(self._hide_always_action)

        self._show_always_action.triggered.connect(self._handle_show_always)
        self._hide_always_action.triggered.connect(self._handle_hide_always)
        self._hide_always_action.triggered.connect(self._handle_show_auto)

        self._context_menu.addAction(self._show_always_action)
        self._context_menu.addAction(self._show_auto_action)
        self._context_menu.addAction(self._hide_always_action)

        self._show_always_action.setCheckable(True)
        self._show_auto_action.setCheckable(True)
        self._hide_always_action.setCheckable(True)

        self._show_auto_action.setChecked(True)

        self.setTextFormat(QtCore.Qt.RichText)
        self.setWordWrap(True)
        self.setOpenExternalLinks(True)
        self.setContentsMargins(1, 1, 1, 1)

        policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                       QtWidgets.QSizePolicy.Minimum)
        self.setSizePolicy(policy)

        self._timer_show = QtCore.QTimer()
        self._timer_show.setInterval(500)
        self._timer_show.setSingleShot(True)

        font_height = self.fontMetrics().height()
        height = font_height + (font_height // 2)
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

        self._timer_show.timeout.connect(self._show)

    def minimumSizeHint(self):
        minimum_size_hint = super().minimumSizeHint()

        return QtCore.QSize(
            self.minimumWidth(),
            min([self.maximumHeight(),
                 minimum_size_hint.height()]))

    def _set_view(self, widget):
        try:
            active = widget.has_status()
        except Exception:
            active = False

        if active:
            show_mode = settings.get_show_message_area()
            self._show_mode = show_mode
            if show_mode == 'Always':
                self._handle_show_always()
                self._show_auto_action.setChecked(False)
            elif show_mode == 'Never':
                self._handle_hide_always()
                self._show_auto_action.setChecked(False)
            elif show_mode in ['Automatic', self._after_first]:
                pass
            else:
                print('Unknown value for show_message_area', show_mode)

    def set_background_color(self, color):
        palette = self.palette()
        palette.setColor(self.backgroundRole(), color)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def set_message(self, message):
        self._message = message
        message = str(message) or ''

        self.setToolTip(message)
        self.update()

        if message == '':
            self.disable()
        else:
            if self._show_mode == self._after_first:
                self._show_mode = 'Always'
                self._handle_show_always()
                self._show_auto_action.setChecked(False)
            self.enable()

    def set_state(self, state):
        """
        Set the state which defines the color. Allowed [0,1,2].

        Parameters
        ----------
        state : int
            The state defines the color of the message area background.
            0 : green   (info)
            1 : yellow  (warning)
            2 : red     (error)
        """
        if state not in [0, 1, 2]:
            state = 2

        colors = {0: QtGui.QColor.fromRgb(204, 235, 197),
                  1: QtGui.QColor.fromRgb(254, 217, 166),
                  2: QtGui.QColor.fromRgb(251, 180, 174)}

        self.set_background_color(colors[state])

    def set_show_interval(self, interval):
        """Set the time after which the error is shown."""
        self._timer_show.setInterval(int(interval))

    def _show(self):
        self.setVisible(True)

    def enable(self):
        if self._show_auto_action.isChecked():
            if not self.isVisible():
                self._timer_show.start()

    def disable(self):
        if self._show_auto_action.isChecked():
            self.setVisible(False)
            self._timer_show.stop()

    def _handle_show_auto(self):
        self._timer_show.stop()
        self.setVisible(False)

    def _handle_hide_always(self):
        self._timer_show.stop()
        self.setVisible(False)

    def _handle_show_always(self):
        self._timer_show.stop()
        self.setVisible(True)

    def contextMenuEvent(self, event):
        # selected_items = self.selectedItems()
        # platform_node = False
        # self._report_issue_action.setEnabled(platform_node)
        self._context_menu.exec_(event.globalPos())
        super().contextMenuEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QtGui.QPainter(self)
        font_metrics = painter.fontMetrics()
        elide_width = font_metrics.boundingRect('...').width()

        text = self._message
        text = self._white_line_re.sub(self._middle_dot, text)
        text = self._white_multi_re.sub(' ', text)
        text = font_metrics.elidedText(
            text, QtCore.Qt.ElideRight, self.width() - elide_width)

        self._doc.setHtml(text)
        self._doc.drawContents(painter)


class BasicNode(object):
    """
    Base class for Sympathy nodes. Fully implements the language interface
    needed to work as a fully functional node inside the Sympathy platform.
    All Python nodes should extend this class.
    """

    def __init__(self, *args, **kwargs):
        """
        The constructor is internal and may change.

        Meant to be defined by Sympathy and should normally not be overridden.
        If you need to override __init__, do not adjust the arguments and
        make sure to call __init__ of this class.

        For purposes of testing and instantiation of your own classes, supply
        no arguments.
        """
        self.active_file = None
        self.address = None
        self.abort_flag = False
        self.filenames = []
        self._expanded = True
        self._managed = False
        self._future__init__()

    def _future__init__(self, identifier=None, definition=None,
                        socket_bundle=None, parent_identifier=None,
                        **kwargs):

        """
        Arguments to this function are so far internal and subject to change.


        Parameters
        ----------

        identifier:
            The node's own identifier, used to identify itself in
            communication.

        definition:
            For future use, may contain all information provided by the worker,
            in essence node.to_dict() from the Sympathy core.

        socket_bundle:
            An object facilitating various means of communication.

        parent_identifier:
            The node's parent identifier, used to identify itself in
            communication. When set, the down identifier is ignored. This is
            useful when, for example, mapping a lambda containing several nodes
            and allows a single group for all messages.
        """
        self._identifier = identifier
        self._parent_identifier = parent_identifier
        self._definition = definition
        self.socket_bundle = socket_bundle
        return self

    def set_progress(self, value):
        """Set and send progress to main program."""
        if self.socket_bundle:
            network.send_all(
                self.socket_bundle.socket,
                self.socket_bundle.output_func(
                    message.ProgressMessage(value)))

    def set_status(self, status):
        """Send status message to main program."""
        msg = b'STATUS %s\n' % status
        if self.socket_bundle:
            network.send_all(
                self.socket_bundle.socket,
                self.socket_bundle.output_func(
                    message.StatusMessage(msg)))

    def request_credentials(self, resource: str, connection_dict: dict
                            ) -> Optional[dict]:
        """
        Request resource with credentials expanded by Sympathy core.

        Returns dict of secrets or None when credentials are disabled.
        """
        res = {}
        if self.socket_bundle:
            # Where does this happen? tests?
            network.send_all(
                self.socket_bundle.socket,
                self.socket_bundle.output_func(
                    message.CredentialRequestMessage(
                        self._parent_identifier or
                        self._identifier, connection_dict)))
            reply = self.socket_bundle.input_func()
            res = message.from_dict(reply).data
        return res

    def _async_request_handle(self, request, handler):
        network.send_all(
            self.socket_bundle.socket,
            self.socket_bundle.output_func(request))
        self.socket_bundle.reader.request(request, handler)

    def request_credentials_async(
            self, resource: str, connection_dict: dict,
            handler: Callable[[Optional[dict]], None]) -> None:
        """
        Register callback handler which will be called asyncronously.
        The value passed to the handler is the same as the return value
        of the synchronous method request_credentials.

        If the resource does not need credentials handler gets called
        immediately with the provided resource.
        """
        if self.socket_bundle:
            request = message.CredentialRequestMessage(
                self._parent_identifier or self._identifier, connection_dict)
            self._async_request_handle(request, handler)
        else:
            handler({})

    def configure_credentials_async(
            self, resource: str, connection_dict: dict, secrets: dict,
            handler: Callable[[Optional[dict]], None]) -> None:
        """
        Register callback handler which will be called asyncronously.
        The value passed to the handler is the same as the return value
        of the synchronous method request_credentials.

        If the resource does not need credentials handler gets called
        immediately with the provided resource.
        """
        if self.socket_bundle:
            request = message.CredentialConfigureMessage(
                self._parent_identifier or self._identifier,
                [connection_dict, secrets])
            self._async_request_handle(request, handler)
        else:
            handler({})

    def edit_credentials_async(
            self, resource: str, connection_dict: dict, kwargs: dict,
            handler: Callable[[Optional[dict]], None]) -> None:
        """
        Request credentials to be edited to match secrets.
        Register callback handler which will be called asyncronously.
        The value passed to the handler is the same as the return value
        of the synchronous method request_credentials.

        If the resource does not need credentials handler gets called
        immediately with the provided resource.
        """
        res = {}
        if self.socket_bundle:
            request = message.CredentialEditMessage(
                self._parent_identifier or self._identifier,
                [connection_dict, kwargs])
            self._async_request_handle(request, handler)
        else:
            handler({})
        return res

    # Methods to be overidden by user.
    @original
    def verify_parameters_basic(self, node_context):
        """Check if configuration is ok."""
        return True

    def update_parameters_basic(self, old_params):
        """
        Update parameters to newer version of node.
        Returns updated parameters.
        """
        raise NotImplementedError(
            'update_parameters() has no default implementation')

    def adjust_parameters_basic(self, node_context):
        """Adjust parameter object."""
        # Default to no changes.
        return node_context

    def execute_basic(self, node_context):
        """
        Execute node. This method should always be extended by
        the inhereting class.
        """
        raise NotImplementedError('execute() must be implemented')

    @managed_context
    def __execute_pass_basic(self, node_context):
        pass

    def available_components(self):
        """
        Return a list of available visual components which the node
        can visualize things through.
        """
        return []

    def exec_parameter_view_basic(self, node_context):
        """
        Return parameter dictionary which was edited by the
        user. Accept and reject is handled by the platform.
        """
        raise NotImplementedError('Specialized class must be '
                                  'used for parameter view.')

    def _manual_context(self, node_context):
        # Used for enabling the user to close the context afterwards.
        # In this base class the close function, int, does nothing and is used
        # as an empty close action since the base behavior is manual
        # context management.
        close_function = int
        close_handles = {'inputs': {key: close_function
                                    for key in node_context.input},
                         'outputs': {key: close_function
                                     for key in node_context.output}}
        return node_context, close_handles

    def _preview_ports(self, node_context):
        def should_preview(pdef, i):
            name = pdef.get('name')
            if not name:
                name = i
            try:
                return self.outputs[name].preview
            except (KeyError, IndexError, AttributeError):
                return False

        return [should_preview(pdef, i) for i, pdef in
                enumerate(
                    node_context.definition['ports']['outputs'])]

    def _build_parameter_widget(self, node_context):
        """
        Creates the configuration widget either from a custom widget
        (exec_parameter_view) or from the parameter definition. The return
        value is a tuple of the parameter root (or None) and the widget.
        """
        def build_binding_widget(widget, parameters):
            conf_type = self._conf_in_port_type(node_context.definition)
            return config.binding_widget_factory(
                parameters, conf_ports[0], conf_type, widget)

        conf_ports = self._conf_in_ports(node_context)

        try:
            # Custom GUI.
            widget = _raise_if_exception(
                self.exec_parameter_view_basic(node_context))
            widget = parameter_helper_gui.to_parameter_view(widget)
            if conf_ports:
                widget = build_binding_widget(widget, node_context.parameters)
            return None, widget
        except NotImplementedError:
            pass

        definition = node_context.definition
        ports_def = definition.get('ports', [])

        visitor_cls = WidgetBuildingVisitor
        if not self._managed:
            # Validator is disabled for basic nodes.
            gui_visitor = visitor_cls(ports=ports_def, node=self)
        else:
            gui_visitor = visitor_cls(
                self.verify_parameters, ports=ports_def, node=self)

        proot = ParameterRoot(node_context.parameters, gui_visitor=gui_visitor)

        # Controller support.
        controllers = getattr(self, 'controllers', None)
        widget = proot.gui(controllers=controllers)

        preview_ports = self._preview_ports(node_context)
        conf_ports = self._conf_in_ports(node_context)

        if any(preview_ports):
            widget = preview.preview_factory(self, node_context, proot, widget)

        if conf_ports:
            widget = build_binding_widget(widget, proot)

        return (proot, widget)

    def _adjust_parameters(self, node_context):
        return _raise_if_exception(self.adjust_parameters_basic(node_context))

    def _execute_parameter_view(self, node_context, return_widget=False,
                                include_messagebox=False):
        """
        Builds the parameters widget and (if return_widget is False) wraps it
        in a ParametersDialog.

        If return_widget is True the parameters widget is returned as is.
        """
        if hasattr(self, 'execute_parameter_view'):
            sywarn('Overriding execute_parameter_view '
                   'is no longer supported.')
        if (hasattr(self, 'has_parameter_view') or
                hasattr(self, 'has_parameter_view_managed')):
            sywarn('Implementing has_parameter_view or '
                   'has_parameter_view_managed no longer has any effect.')

        proot, widget = self._build_parameter_widget(node_context)

        # Save any changes to the parameters from just creating the
        # widget. Each node is responsible that such changes don't
        # change how the node executes.
        widget.save_parameters()
        if isinstance(node_context.parameters, ParameterRoot):
            parameter_dict = node_context.parameters._parameter_dict
        else:
            parameter_dict = node_context.parameters
        old_parameter_dict = copy.deepcopy(parameter_dict)

        # Save parameters in a closure so that ParametersDialog can check
        # them after parameter_dict has (possibly) been mutated.
        def parameters_changed():
            return old_parameter_dict != parameter_dict

        if return_widget:
            if return_widget == 'parameters_widget':
                layout = QtWidgets.QVBoxLayout()
                parameters_widget = ParametersWidget()
                message_area = MessageArea(widget, parent=parameters_widget)
                layout.addWidget(message_area)
                layout.addWidget(widget)
                parameters_widget.set_configuration_widget(widget)
                parameters_widget.set_message_widget(message_area)
                parameters_widget.set_changed_checker(parameters_changed)
                parameters_widget.setLayout(layout)
                parameters_widget.setWindowFlags(QtCore.Qt.Window)

                widget.status_changed.connect(
                    parameters_widget.update_status)

                if proot is not None:
                    proot.value_changed.add_handler(
                        parameters_widget.update_status)

                parameters_widget.update_status()
                return parameters_widget
            return widget

        dialog = None
        try:
            application = QtWidgets.QApplication.instance()
            app_name = format_display_string(
                node_context.definition['label'])
            name = '{} - Parameter View'.format(app_name)
            application.setApplicationName(name)

            dialog = ParametersDialog(widget, name, self.socket_bundle)
            if proot is not None:
                proot.value_changed.add_handler(dialog.update_status)
            dialog.help_requested.connect(functools.partial(
                self._open_node_documentation, node_context))
            dialog.set_changed_checker(parameters_changed)

            icon = node_context.definition.get('icon', None)
            if icon:
                try:
                    icon_data = QtGui.QIcon(uri_to_path(icon))
                    application.setWindowIcon(icon_data)
                except Exception:
                    pass

            application.exec_()
            return dialog.result()
        finally:
            if dialog and hasattr(dialog, 'close'):
                dialog.close()
            # Ensure GC
            dialog = None

    def _sys_exec_parameter_view(self, parameters, type_aliases,
                                 return_widget=False,
                                 builder=BaseContextBuilder()):
        """Execute parameter view and return any changes."""
        # Remember old parameters.
        old = copy.deepcopy(parameters)

        adjusted_parameters = self._sys_adjust_parameters(parameters,
                                                          type_aliases,
                                                          builder=builder)

        node_context = self._build_node_context(adjusted_parameters,
                                                type_aliases,
                                                exclude_output=True,
                                                builder=builder)

        result = self._execute_parameter_view(
            node_context, return_widget=return_widget)
        if return_widget:
            # In this case the result from self.exec_parameter_view is the
            # configuration widget
            return result
        elif result == QtWidgets.QDialog.Accepted:
            return adjusted_parameters
        else:
            return None

    def exec_port_viewer(self, parameters):
        from sympathy.platform.viewer import MainWindow as ViewerWindow
        filename, index, node_name, icon = parameters
        try:
            application = QtWidgets.QApplication.instance()
            name = format_display_string(
                '{}: {} - Viewer'.format(node_name, index))
            application.setApplicationName(name)
            viewer = ViewerWindow(name, self.socket_bundle, icon)
            viewer.open_from_filename(filename)

            viewer.show()
            viewer.resize(800, 600)
            viewer.raise_()
            viewer.activateWindow()
            QtCore.QTimer.singleShot(0, focus_widget(viewer))

            if icon:
                try:
                    icon_data = QtGui.QIcon(viewer.build_icon())
                    application.setWindowIcon(QtGui.QIcon(icon_data))
                except Exception:
                    pass

            application.exec_()
        finally:
            viewer = None

    def _sys_before_execute(self):
        """Always executed before main execution."""
        pass

    def _sys_execute(self, parameters, type_aliases,
                     builder=BaseContextBuilder()):
        """Called by the Sympathy platform when executing a node."""
        node_context = self._build_node_context(parameters, type_aliases,
                                                builder=builder, bind=True)
        if self._only_conf(parameters, node_context):
            res = self.__execute_pass_basic(node_context)
        else:
            res = self.execute_basic(node_context)
        _raise_if_exception(res)

    def _sys_after_execute(self):
        """Always executed after main execution."""
        pass

    def _sys_verify_parameters(self, parameters, type_aliases):
        """Check if parameters are valid."""
        node_context = self._build_node_context(parameters,
                                                type_aliases,
                                                exclude_output=True,
                                                exclude_input=True)
        try:
            return _raise_if_exception(
                self.verify_parameters_basic(node_context))
        except (IOError, OSError):  # NOQA (capture any error in user code)
            sywarn('Error in validate_parameters: input data should not be'
                   ' used for validation.')
        except Exception as e:
            sywarn(f'Error in validate_parameters: {e}')
        return False

    def _sys_adjust_parameters(self, parameters, type_aliases,
                               builder=BaseContextBuilder()):
        """Adjust node parameters."""
        adjusted_parameters = copy.deepcopy(parameters)
        node_context = self._build_node_context(adjusted_parameters,
                                                type_aliases,
                                                exclude_output=True,
                                                builder=builder)
        self._adjust_parameters(node_context)
        return adjusted_parameters

    def _build_node_context(self, parameters, typealiases,
                            exclude_output=False,
                            exclude_input=False,
                            read_only=False,
                            builder=BaseContextBuilder(), bind=False):
        """Build node context object."""
        return builder.build(self, parameters, typealiases,
                             exclude_output=exclude_output,
                             exclude_input=exclude_input,
                             read_only=read_only, bind=bind)

    def _build_file_port_or_dummy(self, dummy_port_maker, port_dict, mode):
        if port_dict['file']:
            return dummy_port_maker(port_dict, mode,
                                    external=False,
                                    expanded=self._expanded,
                                    managed=self._managed)
        else:
            return _build_mem_port(port_dict)

    def _build_file_ports_or_dummys(self, dummy_port_maker, port_dicts, mode):
        return [
            self._build_file_port_or_dummy(dummy_port_maker, port_dict, mode)
            for port_dict in port_dicts]

    @staticmethod
    def create_node_context(inputs, outputs, definition, parameters,
                            typealiases, objects=None, own_objects=None):
        objects = {} if objects is None else objects
        input_ports = definition['ports'].get('inputs', [])
        output_ports = definition['ports'].get('outputs', [])

        return NodeContext(port_util.RunPorts(inputs,
                                              input_ports),
                           port_util.RunPorts(outputs,
                                              output_ports),
                           definition,
                           parameters,
                           typealiases,
                           objects,
                           own_objects)

    @classmethod
    def update_node_context(cls, node_context, inputs=None, outputs=None,
                            parameters=None):
        if parameters is None:
            parameters = node_context.parameters
        if inputs is None:
            inputs = node_context.input
        if outputs is None:
            outputs = node_context.output

        return cls.create_node_context(
            inputs, outputs, node_context.definition,
            parameters, node_context.typealiases, node_context._objects,
            node_context._own_objects)

    def _open_node_documentation(self, node_context):
        node_id = node_context.definition['id']

        if self.socket_bundle:
            network.send_all(
                self.socket_bundle.socket,
                self.socket_bundle.output_func(
                    message.RequestHelpMessage(node_id)))

    def _beg_capture_text_streams(self, node_context):
        self._org_sys_stdout = sys.stdout
        self._org_sys_stderr = sys.stderr
        self._cap_sys_stdout = io.StringIO()
        self._cap_sys_stderr = io.StringIO()
        out = node_context.output.group('__sy_out__')
        err = node_context.output.group('__sy_err__')
        both = node_context.output.group('__sy_both__')

        if both:
            sys.stdout = self._cap_sys_stdout
            sys.stderr = self._cap_sys_stdout
        else:
            if out:
                sys.stdout = self._cap_sys_stdout
            if err:
                sys.stderr = self._cap_sys_stderr

    def _end_capture_text_streams(self, node_context):
        sys.stdout = self._org_sys_stdout
        sys.stderr = self._org_sys_stderr
        out = node_context.output.group('__sy_out__')
        err = node_context.output.group('__sy_err__')
        both = node_context.output.group('__sy_both__')

        if both:
            both[0].set(self._cap_sys_stdout.getvalue())
        else:
            if out:
                out[0].set(self._cap_sys_stdout.getvalue())
            if err:
                err[0].set(self._cap_sys_stderr.getvalue())
        self._cap_sys_stderr = None
        self._cap_sys_stdout = None
        self._org_sys_stdout = None
        self._org_sys_stderr = None

    def _text_stream_ports(self, node_context):
        return [port for name in ['__sy_out__', '__sy_err__', '__sy_both__']
                for port in node_context.output.group(name)]

    def _conf_out_ports(self, node_context):
        return [port for name in ['__sy_conf__']
                for port in node_context.output.group(name)]

    def _conf_in_ports(self, node_context):
        return [port for name in ['__sy_conf__']
                for port in node_context.input.group(name)]

    def _port_type(self, definition, kind, key):
        pdefs = definition.get('ports', {}).get(kind)
        conf_type = None
        for pdef in pdefs:
            if pdef.get('key') == key:
                conf_type = pdef.get('type', None)
                break
        return conf_type

    def _conf_in_port_type(self, node_context):
        return self._port_type(node_context, 'inputs', '__sy_conf__')

    def _only_conf(self, parameters, node_context):
        name = 'only_conf'
        return parameters.get(name) and self._conf_out_ports(node_context)


def focus_widget(dialog):
    def inner():
        os_support.focus_widget(dialog)
    return inner
