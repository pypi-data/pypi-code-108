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
import time
import datetime
import collections

import numpy as np

from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust
from sympathy.api.exceptions import SyNodeError, sywarn


OPTIONS_DICT = collections.OrderedDict([
    ('opt1', 'First option (default)'),
    ('opt2', 'Second option'),
    ('opt3', 'Third option'),
])


EXAMPLE_NODEIDS = [
    'org.sysess.sympathy.examples.helloworld',
    'org.sysess.sympathy.examples.helloworldcustomizable',
    'org.sysess.sympathy.examples.outputexample',
    'org.sysess.sympathy.examples.readwrite',
    'org.sysess.sympathy.examples.adjust',
    'org.sysess.sympathy.examples.errorexample',
    'org.sysess.sympathy.examples.progress',
    'org.sysess.sympathy.examples.allparameters',
    'org.sysess.sympathy.examples.controller',
]


class HelloWorld(synode.Node):
    """
    This, minimal, example prints a fixed "Hello world!" greeting when
    executed.

    See :ref:`nodewriting` for more information about writing nodes.
    """

    name = 'Hello world example'
    nodeid = 'org.sysess.sympathy.examples.helloworld'
    tags = Tags(Tag.Development.Example)

    def execute(self, node_context):
        print('Hello world!')


class HelloWorldCustomizable(synode.Node):
    """
    This example prints a customizable greeting. Default greeting is "Hello
    world!".

    See :ref:`nodewriting` for more information about writing nodes.
    Specifically see :ref:`node_parameters` for an introduction to node
    parameters.
    """

    name = 'Hello world customizable example'
    description = 'Node demonstrating the basics of node creation.'
    icon = 'example.svg'
    nodeid = 'org.sysess.sympathy.examples.helloworldcustomizable'
    author = 'Magnus Sandén'
    version = '1.0'
    tags = Tags(Tag.Development.Example)
    related = EXAMPLE_NODEIDS

    parameters = synode.parameters()
    parameters.set_string(
        'greeting', value='Hello world!', label='Greeting:',
        description='Your preferred greeting.')

    def execute(self, node_context):
        print(node_context.parameters['greeting'].value)


class OutputExample(synode.Node):
    """
    This example demonstrates how to write data to an outgoing Table.

    See :ref:`nodewriting` for more information about writing nodes.
    Specifically see :ref:`node_ports` for an introduction to node ports.
    """

    name = 'Output example'
    description = 'Node demonstrating how to write a table.'
    icon = 'example.svg'
    nodeid = 'org.sysess.sympathy.examples.outputexample'
    author = 'Magnus Sandén'
    version = '1.0'
    tags = Tags(Tag.Development.Example)
    related = EXAMPLE_NODEIDS

    outputs = Ports([
        Port.Table("Table with a column named 'Enumeration' with values 1-99",
                   name='output')])

    def execute(self, node_context):
        tablefile = node_context.output['output']
        data = np.arange(1, 101, dtype=int)
        tablefile.set_name('Output Example')
        tablefile.set_column_from_array('Enumeration', data)


class ErrorExample(synode.Node):
    """
    Demonstrates how to give the user error messages or warnings and how that
    is shown in the platform.

    See :ref:`nodewriting` for more information about writing nodes.
    Specifically see :ref:`node_errors` for an introduction to node errors,
    warnings and output.
    """

    name = 'Error example'
    description = 'Node demonstrating the error handling system.'
    icon = 'example_error.svg'
    nodeid = 'org.sysess.sympathy.examples.errorexample'
    author = 'Stefan Larsson'
    version = '2.0'
    tags = Tags(Tag.Development.Example)
    related = EXAMPLE_NODEIDS

    parameters = synode.parameters()
    parameters.set_string(
        'severity', value='Error', label='Severity:',
        description='Choose how severe the error is.',
        editor=synode.editors.combo_editor(
            options=['Notice', 'Warning', 'Error', 'Exception']))
    parameters.set_string(
        'error_msg', label='Error message:',
        description='This error message will be shown when executing the node',
        value='This is an expected error.')

    def execute(self, node_context):
        severity = node_context.parameters['severity'].value
        error_msg = node_context.parameters['error_msg'].value
        if severity == 'Notice':
            print(error_msg)
        elif severity == 'Warning':
            sywarn(error_msg)
        elif severity == 'Error':
            raise SyNodeError(error_msg)
        elif severity == 'Exception':
            raise Exception(error_msg)


