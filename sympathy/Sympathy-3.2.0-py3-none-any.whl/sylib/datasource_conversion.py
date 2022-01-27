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
import os


_input_label = (
    'Input paths relative to the current {}')

_input_description = (
    'If ticked, relative paths will be interpeted relative to the current {}, '
    'unless they are already absolute.')

_output_label = (
    'Output paths relative to the current {}')

_output_description = (
    'If ticked, output paths will be made relative to the current {}.')


def _set_input_relative_name_param(key, name, parameters):
    parameters.set_boolean(
        key, value=False,
        label=_input_label.format(name),
        description=_input_description.format(name))


def _set_output_relative_name_param(key, name, parameters):
    parameters.set_boolean(
        key, value=False,
        label=_output_label.format(name),
        description=_output_description.format(name))


def set_input_relative_topflow_param(parameters):
    _set_input_relative_name_param('relpath', 'top-flow', parameters)


def set_input_relative_subflow_param(parameters):
    _set_input_relative_name_param('subpath', 'sub-flow', parameters)


def set_output_relative_topflow_param(parameters):
    _set_output_relative_name_param('relpath', 'top-flow', parameters)


def set_output_relative_subflow_param(parameters):
    _set_output_relative_name_param('subpath', 'sub-flow', parameters)


def flow_path(subpath):
    if subpath.value:
        return os.path.dirname(subpath._state_settings['node/flow_filename'])
    else:
        return None
