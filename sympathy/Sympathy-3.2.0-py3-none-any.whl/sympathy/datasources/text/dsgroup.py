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
"""Text group."""
from collections import OrderedDict
import json

from sympathy.version import __version__ as platform_version
IDENTIFIER = 'SFD TEXT'
VERSION_NUMBER = '2.1'


def _encode(string):
    if isinstance(string, str):
        return string.encode('ascii')
    return string


def read_header(filepath):
    """
    Read the header from text file and return an ordered dict with its content.
    """
    with open(filepath, 'rb') as textfile:
        return _read_header(textfile)


def _read_header(textfile):
    identifier = textfile.read(len(IDENTIFIER))
    line = textfile.readline()
    assert(identifier == IDENTIFIER.encode('ascii'))
    header_data = json.loads(
        line.decode('ascii'), object_pairs_hook=OrderedDict)
    return header_data


def create_path(textfile, path):
    """Create path in file returning the group at h5file[path]."""
    curr_group = textfile

    for component in path:
        items = curr_group['items']
        next_group = items[component]
        curr_group = next_group
    return curr_group


class TextGroup(object):
    """Abstraction of an Text-group."""
    def __init__(self,
                 factory,
                 group=None,
                 file_info=None,
                 can_write=False):

        self.factory = factory
        self.group = group
        self.file_info = file_info

        if group is not None:
            self.can_write = can_write
            self.filename = None
            self.mode = None
            self.path = None
        else:
            self.filename = file_info['resource']
            self.mode = file_info['mode']
            self.path = file_info['path']
            self.can_write = can_write or self.mode in ['r+', 'w']

            with open(self.filename, self.mode + 'b') as textfile:
                if self.mode in ['r', 'r+']:
                    _read_header(textfile)
                    self.data = json.loads(textfile.read().decode('ascii'),
                                           object_pairs_hook=OrderedDict)
                elif self.mode == 'w':
                    self.data = {'root': {}}
                else:
                    assert False, 'Invalid mode specified'
                self.group = create_path(self.data['root'], self.path)

    def transferable(self, other):
        """
        Returns True if the content from datasource can be linked directly,
        and False otherwise.
        """
        return False

    def transfer(self, selfname, other, othername):
        """
        Performs linking if possible, this is only allowed if transferrable()
        returns True.
        """
        pass

    def shares_origin(self, other_datasource):
        """
        Checks if two datasources originate from the same resource.
        """
        return False

    def write_link(self, name, other, other_name):
        return False

    @property
    def can_link(self):
        return False

    def close(self):
        """Close the text file using the group member."""
        if self.data and self.mode == 'w':
            data = self.data
            if isinstance(self.data, bytes):
                data = data.decode('ascii')

            with open(self.filename, 'wb') as textfile:
                textfile.write(IDENTIFIER.encode('ascii'))
                textfile.write(json.dumps(OrderedDict([
                    ('Version', VERSION_NUMBER),
                    ('Type', self.file_info['type_expanded']),
                    ('TypeAlias', self.file_info['type']),
                    ('Platform', platform_version)])).encode('ascii'))
                textfile.write(b'\n')
                textfile.write(_encode(json.dumps(data, sort_keys=True)))

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _group_get_or_create(self, key):
        items = self.group.setdefault('items', {})
        return items.setdefault(key, {})

    def _get_items(self):
        return self.group.get('items', {})

    def _create_item(self, type_cls, group):
        return self.factory.from_type_group(
                type_cls, group,
                can_write=self.can_write)
