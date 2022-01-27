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
from sympathy.api import node as synode

from sympathy.api import node_helper
from sympathy.api.exceptions import sywarn
from sympathy.api.nodeconfig import (Port, Ports, Tag, Tags,
                                     adjust)


class DropNaNTable(synode.Node):
    """Remove rows or columns with NaN (not a number) in them."""

    author = 'Greger Cronquist'
    description = 'Drop columns or rows with NaN values'
    name = 'Drop NaN Table'
    nodeid = 'org.sysess.sympathy.data.table.dropnantable'
    version = '1.0'
    icon = 'drop_nan.svg'
    tags = Tags(Tag.DataProcessing.Select)
    related = ['org.sysess.sympathy.data.table.dropnantable',
               'org.sysess.sympathy.data.table.dropnantables',
               'org.sysess.sympathy.table.dropmaskvalues',
               'org.sysess.sympathy.data.table.holdvaluetable']

    _opt_rows, _opt_cols = _opts = ['Rows with NaN', 'Columns with NaN']

    inputs = Ports([Port.Table('Input', name='Input')])
    outputs = Ports([Port.Table('Output', name='Output')])

    parameters = synode.parameters()
    parameters.set_list(
        'columns', label='Select columns', description='Select columns.',
        value=[], editor=synode.Editors.multilist_editor(edit=True))
    parameters['columns']._passthrough = True

    parameters.set_list(
        'direction', label='Drop',
        list=_opts,
        description='Select along which axis to drop values',
        editor=synode.Util.combo_editor())

    def adjust_parameters(self, ctx):
        adjust(ctx.parameters['columns'], ctx.input['Input'])

    def execute(self, ctx):

        def remove_rows(col, index):
            index = index.values
            return col[~index]

        def final_columns(all_columns, columns_to_remove):
            return [c for c in all_columns if c not in columns_to_remove]

        in_table = ctx.input['Input']
        out_table = ctx.output['Output']

        direction = self._opt_rows
        direction_names = ctx.parameters['direction'].value_names

        if direction_names:
            if direction_names[0] in self._opts:
                direction = direction_names[0]
            else:
                sywarn(f'Unknown drop axis "{direction_names[0]}"')
        else:
            sywarn('Fallback to old value for drop axis')

            if ctx.parameters['direction'].value[0] == 1:
                direction = self._opts_cols
            else:
                sywarn('Failed to find drop axis')

        columns = in_table.column_names()
        row_index = None
        columns_to_remove = set()

        for name in ctx.parameters['columns'].selected_names(columns):

            series = in_table.get_column_to_series(name)
            col_index = series.isna()

            if direction == self._opt_cols:
                if col_index.any():
                    columns_to_remove.add(name)

            elif direction == self._opt_rows:
                if row_index is None:
                    row_index = col_index
                else:
                    row_index = row_index | col_index

        has_rows_to_remove = False if row_index is None else row_index.any()

        if has_rows_to_remove:
            for name in final_columns(columns, columns_to_remove):
                out_table[name] = remove_rows(in_table[name], row_index)
            out_table.set_attributes(in_table.get_attributes())
            out_table.name = in_table.name

        elif columns_to_remove:
            for name in final_columns(columns, columns_to_remove):
                out_table.update_column(name, in_table, name)
            out_table.set_table_attributes(in_table.get_table_attributes())
            out_table.name = in_table.name
        else:
            out_table.source(in_table)


@node_helper.list_node_decorator(['Input'], ['Output'])
class DropNaNTables(DropNaNTable):
    name = 'Drop NaN Tables'
    nodeid = 'org.sysess.sympathy.data.table.dropnantables'
