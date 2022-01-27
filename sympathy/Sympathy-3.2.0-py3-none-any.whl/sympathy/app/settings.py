# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
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
import copy
import uuid
from contextlib import contextmanager

import Qt.QtCore as QtCore

from . import qt_support
from . import environment_variables

SETTINGS_MAJOR_VERSION = 2
SETTINGS_MINOR_VERSION = 0
SETTINGS_MAINTENANCE_VERSION = 0

settings_instance = None
properties_instance = None

show_message_area_choice = [
    "Automatic",
    "Always",
    "Never",
    "After first message"]

(show_message_area_automatic,
 show_message_area_always,
 show_message_area_never,
 show_message_area_after_first) = show_message_area_choice

session_temp_files_choice = [
    'Keep',
    'Remove when closing flow',
    'Remove when closing application',
    'Remove unused files']

(session_temp_files_keep,
 session_temp_files_remove_flow,
 session_temp_files_remove_application,
 session_temp_files_remove_unused) = session_temp_files_choice


credential_array_key = 'Credential'
credential_action_choice = [
    'Allow',
    'Ask',
    'Deny']

(credential_action_allow,
 credential_action_ask,
 credential_action_deny) = credential_action_choice

# Removed, for now. Maybe useful later on depending on future user interfaces.
credential_action_choice.remove(credential_action_ask)


on_start_choice = [
    "Nothing",
    "New flow",
    "Last session's flows"]

(on_start_nothing,
 on_start_new_flow,
 on_start_last_session) = on_start_choice

stored_permanent = set([
    'user_id',
])

snap_types = [
    "Grid",
    "Subgrid"]

(snap_type_grid,
 snap_type_subgrid) = snap_types


def migrate_old_settings(old_settings, new_settings):
    """Modify the old settings to make use of settings that have changed."""
    if old_settings.contains('Gui/library_type'):
        v = old_settings.value('Gui/library_type')
        if v in ['Separated Tag layout', 'Disk layout']:
            new_settings.setValue('Gui/library_separated', True)

    if (old_settings.contains('save_session')
            and old_settings.value('save_session')):
        new_settings.setValue('Gui/on_start', on_start_last_session)
    elif (old_settings.contains('new_flow_on_start')
            and not old_settings.value('new_flow_on_start')):
        new_settings.setValue('Gui/on_start', on_start_nothing)
    else:
        new_settings.setValue('Gui/on_start', on_start_new_flow)


class Properties:

    _sessions_folder_var = 'SY_OVERRIDE_TEMP_PATH'

    @property
    def sessions_folder_override(self):
        return os.environ.get(self._sessions_folder_var)

    @property
    def sessions_folder_override_description(self):
        res = ''
        override = self.sessions_folder_override
        if override:
            res = (
                'Path is controlled by the external environment variable '
                f'SY_OVERRIDE_TEMP_PATH which points to: {override}')
        return res

    default_sessions_folder = os.path.join(
        os.path.normpath(
            qt_support.cache_location()), 'Sessions')

    @property
    def sessions_folder(self):
        temp_folder = self.sessions_folder_override
        if not temp_folder:
            temp_folder = self['temp_folder']
        return environment_variables.expand_variables(temp_folder)

    @sessions_folder.setter
    def sessions_folder(self, value):
        if self.sessions_folder != value:
            self['temp_folder'] = value

    @property
    def session_temp_files(self):
        return self['session_temp_files']

    @session_temp_files.setter
    def session_temp_files(self, value):
        if self.session_temp_files != value:
            self['session_temp_files'] = value


