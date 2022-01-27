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
import numpy as np
from sympathy.api import node as synode
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Tag, Tags, adjust, Port, Ports
from sympathy.api import table


_method_extended, _method_legacy = _methods = ['Extended', 'Legacy']


def set_method(parameters, value):
    parameters.set_string(
        'method', value=value, label='Method',
        editor=synode.editors.combo_editor(options=_methods),
        description=(
            'Legacy: lacks support for time types and missing values are '
            'treated as NaN.\n'
            'Extended: supports time types and missing values are treated '
            'as separate a value.'))


class UniqueTable(synode.Node):
    """
    The Table in the output will have no more rows than the incoming Table.
    """
    name = 'Unique Table'
    nodeid = 'org.sysess.sympathy.data.table.uniquetable'
    author = 'Greger Cronquist'
    description = ('For each unique value in selected columns only keep the '
                   'first row with that value. When multiple columns are '
                   'selected, unique combinations of values are considered.')
    icon = 'unique_table.svg'
    version = '1.0'
    inputs = Ports([Port.Table('Input', 'Input')])
    outputs = Ports([Port.Table('Output', 'Output')])
    tags = Tags(Tag.DataProcessing.Select)
    parameters = synode.parameters()

    parameters.set_list(
        'column', label='Columns to filter by',
        description='Columns to use as uniqueness filter.',
        editor=synode.Util.multilist_editor(edit=True))

    set_method(parameters, _method_extended)

    def update_parameters(self, parameters):
        if 'method' not in parameters:
            set_method(parameters, _method_legacy)

    def adjust_parameters(self, ctx):
        adjust(ctx.parameters['column'], ctx.input['Input'])

    def execute(self, ctx):
        in_table = ctx.input['Input']
        out_table = ctx.output['Output']
        current_selected = ctx.parameters['column'].selected_names(
            in_table.names())
        if not (in_table.number_of_rows() and current_selected):
            out_table.update(in_table)
            return

        method = ctx.parameters['method'].value
        if method not in _methods:
            method = _method_extended

        if method == _method_legacy:

            df = in_table.to_dataframe()
            df2 = df.drop_duplicates(current_selected)
            sliced_table = table.File.from_dataframe(df2)
        # elif method == _method_extended:
        #     # Alternative implementation using pandas.
        #     # Might be faster, unclear exactly how it will behave in
        #     # corner cases.
        #     df = in_table.to_dataframe()
        #     index = df.duplicated(current_selected).to_numpy()
        #     sliced_table = in_table[~index]
        elif method == _method_extended:
            column_names = in_table.column_names()
            column_indices = [i for i, n in enumerate(column_names)
                              if n in current_selected]
            selected_table = in_table[:, column_indices]
            unique_values = set()
            unique = object()
            index = np.zeros(in_table.number_of_rows(), dtype=bool)

            for i, row in enumerate(selected_table.to_rows()):
                row = tuple([unique if value != value else value
                             for value in row])
                index[i] = row not in unique_values
                unique_values.add(row)
            sliced_table = in_table[index]
        else:
            assert False, 'Unknown method'

        out_table.source(sliced_table)
        out_table.set_attributes(in_table.get_attributes())
        out_table.set_name(in_table.get_name())


@node_helper.list_node_decorator([0], [0])
class UniqueTables(UniqueTable):
    name = 'Unique Tables'
    nodeid = 'org.sysess.sympathy.data.table.uniquetables'