class AllParametersExample(synode.Node):
    """
    This node includes all available configuration options for initialising
    parameters. The configuration GUI is automatically generated by the
    platform.

    See :ref:`nodewriting` for more information about writing nodes. See
    :ref:`parameter_helper_reference` for a detailed reference of the different
    parameter types and their respective editors.
    """

    name = 'All parameters example'
    description = 'Node showing all different parameter types.'
    icon = 'example.svg'
    nodeid = 'org.sysess.sympathy.examples.allparameters'
    author = 'Alexander Busck'
    version = '1.0'
    tags = Tags(Tag.Development.Example)
    related = EXAMPLE_NODEIDS

    parameters = synode.parameters()
    numbers_page = parameters.create_page('numbers', label='Numbers')
    float_group = numbers_page.create_group('float', label='Floats')
    float_group.set_float('stringfloat',
                          label='Float in a line edit',
                          description='A float',
                          value=0.1234)
    float_group.set_float('spinfloat',
                          label='Float in a spinbox',
                          description='A float',
                          value=0.1234,
                          editor=synode.editors.bounded_decimal_spinbox_editor(
                              0.0, 4.0, 0.1, 4))
    float_group.set_float('combo_float1',
                          label='Float with options',
                          value=0.,
                          description='Float parameter with options.',
                          editor=synode.editors.combo_editor(
                              options=[0.1, 0.2, 0.3]))
    float_group.set_float('combo_float2',
                          label='Float with editable options',
                          value=1.0,
                          description='Float parameter with options.',
                          editor=synode.editors.combo_editor(
                              options=[0.1, 0.2, 0.3], edit=True))

    integer_group = numbers_page.create_group('integer', label='Integers')
    integer_group.set_integer('stringinteger',
                              label='Integer in a line edit',
                              description='An integer',
                              value=1234,
                              editor=synode.editors.bounded_lineedit_editor(
                                  0, 2000, placeholder='Number between 0 '
                                                       'and 2000'))
    integer_group.set_integer('spininteger',
                              label='Integer in a spinbox',
                              description='An integer',
                              value=1234,
                              editor=synode.editors.bounded_spinbox_editor(
                                  0, 2000, 10))
    integer_group.set_integer('combo_integer1',
                              label='Integer with options',
                              value=1,
                              description='Integer parameter with '
                              'options.',
                              editor=synode.editors.combo_editor(
                                  options=[1, 2, 3]))
    integer_group.set_integer('combo_integer2',
                              label='Integer with editable options',
                              value=1,
                              description='Integer parameter with '
                              'editable options.',
                              editor=synode.editors.combo_editor(
                                  options=[1, 2, 3], edit=True))

    string_page = parameters.create_page('strings', label='Strings')
    string_group = string_page.create_group('strings', label='Normal strings')
    string_group.set_string('lineedit',
                            label='String in a line edit',
                            value='Hello',
                            description='Text on a single line',
                            editor=synode.editors.lineedit_editor(
                                'Hello World!'))
    string_group.set_string('textedit',
                            label='String in a text edit',
                            value='This is a\nmulti-line\neditor',
                            editor=synode.editors.textedit_editor())
    string_group.set_string('combo_string1',
                            label='String with options',
                            value='B',
                            description='String parameter with options.',
                            editor=synode.editors.combo_editor(
                                options=['A', 'B', 'C']))
    string_group.set_string('combo_string2',
                            label='String with filtered options',
                            value='',
                            description=(
                                'String parameter with options. '
                                'Filter is enabled and suited to deal with '
                                'a large number of choices'),
                            editor=synode.editors.combo_editor(
                                options=['A', 'B', 'C'],
                                include_empty=True, filter=True))
    string_group.set_string('combo_string3',
                            label='String with key-value options',
                            value='opt1',
                            description='String parameter with options '
                                        'defined as key-value pairs.',
                            editor=synode.editors.combo_editor(
                                options=OPTIONS_DICT))
    string_group.set_string('combo_string4',
                            label='String with editable options',
                            value='B',
                            description='String parameter with '
                            'options. Selected option can be '
                            'edited (press return to confirm edit).',
                            editor=synode.editors.combo_editor(
                                options=['A', 'B', 'C'], edit=True))

    path_group = string_page.create_group('path', label='Paths')
    path_group.set_string('filename',
                          label='Filename',
                          description='A filename including path if needed',
                          value='test.txt',
                          editor=synode.editors.filename_editor(
                              ['Image files (*.png *.xpm *.jpg)',
                               'Text files (*.txt)',
                               'Any files (*)']))
    path_group.set_string('save_filename',
                          label='Save filename',
                          description='A filename including path if needed',
                          value='test.txt',
                          editor=synode.editors.savename_editor(
                              ['Image files (*.png *.xpm *.jpg)',
                               'Text files (*.txt)',
                               'Any files (*)']))
    path_group.set_string('directory',
                          label='Directory',
                          description='A directory including path if needed',
                          value='MyDirectory',
                          editor=synode.editors.directory_editor())

    logics_page = parameters.create_page('logics', label='Logics')
    logics_page.set_boolean('boolflag',
                            label='Boolean',
                            description=('A boolean flag indicating true or '
                                         'false'),
                            value=True)

    times_page = parameters.create_page('times', label='Times')
    times_page.set_datetime('datetime',
                            label='Date Time',
                            description='A date time parameter',
                            value=datetime.datetime(2001, 1, 1))
    times_page.set_datetime(
        'date',
        label='Date',
        description='A date time parameter with date editor',
        value=datetime.datetime(2001, 1, 1),
        editor=synode.editors.datetime_editor(
            datetime_format="yyyy-MM-dd"))

    lists_page = parameters.create_page('lists', label='Lists')
    lists_page.set_list('combo',
                        label='Combo box',
                        description='A combo box',
                        value=[1],
                        plist=['First option',
                               'Second option',
                               'Third option'],
                        editor=synode.editors.combo_editor(include_empty=True))
    lists_page.set_list('editcombo',
                        label='Editable combo box',
                        description='An editable combo box. Selected option '
                        'can be edited (press return to confirm edit).',
                        value=[1],
                        plist=['First option',
                               'Second option',
                               'Third option'],
                        editor=synode.editors.combo_editor(
                            include_empty=True, edit=True))
    lists_page.set_list('combo_with_filter',
                        label='Combo box with filter',
                        description='A combo box with filter suitable for '
                                    'dealing with large numbers of options.',
                        value=[1],
                        plist=['First option',
                               'Second option',
                               'Third option'],
                        editor=synode.editors.combo_editor(
                            include_empty=True,
                            filter=True))
    lists_page.set_list('multilist',
                        label='List view with multiselect',
                        description='A list with multiselect',
                        value=[0, 2],
                        plist=['Element1', 'Element2', 'Element3'],
                        editor=synode.editors.multilist_editor())
    lists_page.set_list('editmultilist',
                        label='Editable list view with multiselect',
                        description=(
                            'An editable multiselect list (use double-click, '
                            'right-click). Only checked elements are saved.'),
                        value=[0, 2],
                        plist=['Element1', 'Element2', 'Element3'],
                        editor=synode.editors.multilist_editor(edit=True))

    def execute(self, node_context):
        """
        You always have to implement the execute method to be able to execute
        the node. In this node we don't want the execute method to actually do
        anything though.
        """
        pass