class Keys:

    debug_graphviz_path = 'Debug/graphviz_path'
    debug_profile_path_type = 'Debug/profile_path_type'
    gui_library_separated = 'Gui/library_separated'
    gui_library_show_hidden = 'Gui/library_show_hidden'
    gui_library_matcher_type = 'Gui/library_matcher_type'
    gui_library_highlighter_type = 'Gui/library_highlighter_type'
    gui_library_highlighter_color = 'Gui/library_highlighter_color'
    gui_quickview_popup_position = 'Gui/quickview_popup_position'
    gui_recent_flows = 'Gui/recent_flows'
    gui_show_message_area = 'Gui/show_message_area'
    gui_show_splash_screen = 'Gui/show_splash_screen'
    gui_snap_enabled = 'Gui/snap_enabled'
    gui_snap_type = 'Gui/snap_type'
    gui_grid_spacing = 'Gui/grid_spacing'
    gui_system_editor = 'Gui/system_editor'
    gui_nodeconfig_confirm_cancel = 'Gui/nodeconfig_confirm_cancel'
    gui_theme = 'Gui/theme'
    gui_code_editor_theme = 'Gui/code_editor_theme'
    gui_docking_enabled = 'Gui/docking_enabled'
    gui_flow_connection_shape = 'Gui/flow_connection_shape'
    gui_max_archived_messages = 'Gui/max_archived_messages'
    gui_experimental = 'Gui/experimental'
    gui_platform_developer = 'Gui/platform_developer'
    gui_on_start = 'Gui/on_start'
    python_library_path = 'Python/library_path'
    python_recent_library_path = 'Python/recent_library_path'
    python_python_path = 'Python/python_path'
    collect_include_system = 'Collect/include_system'
    collect_include_python = 'Collect/include_python'
    collect_include_packages = 'Collect/include_packages'
    user_email = 'User/email'
    matlab_matlab_path = 'MATLAB/matlab_path'
    matlab_matlab_jvm = 'MATLAB/matlab_jvm'
    autosave = 'autosave'
    ask_for_save = 'ask_for_save'
    credential_action = 'credential_action'
    environment = 'environment'
    max_task_chars = 'max_task_chars'
    max_temp_folder_age = 'max_temp_folder_age'
    max_temp_folder_number = 'max_temp_folder_number'
    max_temp_folder_size = 'max_temp_folder_size'
    session_temp_files = 'session_temp_files'
    session_files = 'session_files'
    temp_folder = 'temp_folder'
    default_folder = 'default_folder'
    max_nbr_of_threads = 'max_nbr_of_threads'
    deprecated_warning = 'deprecated_warning'
    user_id = 'user_id'
    send_stats = 'send_stats'
    configured_version = 'configured_version'


# Default values for settings that will be written to the preferences file.
permanent_defaults = {
    'Debug/graphviz_path': '',
    'Debug/profile_path_type': 'Session folder',
    'Gui/library_separated': False,
    'Gui/library_show_hidden': False,
    'Gui/library_matcher_type': 'character',
    'Gui/library_highlighter_type': 'background-color',
    'Gui/library_highlighter_color': '#EECC22',
    'Gui/quickview_popup_position': 'center',
    'Gui/recent_flows': [],
    'Gui/show_message_area': show_message_area_after_first,
    'Gui/show_splash_screen': True,
    'Gui/snap_enabled': True,
    'Gui/snap_type': 'Grid',
    'Gui/grid_spacing': 25,
    'Gui/system_editor': False,
    'Gui/nodeconfig_confirm_cancel': True,
    'Gui/theme': 'Grey',
    'Gui/code_editor_theme': "colorful",
    'Gui/docking_enabled': 'Movable',
    'Gui/flow_connection_shape': 'Spline',
    'Gui/max_archived_messages': 100,
    'Gui/experimental': False,
    'Gui/platform_developer': False,
    'Gui/on_start': on_start_new_flow,
    'Python/library_path': [],
    'Python/recent_library_path': [],
    'Python/python_path': [],
    'Collect/include_system': True,
    'Collect/include_python': True,
    'Collect/include_packages': True,
    'User/email': '',
    'MATLAB/matlab_path': '',
    'MATLAB/matlab_jvm': True,
    'autosave': False,
    'ask_for_save': True,
    'credential_action': credential_action_allow,
    'environment': [],
    'max_task_chars': 32000,
    'max_temp_folder_age': 3,
    'max_temp_folder_number': 100,
    'max_temp_folder_size': '1 G',
    'session_temp_files':  session_temp_files_remove_unused,
    'session_files': [],
    'temp_folder': Properties.default_sessions_folder,
    'default_folder': os.path.join(
        os.path.normpath(
            qt_support.documents_location()),
        'Sympathy for Data'),
    'max_nbr_of_threads': 0,
    'deprecated_warning': True,
    'user_id': str(uuid.uuid4()),
    'send_stats': False,
    'configured_version': '1.0.0',
}


def to_list(value):

    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def to_bool(value):
    if isinstance(value, bool):
        return value
    elif value == 'true':
        return True
    else:
        return False


