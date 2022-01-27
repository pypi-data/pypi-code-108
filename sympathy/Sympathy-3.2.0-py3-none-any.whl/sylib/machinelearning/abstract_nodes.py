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
import Qt.QtWidgets as QtWidgets
import Qt.QtCore as QtCore

from sympathy.api import ParameterView

from sylib.machinelearning.descriptors import BoolType
from sylib.machinelearning.descriptors import StringSelectionType


class SyML_abstract():
    """
    Implements function for configuring model parameters and generate
    docstrings.

    Intended to be inherited by nodes that implement the specific algorithms

    Implements special meaning to the \a (ascii BELL) character inside
    documentation strings.  When converted to tooltips these are
    replaced by newline, when creating the Sphinx documentation
    strings they are replaced with blanks. This allows proper
    formatting of the tooltips without breaking the Sphinx
    parsing. There are no other legitimate uses of the BELL character
    in the documentation.
    """

    @staticmethod
    def generate_parameters(parameters, desc):
        for name, type_ in desc.types.items():
            type_.create_param(parameters, name, desc.descriptions[name])

    def exec_parameter_view(self, node_context):
        return ModelParameterWidget(node_context.parameters,
                                    self.__class__.descriptor)

    @staticmethod
    def indent_string(level, string):
        s = " "*level
        return s+string.replace('\n', '\n'+s)

    @staticmethod
    def generate_docstring(overview, info, attributes, inputs, outputs):
        """Generate docstrings based on the description and info object."""

        docstring = "\n{0}\n\n*Configuration*:\n  \n\n".format(overview)

        def handle_list(L):
            docs = ''
            if len(L) > 0 and isinstance(L[0], str):
                # TODO - add a separate heading for these entries?
                L = L[1:]
            for x in L:
                if isinstance(x, list):
                    docs += handle_list(x)
                elif isinstance(x, dict) and 'desc' in x:
                    docs += "  - *{0}*\n\n{1}\n\n".format(
                        x['name'], SyML_abstract.indent_string(
                            4, x['desc'].replace('\a', '\n')))
                else:
                    raise ValueError('Invalid entry "{}" in description object'
                                     .format(x))
            return docs
        docstring += handle_list(info)
        docstring += "\n\n*Attributes*:\n  \n\n".format(overview)
        for attr in attributes:
            docstring += "  - *{0}*\n\n{1}\n\n".format(
                attr['name'], SyML_abstract.indent_string(4, attr['desc']))
        docstring += '\n'
        docstring += '\n*Input ports*:\n{0}\n\n'.format(
            SyML_abstract.indent_string(4, str(inputs)))
        docstring += '*Output ports*:\n{0}\n\n'.format(
            SyML_abstract.indent_string(4, str(outputs)))
        return docstring

    @staticmethod
    def generate_docstring2(overview, params, inputs, outputs):
        """Generate docstrings based on the description and parameters.

        Overrides default Sympathy behaviour that does not handle large
        text segments well"""
        docstring = "\n{0}\n\n*Configuration*:\n  \n\n".format(overview)
        for p in params:
            docstring += "  - *{0}*\n\n{1}\n\n".format(
                p, SyML_abstract.indent_string(4, params[p].description))
        docstring += '\n'
        docstring += '\n*Input ports*:\n{0}\n\n'.format(
            SyML_abstract.indent_string(4, str(inputs)))
        docstring += '*Output ports*:\n{0}\n\n'.format(
            SyML_abstract.indent_string(4, str(outputs)))
        return docstring


