# This file is part of Sympathy for Data.
# Copyright (c) 2016, Combine Control Systems AB
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
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api.exceptions import SyNodeError, sywarn
from sylib import util


ERROR_LEVEL = ['Error', 'Warning', 'Output']


class ConditionalError(synode.Node):
    """
    Raise an error if the supplied predicate function returns True.

    See https://docs.python.org/3/tutorial/controlflow.html#lambda-expressions
    for a description of lambda functions. Have a look at the :ref:`Data type
    APIs<datatypeapis>` to see what methods and attributes are available on the
    data type that you are working with.
    """

    name = 'Conditional error/warning'
    author = u'Magnus Sandén'
    version = '1.0'
    icon = ''
    description = "Raise an error if a predicate is True."
    nodeid = 'org.sysess.sympathy.data.table.conditionalerror'
    icon = 'error.svg'
    tags = Tags(Tag.Development.Test)

    inputs = Ports([Port.Custom('<a>', 'Input', name='in')])
    outputs = Ports([Port.Custom('<a>', 'Output', name='out')])

    parameters = synode.parameters()
    parameters.set_string(
        'predicate',
        label='Predicate function:',
        value='lambda arg: True',
        description='Error message is printed if this function returns True.',
        editor=synode.Util.code_editor())
    parameters.set_string(
        'error_msg',
        label='Error message:',
        value='Error!',
        description='Error message to display to the user.')
    parameters.set_list(
        'error_type',
        label='Severity:',
        list=ERROR_LEVEL,
        value=[0],
        description='The level "Error" stops flow execution.',
        editor=synode.Util.combo_editor())

    def execute(self, node_context):
        predicate_str = node_context.parameters['predicate'].value
        error_type = node_context.parameters['error_type'].selected
        error_msg = node_context.parameters['error_msg'].value
        in_table = node_context.input['in']
        out_table = node_context.output['out']

        # Evaluate predicate function
        if util.base_eval(predicate_str)(in_table):
            if error_type == 'Error':
                raise SyNodeError(error_msg)
            elif error_type == 'Warning':
                sywarn(error_msg)
            elif error_type == 'Output':
                print(error_msg)
            else:
                raise ValueError('Unknown error_type')

        # Output is equal to input
        out_table.source(in_table)
