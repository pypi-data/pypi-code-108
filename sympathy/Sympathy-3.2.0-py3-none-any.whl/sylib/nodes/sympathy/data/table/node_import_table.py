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
"""
Table is the internal data type in Sympathy for Data representing a
two-dimensional data set. A Table consists of an arbitrary number of
columns, where all columns have the equal number of elements. Each column
has an unique header and a defined data type - all elements in a column
are of the same data type. In a Table, the columns are not bound to have
same data type, columns with different data types can be mixed in a Table.
The supported data types for the columns are the same as for numpy arrays,
with exception for the object type, np.object. Optional, an column can also
be given additional attributes, like unit or description.

This node uses plugins. Each supported file format has its own plugin. The
plugins have their own configurations which are reached by choosing among the
importers in the configuration GUI. The documentation for each plugin is
obtained by clicking at listed file formats below.

The node has an auto configuration which uses a validity check in the plugins
to detect and choose the proper plugin for the considered datasource. When
the node is executed in the auto mode the default settings for the plugins
will be used.

"""
import os
from sylib.importer import base
from sympathy.api import node as synode
from sympathy.api import importers
from sympathy.api.nodeconfig import Port, Ports


def _output_item_filename_hook(output_item, filename):
    if not output_item.name:
        output_item.name = os.path.splitext(
            os.path.basename(filename))[0]


class ImportTable(base.ImportSingle, synode.Node):
    __doc__ = """
    Import Datasource as Table.

    :Configuration: See description for specific plugin
    :Opposite node: :ref:`Export Tables`
    :Ref. nodes: :ref:`Tables`

    For instructions on how to add or write custom plugins, see
    :ref:`pluginwriting`.

    """ + base.SuperNode._url_doc
    author = "Alexander Busck"
    version = '1.0'
    name = 'Table'
    description = 'Data source as a table'
    nodeid = 'org.sysess.sympathy.data.table.importtable'
    icon = 'import_table.svg'
    outputs = Ports([Port.Table('Imported Table', name='port1')])
    plugins = (importers.TableDataImporterBase, )

    def _output_item_filename_hook(self, output_item, filename):
        _output_item_filename_hook(output_item, filename)


class ImportTables(base.ImportMulti, synode.Node):
    __doc__ = """
    Import Datasources as Tables.

    :Configuration: See description for specific plugin
    :Opposite node: :ref:`Export Tables`
    :Ref. nodes: :ref:`Table`

    For instructions on how to add or write custom plugins, see
    :ref:`pluginwriting`.

    """ + base.SuperNode._url_doc
    author = "Alexander Busck"
    version = '1.0'
    name = 'Tables'
    description = 'Import datasources as Tables.'
    nodeid = 'org.sysess.sympathy.data.table.importtablemultiple'
    icon = 'import_table.svg'
    outputs = Ports([Port.Tables('Imported Tables', name='port1')])
    plugins = (importers.TableDataImporterBase, )

    def _output_item_filename_hook(self, output_item, filename):
        _output_item_filename_hook(output_item, filename)
