# This file is part of Sympathy for Data.
# Copyright (c) 2017, Combine Control Systems AB
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


NAN = 'Complement with nan or empty string'
MASK = 'Mask missing values'


def set_fill_strategy_param(params, value):
    params.set_list(
        'fill_strategy', value=[value], plist=[NAN, MASK],
        label='Complement strategy',
        description=('When "{}" is selected missing columns will be replaced '
                     'by columns of nan or empty strings. '
                     'When "{}" is selected missing columns will be result in '
                     'masked values'.format(NAN, MASK)),
        editor=synode.Util.combo_editor())


def base_params():
    parameters = synode.parameters()
    parameters.set_boolean(
        'fill', value=True, label='Complement missing columns',
        description='Select if columns that are not represented in all '
                    'Tables should be complemented')
    set_fill_strategy_param(parameters, 1)
    parameters.set_string(
        'output_index',
        label='Output index',
        value='',
        description=('Specify name for output index column. '
                     'If left empty, no index column will be created'),
        editor=synode.Util.lineedit_editor('(none)'))
    parameters.set_integer(
        'minimum_increment',
        value=1,
        label='Increment for empty tables',
        description=('Specify the increment in the outgoing index column '
                     'for tables with no rows. Either 1 or 0.'),
        editor=synode.Util.bounded_spinbox_editor(0, 1, 1))

    return parameters


def base_controller():
    controller = (
        synode.controller(
            when=synode.field('fill', 'checked'),
            action=synode.field('fill_strategy', 'enabled')),
        synode.controller(
            when=synode.field('output_index', 'value', ''),
            action=synode.field('minimum_increment', 'disabled')))
    return controller


def base_values(parameters):
    input_index = ''
    try:
        output_index = parameters['output_index'].value
    except Exception:
        output_index = ''
    try:
        minimum_increment = parameters['minimum_increment'].value
    except Exception:
        minimum_increment = 0

    try:
        fill = parameters['fill'].value
    except Exception:
        fill = False

    if fill:
        try:
            if parameters['fill_strategy'].selected == MASK:
                fill = None
        except Exception:
            pass
    return (input_index, output_index, minimum_increment, fill)
