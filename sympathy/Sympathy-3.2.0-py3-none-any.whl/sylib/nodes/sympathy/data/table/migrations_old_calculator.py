# This file is part of Sympathy for Data.
# Copyright (c) 2020, Combine Control Systems AB
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
import re
import copy

from sympathy.platform import migrations
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags

import sylib.calculator.plugins


def _update_calc_list(calc_list):
    def get_res_regex(ignored_name):
        # Build a regex which tries to match all references to
        # other calculated columns.
        names_regex = r'|'.join(
            re.escape(name) for name in calcs.keys() - {ignored_name})
        res_regex = r'\${(' + names_regex + r')}'
        return res_regex

    calcs = {}
    for line in calc_list:
        name, calc = line.split(' = ', 1)
        name = re.sub(r'\${([^{}]+)}', r"\1", name)
        calcs[name] = calc

    new_calc_list = []
    for name, calc in calcs.items():
        calc = re.sub(r'\btable\b', 'arg', calc)
        calc = re.sub(get_res_regex(name), r"res['\1']", calc)
        calc = re.sub(r'\${([^{}]+)}', r"arg['\1']", calc)
        new_calc_list.append(f"{name} = {calc}")
    return new_calc_list


class CalculatorTableUpdateParameters(migrations.UpdateParametersMigration):
    nodeid = 'org.sysess.sympathy.data.table.calculatortable'
    to_version = str(migrations.updated_version)

    FAILURE_STRATEGIES = {'Exception': 0, 'Skip calculation': 1}

    def _add_base_parameters(self, parameters):
        parameters.set_list(
            'calc_list', label='List of calculations',
            description='List of calculations.',
            _old_list_storage=True)

        parameters.set_boolean(
            'copy_input', value=False, label='Copy input',
            description=('If enabled the incoming data will be copied to the '
                         'output before running the calculations. This '
                         'requires that the results will all have the same '
                         'length. An exception will be raised if the lengths '
                         'of the outgoing results differ.'))
        parameters.set_list(
            'fail_strategy', label='Action on calculation failure',
            list=self.FAILURE_STRATEGIES.keys(), value=[0],
            description='Decide how a failed calculation should be handled',
            editor=synode.editors.combo_editor())

    def updated_definition(self):
        parameters = synode.parameters()
        self._add_base_parameters(parameters)
        return parameters


class CalculatorTablesUpdateParameters(CalculatorTableUpdateParameters):
    nodeid = 'org.sysess.sympathy.data.table.calculator'

    def _add_same_length_res_parameter(self, parameters):
        parameters.set_boolean(
            'same_length_res',
            label='Put results in common outputs.',
            value=True,
            description=('Gather all the results generated '
                         'from an incoming data into a '
                         'common output table. This '
                         'requires that the results all '
                         'have the same length. An error '
                         'will be given if the lengths of '
                         'the outgoing results differ.'))

    def updated_definition(self):
        parameters = super().updated_definition()
        self._add_same_length_res_parameter(parameters)
        return parameters

    def update_parameters(self, old_params):
        # Old nodes without the same_length_res option work the same way as if
        # they had the option, set to False.
        if 'same_length_res' not in old_params:
            self._add_same_length_res_parameter(old_params)
            old_params['same_length_res'].value = False


class CalculatorTable(migrations.NodeMigration):
    nodeid = 'org.sysess.sympathy.data.table.calculatortable'
    from_version = migrations.updated_version
    to_version = migrations.updated_version

    def forward_status(self):
        old_parameters = self.get_parameters()
        if ('same_length_res' in old_parameters
                and not old_parameters['same_length_res'].value):
            return (migrations.NotAvailable,
                    'The option "Put results in common outputs" '
                    'can no longer be disabled.')
        return (migrations.Imperfect,
                "This migration has some limitations. Please double check "
                "that the new node produces the same result as the old one.")

    def forward_node(self):
        return dict(
            author=('Greger Cronquist, Magnus Sandén, Sara Gustafzelius & '
                    'Benedikt Ziegler'),
            description='Create columns by evaluating python calculations.',
            icon='calculator.svg',
            tags=Tags(Tag.DataProcessing.Calculate),
            plugins=(sylib.calculator.plugins.ICalcPlugin, ),
            name='Calculator',
            nodeid='org.sysess.sympathy.data.table.calculatorgeneric',
            related=['org.sysess.sympathy.data.table.calculatorgenericlist'],
            inputs=Ports([Port.Custom(
                '<a>', 'Generic Input', name='port0', n=(0, 1, 1))]),
            outputs=Ports([Port.Table(
                'Table with results from the calculations.', name='port1')]),
        )

    def forward_parameters(self, old_parameters):
        new_parameters = copy.deepcopy(old_parameters)

        # Delete old parameter:
        try:
            del new_parameters['same_length_res']
        except KeyError:
            # Really old versions of the old calculator node didn't have this
            # parameter.
            pass

        # Add new parameter:
        new_parameters.set_string(
            'calc_attrs_dict',
            value='[]',
            description='Calculation attributes as json dict-list-string!')

        # Update calculation list:
        new_parameters['calc_list'].list = _update_calc_list(
            new_parameters['calc_list'].list)

        return new_parameters

    def forward_ports(self, old_input_ports, old_output_ports):
        # Port names are the same
        return old_input_ports, old_output_ports


class CalculatorTables(CalculatorTable):
    nodeid = 'org.sysess.sympathy.data.table.calculator'

    def forward_node(self):
        return dict(
            author=('Greger Cronquist, Magnus Sandén, Sara Gustafzelius & '
                    'Benedikt Ziegler'),
            description='Create columns by evaluating python calculations.',
            icon='calculator.svg',
            tags=Tags(Tag.DataProcessing.Calculate),
            plugins=(sylib.calculator.plugins.ICalcPlugin, ),
            name='Calculator List',
            nodeid='org.sysess.sympathy.data.table.calculatorgenericlist',
            related=['org.sysess.sympathy.data.table.calculatorgeneric'],
            inputs=Ports([Port.Custom(
                '[<a>]', 'Generic Input', name='port0')]),
            outputs=Ports([Port.Tables(
                'Tables with results from the calculations.', name='port1')]),
        )
