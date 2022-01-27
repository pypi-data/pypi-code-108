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
from collections import OrderedDict
import sys
import json

from sympathy.platform import types
from sympathy.api import table
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api import exceptions

from sylib.calculator import calculator_model as models
from sylib.calculator import calculator_gui
import sylib.calculator.plugins

FAILURE_STRATEGIES = OrderedDict([('Exception', 0), ('Skip calculation', 1)])

GENERIC_DOC = """
The calculations are written as Python code and can consist of simple
arithmetic calculations, Python function calls, or calls to functions defined
in plugins. The result of each calculation is written to a column in the output
table.


Configuration gui
=================
You declare each calculation by typing a name in the text line labeled *Signal
name* and entering the calculation in the textfield labeled *Calculation*. You
can use any of the signals in the list *Signal names* in your calculation.

To use a signal from an incoming table type simply drag-and-drop the signal
name from the list of available signals to the calculation field.
To use a signal from the incoming generic data use ``arg`` in a way that fits the
data format as can be seen in the examples below.

To add a function, drag-and-drop it from the *Avaliable functions* tree
structure. Note that any signal that you reference in the calculation must
exist in all incoming data structures.

To add a new calculation, press the *New* button and the *Calculation* field as
well as *Signal name* will be cleared. If you want to edit a calculation
simply click on the calculation in the *List of calculations*. The signal name
will then appear under *Signal name* and the calculation will appear in the
*Calculation* field. The calculation will be updated in the *Calculation*
field, *List of calculations* and preview simultaneously. To remove a
calculation, mark a calculation in *List of calculations* and press the
*Remove* button.

If something goes wrong when you define the calculations you will get an error
or warning message in the preview window and at the top of the window.
See :ref:`node_config_message_area` for details about the top message.

Some commonly used operators and functions can be found under the function tree
structure and can be added to a calculation by double-clicking or dragging the
function name to the calculation area. If you want more information about a
function, hover its name and its documentation will appear as a tooltip.


Calculations
============
A calculation in the calculator must be a python expression which evaluates to
either a numpy array, a list, or a scalar value (str/int/float etc.).

Things that can be used in expressions include literal values, operators,
function calls, list comprehensions, lambda function definitions, and
conditional expressions. Things that can not be used in expressions include if
statements, for/while loops, function definitions with the def keyword, class
definitions, and import statements.

The data on the input port is available under the name ``arg`` and any calculated
columns are accessable from the Table named ``res``.

Working with Table columns
--------------------------

.. note::
    This node does not support the ``${COLUMN_NAME}`` notation of the older
    Calculator Table nodes. Use ``arg['COLUMN_NAME']`` instead.

If the input is a Table you can get a column from it with
``arg['COLUMN_NAME']``. The column will be returned as a numpy array.

To get the number of rows in the Table use ``arg.number_of_rows()``. To get a
list of the column names, use ``arg.column_names()``. For more information see
the :ref:`Table API reference<tableapi>`.

Element wise calculations
-------------------------
Simple arithmetics and many functions can work directly on numpy arrays, but
for cases where this doesn't work you can use either list comprehensions or
``np.vectorize``.

One such case which comes up often is when working with arrays of strings. Say
for example that you have a Table with a column (*paths*) of file paths and
want to get the path to the containing directory for each file. This is easy to
do with a list comprehension::

    [os.path.dirname(p) for p in arg['paths']]

or with ``np.vectorize``::

    np.vectorize(os.path.dirname, otypes=[str])(arg['paths'])

The ``otypes`` argument declares that the output should be of string type and
is needed to allow the calculation to be performed even if ``arg['paths']`` is
empty (i.e. if the input table has no rows).

Generic input
-------------
The Calculator nodes can perform calculations on any given input. Any type can
by used as input and it is accessed by the keyword *arg*. The API of the
incoming :ref:`data type<datatypeapis>` can be used in the calculator.

Some examples::

    - Table         - Columns are accessed as ``arg['signal1']``
    - List of Table - Columns are accessed as ``arg[0]['signal1']``
    - ADAF          - Time series are accessed as ``arg.sys['system0']['raster0']['signal0'].y``
    - Tuple         - Elements are accessed as ``arg[0]``

Some useful numpy functions
---------------------------
Numpy is available under the name ``np`` in all calculations. A few numpy
functions that are very useful in the calculator node are ``np.where``,
``np.flat_nonzero``, and ``np.vectorize``. See their respective documentations
for more information.

Avoiding errors if Table column is missing
------------------------------------------
If a calculation uses a column from the incoming Table (e.g.
``arg['COLUMN_NAME']``) and that column doesn't exist in the input Table the
calculator node will fail with an error. The simplest way to fix this would
be to change the error handling option to "Skip calculation" which would simply
ignore the calculation if there is any error while running the calculation. The
downside to this is that the output will also sometimes have the calculated
column and sometimes not.

Another way around this can be to iterate through a table's columns, like so::

    [arg[name][0] for name in arg.column_names()]

Or always use for example the first column in the Table::

    arg[arg.column_names()[0]]

Another way is to use conditional expressions. Here is an example of a
calculation which tries to copy a column, but if it doesn't exist it will
instead create a column of zeros::

    arg['My column'] if 'My column' in arg else np.zeros(arg.number_of_rows())


Calculation Attributes
======================
Each calculated column can have any number of custom associated attributes.
These are, at least for now, much more limited than calculations. Each
attribute has a string for its name and another string for its value and both
are treated as text and are not evaluated as python expressions. The use for
these is being able to associate metadata to output columns created by
calculations. For example:

+------+-------+
| Name | Value |
+======+=======+
| unit |  ms   |
+------+-------+

will attach milliseconds for unit to a specific column.


Output
======
Each column of the output will have a *calculation* attribute with a string
representation of the calculation used to create that column.

In the configuration, there is an option on how to handle exceptions
(Action on calculation failure) produced by the node, for example missing
signals or erroneous calculations.

In the list of calculations there is also the option to disable individual
calculations, i.e., exclude them from the output. This makes it possible to
make intermediary calculations that are not actually included in the output
from the node. Such intermediary calculations don't even need to have the same
lengths as the the rest of the calculations.
"""


