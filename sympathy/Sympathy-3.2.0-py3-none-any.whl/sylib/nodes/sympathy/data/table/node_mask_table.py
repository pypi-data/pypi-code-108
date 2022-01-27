# This file is part of Sympathy for Data.
# Copyright (c) 2018 Combine Control Systems AB
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
import numpy as np

from sympathy.api import node as synode
from sympathy.api import dtypes
from sympathy.api.nodeconfig import (Port, Ports, Tag, Tags,
                                     adjust)
from sympathy.api import exceptions as syexc
from sympathy.api import masked


class ConvertError(Exception):
    pass


MASKED_NODEIDS = [
    'org.sysess.sympathy.table.fillmaskedvalues',
    'org.sysess.sympathy.table.maskvalues',
    'org.sysess.sympathy.table.dropmaskvalues',
]

_config_error_msg = (
    'Failure in column {column}: could not convert {name}: '
    '"{value}" to {type}.')


def _convert(value, dtype, name):
    try:
        return dtypes.numpy_value_from_dtype_str(dtype, value)
    except ValueError:
        raise ConvertError(
            dict(name=name, value=value, type=dtypes.typename_from_kind(
                dtype.kind)))


def selected_columns_op(input_table, output_table, columns, set_progress,
                        update=True):
    if update:
        output_table.set_name(input_table.get_name())
        output_table.set_table_attributes(input_table.get_table_attributes())

    column_names = input_table.column_names()
    selected_names = set(columns.selected_names(column_names))
    n_column_names = len(column_names)

    for i, name in enumerate(column_names):
        set_progress(i * (100. / n_column_names))
        if name in selected_names:
            yield name
        elif update:
            output_table.update_column(name, input_table, name)


class FillMaskedTable(synode.Node):
    """
    Fill masked values in Table.
    """

    author = 'Erik der Hagopian'
    description = 'Fill masked values in Table.'
    icon = 'select_table_columns.svg'
    name = 'Fill masked values in Table'
    nodeid = 'org.sysess.sympathy.table.fillmaskedvalues'
    tags = Tags(Tag.DataProcessing.Select)
    version = '1.0'
    related = (MASKED_NODEIDS
               + ['org.sysess.sympathy.data.table.holdvaluetable'])

    inputs = Ports([Port.Table('Input')])
    outputs = Ports([Port.Table('Output')])

    parameters = synode.parameters()
    parameters.set_list(
        'columns', label='Select columns', description='Select columns.',
        value=[], editor=synode.Editors.multilist_editor(edit=True))
    parameters['columns']._passthrough = True
    parameters.set_string(
        'value', label='Value', description='Specified fill value',
        value='')

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['columns'], node_context.input[0])

    def execute(self, node_context):
        in_table = node_context.input[0]
        out_table = node_context.output[0]
        self.fill_columns(
            in_table, out_table, node_context.parameters['columns'],
            self.set_progress, node_context.parameters['value'])

    @staticmethod
    def fill_columns(input_table, output_table, columns, set_progress, fill):

        def fill_conv(column):
            column_dtype = column.dtype
            base_dtype = dtypes.numpy_dtype_factory_for_dtype(
                column_dtype)
            value = _convert(fill.value, base_dtype, 'Value')
            value_dtype = value.dtype
            new_dtype = dtypes.numpy_dtype_factory_for_dtypes(
                column_dtype, value_dtype)
            if new_dtype != column_dtype:
                column = masked.astype(column, new_dtype)
            return column.filled(value)

        for name in selected_columns_op(input_table, output_table, columns,
                                        set_progress):
            array = input_table.get_column_to_array(name)
            if isinstance(array, np.ma.MaskedArray):
                try:
                    output_table.set_column_from_array(
                        name, fill_conv(array))
                    output_table.set_column_attributes(
                        name, input_table.get_column_attributes(name))
                except ConvertError as ce:
                    raise syexc.SyConfigurationError(_config_error_msg.format(
                        column=name, **ce.args[0]))
            else:
                output_table.update_column(name, input_table, name)


