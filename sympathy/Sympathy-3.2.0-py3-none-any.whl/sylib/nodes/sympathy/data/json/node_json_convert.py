# This file is part of Sympathy for Data.
# Copyright (c) 2019, Combine Control Systems AB
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
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api import exceptions
from sympathy.api import json


class JsonToDict(synode.Node):
    """
    Convert from JSON input containing a top-level dict to Sympathy
    dictionary (sydict) containing JSON.
    """

    author = 'Erik der Hagopian'
    icon = 'fromjson.svg'
    name = 'Json to Dict'
    nodeid = 'org.sysess.sympathy.json.jsontodict'
    tags = Tags(Tag.DataProcessing.Convert)

    inputs = Ports([Port.Json('JSON', name='json')])
    outputs = Ports([Port.Custom('{json}', 'JSON dict', name='json_dict')])

    def execute(self, node_context):
        data = node_context.input['json'].get()
        if not isinstance(data, dict):
            raise exceptions.SyDataError(
                'Conversion from json to {json} requires top-level dict')
        else:
            output = node_context.output['json_dict']
            for k, v in data.items():
                item = json.File()
                item.set(v)
                output[k] = item


@node_helper.list_node_decorator(['json'], ['json_dict'])
class JsonsToDicts(JsonToDict):
    nodeid = 'org.sysess.sympathy.json.jsonstodicts'
    name = 'Jsons to Dicts'


class DictToJson(synode.Node):
    """
    Convert from Sympathy dictionary (sydict) input containing JSON to JSON
    dictionary.
    """

    author = 'Erik der Hagopian'
    icon = 'tojson.svg'
    name = 'Dict to Json'
    nodeid = 'org.sysess.sympathy.json.dicttojson'
    tags = Tags(Tag.DataProcessing.Convert)

    inputs = Ports([Port.Custom('{json}', 'JSON dict', name='json_dict')])
    outputs = Ports([Port.Json('JSON', name='json')])

    def execute(self, node_context):
        node_context.output['json'].set(
            {k: v.get() for k, v in node_context.input['json_dict'].items()})


class JsonToList(synode.Node):
    """
    Convert from JSON input containing a top-level list to a Sympathy
    list (sylist) containing JSON.
    """

    author = 'Erik der Hagopian'
    icon = 'fromjson.svg'
    name = 'Json to List'
    nodeid = 'org.sysess.sympathy.json.jsontolist'
    tags = Tags(Tag.DataProcessing.Convert)

    inputs = Ports([Port.Json('JSON', name='json')])
    outputs = Ports([Port.Custom('[json]', 'JSON list', name='json_list')])

    def execute(self, node_context):
        data = node_context.input['json'].get()
        if not isinstance(data, list):
            raise exceptions.SyDataError(
                'Conversion from json to [json] requires top-level list')
        else:
            output = node_context.output['json_list']
            for v in data:
                item = json.File()
                item.set(v)
                output.append(item)


@node_helper.list_node_decorator(['json'], ['json_list'])
class JsonsToLists(JsonToList):
    nodeid = 'org.sysess.sympathy.json.jsonstolists'
    name = 'Jsons to Lists'


class ListToJson(synode.Node):
    """
    Convert from Sympathy list (sylist) input containing JSON to JSON
    list.
    """

    author = 'Erik der Hagopian'
    icon = 'tojson.svg'
    name = 'List to Json'
    nodeid = 'org.sysess.sympathy.json.listtojson'
    tags = Tags(Tag.DataProcessing.Convert)

    inputs = Ports([Port.Custom('[json]', 'JSON list', name='json_list')])
    outputs = Ports([Port.Json('JSON', name='json')])

    def execute(self, node_context):
        node_context.output['json'].set(
            [v.get() for v in node_context.input['json_list']])
