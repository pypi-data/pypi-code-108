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
"""
Convert Text(s) into Table(s). The rows of the incoming Text will be rows in
the resulting output Table.
"""
import numpy as np
from sympathy.api import node as synode
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust

NAME = 'Text'


class Text2Table(synode.Node):
    parameters = synode.parameters()
    parameters.set_string(
        'name',
        label='Output name',
        value=NAME,
        description='Specify name for output column. Must be a legal name.')

    name = 'Text to Table'
    description = 'Convert Text of Table.'
    inputs = Ports([Port.Text('Input Text', name='text')])
    outputs = Ports([Port.Table('Table with input Text', name='table')])

    author = 'Erik der Hagopian'
    nodeid = 'org.sysess.sympathy.data.text.text2table'
    version = '0.1'
    icon = 'text2table.svg'
    tags = Tags(Tag.DataProcessing.Convert)

    def execute(self, node_context):
        name = node_context.parameters['name'].value
        table = node_context.output[0]
        text = node_context.input[0]
        table.set_column_from_array(
            name,
            np.array(text.get().splitlines()))


@node_helper.list_node_decorator(
    {'text': {'name': 'texts'}}, {'table': {'name': 'tables'}})
class Texts2Tables(Text2Table):
    name = 'Texts to Tables'
    nodeid = 'org.sysess.sympathy.data.text.texts2tables'


class Table2Text(synode.Node):
    name = 'Table to Text'
    description = 'Convert Table to Text'
    author = 'Magnus Sandén'
    nodeid = 'org.sysess.sympathy.data.text.table2text'
    version = '0.1'
    icon = 'table2text.svg'
    tags = Tags(Tag.DataProcessing.Convert)

    parameters = synode.parameters()
    parameters.set_string(
        'name', label='Column name',
        description='Specify name for input column.',
        editor=synode.editors.combo_editor(options=[], edit=True))

    inputs = Ports([Port.Table('Table with input Text', name='table')])
    outputs = Ports([Port.Text('Output Text', name='text')])

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['name'], node_context.input[0])

    def execute(self, node_context):
        table = node_context.input[0]
        text = node_context.output[0]
        column = table._require_column(node_context.parameters['name'], 'U')
        text.set("".join(column))


@node_helper.list_node_decorator(
    {'table': {'name': 'tables'}}, {'text': {'name': 'texts'}})
class Tables2Texts(Table2Text):
    name = 'Tables to Texts'
    nodeid = 'org.sysess.sympathy.data.text.tables2texts'
