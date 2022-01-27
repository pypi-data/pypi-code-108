# This file is part of Sympathy for Data.
# Copyright (c) 2018, Combine Control Systems AB
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
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api import importers


class ImportJson(base.ImportSingle, synode.Node):
    __doc__ = """
    Import a JSON or XML file to a JSON structure.

    If ``filtetype``is set to ``auto`` the program will try to guess if it is
    an XML or JSON file, based on the file extension and the content of the
    first line of the file.

    """ + base.SuperNode._url_doc
    author = 'Samuel Genheden'
    version = '0.1'
    icon = 'import_json_xml.svg'
    tags = Tags(Tag.Input.Import)
    name = 'JSON'
    nodeid = 'org.sysess.sympathy.data.json.importjson'
    plugins = (importers.JsonDataImporterBase, )
    outputs = Ports([Port.Json('Imported Json', name='port1')])


class ImportJsons(base.ImportMulti, synode.Node):
    __doc__ = """
    Import multiple JSON or XML files to a multiple JSON objects.

    """ + base.SuperNode._url_doc
    author = 'Samuel Genheden'
    version = '0.1'
    icon = 'import_json_xml.svg'
    tags = Tags(Tag.Input.Import)
    name = 'JSONs'
    nodeid = 'org.sysess.sympathy.data.json.importjsons'
    plugins = (importers.JsonDataImporterBase, )
    outputs = Ports([Port.Jsons('Imported Jsons', name='port1')])
