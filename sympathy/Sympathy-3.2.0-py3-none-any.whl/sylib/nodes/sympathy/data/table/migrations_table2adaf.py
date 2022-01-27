# This file is part of Sympathy for Data.
# Copyright (c) 2021, Combine Control Systems AB
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
from sympathy.platform import migrations


class Table2ADAF300(migrations.UpdateParametersMigration):
    nodeid = 'org.sysess.sympathy.data.table.table2adaf'

    def updated_definition(self):
        parameters = synode.parameters()
        parameters.set_list(
            'export_to_group', plist=['Meta', 'Result', 'Time series'],
            label='Export to group',
            description=(
                'Choose a container in the ADAF as target for the export'),
            editor=synode.Editors.combo_editor())

        parameters.set_string('system', label='Timeseries system name',
                              description=('Specify name of the created '
                                           'system in the ADAF'),
                              value='system0')
        parameters.set_string('raster', label='Timeseries raster name',
                              description=('Specify name of the created '
                                           'raster in the ADAF'),
                              value='')
        parameters.set_list('tb',
                            label="Time basis column",
                            description=('Select a column in the Table '
                                         'which will be the time basis '
                                         'signal in the ADAF'),
                            editor=synode.Editors.combo_editor(filter=True))
        return parameters

    def update_parameters(self, old_params):
        if 'tb' in old_params:
            old_params['tb'].editor = synode.Editors.combo_editor(
                filter=True)


class Tables2ADAFs300(Table2ADAF300):
    nodeid = 'org.sysess.sympathy.data.table.tables2adafs'


class UpdateADAFWithTable300(Table2ADAF300):
    nodeid = 'org.sysess.sympathy.data.table.updateadafwithtable'


class UpdateADAFsWithTables300(Table2ADAF300):
    nodeid = 'org.sysess.sympathy.data.table.updateadafswithtables'


class Table2ADAF310(migrations.Migration):
    nodeid = 'org.sysess.sympathy.data.table.table2adaf'
    from_version = migrations.updated_version
    to_version = '3.1.0'

    def forward_status(self):
        return migrations.Perfect

    def forward_parameters(self, old_parameters):
        group_value = old_parameters['export_to_group'].selected
        del old_parameters['export_to_group']
        old_parameters.set_string(
            'export_to_group', label='Target group', order=0,
            value=group_value,
            description=('Choose an ADAF container as target'),
            editor=synode.Util.combo_editor(
                options=['Meta', 'Result', 'Time series']))
        old_parameters['system'].label = "System name"
        old_parameters['raster'].label = "Raster name"
        old_tb = old_parameters['tb'].selected or ''
        del old_parameters['tb']
        old_parameters.set_string(
            'tb',
            value=old_tb,
            label="Time basis column",
            description=('Select a column in the Table which will '
                         'become the time basis of the new raster'),
            editor=synode.Editors.combo_editor(filter=True, edit=True))
        return old_parameters


class Tables2ADAFs310(Table2ADAF310):
    nodeid = 'org.sysess.sympathy.data.table.tables2adafs'


class UpdateADAFWithTable310(Table2ADAF310):
    nodeid = 'org.sysess.sympathy.data.table.updateadafwithtable'

    def forward_parameters(self, old_parameters):
        old_parameters['system'].editor = synode.Editors.combo_editor(
            edit=True)
        old_parameters['raster'].editor = synode.Editors.combo_editor(
            edit=True)
        return super().forward_parameters(old_parameters)


class UpdateADAFsWithTables310(UpdateADAFWithTable310):
    nodeid = 'org.sysess.sympathy.data.table.updateadafswithtables'
