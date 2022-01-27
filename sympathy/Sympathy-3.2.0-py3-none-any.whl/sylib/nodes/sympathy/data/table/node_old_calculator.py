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
The calculator node can apply calculations on each data column in a list.
The calculations are written as Python code and can consist of simple
arithmetic calculations, Python function calls, or calls to functions defined
in plugins.

Calculations
^^^^^^^^^^^^
You declare each calculation by typing a name in the text line labeled *Signal
name* and entering the calculation in the textfield labeled *Calculation*. You
can use any of the signals in the list *Signal names* in your calculation.

To use a signal from an incoming table type simply drag-and-drop the signal
name from the list of available signals to the calculation field.
To use a signal from the incoming generic data use *arg* in a way that fits the
data format as can be seen below:

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
*Remove* button. The result of your calculation is written to a column in an
outgoing table.

If something goes wrong when you define the calculations you will get an error
or warning message in the preview window and at the top of the window.

Some commonly used operators and functions can be found under the function tree
structure (labeled *Common functions*) and can be added to a calculation by
double-clicking or dragging the function name to the calculation area. If you
want more information about a function, hover its name and its documentation
will appear as a tooltip.

The signals that you access in the calculations are returned as numpy arrays,
the same as if you had called :meth:`get_column_to_array` from the
:ref:`tableapi`. This means that simple arithmetics and the functions from
numpy and pandas work out of the box. But if you want to apply some other
function which only works on a single element of the column you may need to use
Python list comprehensions. For (the contrived) example::

  filenames = np.array([value + value for value in signal])

where signal is a table column.

Output
^^^^^^
Each column of the output will have a *calculation* attribute with a string
representation of the calculation used to create that column.

In the configuration, there is an option on how to handle exceptions
(Action on calculation failure) produced by the node, for example missing
signals or erroneous calculations.

In the list of calculations there is also the option to disable individual
calculations, i.e., exclude them from the output. This makes it possible to
make intermediary calculations that does not have the same lengths as the
the calculations that are actually output by the node. This could for example
be useful for constants.

Compatibility
^^^^^^^^^^^^^
Under python 2 the calculations are evaluated with future imports ``division``
and ``unicode_literals`` activated. This means that in both python 2 and python
3 the calculation `1/2` will give 0.5 as result, and the calculation `'hello'`
will result in a unicode-aware text object (`unicode` in python 2 and `str` in
python 3). To get floor division use the operator ``//`` and to get a binary
string (`str` in python 2 and `bytes` in python 3) use the syntax ``b'hello'``.
"""
from collections import OrderedDict
import os
import tempfile
import sys
import re

from sympathy.api import table
from sympathy.api import node as synode
from sympathy.api.nodeconfig import (
    Port, Ports, Tag, Tags, settings, deprecated_node)
from sympathy.api import exceptions

from sylib.old_calculator import calculator_model as models
from sylib.old_calculator import calculator_gui
import sylib.calculator.plugins

FAILURE_STRATEGIES = OrderedDict([('Exception', 0), ('Skip calculation', 1)])
old_table_format = r'\${([^{}]+)}'
old_table_display = '${{{}}}'

TABLE_DOC = """
The Calculator nodes can perform calculation on Table(s). Accessing a column
can be done either by using the ${} notation (${signal}) or by the
:ref:`tableapi` (table.col('signal').data).

When the option *Put results in common outputs* is enabled (the default) each
input structure results in a single output table with all the new columns. This
means that all the calculated columns must be the same length. When disabled
each calculation instead generates a table with a single column. The length of
the outgoing list therefore depends on the number of incoming structures and
the number of operations that are applied to each structure. As an example, if
the incoming list consist of five tables and there are two calculations, the
number of tables in the outgoing list will be 5*2=10.

Note that the incoming columns don't propagate to the output table by default.
If the results of you calculations are of the same length as the input, and the
option *Put results in common outputs* is enabled you can use the node
:ref:`HJoin Tables` to add calculated results to the input table, or you can
simply use the option 'Copy input' to do this automatically.

Example calculations::

  New signal = ${Old signal} + 1
  area = ${width} * ${height}
  result = (${signal0} == 2) & ca.change_up(${signal1})
  index = np.arange(len(${some signal}))
  sine = np.sin(${angle})

The whole input table is available in the calculations as `table`. This allows
the entire :ref:`tableapi` to be used. For example you can get a list of a
table's column names::

  table_names = table.column_names()
