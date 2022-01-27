# This file is part of Sympathy for Data.
# Copyright (c) 2018, Combine Control Systems AB
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

from sympathy.api import node as synode
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api.exceptions import SyDataError


class RenameDatasource(synode.Node):
    """
    Create Datasources with paths to data sources.
    """

    author = "Mathias Broxvall"
    version = '1.1'
    icon = 'datasource_rename.svg'
    tags = Tags(Tag.DataProcessing.TransformData)
    name = 'Rename datasource with Regex'
    description = ('Applies a regular expression to modify '
                   'the PATH of a datasource.')
    nodeid = 'org.sysess.sympathy.datasources.rename'

    inputs = Ports([Port.Datasource('Datasource input', name='input')])
    outputs = Ports([Port.Datasource('Datasource output', name='output')])

    parameters = synode.parameters()

    parameters = synode.parameters()
    parameters.set_string(
        'search', label='Search',
        description=(
            'Part of path to replace using a regular expression. '
            'Use "$" for end of name and "^" for the beginning.'))
    parameters.set_string(
        'replace', label='Replace',
        description=(
            'Text to replace the matched parts with. Use eg. "\\1" to '
            'substitute the first matched (paranthesis) group. '))

    def execute(self, node_context):
        search = node_context.parameters['search'].value
        replace = node_context.parameters['replace'].value

        input = node_context.input['input']
        output = node_context.output['output']

        path = input.decode_path()
        if path is None:
            raise SyDataError('Path must not be None.')
        typename = input.decode_type()
        path = re.sub(search, replace, path)
        output.encode({'path': path, 'type': typename})


@node_helper.list_node_decorator(input_keys=[0], output_keys=[0])
class RenameDatasources(RenameDatasource):
    name = 'Rename datasources with Regex'
    nodeid = 'org.sysess.sympathy.datasources.renames'
