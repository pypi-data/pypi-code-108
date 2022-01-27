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
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports
from sylib.export import common
from sylib.export import adaf as exportadaf
from sylib.export import base


class ExportADAFs(base.ExportMultiple, synode.Node):
    __doc__ = common.COMMON_DOC + """

Export of ADAFs to the following file formats are supported:
    - SyData
    - MDF

For export of ADAF to file there exist a number of strategies that
can be used to extract filenames from information stored in the ADAFs. If no
strategy is selected one has to declare the base of the filename.

The following strategies exist:
    - **Source identifier as name**
        Use the source identifier in the ADAFs as filenames.
    - **Column with name**
        Specify a column in the metadata container where the first element
        is the filename.

:Opposite nodes: :ref:`ADAFs`
:Ref. nodes: :ref:`Export Tables`
"""
    name = 'Export ADAFs'
    description = 'Export ADAFs'
    icon = 'adaf_export.svg'
    plugins = (exportadaf.TabbedADAFDataExporterBase, )
    author = 'Alexander Busck'
    nodeid = 'org.sysess.sympathy.export.exportadafs'
    version = '0.1'

    inputs = Ports([Port.ADAFs('Input ADAFs', name='port0'),
                    Port.Datasources(
                        'External filenames',
                        name='port1', n=(0, 1, 0))])
    parameters = base.base_params()