"""


def add_same_length_res_parameter(parameters):
    parameters.set_boolean('same_length_res',
                           label='Put results in common outputs.',
                           value=True,
                           description=('Gather all the results generated '
                                        'from an incoming data into a '
                                        'common output table. This '
                                        'requires that the results all '
                                        'have the same length. An error '
                                        'will be given if the lengths of '
                                        'the outgoing results differ.'))


def add_base_parameters(parameters):
    parameters.set_list(
        'calc_list', label='List of calculations',
        description='List of calculations.',
        _old_list_storage=True)

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


def model_output_writer(infiles, calcs, outfiles, exception_handling,
                        same_length_res, copy_input=False):
    generic = False
    calc_list = []
    tmp_list = []
    for calc in calcs:
        name, calculation, enabled = models.parse_calc(calc)
        trimmed_name = models.trim_name(name)
        calc = calc.replace(name, trimmed_name, 1)
        tmp_list.append(models.format_calculation(calc, generic))
        calc_list.append(calc)

    calc_sorting, reverse_sorting = models.get_calculation_order(tmp_list)
    for i, infile in enumerate(infiles):
        try:
            if same_length_res:
                outfile = outfiles.create()
            if copy_input:
                outfile.source(infile)

            output_data = []
            enable = []
            for idx in calc_sorting:
                try:
                    output, enabled = models.python_calculator(
                        infile, calc_list[idx], dict(output_data), generic)
                    output_data.extend(output)
                    enable.append(enabled)
                except Exception:
                    if exception_handling == FAILURE_STRATEGIES['Exception']:
                        raise
                    enable.append(0)
                    output_data.append((None, None))

            for idx, calc_line in zip(reverse_sorting, calc_list):
                calc_line = calc_line.split(models.ENABLED_SPLIT)[0].strip()
                name, calculation, enabled = models.parse_calc(calc_line)
                calc_line = calc_line.replace(
                    name, old_table_display.format(name), 1)
                if enable[idx] and len(output_data):
                    column, output = output_data[idx]
                    if not same_length_res:
                        outfile = outfiles.create()
                    outfile.set_column_from_array(column, output)
                    outfile.set_column_attributes(
                        column,
                        {'calculation': models.display_calculation(calc_line,
                         generic)})
                    if not same_length_res:
                        outfiles.append(outfile)

            if same_length_res:
                outfiles.append(outfile)
        except Exception:
            if isinstance(infiles, list):
                raise
            else:
                raise exceptions.SyListIndexError(i, sys.exc_info())
            exceptions.sywarn('Error occurred in table number ' + str(i))


class SuperCalculator(synode.Node):
    author = ('Greger Cronquist, Magnus Sandén, Sara Gustafzelius & '
              'Benedikt Ziegler')
    description = 'Performs user-defined python calculations'
    version = '3.0'
    icon = 'calculator.svg'
    tags = Tags(Tag.DataProcessing.Calculate)
    plugins = (sylib.calculator.plugins.ICalcPlugin, )

    parameters = synode.parameters()
    add_base_parameters(parameters)

    def _exec_parameter_view(self, node_context, is_single_table):
        generic = False
        input_group = node_context.input.group('port0')
        input_data = table.File()
        if input_group:
            input_data = input_group[0]

        empty_input = False
        if not input_data.is_valid():
            empty_input = True
            if is_single_table:
                input_data = table.File()
            else:
                input_data = table.FileList()
        return calculator_gui.CalculatorWidget(
            input_data, node_context.parameters,
            backend='python', preview_calculator=models.python_calculator,
            generic=generic, multiple_input=not is_single_table,
            empty_input=empty_input)

    @staticmethod
    def _update_calc(parameters, infiles, outfiles, same_length_res):
        calc_list = parameters['calc_list'].list
        exception_handling = parameters['fail_strategy'].value[0]
        copy_input = parameters['copy_input'].value
        model_output_writer(infiles, calc_list, outfiles, exception_handling,
                            same_length_res, copy_input)


@deprecated_node('4.0.0', 'Calculator')
class CalculatorTableNode(SuperCalculator):
    __doc__ = TABLE_DOC
    name = 'Calculator Table'
    nodeid = 'org.sysess.sympathy.data.table.calculatortable'

    inputs = Ports([Port.Table('Input Table', name='port0')])
    outputs = Ports([Port.Table(
        'Table with results from the calculations.', name='port1')])

    def exec_parameter_view(self, node_context):
        return self._exec_parameter_view(node_context, True)

    def execute(self, node_context):
        out_list = table.FileList()
        self._update_calc(node_context.parameters,
                          [node_context.input['port0']], out_list,
                          True)
        node_context.output['port1'].update(out_list[0])


@deprecated_node('4.0.0', 'Calculator List')
class CalculatorNode(SuperCalculator):
    __doc__ = TABLE_DOC
    name = 'Calculator Tables'
    nodeid = 'org.sysess.sympathy.data.table.calculator'

    inputs = Ports([Port.Tables('Input Tables', name='port0')])
    outputs = Ports([Port.Tables(
        'Tables with results from the calculations.', name='port1')])

    parameters = synode.parameters()
    add_base_parameters(parameters)
    add_same_length_res_parameter(parameters)

    def update_parameters(self, old_params):
        # Old nodes without the same_length_res option work the same way as if
        # they had the option, set to False.
        if 'same_length_res' not in old_params:
            add_same_length_res_parameter(old_params)
            old_params['same_length_res'].value = False

    def exec_parameter_view(self, node_context):
        return self._exec_parameter_view(node_context, False)

    def execute(self, node_context):
        self._update_calc(node_context.parameters, node_context.input['port0'],
                          node_context.output['port1'],
                          node_context.parameters['same_length_res'].value)
