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
from sympathy.api import fx
from sympathy.api.nodeconfig import Port, Ports
from sylib.fx_selector import (FxSelector, FxSelectorList)
from sympathy.api.nodeconfig import Tag, Tags


DOCS = """
The F(x) nodes have a similar role as the :ref:`Calculator` node. But where
the :ref:`Calculator` node shines when the calculations are simple expressions,
the F(x) nodes are better suited for more advanced calculations since the code
may span multiple lines, include statements and may even be kept in a separate
python file. You can place this python file anywhere, but it might be a good
idea to keep it in the same folder as your workflow or in a subfolder to that
folder.

Defining a function
===================
The python function that should be called by the node needs to be decorated
with ``fx.decorator``. The function should also take exactly two positional
arguments representing the input and output ports respectively. It is
recommended to name the arguments ``arg`` and ``res``. These variables are of
the same type as the input on port2. Consult the :ref:`API<datatypeapis>` for
that type to figure out relevant operations.

The argument to ``fx.decorator`` is a list of types (as shown in port tooltips)
that you intend your script to support. When selecting functions from a file,
each function is only available if the port type matches one of its types.

Example::

    from sympathy.api import fx

    @fx.decorator(['table'])
    def my_calculation(arg, res):
        spam = arg['spam']

        # My advanced calculation:
        more_spam = spam + 1

        res['more spam'] = more_spam

A quick way to get the skeleton for a function is to use the function wizard
that is started by clicking *File->Wizards->New Function*.

Script without separate file
============================
For short scripts that are not intended to be shared between different nodes it
can convenient not having to create an external file.  To enable this
feature, the datasource port first needs to be deleted.  Once there is no
datasource port, the node will show a code editor when configured.

The format is the same, the only exception is that all calculations (matching
input type) will be executed.

Debugging your functions
========================
When the functions are in a separate file they can be debugged by following the
normal process for debugging nodes. See :ref:`general_debug` for instructions.

List behavior
=============
The same function can be used with both :ref:`F(x)` and :ref:`F(x) List` nodes.
For example a function specified to run for type 'table' can be used with an
F(x) node connected to a single table or with an F(x) List node connected to a
list of tables. In the latter case the function will be executed once per item
in the list.

Configuration
=============
When *Copy input* is disabled (the default) the output table will be empty
when the functions are run.

When the *Copy input* setting is enabled the entire input table will get
copied to the output before running the functions in the file. This is useful
when your functions should only add a few columns to a data table, but in this
case you must make sure that the output has the same number of rows as the
input.

Alternative function definition
===============================
Another syntax for writing a "function" is to define a class which inherits
from ``fx.Fx``. The ``fx.Fx`` class provides access to the input and output
with ``self.arg`` and ``self.res`` respectively. These variables are of the
same type as the input on port2. The field ``arg_types`` should contain the
list of types that you intend your script to support.

Example::

    from sympathy.api import fx

    class MyCalculation(fx.Fx):
        arg_types = ['table']

        def execute(self):
            spam = self.arg['spam']

            # My advanced calculation:
            more_spam = spam + 1

            self.res['more spam'] = more_spam

This syntax is available mostly for backwards compatibility. For new functions
it is recommended to use the syntax with decorated functions.
"""

def _base_params():
    parameters = synode.parameters()
    editor = synode.Util.multilist_editor()
    parameters.set_boolean(
        'copy_input', value=False, label='Copy input',
        description=('If enabled the incoming data will be copied to the '
                     'output before running the nodes.'))
    parameters.set_list(
        'selected_functions', value=[], label='Select functions',
        description=('Choose one or many of the listed functions to apply to '
                     'the content of the incoming item.'), editor=editor)
    parameters.set_string(
        'code',
        label='Python code',
        description='Python code block, input is called arg, output res.',
        value="""from sympathy.api import fx

@fx.decorator(['<a>'])
def function(arg, res):
    raise NotImplementedError('Replace with your function')
""",
        editor=synode.Util.code_editor().value())
    return parameters


class Fx(synode.Node):
    __doc__ = DOCS

    name = 'F(x)'
    description = 'Apply arbitrary python function(s) to data.'
    nodeid = 'org.sysess.sympathy.data.fx'
    author = 'Erik der Hagopian'
    version = '1.0'
    icon = 'fx.svg'
    parameters = _base_params()
    tags = Tags(Tag.DataProcessing.Calculate)
    related = ['org.sysess.sympathy.data.generic.fxlist']

    inputs = Ports([
        Port.Custom(
            'datasource',
            'Path to Python file with scripted functions.',
            name='port1',
            n=(0, 1, 1)),
        Port.Custom(
            '<a>',
            'Item with data to apply functions on',
            name='port2')])
    outputs = Ports([
        Port.Custom(
            '<a>',
            'Item with the results from the applied functions',
            name='port3')])

    _cls = fx.Fx

    def __init__(self, *args, **kwargs):
        super(Fx, self).__init__(*args, **kwargs)
        self._base = FxSelector()

    def adjust_parameters(self, node_context):
        return self._base.adjust_parameters(node_context)

    def exec_parameter_view(self, node_context):
        return self._base.exec_parameter_view(node_context)

    def execute(self, node_context):
        self._base.execute(node_context, self.set_progress)


class FxList(synode.Node):
    __doc__ = DOCS

    name = 'F(x) List'
    description = 'Apply arbitrary python function(s) to each item of a List.'
    author = 'Erik der Hagopian'
    version = '1.0'
    icon = 'fx.svg'
    nodeid = 'org.sysess.sympathy.data.generic.fxlist'
    parameters = _base_params()
    tags = Tags(Tag.DataProcessing.Calculate)
    related = ['org.sysess.sympathy.data.fx']

    inputs = Ports([
        Port.Custom(
            'datasource',
            'Path to Python file with scripted functions.',
            name='port1',
            n=(0, 1, 1)),
        Port.Custom(
            '[<a>]',
            'List with data to apply functions on',
            name='port2')])
    outputs = Ports([
        Port.Custom(
            '[<a>]',
            'List with function(s) applied',
            name='port3')])

    _cls = fx.Fx

    def __init__(self, *args, **kwargs):
        super(FxList, self).__init__(*args, **kwargs)
        self._base = FxSelectorList()

    def exec_parameter_view(self, node_context):
        return self._base.exec_parameter_view(node_context)

    def adjust_parameters(self, node_context):
        return self._base.adjust_parameters(node_context)

    def execute(self, node_context):
        self._base.execute(node_context, self.set_progress)
