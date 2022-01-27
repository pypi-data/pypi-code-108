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
import json

from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api import qt2 as qt
from sympathy.api import ParameterView
from sympathy.api import exceptions as syexceptions
from sympathy.platform import widget_library as sywidgets
from sympathy.platform.exceptions import try_result

QtGui = qt.QtGui
QtCore = qt.QtCore
QtWidgets = qt.QtWidgets


class UpdateConfigurationWithTable(synode.Node):
    """
    Update a parameter configuration (JSON) from a table.

    The typical way to use this node is to use two copies of the node whose
    parameters you want to change. Add a configuration output port on the first
    copy and connect that to the template port of this node. If you want to,
    you can set the first copy of the node to ``Execution mode: Configuration
    only``. The second copy of the node should get an input configuration port
    and should be connected to the output of this node (the updated
    configuration).
    """

    name = 'Update Configuration with Table'
    author = 'Magnus Sandén'
    version = '1.0'
    icon = 'create_json.svg'
    tags = Tags(Tag.Generic.Configuration)

    nodeid = 'org.sysess.sympathy.convert.updateconfigurationwithtable'
    inputs = Ports([Port.Table('Input table', name='input'),
                    Port.Json('Configuration template', name='template')])
    outputs = Ports([Port.Json('Updated configuration', name='output')])

    parameters = synode.parameters()
    parameters.set_list('parameter_names', _old_list_storage=True)
    parameters.set_list('parameter_types', _old_list_storage=True)
    parameters.set_list('column_names', _old_list_storage=True)

    def exec_parameter_view(self, node_context):
        column_names = []
        if node_context.input['input'].is_valid():
            column_names = node_context.input['input'].column_names()
        configuration = {}
        if node_context.input['template'].is_valid():
            configuration = node_context.input['template'].get() or {}
        return UpdateConfigurationWithTableWidget(
            node_context.parameters, configuration, column_names)

    def execute(self, node_context):
        def check_data_column(cname, func, *args, **kwargs):
            try:
                return func(*args, **kwargs)
            except KeyError:
                raise syexceptions.SyDataError(
                    f'Data column, {cname} is missing in data.')

        intable = node_context.input['input']
        conf = node_context.input['template'].get()

        pnames = node_context.parameters['parameter_names'].list
        ptypes = node_context.parameters['parameter_types'].list
        cnames = node_context.parameters['column_names'].list

        if not (len(pnames) == len(ptypes) == len(cnames)):
            raise syexceptions.SyConfigurationError("Corrupt configuration")

        for pname_json, ptype, cname in zip(pnames, ptypes, cnames):
            pname = tuple(json.loads(pname_json))

            def check_column(exc):
                raise syexceptions.SyDataError(
                    f'Data column {cname} is not missing in data.')

            if ptype == 'list':
                key = 'value_names'
                values = try_result(
                    KeyError,
                    intable.get_column_to_array, cname).map_fail(
                        check_column).ok().tolist()

                # Disable value when passing value_names.
                # This prevents problems since ParameterListNoUpdate
                # prioritizes value over value_names.
                self._set_with_flat_key(conf, pname + ('value',), [])
            else:
                key = 'value'
                # Use tolist to convert to python types:
                values = try_result(
                    KeyError,
                    intable.get_column_to_array,
                    cname, index=[0]).map_fail(check_column).ok().tolist()[0]

            try:
                self._set_with_flat_key(conf, pname + (key,), values)
            except KeyError as e:
                raise syexceptions.SyDataError(
                    f'Missing {e}, is selected parameter available?')
        node_context.output[0].set(conf)

    def _set_with_flat_key(self, nested_dict, flat_key, value):
        if len(flat_key) == 0:
            raise KeyError("Can't use empty tuple as flat key.")
        elif len(flat_key) == 1:
            nested_dict[flat_key[0]] = value
        else:
            self._set_with_flat_key(
                nested_dict[flat_key[0]], flat_key[1:], value)


