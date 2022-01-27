# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
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
from collections import OrderedDict

import io
import os
from sympathy.platform.exceptions import sywarn

LIBRARY_INI = 'library.ini'
library_infos = {}


class LibraryInfo(object):
    def __init__(self, filename, info):
        super(LibraryInfo, self).__init__()
        self._filename = filename
        self._info = info

    def keys(self):
        """Return a dict with sections containing a list of keys in each
        section.
        """
        keys = {}
        for section in self._info.keys():
            keys[section] = list(self._info[section].keys())

        return keys

    def file_name(self):
        return self._filename

    def __contains__(self, key):
        """If key is section name only, return true if section is present.
        Else if key is (section name, property name) return true if property
        exists in section.
        """
        if isinstance(key, str):
            return key in self._info
        else:
            return key[1] in self._info[key[0]].keys()

    def __getitem__(self, key):
        """If key is section name only, return section dict if section
        is present. Else if key is (section name, property name) return
        property.
        """
        try:
            if isinstance(key, str):
                return self._info[key]
            return self._info[key[0]][key[1]]
        except KeyError:
            raise KeyError('Library info does not have key: "' + key + '"')

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __setitem__(self, key, value):
        """If key is section name only, create new section. Else if key is
        (section name, property name) create section if not present, then add
        the property to that section.
        """
        if isinstance(key, str):
            self._info[key] = OrderedDict()
        else:
            section = key[0]
            prop = key[1]
            if section in self._info:
                self._info[section][key] = value
            else:
                self._info[section] = {}
            self._info[section][prop] = value

    def sync(self):
        """Save to disk"""
        string = self._to_string()
        try:
            with io.open(self._filename, 'w', encoding='utf8') as ini:
                ini.write(string)
        except (IOError, OSError):
            sywarn('Library file ' + self._filename + ' cannot be written.')

    def _to_string(self):
        lines = []
        for key in self._info:
            lines.append('[' + key + ']')
            for section_key in self._info[key]:
                lines.append('{}={}'.format(
                    section_key, self._info[key][section_key]))
        if len(lines):
            return '\n'.join(lines) + '\n'
        else:
            return ''

    def package_name(self):
        package_name = self['General']['common_path']
        try:
            return os.path.basename(os.path.normpath(package_name))
        except Exception:
            return None

    def library_name(self):
        library_path = self['General']['library_path']
        try:
            return os.path.basename(os.path.normpath(library_path))
        except Exception:
            return None


def package_name(path):
    """
    Returns
    -------
    string or None
        Package name of library, None if path does not point ot a no proper
        library.
    """
    library_info = read_library_info(directory=path)
    package_name = None

    if library_info:
        try:
            package_name = library_info.package_name()
        except Exception:
            pass
    return package_name


def library_name(path):
    """
    Returns
    -------
    string or None
        Library name of library, None if path does not point ot a no proper
        library.
    """
    library_info = read_library_info(directory=path)
    package_name = None

    if library_info:
        try:
            package_name = library_info.library_name()
        except Exception:
            pass
    return package_name


def read_library_info(filename=None, directory=None):
    info = []
    ini_path = filename
    assert filename or directory
    if filename is None:
        ini_path = os.path.join(directory, LIBRARY_INI)

    try:
        with io.open(ini_path, 'r', encoding='utf8') as ini:
            line = ini.readline()
            while len(line):
                info.append(line)
                line = ini.readline()
    except (IOError, OSError):
        pass
    else:
        return LibraryInfo(ini_path, _parse_input(info))


def create_library_info(ini_path, name):
    library_info = read_library_info(ini_path)

    if library_info is None:
        sywarn('Library file ' + ini_path + ' cannot be read.')
        return False
    else:
        global library_infos
        library_infos[name] = library_info
        return True


def _parse_input(info):
    properties = OrderedDict()
    section = None
    for i, line in enumerate(info):
        if len(line):
            if line[0] == '[':
                section = line[1:].split(']')
                if len(section) > 1:
                    properties[section[0]] = OrderedDict()
                else:
                    break
                continue
            prop = line.split('=')
            if len(prop) > 1 and section is not None:
                properties[section[0]][prop[0]] = prop[1].strip()
            elif section is None:
                break
            else:
                sywarn(
                    'File not correctly formatted on line ' +
                    str(i) + '.\n'
                    'Each section in library.ini should be on the form:\n'
                    '[Section]\n'
                    'Property1=property1\n'
                    'Property2=property2\n'
                    'etc.')
    return properties


def remove_library(name):
    if name in library_infos:
        del library_infos[name]


def sync():
    for key in library_infos.keys():
        library_infos[key].sync()


def instance():
    return library_infos
