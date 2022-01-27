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
from sympathy.api import node as synode
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api import json


def remove_key(key, data, remove_all):
    """ Removes a key in a JSON structure """

    def walk_and_select(subdata, lookup_state):

        if isinstance(subdata, list):
            return [walk_and_select(item, lookup_state)
                    if isinstance(item, dict) else item for item in subdata]
        elif isinstance(subdata, dict):
            was_deleted = False
            if not lookup_state["removed"] or (
                    lookup_state["removed"] and lookup_state["remove_all"]):
                try:
                    del subdata[lookup_state["key"]]
                    was_deleted = True
                    lookup_state["removed"] = True
                except KeyError:
                    pass
            if was_deleted and not remove_all:
                return subdata
            else:
                return {itemkey: (walk_and_select(item, lookup_state)
                                  if type(item) in [dict, list] else item)
                        for itemkey, item in subdata.items()}
        else:
            return subdata

    return walk_and_select(data, lookup_state={
        "key": key, "remove_all": remove_all, "removed": False})


def select_key(key, data):
    """ Finds a key in a JSON structure """
    if isinstance(data, list):
        for item in data:
            lookup = select_key(key, item)
            if lookup:
                return lookup
    elif isinstance(data, dict):
        for itemkey, item in data.items():
            if itemkey == key:
                return item
            else:
                lookup = select_key(key, item)
                if lookup:
                    return lookup
    else:
        if data == key:
            return data


def split_on_key(key, data):
    """ Split a JSON structure based on a key """
    if key == "<root>":
        if type(data) in [list, dict]:
            outjson = data
        else:
            return [data]
    else:
        selected = select_key(key, data)
        if selected:
            outjson = selected
        else:
            return [None]

    if isinstance(outjson, list):
        return [item for item in outjson]
    elif isinstance(outjson, dict):
        return [{key: item} for key, item in outjson.items()]
    else:
        return [outjson]


class SuperNode(synode.Node):
    author = 'Samuel Genheden'
    version = '0.1'

    list_atomic_keys = False
    enable_root_select = False

    @staticmethod
    def parameters_base(**kwargs):
        parameters = synode.parameters()

        parameters.set_list(
            'key', label='JSON key',
            description='The key to select',
            **kwargs, editor=synode.Util.combo_editor())
        return parameters

    def adjust_parameters(self, node_context):
        keys = list()

        def enumerate_keys(subdata):
            """ Enumerate all keys that have a list or dictionary as item """
            if isinstance(subdata, list):
                for iitem in subdata:
                    enumerate_keys(iitem)
            elif isinstance(subdata, dict):
                for key, iitem in subdata.items():
                    if type(iitem) in [dict, list] or self.list_atomic_keys:
                        keys.append(key)
                    enumerate_keys(iitem)

        if node_context.input[0].is_valid():

            if isinstance(node_context.input[0], json.File):
                jsons = node_context.input[0].get()
            else:
                jsons = [item.get() for item in node_context.input[0]]
            enumerate_keys(jsons)

        keys = list(sorted(set(keys)))
        if self.enable_root_select:
            keys.insert(0, "<root>")

        # Only update if we found a new list
        key_param = node_context.parameters['key']
        key_param.list = keys

    @staticmethod
    def execute_base(node_context, exec_func, **kwargs):

        def _make_new_file(data):
            jsonfile = json.File()
            jsonfile.set(data)
            return jsonfile

        key = node_context.parameters['key'].selected or ''

        injson = node_context.input[0].get()
        outjson = exec_func(key, injson, **kwargs)

        if isinstance(node_context.output[0], json.File):
            node_context.output[0].set(outjson)
        else:
            node_context.output[0].extend([_make_new_file(item)
                                           for item in outjson])


