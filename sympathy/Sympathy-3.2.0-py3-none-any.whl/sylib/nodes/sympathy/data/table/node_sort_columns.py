# This file is part of Sympathy for Data.
# Copyright (c) 2015, 2017 Combine Control Systems AB
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
import re
from sympathy.api import node
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags


def combined_key(string):
    """
    Alphanumeric key function.
    It computes the sorting key from string using the string and integer parts
    separately.
    """
    def to_int(string):
        try:
            return int(string)
        except ValueError:
            return string
    return [to_int(part) for part in re.split('([0-9]+)', string)]


class SortColumnsInTable(node.Node):
    """
    Sort the columns in incoming table alphabetically. Output table will have
    the same columns with the same data but ordered differently.
    """

    name = 'Sort columns in Table'
    author = 'Magnus Sandén'
    version = '1.0'
    icon = 'sort_table_cols.svg'
    description = "Sort the columns in incoming table alphabeticaly."
    nodeid = 'org.sysess.sympathy.data.table.sortcolumns'
    tags = Tags(Tag.DataProcessing.TransformStructure)

    inputs = Ports([
        Port.Table('Table with columns in unsorted order', name='input')])
    outputs = Ports([
        Port.Table('Table with columns in sorted order', name='output')])

    parameters = node.parameters()
    parameters.set_list(
        'sort_order', label='Sort order',
        list=['Ascending', 'Descending'], value=[0],
        description='Sort order',
        editor=node.Util.combo_editor())

    def execute(self, node_context):
        input_table = node_context.input['input']
        output_table = node_context.output['output']
        kwargs = {'reverse': node_context.parameters['sort_order'].selected ==
                  'Descending'}
        columns = sorted(
            input_table.column_names(), key=combined_key, **kwargs)

        for column in columns:
            output_table.set_column_from_array(
                column, input_table.get_column_to_array(column))
        output_table.set_attributes(input_table.get_attributes())
        output_table.set_name(input_table.get_name())