class AdjustExample(synode.Node):
    """
    In this case we let the user select a column and a row among the ones in
    the input data.

    Two different methods are used for setting the options for *Column* and
    *Row*. Setting options for *Column* is the simplest case, where we can use
    the ``adjust`` helper function which automatically fetches the column
    names.

    See :ref:`nodewriting` for more information about writing nodes.
    Specifically see :ref:`adjust_parameters` for an introduction to
    adjust_parameters.
    """

    name = 'Adjust example'
    description = ('Node demonstrating using adjust to set the available '
                   'options in parameters from input data.')
    icon = 'example.svg'
    nodeid = 'org.sysess.sympathy.examples.adjust'
    author = 'Magnus Sandén'
    version = '1.0'
    tags = Tags(Tag.Development.Example)
    related = EXAMPLE_NODEIDS

    inputs = Ports([Port.Table('Input Table', name='input')])

    parameters = synode.parameters()
    parameters.set_string(
        'column',
        label='Column',
        value='',
        description=(
            'String with options corresponding to the column names '
            'of the input table.'),
        editor=synode.editors.combo_editor(edit=True, filter=True))
    parameters.set_integer(
        'row',
        label='Row',
        value=0,
        description=(
            'Integer with options corresponding to the row indices '
            'of the input table.'),
        editor=synode.editors.combo_editor(edit=True))

    def adjust_parameters(self, node_context):
        """
        This method is called before configure. In this example it fills the
        comboboxes of some of the parameters with options.
        """
        input_table = node_context.input[0]

        # Simplest case: Present the columns of the input Table as available
        # choices in the string parameter. It can be applied to any type of
        # parameter in a combo_editor or multilist_editor.
        adjust(node_context.parameters['column'], input_table)

        # Less simple case: Present the rows of the input Table as available
        # choices in the integer parameter. This method makes it possible to
        # use any list of options, but requires taking some care to not attempt
        # to read from unavailable input.
        if input_table.is_valid():
            available_rows = list(range(input_table.number_of_rows()))
        else:
            available_rows = []
        node_context.parameters['row'].adjust(available_rows)

    def execute(self, node_context):
        """Print the value at selected columns/row."""
        input_table = node_context.input[0]
        column = node_context.parameters['column'].value
        row = node_context.parameters['row'].value
        try:
            print(input_table[column][row])
        except LookupError:
            print('This node needs a column with sufficient rows.')


