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
import numpy as np

from sympathy.api import node as synode
from sympathy.api import table
from sympathy.api import exceptions, dtypes
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust

REPORTING = ['Exception', 'Dummy Signal', 'Masked Signal', 'Zero Signal']
EXE, DUMMY, MASK, ZERO = REPORTING


def ensure_columns(in_table, out_table, selection_table, names_param,
                   types_param, mode):
    out_table.update(in_table)
    column_names = selection_table._require_column(names_param, 'U')
    if mode == MASK or mode == ZERO:
        types = selection_table._require_column(types_param, 'U')

    for i, column_name in enumerate(column_names):

        if column_name not in out_table:
            if mode == EXE:
                raise exceptions.SyDataError(
                    "Column {} missing.".format(column_name))
            elif mode == DUMMY:
                attr = {'info': 'Missing column'}
                out_table.set_column_from_array(
                    column_name,
                    np.repeat(np.nan, out_table.number_of_rows()),
                    attr)
            elif mode == MASK:
                attr = {'info': 'Missing column'}
                out_table.set_column_from_array(
                    column_name,
                    np.ma.MaskedArray(
                        np.empty(
                            out_table.number_of_rows(),
                            dtype=dtypes.dtype(types[i])),
                        mask=True),
                    attr)
            elif mode == ZERO:
                attr = {'info': 'Missing column'}
                out_table.set_column_from_array(
                    column_name,
                    np.zeros(
                        out_table.number_of_rows(),
                        dtype=dtypes.dtype(types[i])),
                    attr)


class EnsureColumnsOperation(synode.Node):
    """
    Ensure the existence of columns in Tables by using an additional
    Table with the name of the columns that must exist. Select to get
    the result of the check as the form of an exception or as an added
    dummy signal. The type of the dummy signal is by default float with
    all elements set to NaN. Finally mask, can also be used. In that case,
    a type column also needs to be selected. Otherwise it is ignored.
    When mask is used, and ensured columns are missing, these will be created
    as fully masked arrays of the select types.
    """

    name = 'Ensure columns in Tables with Table'
    author = 'Daniel Hedendahl'
    version = '1.0'
    description = 'Ensure the existence of columns in Table.'
    nodeid = 'org.sysess.sympathy.data.table.ensuretablecolumns'
    tags = Tags(Tag.DataProcessing.TransformStructure)
    icon = 'ensure_column.svg'

    inputs = Ports([
        Port.Table('Selection', name='selection'),
        Port.Tables('Input Tables', name='tables')])
    outputs = Ports([Port.Tables('Output Table', name='tables')])

    parameters = synode.parameters()
    parameters.set_list(
        'columns', label='Column with column names',
        description=(
            'Name of column with names of the columns that must exist'),
        editor=synode.Util.combo_editor(edit=True, filter=True))

    parameters.set_list(
        'types', label='Column with column types',
        description=(
            'Name of column with types of the columns that must exist, '
            'only for use with "Masked Signal" reporting'),
        editor=synode.Util.combo_editor(edit=True, filter=True))

    parameters.set_list(
        'reporting', label='Action of missing columns:',
        plist=REPORTING, value=[0],
        description='Select action if columns are missing',
        editor=synode.Util.combo_editor())

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['columns'],
               node_context.input['selection'])

        adjust(node_context.parameters['types'],
               node_context.input['selection'])

    def execute(self, node_context):
        parameter_group = synode.parameters(node_context.parameters)
        names_param = parameter_group['columns']
        try:
            names_col = names_param.selected
        except KeyError:
            names_col = None
        types_param = parameter_group['types']

        input_files = node_context.input['tables']
        output_files = node_context.output['tables']
        for input_file in input_files:
            output_file = table.File()
            output_file.set_name(input_file.get_name())

            selection_table = node_context.input['selection']
            if names_col is not None:
                mode = parameter_group['reporting'].selected
                ensure_columns(input_file, output_file, selection_table,
                               names_param, types_param, mode)

            output_files.append(output_file)
