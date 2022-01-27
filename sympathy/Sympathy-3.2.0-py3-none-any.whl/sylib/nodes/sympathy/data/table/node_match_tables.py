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
from sympathy.api import table
from sympathy.api import node as synode
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags


class MatchTablesBase(object):
    author = 'Greger Cronquist'
    version = '1.0'
    icon = 'match_tables.svg'
    tags = Tags(Tag.DataProcessing.TransformStructure)

    parameters = synode.parameters()
    parameters.set_list(
        'fill', value=[0], label='Extend values',
        description=(
            'Specify the values to use if the input has to be extended.'),
        plist=['Last value', '0.0 or empty string', 'np.NaN or empty string'],
        editor=synode.Util.combo_editor().value())

    def _match_table(self, parameters, guide, input_table):
        guide_length = guide.number_of_rows()
        table_length = input_table.number_of_rows()

        if guide_length == 0:
            output_table = input_table[:0]
        else:
            if guide_length == table_length:
                output_table = input_table
            elif guide_length < table_length:
                output_table = input_table[:guide_length]
            elif guide_length > table_length:
                output_table = table.File()
                fill_table = table.File()
                fill_method = parameters['fill'].value[0]
                length_diff = guide_length - table_length

                for name in input_table.column_names():
                    dtype = input_table.column_type(name)

                    if fill_method == 0:
                        # Repeat last value:
                        last_value = input_table.get_column_to_array(
                            name, table_length - 1)

                        if np.ma.is_masked(last_value):
                            column = np.ma.masked_all(length_diff, dtype=dtype)
                        else:
                            column = np.full(length_diff, last_value,
                                             dtype=dtype)
                    elif fill_method == 1:
                        # Use zero-like fill values.
                        if dtype.kind in ['S', 'U']:
                            dtype = dtype.kind + '1'
                        else:
                            dtype = dtype
                        column = np.zeros(length_diff, dtype=dtype)
                    elif fill_method == 2:
                        # Use NaN or empty string.
                        if dtype.kind in ['S', 'U']:
                            dtype = dtype.kind + '1'
                            column = np.zeros(length_diff, dtype=dtype)
                        else:
                            column = np.full(length_diff, np.nan, dtype='f2')
                    else:
                        assert False, 'Unknown extension method.'

                    fill_table[name] = column

                output_table.vjoin([input_table, fill_table])
                output_table.set_attributes(input_table.get_attributes())
                output_table.set_name(input_table.get_name())
        return output_table


class MatchTwoTables(MatchTablesBase, synode.Node):
    """
    To compare the number of rows in two :ref:`Tables` and resize one of them,
    in order to have two Tables with equal numbers of rows, is the
    functionality of the nodes in the considered category. For example, this
    may be helpful if one would like to horisontal join two Tables with
    different number of rows, which is not possible according to the definition
    of a Table, see :ref:`Tables` and :ref:`HJoin Table`.

    In the procedure of the node, the Table connected to the upper of the two
    inputs is used as reference while the Table coming in through the lower
    port is the one that is going to be modified. The modification can either
    be a contraction or an extension of the Table depending if it is longer or
    shorter than the reference Table, respectively.

    The extension will be preformed according to one of the following
    strategies:

        - Use last value
        - Fill with zeroes (or empty strings/dates or similar)
        - Fill with NaNs (or None or similar)

    """

    name = 'Match Table lengths'
    nodeid = 'org.sysess.sympathy.data.table.matchtwotables'
    description = ('Ensure that two Tables match (i.e. have the same number '
                   'of rows) by adding or removing rows in one of them.')
    inputs = Ports([
        Port.Table('Guide', name='guide'),
        Port.Table('Input Table', name='input')])
    outputs = Ports([Port.Table('Length matched Table', name='output')])

    def __init__(self, *args, **kwargs):
        super(MatchTwoTables, self).__init__(*args, **kwargs)

    def execute(self, node_context):
        output = self._match_table(node_context.parameters,
                                   node_context.input['guide'],
                                   node_context.input['input'])
        node_context.output['output'].update(output)


@node_helper.list_node_decorator(['guide', 'input'], ['output'])
class MatchTwoTablesMultiple(MatchTwoTables):
    name = 'Match Tables lengths'
    nodeid = 'org.sysess.sympathy.data.table.matchtwotablesmultiple'