class MaskTable(synode.Node):
    """
    Mask values in Table.
    """

    author = 'Erik der Hagopian'
    description = 'Mask values in Table.'
    icon = 'select_table_columns.svg'
    name = 'Mask values in Table'
    nodeid = 'org.sysess.sympathy.table.maskvalues'
    tags = Tags(Tag.DataProcessing.Select)
    version = '1.0'
    related = MASKED_NODEIDS

    inputs = Ports([Port.Table('Input')])
    outputs = Ports([Port.Table('Output')])

    parameters = synode.parameters()
    parameters.set_list(
        'columns', label='Select columns', description='Select columns.',
        value=[], editor=synode.Editors.multilist_editor(edit=True))
    parameters['columns']._passthrough = True
    parameters.set_string(
        'value', label='Value', description='Specified fill value',
        value='')

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['columns'], node_context.input[0])

    def execute(self, node_context):
        in_table = node_context.input[0]
        out_table = node_context.output[0]
        self.mask_columns(
            in_table, out_table, node_context.parameters['columns'],
            self.set_progress, node_context.parameters['value'])

    @staticmethod
    def mask_columns(input_table, output_table, columns, set_progress, fill):

        def mask_conv(column):
            dtype = dtypes.numpy_dtype_factory_for_dtype(
                column.dtype)

            value = _convert(fill.value, dtype, 'Value')

            if dtype.kind == 'f' and np.isnan(value):
                mask = np.isnan(column)
            elif dtype.kind in ['m', 'M'] and np.isnat(value):
                mask = np.isnat(column)
            else:
                mask = column == value

            if isinstance(column, np.ma.MaskedArray):
                mask |= column.mask
                res = np.ma.MaskedArray(column.data, mask, dtype=dtype)
            else:
                res = np.ma.MaskedArray(column, mask, dtype=dtype)
            return res

        for name in selected_columns_op(input_table, output_table, columns,
                                        set_progress):
            try:
                output_table.set_column_from_array(
                    name, mask_conv(input_table.get_column_to_array(name)))
                output_table.set_column_attributes(
                    name, input_table.get_column_attributes(name))
            except ConvertError as ce:
                raise syexc.SyConfigurationError(_config_error_msg.format(
                    column=name, **ce.args[0]))


class DropMaskTable(synode.Node):
    author = 'Erik der Hagopian'
    description = 'Drop either rows or columns with any masked values.'
    icon = 'select_table_columns.svg'
    name = 'Drop masked values in Table'
    nodeid = 'org.sysess.sympathy.table.dropmaskvalues'
    tags = Tags(Tag.DataProcessing.Select)
    version = '1.0'
    related = MASKED_NODEIDS + ['org.sysess.sympathy.data.table.dropnantable']

    inputs = Ports([Port.Table('Input')])
    outputs = Ports([Port.Table('Output')])

    parameters = synode.parameters()
    parameters.set_list(
        'columns', label='Select columns', description='Select columns.',
        value=[], editor=synode.Editors.multilist_editor(edit=True))
    parameters['columns']._passthrough = True

    directions = ['Rows', 'Columns']

    parameters.set_string(
        'direction', label='Drop',
        value=directions[0],
        description='Select along which axis to drop values',
        editor=synode.Editors.combo_editor(options=directions))

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['columns'], node_context.input[0])

    def execute(self, node_context):
        in_table = node_context.input[0]
        out_table = node_context.output[0]
        self.drop_columns(
            in_table, out_table, node_context.parameters['columns'],
            self.set_progress, node_context.parameters['direction'])

    @staticmethod
    def drop_columns(input_table, output_table, columns, set_progress,
                     direction):

        if direction.value == 'Columns':

            for name in selected_columns_op(input_table, output_table, columns,
                                            set_progress):
                array = input_table.get_column_to_array(name)
                if isinstance(array, np.ma.MaskedArray):
                    if not np.any(array.mask):
                        output_table.set_column_from_array(
                            name, array.data)
                        output_table.set_column_attributes(
                            name, input_table.get_column_attributes(name))
                else:
                    output_table.update_column(name, input_table, name)

        elif direction.value == 'Rows':
            mask = np.zeros(input_table.number_of_rows(), dtype=bool)
            for name in selected_columns_op(input_table, output_table, columns,
                                            set_progress, update=False):
                array = input_table.get_column_to_array(name)
                if isinstance(array, np.ma.MaskedArray):
                    mask |= array.mask
            if not np.any(mask):
                output_table.update(input_table)
            else:
                for name in input_table.column_names():
                    array = input_table.get_column_to_array(name)
                    array = array[~mask]

                    if isinstance(array, np.ma.MaskedArray):
                        if not np.any(array.mask):
                            array = array.data

                    output_table.set_column_from_array(
                        name, array)
                    output_table.set_column_attributes(
                        name, input_table.get_column_attributes(name))