class ModelParameterWidget(ParameterView):

    """
    Prepare the GUI for nodes
    """

    def __init__(self, parameters, desc, parent=None):
        super(ParameterView, self).__init__(parent=parent)
        self._parameters = parameters
        self._validator = None
        self._desc = desc
        self.build_ui()

    def build_ui(self):

        """
        This function builds the actual GUI. 
        
        There are two types 
        of user interfaces: tabbed (like with Model/Advanced/Solver)
        and untabbled (every optin in one widget). 
        Tabbed UIs derive from a list _desc_info (defined in the node_<name>.py script). 
        Otherwise, it's going to default to an untabbed UI. 
        """

        if len(self._desc.info) > 0 and isinstance(self._desc.info[0], list):

            # Tabbed layout: QSplitter object.
            self._layout = QtWidgets.QSplitter()
            self._layout.setOrientation(QtCore.Qt.Vertical)

            tmp_layout = QtWidgets.QVBoxLayout()
            tmp_layout.addWidget(self._layout)

            self.setLayout(tmp_layout)
            
            notebook = QtWidgets.QTabWidget()
            self._layout.addWidget(notebook)
            
            for info in self._desc.info:
                # Generates tabs (number equal the length ofn the "info" vector)
                # plus sub-layouts for evey element in the tabs. 
                self.build_parameter_widgets(info, notebook)
        else:

            # Untabbed layout: just a VBoxLayout with 
            # HBoxLayouts as sub-layouts for every entry 
            # in "info" on every rows.
            tmp_layout = QtWidgets.QVBoxLayout()

            for info in self._desc.info:
                # Generates the sub-layouts (HBoxLayout), 
                # one for every element in "info". 
                layout = self.build_parameter_widget_onetab(info['name'])
                tmp_layout.addLayout(layout)

            self._layout = QtWidgets.QWidget()
            tmp_layout.addStretch()
            self.setLayout(tmp_layout)

    def build_parameter_widgets(self, info, layout):
        if not isinstance(info, list):
            self.build_parameter_widget(info['name'], layout)
        else:
            name = ""
            if isinstance(info[0], str):
                name = info[0]
                info = info[1:]

            if isinstance(layout, QtWidgets.QTabWidget):
                group_widget = QtWidgets.QWidget()
                layout.addTab(group_widget, name)
            else:
                group_widget = QtWidgets.QGroupBox(name)
                layout.addWidget(group_widget)

            group_layout = QtWidgets.QVBoxLayout()
            group_widget.setLayout(group_layout)

            for inf in info:
                self.build_parameter_widgets(inf, group_layout)
            group_layout.addStretch(1)

    @property
    def status(self):
        for name, info in self._desc.parameters.items():
            type_ = info['type']
            try:
                value = type_.from_string(self._parameters[name].value)
            except ValueError:
                return '{} syntax error'.format(name)
            if not type_.test_value(value):
                return '{} invalid value'.format(name)
            if ('deprecated' in info
                    and info['deprecated']
                    and value != type_.default):
                return '{} is deprecated'.format(name)
        return ''

    @property
    def valid(self):
        for name, info in self._desc.parameters.items():
            type_ = info['type']
            try:
                value = type_.from_string(self._parameters[name].value)
            except ValueError:
                return False
            if not type_.test_value(value):
                return False
            if ('deprecated' in info
                    and info['deprecated']
                    and value != type_.default):
                return False
        return True

    def build_parameter_widget_onetab(self, name):

        type_ = self._desc.types[name]
        text_description = type_.description()

        hbox_layout = QtWidgets.QHBoxLayout()

        parameter = self._desc._parameters[name]
        if 'dispname' in parameter.keys():
            widget = QtWidgets.QLabel("{0}".format(parameter['dispname']))
            widget.setToolTip("{0}\n\n{1}".format(self._desc.descriptions[name].replace('\a', '\n'), text_description))
            hbox_layout.addWidget(widget)
        else:
            widget = QtWidgets.QLabel("{0}:".format(name))
            widget.setToolTip("{0}\n\n{1}".format(self._desc.descriptions[name].replace('\a', '\n'), text_description))
            hbox_layout.addWidget(widget)

        hbox_layout.addStretch(1)

        current_text = str(self._parameters[name].value)
        try:
            current_value = type_.from_string(current_text)
        except ValueError:
            raise ValueError('Cannot parse parameter {}, type {}, value: "{}" '
                             ''.format(name, type(current_text), current_text))

        if isinstance(type_, BoolType):
            value_widget = QtWidgets.QCheckBox()
            if current_value:
                value_widget.setCheckState(QtCore.Qt.Checked)
            else:
                value_widget.setCheckState(QtCore.Qt.Unchecked)
        elif isinstance(type_, StringSelectionType):
            value_widget = QtWidgets.QComboBox()
            for val in type_.options:
                value_widget.addItem(str(val))
            try:
                index = type_.options.index(current_text)
            except ValueError:
                index = 0
            value_widget.setCurrentIndex(index)
        else:
            value_widget = QtWidgets.QLineEdit()
            value_widget.setText(current_text)
        hbox_layout.addWidget(value_widget)

        alert_widget = QtWidgets.QPushButton("")
        icon = alert_widget.style().standardIcon(QtWidgets.QStyle.SP_TrashIcon)
        alert_widget.setIcon(icon)
        alert_widget.setVisible(False)
        hbox_layout.addWidget(alert_widget)

        def reset_param(self_=self, value_widget_=value_widget,
                        alert_widget_=alert_widget, name_=name,
                        parameter_=parameter, type__=type_):
            self._parameters[name_].value = type__.to_string(type__.default)
            value_widget_.setText("{0}".format(self_._parameters[name_].value))
            alert_widget_.setVisible(False)
            #if 'deprecated' in parameter and parameter['deprecated']:
            #    hbox_widget.setVisible(False)
            self.status_changed.emit()

        alert_widget.clicked.connect(reset_param)

        def value_updated(text, name_=name, type_=type_,
                          alert_widget_=alert_widget):
            self._parameters[name_].value = text
            self.status_changed.emit()

            try:
                value = type_.from_string(text)
            except Exception:
                alert_widget_.setVisible(True)
                alert_widget_.setToolTip("Warning: cannot parse value")
                return
            if not type_.test_value(value):
                alert_widget_.setVisible(True)
                alert_widget_.setToolTip("Warning: illegal value")
                return
            alert_widget_.setVisible(False)

        def text_updated(widget_=value_widget, update_fn=value_updated):
            update_fn(widget_.text())

        def state_changed(state, update_fn=value_updated):
            update_fn("True" if state else "False")

        def index_changed(index, type_=type_,
                          update_fn=value_updated):
            update_fn(type_.options[index])

        if isinstance(type_, BoolType):
            value_widget.stateChanged.connect(state_changed)
        elif isinstance(type_, StringSelectionType):
            value_widget.currentIndexChanged.connect(index_changed)
        else:
            value_widget.editingFinished.connect(text_updated)

        #if 'deprecated' in parameter and parameter['deprecated']:
        #    if type_.from_string(value_widget.text()) != type_.default:
        #        alert_widget.setVisible(True)
        #    else:
        #        hbox_widget.setVisible(False)

        return hbox_layout

    def build_parameter_widget(self, name, layout):

        type_ = self._desc.types[name]
        text_description = type_.description()

        hbox_layout = QtWidgets.QHBoxLayout()
        hbox_widget = QtWidgets.QWidget()
        hbox_widget.setLayout(hbox_layout)

        layout.addWidget(hbox_widget)

        parameter = self._desc._parameters[name]
        if 'dispname' in parameter.keys():
            hbox_layout.addWidget(QtWidgets.QLabel(
                "{0}".format(parameter['dispname'])))
        else:
            hbox_layout.addWidget(QtWidgets.QLabel("{0}:".format(name)))

        hbox_widget.setToolTip(
            "{0}\n\n{1}"
            .format(self._desc.descriptions[name].replace(
                '\a', '\n'), text_description))
        hbox_layout.addStretch(1)

        current_text = str(self._parameters[name].value)
        try:
            current_value = type_.from_string(current_text)
        except ValueError:
            raise ValueError('Cannot parse parameter {}, type {}, value: "{}" '
                             ''.format(name, type(current_text), current_text))

        if isinstance(type_, BoolType):
            value_widget = QtWidgets.QCheckBox()
            if current_value:
                value_widget.setCheckState(QtCore.Qt.Checked)
            else:
                value_widget.setCheckState(QtCore.Qt.Unchecked)
        elif isinstance(type_, StringSelectionType):
            value_widget = QtWidgets.QComboBox()
            for val in type_.options:
                value_widget.addItem(str(val))
            try:
                index = type_.options.index(current_text)
            except ValueError:
                index = 0
            value_widget.setCurrentIndex(index)
        else:
            value_widget = QtWidgets.QLineEdit()
            value_widget.setText(current_text)
        hbox_layout.addWidget(value_widget)

        alert_widget = QtWidgets.QPushButton("")
        icon = alert_widget.style().standardIcon(QtWidgets.QStyle.SP_TrashIcon)
        alert_widget.setIcon(icon)
        alert_widget.setVisible(False)
        hbox_layout.addWidget(alert_widget)

        def reset_param(self_=self, value_widget_=value_widget,
                        alert_widget_=alert_widget, name_=name,
                        parameter_=parameter, type__=type_):
            self._parameters[name_].value = type__.to_string(type__.default)
            value_widget_.setText("{0}".format(self_._parameters[name_].value))
            alert_widget_.setVisible(False)
            if 'deprecated' in parameter and parameter['deprecated']:
                hbox_widget.setVisible(False)
            self.status_changed.emit()

        alert_widget.clicked.connect(reset_param)

        def value_updated(text, name_=name, type_=type_,
                          alert_widget_=alert_widget):
            self._parameters[name_].value = text
            self.status_changed.emit()

            try:
                value = type_.from_string(text)
            except Exception:
                alert_widget_.setVisible(True)
                alert_widget_.setToolTip("Warning: cannot parse value")
                return
            if not type_.test_value(value):
                alert_widget_.setVisible(True)
                alert_widget_.setToolTip("Warning: illegal value")
                return
            alert_widget_.setVisible(False)

        def text_updated(widget_=value_widget, update_fn=value_updated):
            update_fn(widget_.text())

        def state_changed(state, update_fn=value_updated):
            update_fn("True" if state else "False")

        def index_changed(index, type_=type_,
                          update_fn=value_updated):
            update_fn(type_.options[index])

        if isinstance(type_, BoolType):
            value_widget.stateChanged.connect(state_changed)
        elif isinstance(type_, StringSelectionType):
            value_widget.currentIndexChanged.connect(index_changed)
        else:
            value_widget.editingFinished.connect(text_updated)

        if 'deprecated' in parameter and parameter['deprecated']:
            if type_.from_string(value_widget.text()) != type_.default:
                alert_widget.setVisible(True)
            else:
                hbox_widget.setVisible(False)
