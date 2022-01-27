# This file is part of Sympathy for Data.
# Copyright (c) 2016-2017, Combine Control Systems AB
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
import json
import numpy as np

from sympathy import api
from sympathy.api import node as synode
from sympathy.api import qt2 as qt_compat
from sympathy.api.nodeconfig import (
    Port, Ports, Tag, Tags, adjust, deprecated_node)
from sympathy.api.nodeconfig import join_doc

from sympathy.platform.exceptions import SyConfigurationError

from sylib.old_figure import util, gui


# OVERVIEW_DOCSTRING = """
#  The
# :ref:`Figure Compressor` node allows to compress a list of Figures into one
# single Figure, while the :ref:`Layout Figures in Subplots` generates a Figure
# with subplots. Figures can be exported using the :ref:`Export Figures` node.
# """

TREEVIEW_DOCSTRING = """
.. note::
    This node is being deprecated by
    :ref:`org.sysess.sympathy.visualize.figure`,
    please avoid using it for new flows.

Both of the nodes :ref:`org.sysess.sympathy.visualize.figuretabletreegui` and
:ref:`org.sysess.sympathy.visualize.figurestablestreegui` are used to configure
figures in a graphical user interface. They both output the figure(s) on the
upper port and a configuration table an optional lower port. The configuration
table can be used in the nodes
:ref:`org.sysess.sympathy.visualize.figurefromtablewithtable` and
:ref:`org.sysess.sympathy.visualize.figuresfromtableswithtable`.

The configuration gui for these nodes consists of a toolbar and a tree view.
The tree view has two columns: one for the configuration items and one for
their values.

You can add plots to the figure by clicking on its corresponding button in the
toolbar, or by pressing on a plot button and dragging it to where in the tree
view you want it (possible drop locations will be shown in green). The plot
will be added with some basic properties depending on which plot type you added
(e.g. *X Data* and *Y Data* for line plot). Almost all configuration items
support more than the default properties. To add more, right-click on a
configuration item and choose "Add..." or "Add property" depending on what you
want to add.

Properties that allow free text are interpreted as python code and executed. In
this python evironment the input data table is available under the name ``arg``
(``table`` can also be used for historical reasons). For example one can refer
to data columns in a connected Table by writing something like
``arg['My data column']``. Have a look at the :ref:`datatypeapis` to see all
the available methods and attributes for the data type that you connect to the
node.

Use the node :ref:`Export figures` to write any figures you produce to files.
"""

