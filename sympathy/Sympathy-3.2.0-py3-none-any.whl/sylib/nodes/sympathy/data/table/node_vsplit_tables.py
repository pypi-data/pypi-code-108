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
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust, join_doc
from sympathy.api.exceptions import SyDataError

COMMON_DOCS = """
If "One table for each row" is used each row in the input will result in a
table with one row in the output list. So if the input table had N rows the
output list will contain N Table items, each with only a single row.

If "One table for each row" is unchecked and an index column is specified the
split will instead be performed according to the values in this column. All
rows with the same value in the index column will be grouped together into one
output table.

An example of an index column can be created by :ref:`VJoin Table`. With this
option enabled rows that originate from the same incoming Table will be given
the same index, making it easy to "undo" a vjoin operation with a vsplit node.

If index column is missing
--------------------------
If an index column has been specified, but that column is missing in an input
table, "Action on missing Index" will control the behavior.

If the selected action is "Error", the node will give an error if the selected
index column is missing. This is very useful for finding cases where the index
column wasn't intended to be missing.

If the selected action is "Single table, one table for all rows", the node will
fall back to simply forwarding the entire input table to the output list is the
index column is missing.

If the selected action is "Multiple tables, one for each row", the node will
fall back to splitting the input as if "One table for each row was selected."

Remove complement columns
-------------------------
Yet another available option in the node is to remove columns that after the
split contain only NaNs or empty strings. This is called "Remove complement
columns" in the configuration GUI and is (loosly speaking) the reversal of the
creation of complements for missing columns preformed by the :ref:`VJoin Table`
node. After using this option, the output Tables can have different numbers of
columns.

Splitting on multiple columns
-----------------------------
In the configuration gui you can only select a single column to split on, but
this limitation is easy to work around. To split on unique combinations of two
columns, simply put one :ref:`org.sysess.sympathy.data.table.vsplittablenode`
and one :ref:`org.sysess.sympathy.data.table.vsplittablenodes` in series,
configured to split on one of the columns each. To split on unique
combinations of values in even more columns, just add more
:ref:`org.sysess.sympathy.data.table.vsplittablenodes` nodes. See example flow.

"""

_missing_options = [
    'Multiple tables, one for each row',
    'Single table, one table for all rows',
    'Error']


def _set_missing_index(parameters):
    parameters.set_string(
        'missing_index',
        label='Action on missing index',
        value=_missing_options[0],
        description=(
            'Choose how to handle tables where the selected index column '
            ' is missing.'),
        editor=synode.Util.combo_editor(options=_missing_options))


def _missing_action(parameters):
    index = parameters['missing_index'].value
    action = False
    if 'Multi' in index:
        action = 'm'
    elif 'Single' in index:
        action = 's'
    else:
        action = 'e'
    return action


class VSplitBase(synode.Node):
    parameters = synode.parameters()
    parameters.set_boolean(
        'no_index',
        label='One table for each row',
        value=True,
        description=(
            'If checked, each row in the input table will be put in a '
            'different table in the output. If unchecked, you need to specify '
            'an index column which will then be used to determine what rows '
            'go in which table.'))

    parameters.set_string(
        'input_index',
        label='Index column',
        value='',
        description=(
            'Choose name for index column. All rows with the same value in '
            'this column will end up in the same output table.'),
        editor=synode.Util.combo_editor(edit=True))

    _set_missing_index(parameters)

    parameters.set_boolean(
        'remove_fill', value=False, label='Remove complement columns',
        description=('After splitting, remove columns that contain only '
                     'NaN or empty strings.'))
    tags = Tags(Tag.DataProcessing.TransformStructure)

    controllers = synode.controller(
        when=synode.field('no_index', 'checked'),
        action=(synode.field('input_index', 'disabled'),
                synode.field('missing_index', 'disabled')))

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['input_index'],
               node_context.input[0])

    def update_parameters(self, old_params):
        # Add no_index checkbox with backward compatible value.

        if 'no_index' not in old_params:
            old_params['no_index'] = self.parameters['no_index']
            old_params['no_index'].value = (
                not old_params['input_index'].value)

        if 'missing_index' not in old_params:
            _set_missing_index(old_params)

        # Update editor for input index. Old version of node had a simple
        # lineedit (editor=None).
        if old_params['input_index'].editor is None:
            old_params['input_index'].editor = (
                synode.Util.combo_editor(edit=True))

        if 'require_index' in old_params:
            if old_params['require_index'].value is True:
                old_params['missing_index'].value = 'Error'
            del old_params['require_index']


