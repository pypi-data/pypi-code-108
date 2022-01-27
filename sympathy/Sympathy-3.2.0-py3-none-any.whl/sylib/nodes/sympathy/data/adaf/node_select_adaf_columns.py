# This file is part of Sympathy for Data.
# Copyright (c) 2015, Combine Control Systems AB
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
If you're only interested in some of the data in an ADAF (maybe for performance
reasons) you can use e.g. :ref:`Select columns in ADAF with structure Table`.

The Table/Tables argument shall have four columns, which must be named Type,
System, Raster, and Parameter. These columns hold the names of the
corresponding fields in the ADAF/ADAFs.
"""
import contextlib
from collections import OrderedDict
from sympathy.api import node, table
from sympathy.api import node_helper, dtypes
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags

from sympathy.api.exceptions import SyDataError, sywarn


def actual_selection(info, selection, complement):

    def actual_keys(igroup, sgroup):
        if complement:
            keys = [key for key in igroup if key not in sgroup]
        else:
            keys = [key for key in igroup if key in sgroup]

        len_keys = len(keys)
        if len_keys and len_keys == len(igroup):
            return 'all'
        return keys

    meta_selection = actual_keys(
        info['meta']['columns'].keys(), selection['meta'])
    res_selection = actual_keys(
        info['res']['columns'].keys(), selection['res'])
    systems = selection['sys']
    systems_selection = {}

    for system_name, isys in info['sys'].items():
        raster_selection = systems_selection.setdefault(system_name, {})
        ssys = systems.get(system_name, {})

        for raster_name, iraster in isys.items():
            raster_selection[raster_name] =  actual_keys(
                iraster['signals'], ssys.get(raster_name, []))

    return {
        'meta': meta_selection, 'res': res_selection, 'sys': systems_selection
    }


def apply_selection(in_adaf, out_adaf, selection):
    meta_selection = selection['meta']
    res_selection = selection['res']
    systems_selection = selection['sys']

    out_adaf.set_source_id(in_adaf.source_id())

    def forward_group(in_data, out_data, out_keys):
        in_table = in_data.to_table()
        if out_keys == 'all':
            out_table = in_table
        else:
            out_table = table.File()
            for key in out_keys:
                out_table.update_column(key, in_table)

        out_data.from_table(out_table)

    if meta_selection:
        forward_group(in_adaf.meta, out_adaf.meta, meta_selection)

    if res_selection:
        forward_group(in_adaf.res, out_adaf.res, res_selection)

    in_systems = {}
    out_systems = {}

    for system_name, system_selection in systems_selection.items():
        for raster_name, raster_selection in system_selection.items():

            if raster_selection:
                if system_name in out_systems:
                    out_sys = out_systems[system_name]
                else:
                    out_sys = out_adaf.sys.create(system_name)
                    out_systems[system_name] = out_sys

                if system_name in in_systems:
                    in_sys = in_systems[system_name]
                else:
                    in_sys = in_adaf.sys[system_name]
                    in_systems[system_name] = in_sys

                in_raster = in_sys[raster_name]

                if raster_selection == 'all':
                    out_sys.copy(raster_name, in_sys)
                else:
                    out_raster = out_sys.create(raster_name)
                    out_raster.update_basis(in_raster)
                    for key in raster_selection:
                        out_raster.update_signal(key, in_raster)


def build_selection(selection):
    selection_columns = ['Type', 'System', 'Raster', 'Parameter']
    columns = selection.column_names()

    if not all([column_name in columns
                for column_name in selection_columns]):
        raise SyDataError(
            'Selection Table must have the following columns: {}\n'
            'Using ADAF structure to Table ensures it.'.format(
                ', '.join(selection_columns)))

    narrow_selection = table.File()

    for column in selection_columns:
        narrow_selection.update_column(column, selection)

        kind = selection.column_type(column).kind
        if kind != 'U':
            msg = (
                'Selection column "{}" needs to be in text format, it is {}. '
                'While this is true, the selection will be ignored.'
                .format(column, dtypes.typename_from_kind(kind)))
            warn('col_type', msg)
    meta = []
    res = []
    syss = {}

    for typec, systemc, rasterc, parameterc in narrow_selection.to_rows():
        if typec == 'Metadata':
            meta.append(parameterc)
        elif typec == 'Result':
            res.append(parameterc)
        elif typec == 'Timeseries':
            sys = syss.setdefault(systemc, {})
            raster = sys.setdefault(rasterc, [])
            raster.append(parameterc)

    return {'meta': meta, 'res': res, 'sys': syss}


def _set_complement_parameter(parameter_root):
    parameter_root.set_boolean(
        'complement', value=False,
        label='Remove selected columns',
        description=(
            'When enabled, the selected columns will be removed. '
            'When disabled, the non-selected columns will be '
            'removed.'))


_warn_once = False
_warn_categories = set()


@contextlib.contextmanager
def set_warn_once():
    global _warn_once
    global _warn_categories

    _warn_once = True
    _warn_categories = set()
    yield
    _warn_once = False
    _warn_categories = set()


def warn(category, msg):
    global _warn_once
    global _warn_categories

    if not _warn_once:
        sywarn(msg)
    elif category not in _warn_categories:
        sywarn(msg)
        _warn_categories.add(category)


class SelectColumnsADAFWithTable(node.Node):
    name = 'Select columns in ADAF with structure Table'
    author = 'Erik der Hagopian'
    version = '1.0'
    icon = 'select_adaf_columns.svg'
    description = (
        'Select the columns to keep in ADAF using selection table created by '
        'ADAF structure to table')
    nodeid = 'org.sysess.sympathy.data.adaf.selectcolumnsadafwithtable'
    tags = Tags(Tag.DataProcessing.Select)

    inputs = Ports([
        Port.Table('ADAF structure selection', name='selection'),
        Port.ADAF('ADAF data matched with selection', name='data')])
    outputs = Ports([
        Port.ADAF('ADAF data after selection', name='data')])

    parameters = node.parameters()
    _set_complement_parameter(parameters)

    def execute(self, node_context):
        selection = node_context.input['selection']
        in_data = node_context.input['data']
        out_data = node_context.output['data']
        complement = node_context.parameters['complement'].value

        if in_data.is_empty():
            # Result should be empty.
            pass
        elif selection.is_empty():
            if complement:
                out_data.source(in_data)
            else:
                # Result should be empty.
                pass
        else:
            selection = build_selection(selection)
            selection = actual_selection(in_data.info(), selection, complement)
            apply_selection(in_data, out_data, selection)


@node_helper.list_node_decorator(['data'], ['data'])
class SelectColumnsADAFsWithTable(SelectColumnsADAFWithTable):
    name = 'Select columns in ADAFs with structure Table'
    nodeid = 'org.sysess.sympathy.data.adaf.selectcolumnsadafswithtable'

    def execute(self, node_context):
        with set_warn_once():
            super().execute(node_context)


@node_helper.list_node_decorator(['selection', 'data'], ['data'])
class SelectColumnsADAFsWithTables(SelectColumnsADAFWithTable):
    name = 'Select columns in ADAFs with structure Tables'
    nodeid = 'org.sysess.sympathy.data.adaf.selectcolumnsadafswithtables'

    def execute(self, node_context):
        with set_warn_once():
            super().execute(node_context)
