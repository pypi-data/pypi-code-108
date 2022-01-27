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
from sympathy.api import node as synode
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust
from sympathy.api import table
from sympathy.api import exceptions as exc
from sympathy.api import masked as utils_masked
import numpy as np


def _add_nomasks_parameter(parameters):
    parameters.set_boolean(
        'nomasks', value=False,
        label='Use zeros/empty strings instead of masks',
        description='When unchecked any positions in the output which '
                    'arn\'t mentioned in the input will be masked. '
                    'When checked such positions are instead assigned '
                    'a zero value, an empty string, or some other value '
                    'depending on the type of the values column.')


def _add_include_index_parameter(parameters):
    parameters.set_boolean(
        'include_index', value=True,
        label='Include index column',
        description='Include a column with the index of each row.')


def _add_new_pivot_parameters(parameters):
    _add_nomasks_parameter(parameters)
    _add_include_index_parameter(parameters)


def _nans(shape, dtype):
    return np.full(shape, np.nan)


class PivotTableSuper(synode.Node):
    """Pivot a Table, spreadsheet-style."""

    author = 'Greger Cronquist'
    version = '1.0'
    icon = 'pivot_table.svg'
    tags = Tags(Tag.DataProcessing.TransformStructure)

    parameters = synode.parameters()
    parameters.set_list(
        'index', label='Index column',
        description='Column that contains a unique identifier for each '
                    'new row',
        editor=synode.Util.combo_editor(edit=True))
    parameters.set_list(
        'columns', label='Column names column',
        description='Column that contains the new column names',
        editor=synode.Util.combo_editor(edit=True))
    parameters.set_list(
        'values', label='Value column',
        description='Column that contains the new values',
        editor=synode.Util.combo_editor(edit=True))
    _add_new_pivot_parameters(parameters)

    def update_parameters(self, parameters):
        if 'nomasks' not in parameters:
            _add_nomasks_parameter(parameters)
            parameters['nomasks'].value = True
        if 'include_index' not in parameters:
            _add_include_index_parameter(parameters)
            parameters['include_index'].value = False

    def adjust_parameters(self, node_context):
        parameters = node_context.parameters
        in_table = node_context.input['Input']
        for p in ('index', 'columns', 'values'):
            adjust(parameters[p], in_table)


def _pivot_table(raw_index, columns, values, outtable,
                 nomasks=False, index_output_name=None):
    if nomasks:
        if values.dtype.kind in 'fiu':
            zeros = _nans
        else:
            zeros = np.zeros
    else:
        zeros = np.ma.masked_all

    columns_u, columns_uinv = np.unique(columns, return_inverse=True)
    index_u, index = np.unique(raw_index, return_inverse=True)
    row_count = len(index_u)
    for ci, column_name in enumerate(columns_u):
        output_column = zeros(row_count, values.dtype)
        column_values = values[columns_uinv == ci]
        column_index = index[columns_uinv == ci]
        output_column[column_index] = column_values
        outtable.set_column_from_array(
            str(column_name), output_column)

    if index_output_name is not None:
        outtable.set_column_from_array(index_output_name, index_u)


class PivotTable(PivotTableSuper):
    name = 'Pivot Table'
    nodeid = 'org.sysess.sympathy.data.table.pivottablenode'
    inputs = Ports([Port.Table('Input Table', name='Input')])
    outputs = Ports([Port.Table('Output Table', name='Output')])

    def execute(self, node_context):
        in_table = node_context.input['Input']
        out_table = node_context.output['Output']
        if in_table.is_empty():
            return

        parameters = node_context.parameters
        nomasks = parameters['nomasks'].value
        if parameters['include_index'].value:
            index_output_name = parameters['index'].selected
        else:
            index_output_name = None

        index = in_table._require_column(parameters['index'])
        columns = in_table._require_column(parameters['columns'])
        values = in_table._require_column(parameters['values'])

        _pivot_table(index, columns, values, out_table,
                     nomasks, index_output_name)
        out_table.set_name(in_table.get_name())


@node_helper.list_node_decorator(['Input'], ['Output'])
class PivotTables(PivotTable):
    name = 'Pivot Tables'
    nodeid = 'org.sysess.sympathy.data.table.pivottablesnode'