class SelectKeyJson(SuperNode):
    """
    Select key in a JSON structure and from that create a new JSON

    Will only select the first occurrence of the key

    For example from the JSON:

    .. code-block:: python

        {
            "version":"1.0",
            "software":"sfd",
            "items" : {
                "a":"1",
                "b":"2",
                 "c":"3"
            }
        }

    we can select the key ``"items"``, which will produce the new JSON

    .. code-block:: python

        {
            "a":"1",
            "b":"2",
            "c":"3"
        }

    """
    name = 'Select key JSON'
    icon = 'select_json_key.svg'
    tags = Tags(Tag.DataProcessing.Select)
    nodeid = 'org.sysess.sympathy.data.json.selectkeyjson'

    inputs = Ports([Port.Json('Input', name='input')])
    outputs = Ports([Port.Json('Output', name='output')])
    parameters = SuperNode.parameters_base()

    def execute(self, node_context):
        SuperNode.execute_base(node_context, select_key)


@node_helper.list_node_decorator(['input'], ['output'])
class SelectKeyJsons(SelectKeyJson):
    name = "Select key JSONs"
    nodeid = "org.sysess.sympathy.data.json.selectkeyjsons"


class RemoveKeyJson(SuperNode):
    """
    Remove a key from a JSON structure

    For example from the JSON:

    .. code-block:: python

        {
            "version":"1.0",
            "software":"sfd",
            "items" : {
                "a":"1",
                "b":"2",
                 "c":"3"
            }
        }

    we can remove the keys ``"version"`` and ``"software"`` producing the new
    JSON

    .. code-block:: python

        {
           "items" : {
                "a":"1",
                "b":"2",
                 "c":"3"
            }
        }

    """
    name = 'Remove key JSON'
    icon = 'remove_json_key.svg'
    tags = Tags(Tag.DataProcessing.TransformStructure)
    nodeid = 'org.sysess.sympathy.data.json.removekeyjson'
    list_atomic_keys = True

    inputs = Ports([Port.Json('Input', name='input')])
    outputs = Ports([Port.Json('Output', name='output')])
    parameters = SuperNode.parameters_base()
    parameters.set_boolean("all", label='Remove all', value=False,
                           description="Remove all occurences of key, "
                           "not just first")

    def execute(self, node_context):
        remove_all = node_context.parameters['all'].value
        SuperNode.execute_base(
            node_context, remove_key, remove_all=remove_all)


@node_helper.list_node_decorator(['input'], ['output'])
class RemoveKeyJsons(RemoveKeyJson):
    name = "Remove key JSONs"
    nodeid = "org.sysess.sympathy.data.json.removekeyjsons"


class SplitOnKeyJson(SuperNode):
    """
    Select key in a JSON structure and split into multiple JSONs based on that
    key.
    Will only select the first occurrence of the key
    The special key ``<root>`` splits the JSON based on the root key

    For example the JSON:

    .. code-block:: python

        {
            "version":"1.0",
            "items" : [
                {
                    "a":"1",
                    "b":"2",
                    "c":"3"
                },
                {
                    "g":"1",
                    "h":"2",
                    "j":"3"
                }
            ]
        }

    can be splitted on the key ``"items"``, which will produce two new JSONs

    .. code-block:: python

        {
            "a":"1",
            "b":"2",
            "c":"3"
        }

    and

    .. code-block:: python

        {
            "g":"1",
            "h":"2",
            "j":"3"
        }

    """
    name = 'Split on key JSON'
    icon = 'split_json_key.svg'
    tags = Tags(Tag.DataProcessing.TransformStructure)
    description = 'Split a JSON structure into multiple JSONs'
    nodeid = 'org.sysess.sympathy.data.json.splitonkeyjson'

    inputs = Ports([Port.Json('Input', name='input')])
    outputs = Ports([Port.Jsons('Output', name='output')])
    parameters = SuperNode.parameters_base(value_names=['<root>'])
    enable_root_select = True

    def execute(self, node_context):
        SuperNode.execute_base(node_context, split_on_key)


@node_helper.list_node_decorator(['input'], ['output'])
class SplitOnKeyJsons(SplitOnKeyJson):
    name = "Split on key JSONs"
    nodeid = "org.sysess.sympathy.data.json.splitonkeyjsons"
