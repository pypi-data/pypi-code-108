# This file is part of Sympathy for Data.
# Copyright (c) 2013, 2017, Combine Control Systems AB
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
With the considered node it is possible to convert the data types of a number
of selected columns in the incoming Table. In general, the columns in the
internal :ref:`Table` type can have the same data types that exist for numpy
arrays, except for numpy object type. For this node the list of available data
types to convert to is restricted.

The following data types are available for conversion:
    - binary
    - bool
    - datetime (UTC or naive)
    - float
    - integer
    - text


Converting strings to datetimes
-------------------------------
Converting a str/unicode column to datetime might require some extra thought if
the strings include time-zone information. The datetimes stored by Sympathy
have no time zone information (due to limitations in the underlying data
libraries), but Sympathy is able to use the time-zone information when creating
the datetime columns. This can be done in two different ways, which we call
"UTC" and "naive".

datetime (UTC)
##############
The option *datetime (UTC)* will calculate the UTC-time corresponding to each
datetime in the input column. This is especially useful when your data contains
datetimes from different time zones (a common reason for this is daylight
savings time), but when looking in the viewer, exports etc. the datetimes will
not be the same as in the input.

For example the string ``'2016-01-01T12:00:00+0100'`` will be stored as
``2016-01-01T11:00:00`` which is the corresponding UTC time.

There is currently no standard way of converting these UTC datetimes back to
the localized datetime strings with time-zone information.

datetime (naive)
################
The option *datetime (naive)* simply discards any time-zone information. This
corresponds pretty well to how we "naively" think of time when looking at a
clock on the wall.

For example the string ``'2016-01-01T12:00:00+0100'`` will be stored as
``2016-01-01T12:00:00``.

Text vs. binary
---------------
Text data is a string of arbitrary characters from any writing system. Binary
data on the other hand is a series of bytes as they would be stored in a
computer. Text data can be converted to binary data and vice versa by choosing
one of several different character encodings. The character encoding maps the
characters onto series of bytes, but many encodings only support some subset of
all the different writing systems.

