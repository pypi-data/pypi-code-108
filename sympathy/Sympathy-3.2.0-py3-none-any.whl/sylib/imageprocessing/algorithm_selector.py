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

"""Implements utility widgets and classes for creating Gui parts selecting
(image processing) algorithm and their parameters"""
import Qt.QtWidgets as QtWidgets
import Qt.QtCore as QtCore

from sympathy.api import ParameterView


class ImageFiltering_abstract():
    """Implements common methods for all of the image filtering nodes"""

    @staticmethod
    def generate_parameters(parameters, options_types, options_default):
        for option_name, option_type in options_types.items():
            if option_type == float:
                parameters.set_float(option_name,
                                     value=options_default[option_name], label=option_name)
            elif option_type == int:
                parameters.set_integer(option_name,
                                       value=options_default[option_name], label=option_name)
            elif option_type == bool:
                parameters.set_boolean(option_name,
                                       value=options_default[option_name], label=option_name)
            elif isinstance(option_type, list):
                parameters.set_string(option_name,
                                      value=option_type[0], label=option_name)
            elif option_type is None:
                pass
            else:
                parameters.set_string(option_name,
                                      value=options_default[option_name], label=option_name)

    def exec_parameter_view(self, node_context):
        return AlgorithmParameterWidget(node_context.parameters,
                                        self.algorithms,
                                        self.options_list,
                                        self.options_types)

    @staticmethod
    def indent_string(level, txt):
        s = " " * level
        return s + txt.replace('\n', '\n\n' + s)

    @staticmethod
    def generate_docstring(description, algorithms, param_order,
                           inputs, outputs):
        algs = list(algorithms.keys())
        algs.sort()
        docstring = "\n{0}\n\n*Algorithms*:\n  \n\n".format(description)
        for alg in algs:
            d = algorithms[alg]
            if 'url' in d:
                docstring += "  - `{0}`_\n\n{1}\n\n".format(
                    alg,
                    ImageFiltering_abstract.indent_string(4, d['description']))
            else:
                docstring += "  - *{0}*\n\n{1}\n\n".format(
                    alg,
                    ImageFiltering_abstract.indent_string(4, d['description']))
            params = filter(lambda x: x in d.keys(), param_order)
            for par in params:
                docstring += "    **{0}:**\n{1}\n".format(
                    par,
                    ImageFiltering_abstract.indent_string(6, d[par]))
                docstring += "  \n"
            docstring += "\n"
        for alg in algs:
            d = algorithms[alg]
            if 'url' not in d:
                continue
            docstring += '.. _{0}: {1}\n'.format(alg, d['url'])
        docstring += '\n*Input ports*:\n{0}\n\n'.format(
            ImageFiltering_abstract.indent_string(4, str(inputs)))
        docstring += '*Output ports*:\n{0}\n\n'.format(
            ImageFiltering_abstract.indent_string(4, str(outputs)))
        return docstring


class AlgorithmParameterWidget(ParameterView):
    def __init__(self, parameters, algorithms,
                 options_list, options_types, parent=None):
        super(ParameterView, self).__init__(parent=parent)
        self._parameters = parameters
        self._validator = None
        self.algorithms = algorithms
        self.options_list = options_list
        self.options_types = options_types

        # Create combo_button for selecting between all algorithms and keep
        # track of used algorithm in self.algorithm
        self.alg_select = QtWidgets.QComboBox()
        self.algorithm_order = list(self.algorithms.keys())
        self.algorithm_order.sort()
        for pos, algname in enumerate(self.algorithm_order):
            alg = self.algorithms[algname]
            self.alg_select.addItem(algname)
            self.alg_select.setItemData(
                pos, alg['description'], QtCore.Qt.ToolTipRole)

        # Set initially used algorithm
        self.algorithm = None
        index = self.alg_select.findText(
            self._parameters['algorithm'].value, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.alg_select.setCurrentIndex(index)
        else:
            self.alg_select.setCurrentIndex(0)
        self.algorithm = self.algorithms[self._parameters['algorithm'].value]
        self.alg_select.currentIndexChanged.connect(self.algorithm_selected)

        # Add to layout
        self.options_layout = QtWidgets.QVBoxLayout()
        self.options_layout.addWidget(self.alg_select)
        self.create_option_widgets()
        self.options_layout.addStretch(1)
        self.setLayout(self.options_layout)
        self.set_visibility()

    def create_option_widgets(self):
        """Generate a widget for editing each option in the list of options"""
        self.option_widgets = []
        for pos, option in enumerate(self.options_list):
            option_type = self.options_types[option]
            widget = QtWidgets.QWidget()
            hbox   = QtWidgets.QHBoxLayout()

            if isinstance(option_type, list):
                editor = QtWidgets.QComboBox()
                for val in option_type:
                    editor.addItem(str(val))
                index = option_type.index(self._parameters[option].value)
                index = max(0, index)
                editor.setCurrentIndex(index)
            elif option_type is bool:
                editor = QtWidgets.QCheckBox()
                editor.setCheckState(
                    QtCore.Qt.Checked if self._parameters[option].value
                    else QtCore.Qt.Unchecked)
            elif option_type is None:
                pass
            else:
                editor = QtWidgets.QLineEdit(str(self._parameters[option].value))

            def editingFinished(option_=option, editor_=editor):
                option_type = self.options_types[option_]
                text = editor_.text()
                if option_type == float:
                    val = float(text)
                elif option_type == int:
                    val = int(text)
                else:
                    val = text
                self._parameters[option_].value = val

            def indexChanged(index, option_=option, editor_=editor):
                self._parameters[option_].value = (
                    self.options_types[option_][index])

            def checkChanged(state, option_=option):
                self._parameters[option_].value = bool(state)

            hbox.addWidget(QtWidgets.QLabel(option.capitalize()))
            hbox.addStretch(1)

            if isinstance(option_type, list):
                editor.currentIndexChanged.connect(indexChanged)
                hbox.addWidget(editor)
            elif option_type is bool:
                editor.stateChanged.connect(checkChanged)
                hbox.addWidget(editor)
            elif option_type is None:
                pass
            else:
                editor.editingFinished.connect(editingFinished)
                hbox.addWidget(editor)

            widget.setLayout(hbox)
            self.options_layout.addWidget(widget)
            self.option_widgets.append(widget)

    def set_visibility(self):
        """Update the visibility status of all widgets except for the
        actual algorithm selection"""
        if self.algorithm is None:
            for widget in self.option_widgets:
                widget.setVisible(False)
        else:
            for pos, option in enumerate(self.options_list):
                tooltip = (
                    self.algorithm[option] if option in self.algorithm
                    else None)
                if tooltip is not None:
                    self.option_widgets[pos].setVisible(True)
                    self.option_widgets[pos].setToolTip(tooltip)
                else:
                    self.option_widgets[pos].setVisible(False)

    def algorithm_selected(self, index):
        """Called by Qt to update the selected algorithm"""
        algname = self.algorithm_order[index]
        self._parameters['algorithm'].value = algname
        self.algorithm = self.algorithms[algname]
        self.set_visibility()
