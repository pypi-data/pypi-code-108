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
from collections import abc
from sympathy.platform import state
from .. utils import prim


def _settings():
    return state.node_state().attributes.get('worker_settings', {})


def get_default_dir():
    default_dir = _settings().get('default_folder')
    if not default_dir:
        return prim.get_home_dir()
    return default_dir


def get_show_message_area():
    return _settings()['Gui/show_message_area']


def get_code_editor_theme():
    return _settings()['Gui/code_editor_theme']


def get_flow_filename():
    default_dir = _settings().get('flow_filename')
    if not default_dir:
        return prim.get_home_dir()
    return default_dir


class Settings(abc.Mapping):
    """Readable dictlike object of worker settings available."""

    def __init__(self):
        self._attributes = state.node_state().attributes

    def __getitem__(self, key):
        return self._attributes.get('worker_settings', {})[key]

    def __iter__(self):
        return iter(self._attributes.get('worker_settings', {}))

    def __len__(self):
        return len(list(iter(self)))


def settings():
    return Settings()
