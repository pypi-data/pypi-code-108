# This file is part of Sympathy for Data.
# Copyright (c) 2013, 2017, Combine Control Systems AB
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

from sympathy.api import exporters
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sylib.export import common
from sylib.export import base


class ExportTexts(base.ExportMultiple, synode.Node):
    __doc__ = common.COMMON_DOC + """

Export of Texts to the following file formats are supported:
    - Text

:Opposite node: :ref:`Texts`
"""
    name = 'Export Texts'
    description = 'Export Texts'
    icon = 'export_text.svg'
    tags = Tags(Tag.Output.Export)
    plugins = (exporters.TextDataExporterBase, )
    author = 'Erik der Hagopian'
    nodeid = 'org.sysess.sympathy.export.exportexts'
    version = '0.1'

    inputs = Ports([Port.Texts('Texts to be exported', name='port0'),
                    Port.Datasources(
                        'External filenames',
                        name='port1', n=(0, 1, 0))])

    parameters = base.base_params()
