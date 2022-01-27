# This file is part of Sympathy for Data.
# Copyright (c) 2017-2019, Combine Control Systems AB
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
from .. import widget_library as sywidgets
from .. import qt_compat2 as qt
from .. import exceptions as syexceptions
from .. import parameter_helper_gui


QtGui = qt.QtGui
QtCore = qt.QtCore
QtWidgets = qt.QtWidgets

ParameterRole = QtCore.Qt.UserRole

parameter_col = 0
binding_col = 1


class BaseOptionsItemDelegate(QtWidgets.QItemDelegate):
    """Item delegate which shows a combox with options."""

    def __init__(self, options=None, parent=None):
        super().__init__(parent=parent)
        self._options = options or []

    def _reset_editor_options(self, editor, options=None):
        editor.clear()
        if options is None:
            options = self._options
        for item in options:
            editor.addItem(self.display(item), item)

    def createEditor(self, parent, option, index):
        editor = QtWidgets.QComboBox(parent)
        self._reset_editor_options(editor)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, ParameterRole)
        i = editor.findData(value, ParameterRole)
        editor.setCurrentIndex(i)

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        user_data = editor.itemData(
            editor.currentIndex(), ParameterRole)
        index.model().setData(index, value, QtCore.Qt.EditRole)
        index.model().setData(index, user_data, ParameterRole)
        index.model().setData(index, self.tooltip(user_data),
                              QtCore.Qt.ToolTipRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def display(self, item):
        """
        Text representation of item, used for EditRole.
        """
        return str(item)

    def tooltip(self, item):
        """
        ToolTip representation of item, used for ToolTipRole.
        """
        return ''


class BindingDelegate(BaseOptionsItemDelegate):
    def __init__(self, options=None, parent=None):
        super().__init__(options=options, parent=parent)

    @classmethod
    def display(cls, item):
        path = []
        for seg in item:
            op, name = seg
            name = str(name)

            if op == '[]':
                path.append(name)
            elif op == '.':
                path.append(name)
            elif op == '()':
                path.append(f'{name}()')
            else:
                assert False, 'Unknown binding operator'

        return '/'.join(path)


class ParameterDelegate(BaseOptionsItemDelegate):
    def __init__(self, options=None, flat_template=None, parent=None):
        self._flat_template = flat_template
        super().__init__(options=options, parent=parent)

    def createEditor(self, parent, option, index):
        # Custom creation of editor to limit options so that already used
        # options cannot be reused in multiple rows.
        editor = QtWidgets.QComboBox(parent)

        params = []
        model = index.model()
        curr_data = index.model().data(index, ParameterRole)
        if curr_data is not None:
            curr_data = list(curr_data)

        for row in range(model.rowCount()):
            row_index = model.index(row, index.column())
            data = index.model().data(row_index, ParameterRole)

            if data is not None:
                params.append(list(data))

        options = []
        for option in self._options:
            lopt = list(option)
            if lopt == curr_data or lopt not in params:
                options.append(option)

        self._reset_editor_options(editor, options)
        return editor

    def display(self, item):
        res = ''
        if item:
            param = self._flat_template.get(tuple(item))

            if param is not None:
                res = param.get('label', '')
            if not res:
                res = ''.join(item[-1:])
        return res

    def tooltip(self, item):
        res = ''
        if item:
            param = self._flat_template.get(tuple(item))
            if param is not None:
                res = param.get('description', '')
        return res


class BindingTableWidget(QtWidgets.QWidget):
    def __init__(self, parameters, config_port, parent=None):
        super().__init__(parent=parent)
        self._parameters = parameters
        self._conf = {}

        self._flat_template = self._flatten_params_dict(
            parameters._parameter_dict)

        toolbar = sywidgets.SyToolBar(self)
        self._append_row_action = toolbar.add_action(
            'Add row', 'actions/edit-add-row-symbolic.svg', 'Add row',
            receiver=self._append_row)
        self._append_row_action = toolbar.add_action(
            'Remove row', 'actions/edit-delete-row-symbolic.svg', 'Remove row',
            receiver=self._remove_selected_row)

        self._table = QtWidgets.QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(['Parameter', 'Data'])
        self._parameter_delegate = ParameterDelegate(
            options=list(self._flat_template.keys()),
            flat_template=self._flat_template)

        col_paths = []
        if config_port.is_valid():
            col_paths = list(config_port.names('col_paths'))
        self._column_name_delegate = BindingDelegate(
            options=col_paths)

        self._table.setItemDelegateForColumn(
            parameter_col, self._parameter_delegate)
        self._table.setItemDelegateForColumn(
            binding_col, self._column_name_delegate)

        self._init_from_parameters(parameters)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self._table)
        self.setLayout(layout)

    def _init_from_parameters(self, parameters):
        pnames = []
        cnames = []

        if len(pnames) != len(cnames):
            syexceptions.sywarn("Ignoring corrupt configuration")
            return

        row_data = list(self._flat_template.items())

        bind_rows = [(path, param) for path, param in
                     row_data if param.get('binding') is not None]

        self._table.setRowCount(len(bind_rows))
        self._table.setVerticalHeaderLabels(
            [str(i) for i in range(self._table.rowCount())])

        for row, (path, param) in enumerate(bind_rows):
            bind = param['binding']
            if param['type'] != 'list':
                bind = bind[:-1]

            model = self._table.model()

            for col, data in [(parameter_col, path), (binding_col, bind)]:
                delegate = self._table.itemDelegateForColumn(col)
                model.setData(model.index(row, col),
                              delegate.display(data),
                              QtCore.Qt.EditRole)
                model.setData(model.index(row, col), data, ParameterRole)
                model.setData(model.index(row, col), delegate.tooltip(data),
                              QtCore.Qt.ToolTipRole)

        self._table.resizeColumnsToContents()
        for col in [parameter_col, binding_col]:
            self._table.setColumnWidth(
                col, max(150, self._table.columnWidth(col)))
        self._table.setMinimumWidth(350)

    def _flatten_params_dict(self, old_params):
        res = {}

        def inner(param, path):

            for key, item_dict in param.items():
                if isinstance(item_dict, dict):
                    item_path = path + (key,)
                    param_type = item_dict.get('type', '')

                    if param_type in ['group', 'page']:
                        inner(item_dict, item_path)
                    else:
                        label = item_dict.get('label')
                        item_dict_copy = dict(item_dict)
                        if label:
                            if label.endswith(':'):
                                label = label[:-1]
                            item_dict_copy['label'] = label
                        res[item_path] = item_dict_copy

        inner(old_params, tuple())
        return res

    def _append_row(self):
        row = self._table.rowCount()
        self._table.insertRow(row)
        self._table.setVerticalHeaderLabels(
            [str(i) for i in range(row + 1)])

    def _remove_selected_row(self):
        rows = {item.row() for item in self._table.selectedIndexes()}
        for row in sorted(rows, reverse=True):
            self._table.removeRow(row)
        self._table.setVerticalHeaderLabels(
            [str(i) for i in range(self._table.rowCount())])

    def save_parameters(self):
        # Set new bindings.
        for row in range(self._table.rowCount()):

            try:
                parameter = None
                binding = None
                parameter_item = self._table.item(row, parameter_col)
                binding_item = self._table.item(row, binding_col)

                if parameter_item:
                    parameter = parameter_item.data(ParameterRole)

                if binding_item:
                    binding = self._table.item(row, 1).data(ParameterRole)

                if parameter is not None and binding is not None:
                    param = self._parameters
                    for seg in parameter:
                        param = param[seg]

                        if param.type != 'list':
                            binding = list(binding) + [['[]', 0]]

                        param._binding = binding
            except Exception:
                # Ignore parameters that do not have set value for both
                # columns.
                pass
        self._parameters._binding_mode = (
            self._parameters._binding_mode_internal)