class TransposeTableNew(synode.Node):
    """
    This node performs a standard transpose of tables. Bear in mind, since
    a column can only contain one type, if the rows contain different types
    the transposed columns will be converted to the closest matching type. The
    worst case is therefore strings.

    An exception to this behaviour is when the first column contains strings.
    Using the option 'Use selected column as column names' the selected column
    will replace the column names in the new table. The rest of the input table
    will be transposed, discarding the name column.

    The other option is 'Column names as first column' which will take the
    table's column names and put them in the first column in the output table.
    This is convenient if you simply want to extract column names from a table.

    When the columns transposed have different types, the node will try to find
    a result type to accommodate the new values. For example, combining an
    integer and a boolean would result in an integer column with the boolean
    values translated from False to 0 and True to 1. LIMITATION: If the types
    differ and part of the column is date-time or time-delta no resulting type
    can be found.
    """

    author = 'Andreas Tagerud'
    version = '1.0'
    icon = 'pivot_table.svg'
    tags = Tags(Tag.DataProcessing.TransformStructure)
    name = 'Transpose Table'
    nodeid = 'org.sysess.sympathy.data.table.transposetablenew'
    inputs = Ports([Port.Table('The Table to transpose', name='input')])
    outputs = Ports([Port.Table('The transposed Table', name='output')])

    parameters = synode.parameters()
    parameters.set_boolean(
        'use_col_names',
        label='Column names as first column',
        description=('Set column names from the input table as the first '
                     'column in the transposed table'),
        dvalue=False)
    parameters.set_boolean(
        'reverse_col_names',
        label='Use selected column as column names',
        description=('Use the selected column from input table as column '
                     'names in the transposed table, and discarding the '
                     'selected column from the transpose.'),
        dvalue=False)
    parameters.set_list(
        'columns', label='Column names column',
        description='Column that contains the new column names',
        editor=synode.Util.combo_editor(edit=True))

    controllers = (
        synode.controller(
            when=synode.field('reverse_col_names', 'checked'),
            action=(
                synode.field('columns', 'enabled'))))

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['columns'],
               node_context.input['input'])

    def execute_table(self, in_table, names_to_column, column_to_names,
                      name_column):
        try:
            return self._execute_table(
                in_table, names_to_column, column_to_names, name_column)
        except exc.SyColumnTypeError:
            raise exc.SyDataError(
                'Input columns to transpose have incompatible types',
                details=(
                    'Input columns to transpose have incompatible types. '
                    'Keep in mind that datetime and timedelta cannot be '
                    'used in a column with other types'))

    def _execute_table(self, in_table, names_to_column, column_to_names,
                       name_column):
        def clear_nomask(array):
            if isinstance(array, np.ma.MaskedArray):
                mask = np.ma.getmaskarray(array)
                if not np.any(mask):
                    array = array.data
            return array

        column_names = in_table.column_names()
        out_table = table.File()
        out_table.set_name(in_table.get_name())

        columns = []

        if column_to_names and name_column:
            columns = in_table.get_column_to_array(name_column)
            columns = np.array([str(name) for name in columns])
            out_columns = []
            column_names.remove(name_column)
            for column in column_names:
                out_columns.append(in_table.get_column_to_array(column))
        else:
            columns = np.array([str(i)
                                for i in range(in_table.number_of_rows())])
            out_columns = []
            for column in column_names:
                out_columns.append(in_table.get_column_to_array(column))

        dtypes = set([c.dtype.kind for c in out_columns])

        if len(dtypes) > 1 and in_table.number_of_rows():
            tmp_out_columns = []
            for column in out_columns:
                if column.dtype.kind == 'M':
                    tmp_out_columns.append(
                        np.array([v.isoformat() for v in column.tolist()]))
                elif column.dtype.kind == 'm':
                    tmp_out_columns.append(
                        np.array(['{} s'.format(v.total_seconds())
                                  for v in column.tolist()]))
                else:
                    tmp_out_columns.append(column)
            out_columns = tmp_out_columns

        matrix = utils_masked.asarray(out_columns)
        out_matrix = np.ma.transpose(matrix)

        if names_to_column:
            out_table.set_column_from_array(
                'Column names', np.array(column_names))

        for i in range(len(columns)):
            name = str(i) if not column_to_names else columns[i]
            if column_names:
                try:
                    out_table.set_column_from_array(
                        name, clear_nomask(out_matrix[i, :]))
                except IndexError:
                    out_table.set_column_from_array(
                        name, np.ma.masked_all((len(column_names))))
                except ValueError:
                    column = np.ma.array(out_matrix[i, :])
                    masked = np.ma.masked_all(
                        (len(column_names) - len(column)))
                    column = np.ma.concatenate([column, masked])
                    out_table.set_column_from_array(name, column)
            else:
                out_table.set_column_from_array(name, np.array([]))
        return out_table

    def execute(self, node_context):
        column = node_context.parameters['columns'].selected
        node_context.output['output'].source(self.execute_table(
            node_context.input['input'],
            node_context.parameters['use_col_names'].value,
            node_context.parameters['reverse_col_names'].value,
            column))


@node_helper.list_node_decorator(['input'], ['output'])
class TransposeTablesNew(TransposeTableNew):
    name = 'Transpose Tables'
    nodeid = 'org.sysess.sympathy.data.table.transposetablesnew'