This node currently only supports the ASCII encoding, which means that only the
letters a-z (lower and upper case), as well as digits and a limited number of
punctuation characters can be converted. Trying to convert a string with any
other characters will lead to errors.
"""
import pytz
import dateutil.parser
from collections import defaultdict
import numpy as np

from sympathy.api import node_helper
from sympathy.api import qt2 as qt_compat
from sympathy.api import node as synode
from sympathy.api.nodeconfig import (Port, Ports, Tag, Tags, adjust,
                                     deprecated_node)
from sympathy.api import exceptions
from sympathy.api import table
from sympathy.api import dtypes
from sylib.converters import TYPE_NAMES, CONVERSION_OLD_TYPES_NEW_TYPES, CONVERSIONS

QtCore = qt_compat.QtCore
QtGui = qt_compat.import_module('QtGui')
QtWidgets = qt_compat.import_module('QtWidgets')


# def extract(column, dtype):
#     return (column, (dtype, CONVERSIONS))


def convert_table_base(input_table, output_table, conversion):
    """
    Convert table using convert_table with CONVERSIONS as only column
    conversion dictionary.

    Add data from input_table to output_table converting it according to
    conversion.
    """
    conversion_base = dict(((k, (v, CONVERSIONS))
                            for k, v in conversion.items()))
    return convert_table(input_table, output_table, conversion_base)


def convert_table(input_table, output_table, conversion, keep_other=True,
                  set_progress=None):
    """
    Add data from input_table to output_table converting it according to
    conversion.

    >>> input_table = table.File()
    >>> output_table = table.File()
    >>> input_table.set_column_from_array('col1', np.array([1.1]))
    >>> input_table.set_column_from_array('col2', np.array([1]))
    >>> input_table.set_column_from_array('col3', np.array(['hi']))
    >>> conversion = {'col1': ('i', CONVERSIONS), 'col2': ('b', CONVERSIONS)}
    >>> convert_table(input_table, output_table, conversion)
    >>> print str(input_table)
    col1 float64
    col2 int64
    col3 |S2
    >>> '{0:0.1f}'.format(output_table.get_column_to_array('col1')[0])
    '1.1'
    >>> output_table.get_column_to_array('col2')[0]
    True
    >>> output_table.get_column_to_array('col3')[0]
    'hi'
    """
    columns = input_table.column_names()
    converted_columns = conversion.keys()
    n_columns = len(columns)

    for i, column in enumerate(columns):
        set_progress(i * 100. / n_columns)

        if column in converted_columns:
            # Convert column
            output_table.set_column_from_array(column, convert_column(
                input_table.get_column_to_array(column), conversion[column]))
        elif keep_other:
            # Copy column
            output_table.update_column(column, input_table)

        output_table.set_attributes(input_table.get_attributes())
        output_table.set_name(input_table.get_name())


def convert_column(column, conversion):
    """
    Convert column with conversion.
    Return converted column.
    """
    target, convert = conversion
    origin = column.dtype.kind
    return convert[target][origin](column)


def set_child_progress(set_parent_progress, parent_value, factor):
    def inner(child_value):
        return set_parent_progress(
            parent_value + (child_value * factor / 100.))
    return inner


@deprecated_node('4.0.0', 'one or several Convert columns in Table')
class ConvertTableColumns(synode.Node):
    """
    Convert selected columns in Table to new specified data types.
    """

    author = "Erik der Hagopian"
    version = '1.0'

    name = 'Convert specific columns in Table'
    description = 'Convert selected columns in Table to new data types.'
    nodeid = 'org.sysess.sympathy.data.table.converttablecolumns'
    icon = 'select_table_columns.svg'
    tags = Tags(Tag.DataProcessing.TransformData)

    inputs = Ports([Port.Table(
        'Input Table', name='port1')])
    outputs = Ports([Port.Table('Table with converted columns', name='port2')])

    parameters = synode.parameters()
    editor = synode.Util.multilist_editor(edit=True, mode=False)
    parameters.set_list(
        'in_column_list', label='Select columns',
        description='Select the columns to use', value=[],
        editor=editor)
    parameters.set_list(
        'in_type_list', label='Select type',
        description='Select the type to use', value=[],
        editor=synode.Util.combo_editor(edit=False))
    parameters.set_list(
        'out_column_list', label='Convert columns',
        description='Selected columns to convert', value=[],
        editor=synode.Util.multilist_editor(),
        _old_list_storage=True)
    parameters.set_list(
        'out_type_list', label='Convert types',
        description='Selected types to use', value=[],
        editor=synode.Util.multilist_editor(),
        _old_list_storage=True)

    def update_parameters(self, old_params):
        # Move list configurations from .value to .list to better conform with
        # current best practice.
        for pname in ('out_type_list', 'out_column_list'):
            parameter = old_params[pname]
            if parameter.value:
                parameter.list = parameter.value
                parameter.value = []

        old_params['out_type_list'].list = [
            CONVERSION_OLD_TYPES_NEW_TYPES.get(v, v)
            for v in old_params['out_type_list'].list]

    def exec_parameter_view(self, node_context):
        input_table = node_context.input['port1']
        if not input_table.is_valid():
            input_table = table.File()

        return ConvertTableColumnsWidget(
            input_table, node_context.parameters)

    def execute(self, node_context):
        self.run(node_context.parameters, node_context.input['port1'],
                 node_context.output['port2'], True, self.set_progress)

    def run(self, parameters, input_table, output_table, keep_other,
            set_progress):
        columns = parameters['out_column_list'].list
        types = parameters['out_type_list'].list
        conversion = dict([(column, (dtype, CONVERSIONS))
                           for column, dtype in
                           zip(columns, types)])
        convert_table(input_table, output_table, conversion, keep_other,
                      set_progress)


@deprecated_node('4.0.0', 'one or several Convert columns in Tables')
class ConvertTablesColumns(ConvertTableColumns):
    name = 'Convert specific columns in Tables'
    description = 'Convert selected columns in Tables to new data types.'
    nodeid = 'org.sysess.sympathy.data.table.converttablescolumns'

    inputs = Ports([Port.Tables(
        'Input Table', name='port1')])
    outputs = Ports([Port.Tables(
        'Tables with converted columns', name='port2')])

    def update_parameters(self, old_params):
        # Move list configurations from .value to .list to better conform with
        # current best practice.
        for pname in ('out_type_list', 'out_column_list'):
            parameter = old_params[pname]
            if parameter.value:
                parameter.list = parameter.value
                parameter.value = []

        old_params['out_type_list'].list = [
            CONVERSION_OLD_TYPES_NEW_TYPES.get(v, v)
            for v in old_params['out_type_list'].list]

    def exec_parameter_view(self, node_context):
        input_tables = node_context.input['port1']
        if not input_tables.is_valid():
            input_table = table.File()
        else:
            try:
                input_table = input_tables[0]
            except IndexError:
                input_table = table.File()

        return ConvertTableColumnsWidget(
            input_table, node_context.parameters)

    def execute(self, node_context):
        input_tables = node_context.input['port1']
        output_tables = node_context.output['port2']

        def convert_table(input_table, output_table, set_progress):
            self.run(node_context.parameters, input_table, output_table, True,
                     set_progress)
        synode.map_list_node(convert_table, input_tables, output_tables,
                             self.set_progress)


class ConvertTableColumnsWidget(QtWidgets.QWidget):
    def __init__(self, input_table, parameters, parent=None):
        super(ConvertTableColumnsWidget, self).__init__(parent)
        self._parameters = parameters
        self._input_table = input_table
        self._init_parameters()
        self._init_gui()
        self._connect_gui()

    def _init_parameters(self):
        self._convert_items = {}
        self._parameters['in_column_list'].value_names = []
        self._parameters['in_column_list'].value = []
        self._parameters['in_column_list'].list = (
            self._input_table.column_names())
        self._parameters['in_type_list'].list = TYPE_NAMES.values()
        self._parameters['in_type_list'].value_names = []
        self._parameters['in_type_list'].value = []

    def _init_gui(self):
        vlayout = QtWidgets.QVBoxLayout()
        selection_hlayout = QtWidgets.QHBoxLayout()
        button_hlayout = QtWidgets.QHBoxLayout()

        self.add_button = QtWidgets.QPushButton('Add')
        self.remove_button = QtWidgets.QPushButton('Remove')
        self.preview_button = QtWidgets.QPushButton('Preview')

        self.type_list = self._parameters['in_type_list'].gui()
        self.column_list = self._parameters['in_column_list'].gui()
        self.convert_list = QtWidgets.QListWidget()

        self.convert_label = QtWidgets.QLabel('Conversions')
        self.preview_label = QtWidgets.QLabel('Not previewed')

        self.convert_list.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)

        self.convert_list.setAlternatingRowColors(True)

        for column, dtype in zip(self._parameters['out_column_list'].list,
                                 self._parameters['out_type_list'].list):
            label = u'{dtype} / {column}'.format(
                column=column, dtype=TYPE_NAMES[dtype])
            item = QtWidgets.QListWidgetItem(label)
            self.convert_list.addItem(item)
            self._convert_items[column] = item

        selection_hlayout.addWidget(self.column_list)
        selection_hlayout.addWidget(self.type_list)

        button_hlayout.addWidget(self.add_button)
        button_hlayout.addWidget(self.remove_button)
        button_hlayout.addWidget(self.preview_button)
        button_hlayout.addWidget(self.preview_label)

        vlayout.addLayout(selection_hlayout)
        vlayout.addLayout(button_hlayout)
        vlayout.addWidget(self.convert_label)
        vlayout.addWidget(self.convert_list)

        self.setLayout(vlayout)

    def _connect_gui(self):
        self.add_button.clicked.connect(self.add)
        self.remove_button.clicked.connect(self.remove)
        self.preview_button.clicked.connect(self.preview)

    def add(self):
        columns = self._parameters['in_column_list'].value_names
        type_name = self._parameters['in_type_list'].selected
        dtype = None
        for k, v in TYPE_NAMES.items():
            if v == type_name:
                dtype = k
                break
        if dtype is None:
            return

        for column in columns:
            label = u'{dtype} / {column}'.format(
                column=column, dtype=type_name)

            if column in self._convert_items:
                item = self._convert_items[column]
                index = self.convert_list.row(item)
                for value, pname in [(column, 'out_column_list'),
                                     (dtype, 'out_type_list')]:
                    list_ = self._parameters[pname].list
                    list_[index] = value
                    self._parameters[pname].list = list_
                item.setText(label)
            else:
                item = QtWidgets.QListWidgetItem(label)
                self._convert_items[column] = item
                for value, pname in [(column, 'out_column_list'),
                                     (dtype, 'out_type_list')]:
                    list_ = self._parameters[pname].list
                    list_.append(value)
                    self._parameters[pname].list = list_
                self.convert_list.addItem(item)

    def remove(self):
        for item in self.convert_list.selectedItems():
            index = self.convert_list.row(item)
            column = self._parameters['out_column_list'].list[index]
            del self._convert_items[column]
            for pname in ['out_column_list', 'out_type_list']:
                list_ = self._parameters[pname].list
                del list_[index]
                self._parameters[pname].list = list_
            self.convert_list.takeItem(index)

    def preview(self):
        input_table = self._input_table
        output_table = table.File()
        node = ConvertTableColumns()
        try:
            node.run(
                self._parameters, input_table, output_table, False,
                lambda x: None)
            self.preview_label.setText('Ok!')
            self.preview_label.setStyleSheet('QLabel { color : black; }')
        except Exception:
            self.preview_label.setText('Failed.')
            self.preview_label.setStyleSheet('QLabel { color : red; }')


class ConvertColumnsTable(synode.Node):
    """
    Convert selected columns to specified data type.
    """
    author = 'Erik der Hagopian'
    description = 'Select columns to convert to specified data type.'
    icon = 'select_table_columns.svg'
    name = 'Convert columns in Table'
    nodeid = 'org.sysess.sympathy.data.table.convertcolumnstable'
    tags = Tags(Tag.DataProcessing.TransformData)
    version = '1.0'

    inputs = Ports([Port.Table('Input')])
    outputs = Ports([Port.Table('Output')])

    parameters = synode.parameters()
    editor = synode.Util.multilist_editor(edit=True)
    parameters.set_list(
        'columns', label='Columns',
        description='Columns that should be converted.',
        value=[], editor=editor)
    editor = synode.Util.combo_editor()
    parameters.set_list(
        'types', label='Target type',
        description='The type that these columns should be converted to.',
        list=list(sorted(TYPE_NAMES.values())),
        value_names=['text'],
        editor=editor)

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['columns'], node_context.input[0])

    def execute(self, node_context):
        in_table = node_context.input[0]
        out_table = node_context.output[0]
        self.convert_columns(
            in_table, out_table, node_context.parameters['columns'],
            self.conversion(node_context.parameters['types'].selected),
            self.set_progress)

    @staticmethod
    def conversion(type_):
        for k, v in TYPE_NAMES.items():
            if v == type_:
                return CONVERSIONS[k][None]
        assert False, 'Unknown conversion: "{}".'.format(type_)

    @staticmethod
    def convert_columns(input_table, output_table, parameter, conversion,
                        set_progress):
        output_table.set_name(input_table.get_name())
        output_table.set_attributes(input_table.get_attributes())
        column_names = input_table.column_names()
        selected_names = set(parameter.selected_names(column_names))
        n_column_names = len(column_names)

        for i, name in enumerate(column_names):
            set_progress(i * (100. / n_column_names))
            if name in selected_names:
                output_table.set_column_from_array(
                    name, conversion(input_table.get_column_to_array(name)))
                output_table.set_column_attributes(
                    name, input_table.get_column_attributes(name))
            else:
                output_table.update_column(name, input_table, name)


@node_helper.list_node_decorator(input_keys=[0], output_keys=[0])
class ConvertColumnsTables(ConvertColumnsTable):
    name = 'Convert columns in Tables'
    nodeid = 'org.sysess.sympathy.data.table.convertcolumnstables'
