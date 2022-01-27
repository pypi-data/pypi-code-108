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
from sylib.export import common
from sylib.export import table as exporttable
from sylib.export import base
from sympathy.api.nodeconfig import Port, Ports


class ExportTables(base.ExportMultiple, synode.Node):
    __doc__ = common.COMMON_DOC + """

:Opposite node: :ref:`Tables`
:Ref. nodes: :ref:`Export ADAFs`
    """
    name = 'Export Tables'
    description = 'Export Tables'
    icon = 'export_table.svg'
    inputs = Ports([Port.Tables('Tables to be exported', name='port0'),
                    Port.Datasources(
                        'External filenames',
                        name='port1', n=(0, 1, 0))])

    plugins = (exporttable.TableDataExporterBase, )
    author = 'Alexander Busck'
    nodeid = 'org.sysess.sympathy.export.exporttables'
    version = '0.1'
    parameters = base.base_params()