class ProgressExample(synode.Node):
    """
    This node runs with a delay and updates its progress during execution to
    let the user know how far it has gotten.

    See :ref:`nodewriting` for more information about writing nodes. See
    :ref:`Node interface reference<node_progress>` for more information about
    the ``set_progress`` method.
    """

    name = 'Progress example'
    description = 'Node demonstrating progress usage'
    icon = 'example.svg'
    nodeid = 'org.sysess.sympathy.examples.progress'
    author = 'Magnus Sandén'
    version = '1.0'
    tags = Tags(Tag.Development.Example)
    related = EXAMPLE_NODEIDS

    parameters = synode.parameters()
    parameters.set_float(
        'delay', value=0.02, label='Delay:',
        description='Delay between tables')

    def execute(self, node_context):
        """
        Loop with customizable delay from 0 to 99 and update the node's
        progress accordingly each iteration.
        """
        delay = node_context.parameters['delay'].value
        for i in range(100):
            self.set_progress(float(i))

            # In real applications this would be some lengthy calculation.
            time.sleep(delay)


class ControllerExample(synode.Node):
    """
    This example demonstrates how to use controllers to create more advanced
    configuration guis, while still relying on the automatic configuration
    builder. For more information about controllers see :ref:`the user
    manual<controllers>`.

    See :ref:`nodewriting` for more information about writing nodes.
    Specifically see :ref:`controllers` for an introduction to controllers.
    """

    name = 'Controller example'
    description = 'Node demonstrating controller usage'
    icon = 'example.svg'
    nodeid = 'org.sysess.sympathy.examples.controller'
    author = 'Magnus Sandén'
    version = '1.0'
    tags = Tags(Tag.Development.Example)
    related = EXAMPLE_NODEIDS

    parameters = synode.parameters()
    value_group = parameters.create_group('fruit', label='Fruit')
    value_group.set_string(
        'fruit', value='Apples', label='Apples or oranges?',
        description='Which fruit do you prefer?',
        editor=synode.editors.combo_editor(['Apples', 'Oranges']))
    value_group.set_string(
        'color', value='', label='Color:',
        description='What color should the apples have?')
    value_group.set_string(
        'size', value='Small', label='Size:',
        description='What size should the oranges have?',
        editor=synode.editors.combo_editor(['Small', 'Big', 'Really big']))
    checked_group = parameters.create_group('delivery', label='Delivery')
    checked_group.set_boolean(
        'delivery', value=False, label='Drone delivery:',
        description='When checked, drones will deliver the fruit to you, '
                    'wherever you are.')
    checked_group.set_string(
        'address', value='', label='Adress:',
        description='Your full address.')

    controllers = (
        synode.controller(
            when=synode.field('fruit', 'value', value='Apples'),
            action=(synode.field('color', 'enabled'),
                    synode.field('size', 'disabled'))),
        synode.controller(
            when=synode.field('delivery', 'checked'),
            action=synode.field('address', 'enabled')))

    def execute(self, node_context):
        pass


class ReadWriteExample(synode.Node):
    """
    This example node demonstrates how to read from and write to a list of
    tables. It forwards tables from the input to the output using the source
    method available for tables and other data types. This will forward data
    from one file to another, without making needless copies. Instead the data
    is linked to the source whenever possible.

    To run this node you can connect its input port to e.g. a
    :ref:`Random Tables` node.

    See :ref:`nodewriting` for more information about writing nodes. See
    :ref:`datatypeapis` for more information on how to use the APIs of the
    different data types in Sympathy for Data.
    """

    name = 'Read/write example'
    description = (
        'Node demonstrating how to read from/write to lists of tables.')
    icon = 'example.svg'
    nodeid = 'org.sysess.sympathy.examples.readwrite'
    author = 'Magnus Sandén'
    version = '1.0'
    tags = Tags(Tag.Development.Example)
    related = EXAMPLE_NODEIDS

    inputs = Ports([Port.Tables('Input Tables', name='input')])
    outputs = Ports([Port.Tables('Output Tables', name='output')])

    def execute(self, node_context):
        """Loop over all the tables in the input and forward some them."""
        out_tables = node_context.output['output']
        for i, in_table in enumerate(node_context.input['input']):
            # Forward every second table:
            if i % 2 == 0:
                out_table = out_tables.create()
                out_table.source(in_table)
                out_tables.append(out_table)