def add_base_parameters(parameters):
    parameters.set_list(
        'calc_list', label='List of calculations',
        description='List of calculations.',
        _old_list_storage=True)

    parameters.set_string(
        'calc_attrs_dict',
        value='[]',
        description='Calculation attributes as json dict-list-string!')

    parameters.set_boolean(
        'copy_input', value=False, label='Copy input',
        description=('If enabled the incoming data will be copied to the '
                     'output before running the calculations. This requires '
                     'that the results will all have the same length. An '
                     'exception will be raised if the lengths of the outgoing '
                     'results differ.'))
    parameters.set_list(
        'fail_strategy', label='Action on calculation failure',
        list=FAILURE_STRATEGIES.keys(), value=[0],
        description='Decide how a failed calculation should be handled',
        editor=synode.Util.combo_editor())


def model_output_writer(input_files, calc_lines, output_files,
                        exception_handling, copy_input=False, attributes=None):

    attributes = attributes or {}
    calc_nodes = models.parse_nodes(calc_lines)
    graph = models.CalculationGraph(calc_nodes)
    calculation_order = graph.topological_sort(calc_nodes)
    calc_map = OrderedDict()

    for calc in graph.nodes():
        calc_map[calc.name] = calc

    calc_outputs = [calc for calc in calc_nodes
                    if calc.enabled and not calc.is_empty]
    calc_indices = dict(zip(calc_nodes, range(len(calc_nodes))))

    skip = exception_handling != FAILURE_STRATEGIES['Exception']

    for i, input_file in enumerate(input_files):

        try:
            output_file = output_files.create()
            if copy_input:
                if isinstance(input_file, table.File):
                    output_file.source(input_file)

            res = models.ResTable()
            models.execute_calcs(
                graph, calculation_order, input_file, res, skip)

            for calc in calc_outputs:
                name = calc.name

                if name in res:
                    output = res[name]
                    output_file.set_column_from_array(name, output)
                    col_attributes = attributes.get(calc_indices[calc], [])
                    col_attributes.append(
                        ('calculation',
                         models.display_calculation(str(calc))))

                    output_file.set_column_attributes(
                        models.display_calculation(name), dict(col_attributes))

            output_files.append(output_file)

        except Exception:
            if exception_handling == FAILURE_STRATEGIES['Exception']:
                if isinstance(input_files, list):
                    raise
                else:
                    raise exceptions.SyListIndexError(i, sys.exc_info())
            else:
                exceptions.sywarn('Error occurred in table number ' + str(i))