CONF_TABLE_DOCSTRING = """
Having the full configuration for the figure as a table on an input port allow
you to programmatically configure a figure. If you are looking for an eaiser
but slightly less powerful way to configure a figure you should instead use one
of the nodes :ref:`org.sysess.sympathy.visualize.figure` or
:ref:`org.sysess.sympathy.visualize.figures` where you can
configure the figure in a graphical user interface.

The configuration table consists of one parameter column and one value column.
Both column should be of text type. The easiest way to learn how to create a
specific figure with this node is to first build the same figure using the node
"Figure (deprecated)" and look at the configuration table that that node
produces.

Here is a simple example of a configuration table for a line plot:

    =========================== ===================
    Parameters                  Values
    =========================== ===================
    axes.axes-1.xaxis_position  bottom
    axes.axes-1.yaxis_position  left
    axes.axes-1.title           Plot title
    axes.axes-1.xlabel          The xlabel
    axes.axes-1.ylabel          The ylabel
    line.line-1.axes            axes-1
    line.line-1.xdata           ``table.col('x').data``
    line.line-1.ydata           ``table.col('y').data``
    =========================== ===================


**Plots**

Every line/scatter is addressed with a unique
identifier *{id}*, which can be any string without a '.'. A
line parameter is constructed as with *line.{id}.{property}*
in the parameter column and the corresponding value in the
value column. Every line needs to have at least the 'xdata'
and 'ydata' specified. All line properties, except the 'ydata',
can also be given on a *global* level like *line.{property}*.
All properties given on a global level with be copied to all
configured lines without overriding locally declared properties.

Currently supported properties are (some properties allow
alternative names *longname/shortname*):

===================== =====================
Property              Type
===================== =====================
xdata                 unicode
ydata                 unicode
axes                  *axes id* (see below)
label                 unicode
marker                matplotlib marker: o, ., ^, d, etc
markersize            float
markeredgecolor       mpl color (see below)
markeredgewidth       float
markerfacecolor       mpl color (see below)
linestyle             matplotlib line style: -, --, .-, etc
linewidth             float
color                 mpl color (see below)
alpha                 float [0., 1.]
zorder                number
drawstyle             matplotlib drawstyle: default, steps, etc
===================== =====================

Please see the matplotlib_ documentation for sensible values of the
different types.

.. _matplotlib: http://matplotlib.org/api/lines_api.html

Example
^^^^^^^
An example assigning the 'index' column as x values and the 'signal' column as
y values to a line with id 'line-1', as well as drawing it in red with a
circular marker:

    ==================== ==================
    Parameters           Values
    ==================== ==================
    line.line-1.xdata    ``table.col('index').data``
    line.line-1.ydata    ``table.col('signal').data``
    line.line-1.color    red
    line.line-1.marker   o
    ==================== ==================

**Axes**

Axes are defined similarly to lines. All axes are overlaid on top of each
other. Every axes also has a unique identifier *{id}* (without '.'). The
parameter name is constructed as *axes.{id}.{property}* on the local level
or *axes.{property}* for global properties, valid for all defined axes.

===================== =====================
Property              Type
===================== =====================
xaxis_position        bottom, top
yaxis_position        left, right
title                 unicode
xlabel                unicode
ylabel                unicode
xlim                  str of two comma separated numbers
ylim                  str of two comma separated numbers
xscale                linear, log
yscale                linear, log
aspect                auto, equal, float
grid                  GRID (see below)
legend                LEGEND (see below)
===================== =====================

**Grid**

Every axes can also have a grid with the following optional
properties:

===================== =====================
Property              Type
===================== =====================
show                  bool
color                 mpl color (see below)
linestyle             matplotlib line style: -, --, .-, etc
linewidth             float
which                 major, minor, both
axis                  both, x, y
===================== =====================

**Legend**

Every axes can also have a legend defined with the following
optional properties:

===================== =====================
Property              Type
===================== =====================
show                  bool
loc                   mpl legend location (e.g. best, upper left)
ncol                  int
fontsize              e.g. x-small, medium, x-large, etc
markerfirst           bool
frameon               bool
title                 unicode
===================== =====================


Example
^^^^^^^

The example defines two axes, one (id=xy) with the y axis on the left and the
other (id=foo) with the y axis on the right while sharing the bottom x axis.
Since the xaxis_position is shared between the two axes, it is defined on the
global level. For *xy*, a legend will be shown in the upper left corner, while
the *foo* axes will have a green grid.

    ======================= ===================
    Parameters              Values
    ======================= ===================
    axes.xaxis_position     bottom
    axes.xy.yaxis_position  left
    axes.xy.xlabel          The xy xlabel
    axes.xy.ylabel          The xy ylabel
    axes.xy.legend.show     True
    axes.xy.legend.loc      upper left
    axes.foo.yaxis          y2
    axes.foo.ylabel         The y2 ylabel
    axes.foo.grid.show      True
    axes.foo.grid.color     green
    ======================= ===================

**MPL colors**

All properties with *mpl colors* values expect a string with
either a hex color (with or without extra alpha channel), 3 or 4
comma separated integers for the RGBA values (range [0, 255]),
3 or 4 comma separated floats for the RGBA values (range [0., 1.])
or a matplotlib color_ name (e.g. r, red, blue, etc.).

.. _color: http://matplotlib.org/examples/color/named_colors.html
"""
QtCore = qt_compat.QtCore
QtGui = qt_compat.QtGui
qt_compat.backend.use_matplotlib_qt()


