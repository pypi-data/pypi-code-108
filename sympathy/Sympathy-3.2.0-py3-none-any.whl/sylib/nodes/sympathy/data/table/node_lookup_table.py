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
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api import table

from sylib.lookup_gui import LookupWidget
from sylib.lookup import apply_index_datacolumn_and_write_to_file


DOCS = """
The lookup node takes rows from a lookup table (upper port) in the order
defined by a control table (lower port).

In the gui you can define pairs of columns, one from the control table and one
from the lookup table. During the execution of the node, it will step through
the rows of the selected control columns and try to find a match among the rows
in the corresponding columns in the lookup table. If there is a match, that
entire row in the lookup table is copied to the output.

Since there is one row in the output for each row in the control table, the
output from this node should always be possible to :ref:`hjoin <Hjoin Table>`
with the control table. This is often a useful first step for using the output
from this node.

Rows not found lookup table
===========================
The behavior when some rows in the control table can not be found in the lookup
table depends on the state of the two checkboxes below the table with column
pairs: *Require perfect match* and *Use zero-like value instead of
masks*. By default both boxes are unchecked which means that any rows that can
not be found in the lookup table are masked in the output.

If *Use zero-like values instead of masks* is checked, unmatched rows are
instead assigned appropriate zero-like values depending on the data type
of the columns.

Examples of zero-like values for different column types:

    :float: 0.0
    :integer: 0
    :bool: False
    :text: ""

This setting is mostly for backwards compatibility and is
therefore not recommended for new flows.

If *Require perfect match* is checked an exception will be raised if row can
not be matched. So with this setting all rows in the control table must be
matched if the node is to execute successfully. This can be useful to avoid
trickier errors in later nodes.

Copying input columns
=====================
By default only the data from the lookup table is written to the output, but if
*Copy input* is checked, the columns from the control table are also copied.
If any columns have the same name in both tables, the column from the control
table is used.

Using an event column
=====================
In the configuration GUI you can also choose to treat one of the defined column
pairs as event columns. The event columns will typically consist of dates or
times. But can actually be of any sortable data type. Only one event column
pair can be chosen at a time.

When an event column pair has been defined, the matching is performed in a
slightly different way. Each row in this control table will now be matched with
the last preceding event in the lookup table which also matches in all other
column pairs. This means that an entry in the event column of the control table
doesn't have to have an exact match in the lookup table for there to be a
match. It is enough that there is any preceding event.

"""


def _add_nomasks_parameter(parameters):
    parameters.set_boolean(
        'nomasks', value=False,
        label='Use zero-like values instead of masks',
        description='When unchecked rows that can not be matched '
                    'will be masked. When checked such rows are instead '
                    'assigned 0, 0.0, False, "", etc. depending on the type '
                    'of the value column.')


def _add_copy_input_parameter(parameters):
    parameters.set_boolean(
        'copy_input', value=False,
        label='Copy input',
        description='Copy the columns from the control table to the output '
                    'giving them priority over columns from lookup table in '
                    'case of same column names.'
    )


class LookupDefinition:
    description = ("Take rows from the lookup table in the "
                   "order defined by the control table.")
    author = "Alexander Busck & Magnus Sanden"
    version = "1.0"
    icon = "lookup.svg"

    parameters = synode.parameters()
    parameters.set_list(
        'template_columns', label='Lookup columns', value=[],
        description=('A list storing columns in the lookup table '
                     'used for matching. At each index there is '
                     'a corresponding entry in lookupee_columns.'),
        _old_list_storage=True)
    parameters.set_list(
        'lookupee_columns', label='Control columns', value=[],
        description=('A list storing columns in the control table '
                     'used for matching. At each index there is '
                     'a corresponding entry in template_columns.'),
        _old_list_storage=True)
    parameters.set_integer(
        'event_column', label='Event column', value=-1,
        description='Stores the index of the column pair which is '
                    'to be matched as events, or -1 if no such column '
                    'pair has been selected.')
    parameters.set_boolean(
        'perfect_match', value=False, label='Require perfect match',
        description=("If checked, each row in the control table has "
                     "to match exactly one row in the lookup table."))
    _add_nomasks_parameter(parameters)
    _add_copy_input_parameter(parameters)

    def update_parameters(self, old_params):
        if 'nomasks' not in old_params:
            _add_nomasks_parameter(old_params)
            old_params['nomasks'].value = True
        if 'copy_input' not in old_params:
            _add_copy_input_parameter(old_params)


def get_files(node_context):
    try:
        lookup_file = node_context.input['lookup']
    except KeyError:
        lookup_file = None
    try:
        control_file = node_context.input['lookupee']
    except KeyError:
        control_file = None
    try:
        out_file = node_context.output['out']
    except KeyError:
        out_file = None
    return lookup_file, control_file, out_file


class LookupTableNode(LookupDefinition, synode.Node):
    __doc__ = DOCS

    name = "Lookup Table"
    nodeid = "org.sysess.sympathy.data.table.lookuptable"
    tags = Tags(Tag.DataProcessing.TransformStructure)

    inputs = Ports([
        Port.Table("Lookup table", name="lookup"),
        Port.Table("Control table", name="lookupee")])
    outputs = Ports([
        Port.Table("Result table", name="out")])

    def exec_parameter_view(self, node_context):
        lookup_file, control_file, _ = get_files(node_context)
        return LookupWidget(
            node_context.parameters, lookup_file, control_file)

    def execute(self, node_context):
        lookup_file, control_file, out_file = get_files(node_context)

        tmp_file = table.File()
        apply_index_datacolumn_and_write_to_file(
            node_context.parameters, lookup_file, control_file, tmp_file)
        tmp_file.set_attributes(lookup_file.get_attributes())

        if node_context.parameters['copy_input'].value:
            out_file.source(control_file)
            for col_name in tmp_file.column_names():
                if col_name not in out_file:
                    out_file.update_column(col_name, tmp_file)
        else:
            out_file.source(tmp_file)


@node_helper.list_node_decorator(['lookupee'], ['out'])
class LookupTablesNode(LookupTableNode):
    name = "Lookup Tables"
    nodeid = "org.sysess.sympathy.data.table.lookuptables"