class SuperCalculator(synode.Node):
    author = ('Greger Cronquist, Magnus Sandén, Sara Gustafzelius & '
              'Benedikt Ziegler')
    description = 'Create columns by evaluating python calculations.'
    version = '3.0'
    icon = 'calculator.svg'
    tags = Tags(Tag.DataProcessing.Calculate)
    plugins = (sylib.calculator.plugins.ICalcPlugin, )

    parameters = synode.parameters()
    add_base_parameters(parameters)

    def _exec_parameter_view(self, node_context, is_single_input):
        input_group = node_context.input.group('port0')
        input_data = table.File()
        if input_group:
            input_data = input_group[0]

        show_copy_input = False

        for port in node_context.definition['ports']['inputs']:
            if port['name'] == 'port0':
                port_type = types.from_string(port['type'])
                if not is_single_input:
                    port_type = port_type[0]

                show_copy_input = types.match(
                    types.from_string(port_type, False),
                    types.from_string('table'))

        empty_input = False
        if not input_data.is_valid():
            empty_input = True
            if is_single_input:
                input_data = table.File()
            else:
                input_data = table.FileList()
        return calculator_gui.CalculatorWidget(
            input_data, node_context.parameters,
            preview_calculator=models.python_calculator,
            multiple_input=not is_single_input,
            empty_input=empty_input,
            show_copy_input=show_copy_input)

    @staticmethod
    def _update_calc(parameters, infiles, outfiles):
        calc_list = parameters['calc_list'].list
        exception_handling = parameters['fail_strategy'].value[0]
        copy_input = parameters['copy_input'].value

        calc_attrs_dict = dict(json.loads(
            parameters['calc_attrs_dict'].value or '[]'))

        model_output_writer(infiles, calc_list, outfiles, exception_handling,
                            copy_input, calc_attrs_dict)


class CalculatorGenericNode(SuperCalculator):
    __doc__ = GENERIC_DOC
    name = 'Calculator'
    nodeid = 'org.sysess.sympathy.data.table.calculatorgeneric'
    related = ['org.sysess.sympathy.data.table.calculatorgenericlist']

    inputs = Ports([Port.Custom('<a>', 'Generic Input', name='port0',
                                n=(0, 1, 1))])
    outputs = Ports([Port.Table(
        'Table with results from the calculations.', name='port1')])

    def exec_parameter_view(self, node_context):
        return self._exec_parameter_view(node_context, True)

    def execute(self, node_context):
        input_group = node_context.input.group('port0')
        input_data = table.File()
        if input_group:
            input_data = input_group[0]

        out_list = table.FileList()
        self._update_calc(node_context.parameters,
                          [input_data], out_list)
        node_context.output['port1'].source(out_list[0])


class CalculatorGenericListNode(SuperCalculator):
    __doc__ = GENERIC_DOC
    name = 'Calculator List'
    nodeid = 'org.sysess.sympathy.data.table.calculatorgenericlist'
    related = ['org.sysess.sympathy.data.table.calculatorgeneric']

    inputs = Ports([Port.Custom('[<a>]', 'Generic Input', name='port0')])
    outputs = Ports([Port.Tables(
        'Tables with results from the calculations.', name='port1')])

    def exec_parameter_view(self, node_context):
        return self._exec_parameter_view(node_context, False)

    def execute(self, node_context):
        self._update_calc(node_context.parameters, node_context.input['port0'],
                          node_context.output['port1'])
