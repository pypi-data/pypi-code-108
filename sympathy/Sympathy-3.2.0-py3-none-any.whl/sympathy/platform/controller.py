# This file is part of Sympathy for Data.
# Copyright (c) 2017, Combine Control Systems AB
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

from sympathy.platform import qt_compat2

QtCore = qt_compat2.QtCore
QtGui = qt_compat2.import_module('QtGui')


class StaticFilter(QtCore.QObject):
    signal = qt_compat2.Signal(bool)

    def __init__(self, value, parent):
        self._value = value
        super().__init__(parent)

    def emit_(self, *args):
        self.signal.emit(self._value)

    def connect_(self, slot):
        self.signal.connect(slot)


class SignalFilter(QtCore.QObject):
    signal = qt_compat2.Signal(bool)

    def __init__(self, raw_signal, target_value, editor_widget):
        super(SignalFilter, self).__init__(editor_widget)
        self._raw_signal = raw_signal
        self._target_value = target_value
        self._parameter = editor_widget._parameter_value
        self._raw_signal.connect(self.emit_)

    def emit_(self, *args):
        if self._parameter.value == self._target_value:
            self.signal.emit(True)
        else:
            self.signal.emit(False)

    def connect_(self, slot):
        self.signal.connect(slot)


class Field(object):
    def __init__(self, name, state, value=None):
        self._name = name
        self._state = state
        self._value = value

    def signal(self, widget_dict, ports=None, parent=None):
        signal_name_dict = {
            'checked': ('stateChanged', None, True),
            'value': ('valueChanged', None, self._value)}
        signal_name, signal_type, target_value = signal_name_dict[self._state]
        signal_no_type = getattr(widget_dict[self._name], signal_name)
        if signal_type is not None:
            raw_signal = signal_no_type[signal_type]
        else:
            raw_signal = signal_no_type
        return SignalFilter(
            raw_signal, target_value, widget_dict[self._name])

    def slot(self, widget_dict):
        slot_name_dict = {
            'enabled': 'set_enabled',
            'disabled': 'set_disabled',
            'visible': 'set_visible',
            'hidden': 'set_hidden',
        }
        slot_name = slot_name_dict[self._state]
        slot = getattr(widget_dict[self._name], slot_name)
        return slot


class Port(object):
    def __init__(self, name, state, value, group=None):
        self._name = name
        self._state = state
        self._value = value
        self._group = group

    def signal(self, widget_dict, ports=None, parent=None):
        ports = ports or {}
        if self._group:
            ports = ports.get(self._group, [])
        else:
            ports = ports.get('inputs', []) + ports.get('outputs', [])
        ports = {p.get('name'): p for p in ports}

        res = False
        if self._state == 'exists' and self._name:
            res = (self._name in ports) == self._value
        return StaticFilter(res, parent=parent)


class Controller(object):
    def __init__(self, when=None, action=None, function=None):
        # assert(when is not None and action is not None)
        self._when = when
        self._action = action
        self._function = function

    def connect(self, widget_dict, ports=None, parent=None):
        if self._when is not None and self._action is not None:
            self._connect_when_action(widget_dict, ports=ports, parent=parent)
        elif self._function is not None:
            self._connect_function(widget_dict)
        else:
            raise NotImplementedError('Not a valid controller choice.')

    def _connect_function(self, widget_dict):
        self._function(widget_dict)

    def _connect_when_action(self, widget_dict, ports=None, parent=None):
        signal = self._when.signal(widget_dict, ports=ports, parent=parent)
        if isinstance(self._action, collections.Iterable):
            for action in self._action:
                slot = action.slot(widget_dict)
                signal.connect_(slot)
        else:
            slot = self._action.slot(widget_dict)
            signal.connect_(slot)
        # Trigger checking value and emitting the result
        signal.emit_()
