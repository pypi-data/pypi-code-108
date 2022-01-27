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
from sylib.importer import base
from sympathy.api import node as synode
from sympathy.api import importers
from sympathy.api.nodeconfig import Port, Ports


class ImportText(base.ImportSingle, synode.Node):
    __doc__ = """
    Import data as a Text.

    :Opposite node: :ref:`Export Texts`
    :Ref. nodes: :ref:`Texts`

    For instructions on how to add or write custom plugins, see
    :ref:`pluginwriting`.

    """ + base.SuperNode._url_doc

    author = "Erik der Hagopian"
    version = '1.0'
    name = 'Text'
    description = 'Data source as text'
    nodeid = 'org.sysess.sympathy.data.text.importtext'
    icon = 'import_text.svg'
    outputs = Ports([Port.Text('Imported Text', name='port1')])
    plugins = (importers.TextDataImporterBase, )


class ImportTexts(base.ImportMulti, synode.Node):
    __doc__ = """
    Import data as Texts.

    :Opposite node: :ref:`Export Texts`
    :Ref. nodes: :ref:`Text`

    For instructions on how to add or write custom plugins, see
    :ref:`pluginwriting`.

    """ + base.SuperNode._url_doc

    author = "Erik der Hagopian"
    version = '1.0'
    name = 'Texts'
    description = 'Data source as Texts'
    nodeid = 'org.sysess.sympathy.data.text.importtexts'
    icon = 'import_text.svg'
    outputs = Ports([Port.Texts('Imported Texts', name='port1')])
    plugins = (importers.TextDataImporterBase, )
