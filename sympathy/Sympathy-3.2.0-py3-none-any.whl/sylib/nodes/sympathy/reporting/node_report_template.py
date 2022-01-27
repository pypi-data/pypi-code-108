# This file is part of Sympathy for Data.
# Copyright (c) 2015, 2017, Combine Control Systems AB
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
Editor for designing a report template
======================================

Configuration
^^^^^^^^^^^^^

The configuration dialog is a large complex editor to design a layout
for report templates. On the left side there are sections for
handling scales, pages and properties. In the middle is the area
showing the report given the input data. On the right is a view of
the underlying JSON-data model (mostly used for debugging and will be
removed in the future).

**Scales**
    Scales translates values in a domain (source) to values in a range
    (output). This is useful to generalize how data should be
    interpreted to achieve certain effects when generating a plot.
    Currently a numeric domain is mapped to either a numeric range or
    a range of colors.

    A new scale is created by clicking the plus sign above the list
    of scales. Double clicking the scale opens a configuration dialog.

    * Id: Unique identifier of the scale.
      This name is used to reference the scale in other parts of the
      editor.
    * Type: Type of scale, i.e. how domain data is mapped to range data.
    * Extent: When enabled the total span of the input data to the scale
      is used as domain. This is useful when wanting to use a scale
      for many different data sources, but the same output is desired.
    * Domain: The domain contains a list of numbers which must be given
      in ascending order.
    * Range: The range should be either a list of numbers or a list of
      colors with the same length as the domain list. Colors are
      specified according to hex-RGB: ``#rrggbb``, e.g. ``#3288ed``.

    .. image:: scale_dialog.png

**Pages**
    The pages view is used to change the appearance of the template.
    There are two toolbars available with icons which can be
    dragged and dropped into the tree area below.

    .. image:: tools_and_layers.png

    The first toolbar row contains the following icons from left to
    right:

    * Page: A page is only allowed in the root level of the tree and
      translates into new tabs. When rendered using :ref:`Report Apply
      Tables` each page becomes a separate image.
    * Layout: A layout can be specified as either horizontal och
      vertical. It can be a child of either a page or another layout. It
      is possible to build complex layouts by nesting different layout
      elements in each other.
    * Text: A free text item.
    * Image: A static image.
    * Graph: The graph is a representation for a plot area, i.e. a set
      of axes. A graph has a set of dimensions which contain axes. The
      first dimension contains the x-axes, the second dimension the
      y-axes, and so forth. Currently only one axis per dimension is
      allowed, but the plan is to support several axes per dimension.
      The last node is called Layers and contains all plot layers which
      shows the total plot.

    The second toolbar contains the layers which are currently
    available:

    * Bar chart
    * 1D histogram
    * 2D histogram
    * Line chart
    * Scatter chart

**Properties**
    The property view is used to manipulate parameters of the
    currently selected item in the page view.
"""
import json

from sympathy.api import node as synode
from sympathy.api.nodeconfig import Ports, Port, Tag, Tags
from sympathy.api import report
from sylib.report.gui import MainWindow
from sylib.report import data_manager
from sylib.report import models


class DataType(object):
    adaf = 'adafs'
    table = 'tables'


THUMBNAIL_WIDTH = 64


def common_execute(node, node_context, data_type):
    # Read files and parameters
    input_data = node_context.input[0]
    report_json = node_context.parameters['document'].value
    if report_json == '':
        report_json = (
            '{"scales": [], "signals": [], "version": 1, "type": "root", '
            '"pages": [], "sytype": "report"}')

    # Extract all input signals which were used.
    report_data = json.loads(report_json)
    data_manager.init_data_source(input_data, data_type)
    report_data['signals'] = data_manager.data_source.signal_list()

    # Get rid of those which has not been used at all.
    report_data['signals'] = models.compress_signals(report_data)

    output_report = node_context.output[0]
    output_report.set(report_json)


def common_parameter_view(node_context, data_type):
    input_tables = None
    if node_context.input[0].is_valid():
        input_tables = node_context.input[0]
    return MainWindow(node_context.parameters, input_tables, data_type)


class ReportTemplateTables(synode.Node):
    """
    Editor for designing a report template.
    """

    name = 'Report Template Tables'
    nodeid = 'org.sysess.sympathy.report.template.tables'
    author = 'Stefan Larsson'
    version = '1.0'
    icon = 'report.svg'
    tags = Tags(Tag.Visual.Report)
    related = ['org.sysess.sympathy.report.template.adafs',
               'org.sysess.sympathy.report.apply.tables']

    inputs = Ports([Port.Tables(
        'List of tables to use as source of data when building template',
        name='tables')])
    outputs = Ports([report.Report('Report Template', name='template')])

    parameters = synode.parameters()
    parameters.set_string(
        'document',
        value='',
        label='Document',
        description='JSON-data containing description of template.'
    )

    def execute(self, node_context):
        common_execute(self, node_context, DataType.table)

    def exec_parameter_view(self, node_context):
        return common_parameter_view(node_context, DataType.table)


class ReportTemplateADAFs(synode.Node):
    """
    Editor for designing a report template.
    """

    name = 'Report Template ADAFs'
    nodeid = 'org.sysess.sympathy.report.template.adafs'
    author = 'Stefan Larsson'
    version = '1.0'
    icon = 'report.svg'
    tags = Tags(Tag.Visual.Report)
    related = ['org.sysess.sympathy.report.template.tables',
               'org.sysess.sympathy.report.apply.adafs']

    inputs = Ports([Port.ADAFs(
        'List of ADAFs to use as source of data when building template',
        name='adafs')])
    outputs = Ports([report.Report(
        'Template to be used by :ref:`Report Apply ADAFs` to generate output',
        name='template')])

    parameters = synode.parameters()
    parameters.set_string(
        'document',
        value='',
        label='Document',
        description='JSON-data containing description of template.'
    )

    def execute(self, node_context):
        common_execute(self, node_context, DataType.adaf)

    def exec_parameter_view(self, node_context):
        return common_parameter_view(node_context, DataType.adaf)