class SuperNodeFigureWithTable(synode.Node):
    author = 'Benedikt Ziegler'
    version = '0.1'
    icon = 'figure.svg'
    tags = Tags(Tag.Visual.Figure)

    parameters = synode.parameters()
    parameters.set_list(
        'parameters', label='Parameters:',
        description='The column containing the parameter names.',
        editor=synode.Util.combo_editor(edit=True, filter=True))
    parameters.set_list(
        'values', label='Values:',
        description='The column containing the parameter values.',
        editor=synode.Util.combo_editor(edit=True, filter=True))

    def verify_parameters(self, node_context):
        parameters = node_context.parameters
        param_list = [] != parameters['parameters'].list
        value_list = [] != parameters['values'].list
        return param_list and value_list

    def adjust_parameters(self, node_context):
        config_input = node_context.input['config']
        adjust(node_context.parameters['parameters'], config_input)
        adjust(node_context.parameters['values'], config_input)

    def execute(self, node_context):
        config_table = node_context.input['config']

        parameters = node_context.parameters
        param_col = parameters['parameters'].selected
        value_col = parameters['values'].selected

        if param_col is None or value_col is None:
            raise SyConfigurationError(
                "No columns were selected or the columns you have selected "
                "are not present in the input please make sure to use data "
                "that contains the selected columns before executing this "
                "node.")

        param_names = config_table.get_column_to_array(param_col)
        param_values = config_table.get_column_to_array(value_col)
        configuration = list(zip(param_names, param_values))

        figure_param = util.parse_configuration(configuration)

        self._create_figure(node_context, figure_param)

    def _create_figure(self, node_context, figure_param):
        raise NotImplementedError()


@deprecated_node('4.0.0', 'Figure, with config port')
class FigureFromTableWithTable(SuperNodeFigureWithTable):
    __doc__ = join_doc(
        """
        Create a Figure from a data Table (upper port) using another Table for
        configuration (lower port).
        """,
        CONF_TABLE_DOCSTRING)

    name = 'Figure from Table with Table (deprecated)'
    description = ('Create a Figure from a Table using a '
                   'configuration Table')
    nodeid = 'org.sysess.sympathy.visualize.figurefromtablewithtable'

    inputs = Ports([Port.Table('Input data', name='input'),
                    Port.Table('Configuration', name='config')])
    outputs = Ports([Port.Figure('Output figure', name='figure')])

    def _create_figure(self, node_context, figure_param):
        data_table = node_context.input['input']
        if not data_table.column_names():
            figure_param = util.parse_configuration([])
        figure = node_context.output['figure']

        figure_creator = util.CreateFigure(data_table, figure, figure_param)
        figure_creator.create_figure()


@deprecated_node('4.0.0', 'Figures, with configuration port')
class FiguresFromTablesWithTable(SuperNodeFigureWithTable):
    __doc__ = join_doc(
        """
        Create Figures from a list of data Tables (upper port) using another
        Table for configuration (lower port).
        """,
        CONF_TABLE_DOCSTRING)

    name = 'Figures from Tables with Table (deprecated)'
    description = ('Create Figures from List of Tables using a '
                   'configuration Table')
    nodeid = 'org.sysess.sympathy.visualize.figuresfromtableswithtable'

    inputs = Ports([Port.Tables('Input data', name='input'),
                    Port.Table('Configuration', name='config')])
    outputs = Ports([Port.Figures('Output figure', name='figure')])

    def _create_figure(self, node_context, figure_param):
        data_tables = node_context.input['input']
        figures = node_context.output['figure']

        for i, data_table in enumerate(data_tables):
            figure = api.figure.File()
            figure_creator = util.CreateFigure(
                data_table, figure, figure_param)
            figure_creator.create_figure()

            figures.append(figure)

            self.set_progress(100 * (i + 1) / len(data_tables))