# Types for settings that will be written to the preferences file.
# None means, value returned as is.
permanent_types = {
    'Debug/graphviz_path': None,
    'Debug/profile_path_type': None,
    'Gui/geometry': None,
    'Gui/library_separated': to_bool,
    'Gui/library_show_hidden': to_bool,
    'Gui/library_matcher_type': None,
    'Gui/library_highlighter_type': None,
    'Gui/library_highlighter_color': None,
    'Gui/quickview_popup_position': None,
    'Gui/recent_flows': to_list,
    'Gui/show_message_area': None,
    'Gui/show_splash_screen': to_bool,
    'Gui/snap_enabled': to_bool,
    'Gui/snap_type': None,
    'Gui/grid_spacing': int,
    'Gui/system_editor': to_bool,
    'Gui/code_editor_theme': None,
    'Gui/theme': None,
    'Gui/window_state': None,
    'Gui/nodeconfig_confirm_cancel': to_bool,
    'Gui/docking_enabled': None,
    'Gui/flow_connection_shape': None,
    'Gui/max_archived_messages': int,
    'Gui/experimental': to_bool,
    'Gui/platform_developer': to_bool,
    'Gui/on_start': None,
    'Python/library_path': to_list,
    'Python/recent_library_path': to_list,
    'Collect/include_system': to_bool,
    'Collect/include_python': to_bool,
    'Collect/include_packages': to_bool,
    'User/email': None,
    'Python/python_path': to_list,
    'MATLAB/matlab_path': None,
    'MATLAB/matlab_jvm': to_bool,
    'ask_for_save': to_bool,
    'autosave': to_bool,
    'credential_action': None,
    'environment': to_list,
    'max_task_chars': int,
    'max_temp_folder_age': int,
    'max_temp_folder_number': int,
    'max_temp_folder_size': None,
    'session_files': to_list,
    'session_temp_files': None,
    'temp_folder': None,
    'default_folder': None,
    'max_nbr_of_threads': int,
    'config_file_version': None,
    'deprecated_warning': to_bool,
    'user_id': None,
    'send_stats': to_bool,
    'configured_version': None,
}


# These settings will be available in worker processes.
worker_settings = [
    'Gui/code_editor_theme',
    'Gui/show_message_area',
    'Gui/nodeconfig_confirm_cancel',
    'MATLAB/matlab_path',
    'MATLAB/matlab_jvm',
    'default_folder',
    'session_folder',
    'deprecated_warning',
    'Debug/graphviz_path',
    'max_task_chars',
]


def get_worker_settings():
    """
    Return a dictionary with all the settings that should be exposed to the
    worker.
    """
    return {k: instance()[k] for k in worker_settings}


@contextmanager
def temporary_settings_context():
    """
    Temporarily replace the settings instance with one that will never modify
    the permanent storage.

    Can be useful to e.g. run tests with specific settings enabled/disabled.
    """
    global settings_instance
    old_settings = settings_instance
    settings_instance = TempSettings(settings_instance)
    yield settings_instance
    settings_instance = old_settings


class TempSettings(Properties):
    """Temporary settings not stored on disk. Useful for testing."""

    def __init__(self, settings_):
        self._instance = settings_
        self._overrides = {}

    def __contains__(self, key):
        return key in self._overrides or key in self._instance

    def __getitem__(self, key):
        if key in self._overrides:
            return self._overrides[key]
        return self._instance[key]

    def get(self, key, default=None):
        if key in self._overrides:
            return self._overrides[key]
        return self._instance.get(key, default=default)

    def keys(self, section=None):
        """Return all permanent keys in section."""
        return self._overrides.keys() + self._instance.keys(section=section)

    def __setitem__(self, key, value):
        self._overrides[key] = value


