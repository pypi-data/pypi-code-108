# This file is part of Sympathy for Data.
# Copyright (c) 2017 Combine Control Systems AB
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
import copy
import sys
import os
import datetime

from sympathy.utils import log
from collections import abc

from sympathy.utils import environment
from sympathy.platform import parameter_helper

core_logger = log.get_logger('core')
env_logger = log.get_logger('core.env')

_instance = None


def error_message(msg):
    timestamp = datetime.datetime.now().replace(microsecond=0).isoformat()
    env_logger.error(
        u'{}  ERROR    {}\n'.format(timestamp, msg))


def warning_message(msg):
    timestamp = datetime.datetime.now().replace(microsecond=0).isoformat()
    env_logger.warning(
        u'{}  WARNING    {}\n'.format(timestamp, msg))


def expanded_node_dict(old_node_dict, workflow_variables):
    node_dict = copy.deepcopy(old_node_dict)

    def inner(parameter_dict):
        if isinstance(parameter_dict, dict):
            parameter_type = parameter_dict.get('type')
            if parameter_type in ['group', 'page']:
                for v in parameter_dict.values():
                    inner(v)
            else:
                cls = parameter_helper.get_parameter_cls(parameter_type)
                if cls:
                    copy_dict = copy.deepcopy(parameter_dict)
                    try:
                        obj = cls.from_dict(parameter_dict)
                        expanded = obj._expand_variables(variables)
                    except Exception:
                        expanded = False

                    if not expanded:
                        parameter_dict.clear()
                        parameter_dict.update(copy_dict)
                    else:
                        # Remove harmless parameters added, for example,
                        # description.
                        for key in set(parameter_dict).difference(copy_dict):
                            del parameter_dict[key]
    try:
        data = node_dict['parameters']['data']
    except Exception:
        data = None
    else:
        variables = ExecutionEnvironment(workflow_variables)
        inner(data)
    return node_dict


def expand_variables(string):
    return environment.expand_variables(string, instance())


class ExecutionEnvironment(abc.Mapping):

    def __init__(self, workflow_variables):
        self._workflow_variables = workflow_variables

    def get(self, name, warn=False):
        value = None
        if sys.platform == 'win32':
            value = instance().shell_variables().get(name.upper())
        if value is None:
            value = (
                instance().shell_variables().get(name) or
                self._workflow_variables.get(name) or
                instance().global_variables().get(name))
        if value is None and warn:
            # Remove this warning and simplify the code a bit?
            warning_message(
                f'Cannot find variable {name} in the environment.')
        return value

    def __getitem__(self, name):
        value = self.get(name, warn=True)
        if value is None:
            raise KeyError(name)
        else:
            return value

    def __contains__(self, name):
        return self[name] is not None

    def __iter__(self):
        items = {}
        for variables in [
                instance().global_variables(),
                self._workflow_variables,
                instance().shell_variables(),
        ]:
            items.update(dict.fromkeys(variables.keys()))

        if sys.platform == 'win32':
            for k in instance.shell_variables():
                items[k.upper()] = None

        for k in items:
            yield k

    def __len__(self):
        return len(list(iter(self)))


class Environment(abc.Mapping):
    def __init__(self):
        self._shell_variables = {}
        self._global_variables = {}
        self._shell_variables.update(os.environ.items())

    def shell_variables(self):
        return self._shell_variables

    def global_variables(self):
        return self._global_variables

    def set_shell_variables(self, variable_dict):
        self._shell_variables.clear()
        self._shell_variables.update(variable_dict)

    def set_global_variables(self, variable_dict):
        self._global_variables.clear()
        self._global_variables.update(variable_dict)

    def __getitem__(self, name):
        return (self._shell_variables.get(name) or
                self._global_variables.get(name))

    def __contains__(self, name):
        return self[name] is not None

    def __iter__(self):
        items = {}
        items.update(dict.fromkeys(self._global_variables.keys()))
        items.update(dict.fromkeys(self._shell_variables.keys()))
        for k in items:
            yield k

    def __len__(self):
        return len(list(iter(self)))

    def to_dict(self):
        return {
            'shell': self._shell_variables,
            'global': self._global_variables,
        }

    def set_from_dict(self, data):
        self.set_global_variables(data['global'])
        self.set_shell_variables(data['shell'])


def instance():
    global _instance
    if _instance is None:
        _instance = Environment()
    return _instance