@deprecated_node('4.0.0', 'Figure')
class FigureFromAnyWithTreeView(synode.Node):
    __doc__ = join_doc(
        """
        Create a Figure from some data using a GUI.
        """,
        TREEVIEW_DOCSTRING)

    author = 'Benedikt Ziegler'
    version = '0.2'
    icon = 'figure.svg'
    name = 'Figure (deprecated)'
    description = 'Create a single Figure using a GUI.'
    nodeid = 'org.sysess.sympathy.visualize.figuretabletreegui'
    tags = Tags(Tag.Visual.Figure)

    parameters = synode.parameters()
    parameters.set_string(
        'parameters', value='[]',
        label='GUI', description='Configuration window')

    inputs = Ports([Port.Custom('<a>', 'Input', name='input')])
    outputs = Ports([Port.Figure('Output figure', name='figure'),
                     Port.Custom('table', 'Configuration', name='config',
                                 n=(0, 1, 1))])

    def update_parameters(self, old_params):
        # Old nodes have their parameters stored as a list, but nowadays we
        # json-encode that list into a string instead.
        if old_params['parameters'].type == 'list':
            parameters_list = old_params['parameters'].list
            del old_params['parameters']
            old_params.set_string(
                'parameters', value=json.dumps(parameters_list))

    def exec_parameter_view(self, node_context):
        input_data = node_context.input['input']
        if not input_data.is_valid():
            input_data = api.table.File()
        return gui.FigureFromTableWidget(input_data, node_context.parameters)

    def execute(self, node_context):
        data_table = node_context.input['input']
        figure = node_context.output['figure']

        config_table = node_context.output.group('config')
        if len(config_table) > 0:
            config_table = config_table[0]
        else:
            config_table = None

        fig_parameters = json.loads(
            node_context.parameters['parameters'].value)
        parsed_param = util.parse_configuration(fig_parameters)

        figure_creator = util.CreateFigure(data_table, figure, parsed_param)
        figure_creator.create_figure()

        fig_parameters = np.atleast_2d(np.array(fig_parameters))
        if len(fig_parameters) and fig_parameters.shape >= (1, 2):
            parameters = fig_parameters[:, 0]
            values = fig_parameters[:, 1]
        else:
            parameters = np.array([])
            values = np.array([])

        if config_table is not None:
            config_table.set_column_from_array('Parameters', parameters)
            config_table.set_column_from_array('Values', values)


@deprecated_node('4.0.0', 'Figures')
class FiguresFromAnyListWithTreeView(FigureFromAnyWithTreeView):
    __doc__ = join_doc(
        """
        Create a List of Figures from a List of data using a GUI.
        """,
        TREEVIEW_DOCSTRING)

    version = '0.2'
    name = 'Figures (deprecated)'
    description = 'Create a list of Figures from a list of data using a GUI.'
    nodeid = 'org.sysess.sympathy.visualize.figurestablestreegui'
    tags = Tags(Tag.Visual.Figure)

    inputs = Ports([Port.Custom('[<a>]', 'Inputs', name='inputs')])
    outputs = Ports([Port.Figures('Output figure', name='figures'),
                     Port.Custom('table', 'Configuration', name='config',
                                 n=(0, 1, 1))])

    def exec_parameter_view(self, node_context):
        input_data = node_context.input['inputs']
        if not input_data.is_valid() or not len(input_data):
            first_input = api.table.File()
        else:
            first_input = input_data[0]
        return gui.FigureFromTableWidget(first_input, node_context.parameters)

    def execute(self, node_context):
        data_tables = node_context.input['inputs']
        figures = node_context.output['figures']

        config_table = node_context.output.group('config')
        if len(config_table) > 0:
            config_table = config_table[0]
        else:
            config_table = None
        fig_parameters = json.loads(
            node_context.parameters['parameters'].value)
        parsed_param = util.parse_configuration(fig_parameters)

        number_of_tables = len(data_tables) + 1  # +1 for writing config table

        i = 0
        for i, data_table in enumerate(data_tables):
            figure = api.figure.File()
            figure_creator = util.CreateFigure(data_table, figure,
                                               parsed_param.copy())
            figure_creator.create_figure()
            figures.append(figure)
            self.set_progress(100 * (i + 1) / number_of_tables)

        fig_parameters = np.atleast_2d(np.array(fig_parameters))
        if len(fig_parameters) and fig_parameters.shape >= (1, 2):
            parameters = fig_parameters[:, 0]
            values = fig_parameters[:, 1]
        else:
            parameters = np.array([])
            values = np.array([])
        if config_table is not None:
            config_table.set_column_from_array('Parameters', parameters)
            config_table.set_column_from_array('Values', values)
        self.set_progress(100 * (i + 1) / number_of_tables)