class UpdateConfigurationWithTableWidget(ParameterView):
    def __init__(self, parameters, template, column_names, parent=None):
        super(UpdateConfigurationWithTableWidget, self).__init__(parent=parent)
        self._parameters = parameters
        self._flat_template = self._flatten_params_dict(template)
        self._labels_to_keys = self._get_labels_to_keys_dict(
            self._flat_template)

        toolbar = sywidgets.SyToolBar(self)
        self._append_row_action = toolbar.add_action(
            'Add row', 'actions/edit-add-row-symbolic.svg', 'Add row',
            receiver=self._append_row)
        self._append_row_action = toolbar.add_action(
            'Remove row', 'actions/edit-delete-row-symbolic.svg', 'Remove row',
            receiver=self._remove_selected_row)

        self._table = QtWidgets.QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(['Parameter', 'Data column'])
        self._init_from_parameters(parameters)

        self._parameter_delegate = ListOptionsItemDelegate(
            options=list(self._labels_to_keys.keys()))
        self._table.setItemDelegateForColumn(0, self._parameter_delegate)
        self._column_name_delegate = ListOptionsItemDelegate(
            options=list(column_names))
        self._table.setItemDelegateForColumn(1, self._column_name_delegate)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self._table)
        self.setLayout(layout)

    def _init_from_parameters(self, parameters):
        pnames = parameters['parameter_names'].list
        ptypes = parameters['parameter_types'].list
        cnames = parameters['column_names'].list
        if len(pnames) != len(cnames):
            syexceptions.sywarn("Ignoring corrupt configuration")
            return

        self._table.setRowCount(len(pnames))
        self._table.setVerticalHeaderLabels(
            [str(i) for i in range(self._table.rowCount())])
        for row, (pname_json, ptype, cname) in enumerate(
                zip(pnames, ptypes, cnames)):
            pname = tuple(json.loads(pname_json))
            if pname in self._flat_template:
                label = self._flat_template[pname].get('label', pname)
            else:
                # Add parameter names from the current configuration to
                # available options.
                label = '/'.join(pname)
                self._labels_to_keys[label] = pname
                self._flat_template[pname] = {
                    'label': label,
                    'type': ptype}
            pname_item = QtWidgets.QTableWidgetItem(label)
            cname_item = QtWidgets.QTableWidgetItem(cname)
            self._table.setItem(row, 0, pname_item)
            self._table.setItem(row, 1, cname_item)

    def _get_labels_to_keys_dict(self, flat_template):
        res = {}
        for key, param_dict in flat_template.items():
            if 'label' in param_dict:
                label = param_dict['label']
            else:
                label = '/'.join(key)
            res[label] = key
        return res

    def _flatten_params_dict(self, old_params, path=()):
        new_params = {}
        for key, param_dict in old_params.items():
            if not isinstance(param_dict, dict):
                continue
            param_path = path + (key,)
            param_type = param_dict.get('type', '')
            if param_type in ['group', 'page']:
                new_params.update(self._flatten_params_dict(
                    param_dict, path=param_path))
            else:
                new_params[param_path] = {
                    k: param_dict[k] for k in param_dict.keys()
                    if k in ['value', 'value_names', 'type']}
                label = param_dict.get('label', '/'.join(param_path))
                if label.endswith(':'):
                    label = label[:-1]
                new_params[param_path]['label'] = label
        return new_params

    def _append_row(self):
        row = self._table.rowCount()
        self._table.insertRow(row)
        self._table.setVerticalHeaderLabels(
            [str(i) for i in range(row + 1)])

    def _remove_selected_row(self):
        rows = {item.row() for item in self._table.selectedIndexes()}
        for row in sorted(rows, reverse=True):
            self._table.removeRow(row)

    def save_parameters(self):
        pnames = []
        ptypes = []
        cnames = []

        for row in range(self._table.rowCount()):
            try:
                label = self._table.item(row, 0).data(QtCore.Qt.DisplayRole)
                cname = self._table.item(row, 1).data(QtCore.Qt.DisplayRole)
            except AttributeError:
                label = None
                cname = None
            if not (label and cname):
                continue
            key = self._labels_to_keys[label]
            pnames.append(json.dumps(key))
            ptype = self._flat_template[key].get('type', '')
            ptypes.append(ptype)
            cnames.append(cname)

        self._parameters['parameter_names'].list = pnames
        self._parameters['parameter_types'].list = ptypes
        self._parameters['column_names'].list = cnames


class ListOptionsItemDelegate(QtWidgets.QItemDelegate):
    """Item delegate which shows a combox with options."""

    def __init__(self, options=None, parent=None):
        super(ListOptionsItemDelegate, self).__init__(parent=parent)
        self._options = options or []

    def createEditor(self, parent, option, index):
        editor = QtWidgets.QComboBox(parent)
        editor.clear()
        editor.addItems(self._options)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, QtCore.Qt.EditRole)
        if value in self._options:
            options = self._options
        else:
            options = [value] + self._options
        editor.clear()
        editor.addItems(options)
        i = options.index(value)
        editor.setCurrentIndex(i)

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        index.model().setData(index, value, QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
