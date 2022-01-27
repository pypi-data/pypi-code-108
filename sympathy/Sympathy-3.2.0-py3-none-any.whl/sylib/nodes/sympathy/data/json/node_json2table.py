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
from sympathy.api.exceptions import SyDataError
from sylib.json_table import (JsonTableWidget, JsonTable,
                              add_jsontable_parameters, TABLE_KIND)


def parameters_base():
    parameters = synode.parameters()
    add_jsontable_parameters(parameters)
    return parameters


class JsonToTable(synode.Node):
    """
    Convert a JSON file to a Table

    There are two kinds of tables that can be created:

        * Single row – where the JSON structure is simply flattened
        * Multiple rows - where the JSON structure is recursively expanded to
          create several rows

    If a single-row table is created, there is an option to minimize the
    column names to remove unnecessary path information from the JSON keys.

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

    we can create the following single-row table

    .. code-block:: python

        version    software    items.a    items.b    items.c
        ----------------------------------------------------
        1.0        sfd         1          2          3

    and the column names can be *minimized* to

     .. code-block:: python

        version    software    a    b    c
        -------------------------------------
        1.0        sfd         1    2    3


    If a multiple rows-table is created, the recursive algorithm might identify
    keys and therefore columns that are lacking some values. One can choose to
    fill in the missing values with a **empty string**, a **nan** string or
    **mask** the value.

    For example from the JSON:

    .. code-block:: python

        {
            "version":"1.0",
            "software":"sfd",
            "items" : [
                {
                    "a":"1",
                    "b":"2",
                    "c":"3"
                },
                {
                    "a":"67",
                    "b":"77",
                    "d":"97"
                }
            ]
        }

    we can create the following multiple-rows table

    .. code-block:: python

        version    software    a    b    c    d
        -------------------------------------------
        1.0        sfd         1    2    3    ---
        1.0        sfd         67   77   ---  97

    where the ``c`` column is masked in the second row and the ``d``
    column is masked in the first row.

    If the algorithm that creates tnhe multi-row table fails to produce
    the desired table, it might be worth using other nodes to remove,
    select or split the JSON structure on some key.
    """
    name = 'JSON to Table'
    author = 'Samuel Genheden'
    version = '0.1'
    icon = 'json2table.svg'
    tags = Tags(Tag.DataProcessing.Convert)
    nodeid = 'org.sysess.sympathy.data.json.jsontotable'

    inputs = Ports([Port.Json('Input JSON object', name='input')])
    outputs = Ports([Port.Table('Output table', name='output')])
    parameters = parameters_base()

    def exec_parameter_view(self, node_context):
        return JsonTableWidget(node_context.parameters)

    def execute(self, node_context):
        table_kind = node_context.parameters['table_kind'].value
        min_col_names = node_context.parameters['minimize_col_names'].value
        nomask = node_context.parameters['nomask'].value

        tbl = JsonTable(node_context.input[0])
        if not tbl.is_group():
            value = node_context.input[0].get()
            raise SyDataError(
                f'Inputs must be list or dict, it is '
                f'{value} ({type(value).__name__}).')
        if table_kind == TABLE_KIND["SINGLE"]:
            node_context.output[0].source(
                tbl.create_single_row_table(min_col_names))
        else:
            node_context.output[0].source(
                tbl.create_multiple_rows_table(nomask))


@node_helper.list_node_decorator(['input'], ['output'])
class JsonsToTables(JsonToTable):
    name = "JSONs to Tables"
    nodeid = "org.sysess.sympathy.data.json.jsonstotables"