class VSplitTableNode(VSplitBase):
    __doc__ = COMMON_DOCS

    author = "Alexander Busck"
    version = '1.0'
    icon = 'vsplit_table.svg'

    name = 'VSplit Table'
    description = ('Split Table row wise (vertically), '
                   'grouping unique values of an index column.')
    nodeid = 'org.sysess.sympathy.data.table.vsplittablenode'
    related = ['org.sysess.sympathy.data.table.vsplittablenodes',
               'org.sysess.sympathy.data.table.vjointablenode']

    inputs = Ports([Port.Table('Input Table', name='port1')])
    outputs = Ports([Port.Tables('Split Tables', name='port1')])

    def execute(self, node_context):
        input_table = node_context.input['port1']
        output_tables = node_context.output['port1']
        input_index = node_context.parameters['input_index'].value
        missing_action = _missing_action(node_context.parameters)
        no_index = node_context.parameters['no_index'].value

        if no_index:
            input_index = None
            missing_action = 'm'

        if input_index not in input_table:
            if missing_action == 'm':
                input_index = None
            elif missing_action == 's':
                input_index = np.zeros(input_table.number_of_rows(), dtype=int)
            else:
                raise SyDataError(
                    'Selected and required input index is missing.')

        input_table.vsplit(
            output_tables,
            input_index,
            node_context.parameters['remove_fill'].value)


class VSplitTablesNode(VSplitBase):
    __doc__ = join_doc(COMMON_DOCS, """
    Flattened output
    ----------------
    This node flattens the output into a single list of Tables which can be
    convenient, but it makes it difficult to know the origin of a specific
    table in the output. If this is important to your use case, you can also
    consider using :ref:`org.sysess.sympathy.data.table.vsplittablenode`
    inside a Lambda and Map that over the input resulting in the type
    ``[[table]]``.

    """)

    author = "Alexander Busck"
    version = '1.0'
    icon = 'vsplit_table.svg'

    name = 'VSplit Tables'
    description = ('Split Tables row wise (vertically), '
                   'grouping unique values of an index column.')
    nodeid = 'org.sysess.sympathy.data.table.vsplittablenodes'
    related = ['org.sysess.sympathy.data.table.vsplittablenode',
               'org.sysess.sympathy.data.table.vjointablenode']

    inputs = Ports([Port.Tables('Input Tables', name='port1')])
    outputs = Ports([Port.Tables('Split Tables', name='port1')])

    def execute(self, node_context):
        input_list = node_context.input['port1']
        output_tables = node_context.output['port1']
        input_index = node_context.parameters['input_index'].value
        number_of_files = len(input_list)
        missing_action = _missing_action(node_context.parameters)
        no_index = node_context.parameters['no_index'].value

        if no_index:
            input_index = None
            missing_action = 'm'

        for i, table in enumerate(input_list):
            index = input_index
            if input_index not in table:
                if missing_action == 'm':
                    index = None
                elif missing_action == 's':
                    index = np.empty(table.number_of_rows(), dtype=int)
                    index.fill(i)
                else:
                    raise SyDataError(
                        'Selected and required input index is missing.')

            table.vsplit(
                output_tables,
                index,
                node_context.parameters['remove_fill'].value)

            self.set_progress(100.0 * (i + 1) / number_of_files)