class Settings(Properties):

    def __init__(self, ini_file_name=None):
        super(Settings, self).__init__()
        self._file_name = ini_file_name
        self._permanent_storage = None
        self._temporary_storage = {}
        self._error = False
        self._init()

    def _init(self):
        if self._file_name:
            self.set_ini_file(self._file_name)
        else:
            self._permanent_storage = QtCore.QSettings(
                QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope,
                'Combine', 'Sympathy')
            if not os.path.exists(self._permanent_storage.fileName()):
                old_storage = QtCore.QSettings(
                    QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope,
                    'Sysess', 'Sympathy_1.3')
                if os.path.exists(old_storage.fileName()):
                    print('Copying settings from older version:',
                          old_storage.fileName())
                    migrate_old_settings(old_storage, self._permanent_storage)
                    for k in old_storage.allKeys():
                        if self._is_permanent(k):
                            self._permanent_storage.setValue(k, old_storage.value(k))
                self._permanent_storage.sync()

            if len(self._permanent_storage.allKeys()) == 0:
                self._update_version()

            self._error = not self._check_version()
        for key in stored_permanent:
            if not self._permanent_storage.contains(key):
                self._set_permanent(key, permanent_defaults[key])

    def _check_version(self):
        version = self._permanent_storage.value(
            'config_file_version', '0.0.0').split('.')
        major_version = int(version[0])
        minor_version = int(version[1])
        # maintenance_version = int(version[2])
        version_is_supported = ((major_version == SETTINGS_MAJOR_VERSION) and
                                (minor_version <= SETTINGS_MINOR_VERSION))
        if (version_is_supported):
            self._update_version()

        return version_is_supported

    def _update_version(self):
        self['config_file_version'] = '{}.{}.{}'.format(
            SETTINGS_MAJOR_VERSION,
            SETTINGS_MINOR_VERSION,
            SETTINGS_MAINTENANCE_VERSION)

    def _is_array(self, key):
        return key in [credential_array_key]

    def _is_permanent(self, key):
        return key in permanent_types or self._is_array(key)

    def set_ini_file(self, file_name):
        self._error = False
        self._file_name = file_name

        new_file = os.path.exists(file_name)

        self._permanent_storage = QtCore.QSettings(
            self._file_name, QtCore.QSettings.IniFormat)
        if new_file:
            self._update_version()
        else:
            self._error = not self._check_version()

    def clear(self):
        self._permanent_storage.clear()
        self._temporary_storage.clear()
        self._error = False
        self._update_version()

    def error(self):
        return self._error

    def file_name(self):
        return self._file_name

    def __contains__(self, key):
        if key in permanent_defaults:
            return True
        elif self._is_array(key):
            return True
        elif self._is_permanent(key) and self._permanent_storage.contains(key):
            return True
        return key in self._temporary_storage

    def _get_array(self, key):
        items = []
        for i in range(self._permanent_storage.beginReadArray(key)):
            item = {}
            self._permanent_storage.setArrayIndex(i)
            for k in self._permanent_storage.allKeys():
                item[k] = self._permanent_storage.value(k)
            items.append(item)
        self._permanent_storage.endArray()
        return(items)

    def __getitem__(self, key):
        if self._is_array(key):
            return self._get_array(key)

        elif self._is_permanent(key):
            if self._permanent_storage.contains(key):
                value = self._permanent_storage.value(key)
                type_ = permanent_types.get(key)
                if type_:
                    return type_(value)
                return value
            elif key in permanent_defaults:
                return copy.copy(permanent_defaults[key])
            raise KeyError('Settings instance does not have key: "{}"'.
                           format(key))
        else:
            try:
                return copy.copy(self._temporary_storage[key])
            except KeyError:
                raise KeyError('Settings instance does not have key: "{}"'.
                               format(key))

    def _set_permanent(self, key, value):
        self._permanent_storage.setValue(key, value)
        self._permanent_storage.sync()

    def _set_array(self, key, value):
        current = self._get_array(key)
        if current != value:
            # Must start by removing the group in order to overwrite
            # the whole array in case it has shrunk.
            self._permanent_storage.beginGroup(key)
            self._permanent_storage.remove("")
            self._permanent_storage.endGroup()

            self._permanent_storage.beginWriteArray(key)
            for i, item in enumerate(value):
                self._permanent_storage.setArrayIndex(i)
                for k, v in item.items():
                    self._permanent_storage.setValue(k, v)
            self._permanent_storage.endArray()

    def __setitem__(self, key, value):
        if self._is_array(key):
            self._set_array(key, value)

        elif self._is_permanent(key):
            current = self.get(key)
            if current is None or current != value:
                self._set_permanent(key, value)
        else:
            self._temporary_storage[key] = value

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def sync(self):
        self._permanent_storage.sync()

    def keys(self, section=None):
        """Return all permanent keys in section."""
        res = self._permanent_storage.allKeys()
        if section:
            try:
                self._permanent_storage.beginGroup(section)
                res = self._permanent_storage.allKeys()
            finally:
                self._permanent_storage.endGroup()
        return res

    def remove(self, key):
        if self._is_permanent(key):
            self._permanent_storage.remove(key)
        else:
            del self._temporary_storage[key]


def create_settings(fq_ini_filename=None):
    global settings_instance
    if settings_instance is not None:
        raise RuntimeError('Settings already instantiated.')
    if fq_ini_filename is None:
        settings_instance = Settings()
    else:
        settings_instance = Settings(fq_ini_filename)


def create(filename=None):
    create_settings(filename)


def remove():
    global settings_instance
    settings_instance = None


def instance():
    if settings_instance is None:
        create_settings()
    return settings_instance