class JsonBindingWidget(QtWidgets.QLabel):
    def __init__(self, parameters, parent=None):
        super().__init__(parent=parent)
        self._parameters = parameters
        self.setText('Using JSON configuration. Parameters will be '
                     'updated/configured using the supplied JSON data')

    def save_parameters(self):
        self._parameters._binding_mode = (
            self._parameters._binding_mode_external)


class BindingWidget(QtWidgets.QWidget):
    def __init__(self, parameters, config_port, config_type, parent=None):
        super().__init__(parent)
        self._parameters = parameters
        binding_mode = parameters._binding_mode

        new_binding_mode = parameters._binding_mode_external
        if config_type != 'json':
            new_binding_mode = parameters._binding_mode_internal

        self._change_warning = None
        if binding_mode is not None and binding_mode != new_binding_mode:
            self._change_warning = QtWidgets.QLabel(
                'Applying configuration will change bind mode!')

        if new_binding_mode == parameters._binding_mode_internal:
            self._table_widget = BindingTableWidget(parameters, config_port)
            self._widget = self._table_widget
        elif new_binding_mode == parameters._binding_mode_external:
            self._json_widget = JsonBindingWidget(parameters)
            self._widget = self._json_widget

        layout = QtWidgets.QVBoxLayout()
        if self._change_warning:
            layout.addWidget(self._change_warning)
        layout.addWidget(self._widget)
        self.setLayout(layout)

    def save_parameters(self):
        def clear_bindings(param):
            param._binding = None
            try:
                for child in param.children():
                    param._binding = None
                    clear_bindings(child)
            except Exception:
                pass

        clear_bindings(self._parameters)
        return self._widget.save_parameters()


class BindingParameterView(parameter_helper_gui.CustomProxyParameterView):
    def __init__(self, binding_widget, parameter_view, parent=None):
        super().__init__(parameter_view, parent=parent)
        tab_widget = QtWidgets.QTabWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self._binding_widget = binding_widget
        self._parameter_view = parameter_view

        tab_widget.addTab(binding_widget, 'Data Binding')
        tab_widget.addTab(parameter_view, 'Configuration')
        layout.addWidget(tab_widget)
        self.setLayout(layout)

    def save_parameters(self):
        try:
            self._parameter_view.save_parameters()
        except AttributeError:
            pass
        self._binding_widget.save_parameters()


def binding_widget_factory(parameters, conf_port, conf_type,
                           parameter_view):
    binding_widget = BindingWidget(
        parameters, conf_port, conf_type)
    widget = BindingParameterView(binding_widget, parameter_view)
    return widget
