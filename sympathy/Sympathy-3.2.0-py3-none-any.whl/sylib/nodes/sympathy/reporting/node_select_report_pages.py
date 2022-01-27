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
import json

from sympathy.api import node as synode
from sympathy.api.nodeconfig import Ports, Tag, Tags
from sympathy.api import report
from sylib.report import models
from sylib.report import gui_select_report_pages


class SelectReportPages(synode.Node):
    """
    Selects a set of pages from an existing report template and
    exports a new template with only those pages left.
    """

    name = 'Select Report Pages'
    nodeid = 'org.sysess.sympathy.report.select.pages'
    author = 'Stefan Larsson'
    version = '1.0'
    icon = 'report-select.svg'
    tags = Tags(Tag.Visual.Report)

    inputs = Ports([report.Report('Input Report Template',
                                  name='input_template')])
    outputs = Ports([report.Report('Output Report Template',
                                   name='output_template')])

    parameters = synode.parameters()
    parameters.set_list(
        'selected_pages',
        value=[],
        plist=[],
        label='Selected Pages',
        description='Selected pages of report.',
        _old_list_storage=True)

    def execute(self, node_context):
        self.set_progress(0)

        p = synode.parameters(node_context.parameters)
        selected_page_uuids = [x[0] for x in p['selected_pages'].list]

        if len(selected_page_uuids) == 0:
            raise ValueError('At least one page has to be selected')

        document = json.loads(node_context.input[0].get())
        model = models.Root(document)
        self.set_progress(5)

        # Remove pages which have not been selected.
        page_list = model.find_all_nodes_with_class(models.Page)
        for i, page in enumerate(page_list):
            if page.data['uuid'] not in selected_page_uuids:
                models.remove_node(page)
            self.set_progress(
                float(i) / float(len(selected_page_uuids)) * 95 + 5)

        # Compress signal list.
        compressed_signal_list = models.compress_signals(model.data)
        output_document = model.data
        output_document['signals'] = compressed_signal_list

        output_template_port = node_context.output[0]
        output_template_port.set(json.dumps(output_document))

    def exec_parameter_view(self, node_context):
        inport = node_context.input[0]
        model = None
        if inport.is_valid():
            document = json.loads(inport.get())
            model = models.Root(document)
        return gui_select_report_pages.SelectReportPages(
            model, node_context.parameters)
