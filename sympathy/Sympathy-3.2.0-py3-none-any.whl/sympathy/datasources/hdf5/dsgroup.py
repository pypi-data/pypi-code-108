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
"""HDF5 group."""
import sys
import json
import math
import warnings
from collections import OrderedDict

# Ignore a warning from numpy>=1.14 when importing h5py<=2.7.1:
with warnings.catch_warnings():
    warnings.simplefilter('ignore', FutureWarning)
    import h5py

from . dsstate import hdf5_state
from sympathy.version import __version__ as platform_version
_fs_encoding = sys.getfilesystemencoding()


UTF8 = 'utf-8'
REPLACE_SLASH = chr(0x01)
USERBLOCK_MIN_SIZE = 512
VERSION = 'Version'
VERSION_NUMBER = '1.0'
TYPE = 'Type'
TYPEALIAS = 'TypeAlias'
IDENTIFIER = 'SFD HDF5'
PLATFORM = 'Platform'


def read_header(filepath):
    """
    Read the header from hdf5 file and return an ordered dict with its content.
    """
    with open(filepath, 'rb') as hdf5:
        identifier = hdf5.read(len(IDENTIFIER))
        line = hdf5.readline()
        assert(identifier == IDENTIFIER.encode('ascii'))
        header_data = json.loads(
            line.decode('ascii'), object_pairs_hook=OrderedDict)
        return header_data


def write_header(filepath, header_data):
    """
    Write header_data dictionary to the file at filepath.
    The file must have sufficient space in its userblock.
    """
    with open(filepath, 'r+b') as hdf5:
        hdf5.write(header_data)
        hdf5.write(b'\x00' * (
            _header_data_size(header_data) - len(header_data)))


def _header_data(datatype, type):
    """Return dictionary of header data with data type included."""
    return '{}{}\n'.format(
        IDENTIFIER,
        json.dumps(OrderedDict(
            [(VERSION, VERSION_NUMBER),
             (TYPE, datatype),
             (TYPEALIAS, type),
             (PLATFORM, platform_version)]))).encode('ascii')


def _header_data_size(header_data):
    """Return length of header data with data type included."""
    length = len(header_data)
    return max(2 ** int(math.ceil(math.log(length, 2))), USERBLOCK_MIN_SIZE)


def replace_slash(string):
    """
    Replace special '/' character with very rare unicode character 0xFFFF.
    """
    return string.replace('/', REPLACE_SLASH)


def restore_slash(string):
    """
    Restore special '/' character replaced with very rare unicode character
    0xFFFF.
    """
    return string.replace(REPLACE_SLASH, '/')


def create_path(h5file, path):
    """Create path in file returning the group at h5file[path]."""
    curr_group = h5file
    for component in path:
        curr_group = curr_group[component]
    return curr_group


class GroupWrapper(object):
    def __init__(self, group):
        file_ = group.file
        self.filename = file_.filename
        self.mode = file_.mode
        self.name = group.name
        self._files = {}
        self._cache = {}

    @property
    def _group(self):
        return hdf5_state().open(self.filename, 'r')[self.name]

    def create_group(self, name):
        assert name not in self._cache
        group = GroupWrapper(
            self._group.create_group(name))
        self._cache[name] = group
        return group

    def create_dataset(self, name, **kwargs):
        assert name not in self._cache
        return self._group.create_dataset(name, **kwargs)

    def __getitem__(self, key):
        res = self._cache.get(key)
        group = self._group
        if not res:
            lnk = group.get(key, getlink=True)
            if not isinstance(lnk, h5py.ExternalLink):
                res = group[key]
                if isinstance(res, h5py.Group):
                    res = GroupWrapper(res)
                    self._cache[key] = res
            else:
                # We do not allow linking to links, so when we encounter
                # a link we must trace the path to the source to get the
                # right data.
                lnk_filename = lnk.filename
                file_group = self._files.get(lnk_filename)
                if not file_group:
                    file_group = GroupWrapper(hdf5_state().open(
                        lnk_filename, 'r'))
                    self._files[lnk_filename] = file_group

                full_path = tuple([x for x in lnk.path.split('/') if x])
                res = file_group._group
                for path in full_path:
                    res = res[path]

                if isinstance(res, h5py.Group):
                    res = GroupWrapper(res)
                    self._cache[key] = res
        return res

    def __setitem__(self, key, value):
        assert not (isinstance(value, GroupWrapper) or
                    isinstance(value, h5py.Group))
        assert key not in self._cache
        self._group[key] = value

    def __contains__(self, key):
        return key in self._group

    def __len__(self):
        return len(self._group)

    def get(self, key, default=None):
        if key in self:
            return self[key]
        return default

    def getlink(self, key):
        lnk = self._group.get(key, getlink=True)
        if isinstance(lnk, h5py.ExternalLink):
            return lnk

    def keys(self):
        return self._group.keys()

    @property
    def attrs(self):
        return self._group.attrs

    def is_closed(self):
        return not hdf5_state().is_closed(self.filename)

    def __bool__(self):
        return hdf5_state().is_closed(self.filename)

    def __nonzero__(self):
        return self.__bool__()

    @property
    def file(self):
        return hdf5_state().file(self.filename)


class Hdf5Group(object):
    """Abstraction of an HDF5-group."""
    def __init__(self, factory, group=None, file_info=None, can_write=False,
                 can_link=False, external=True):
        self.factory = factory
        self._group = group
        self._header_data = None

        if self._group is not None:
            self.can_link = can_link
            self.can_write = can_write
            self.filepath = None
            self.external = external
            self.mode = None
            self.path = None
            if not isinstance(group, GroupWrapper):
                self._group = GroupWrapper(group)
        else:
            self.mode = file_info['mode']
            self.can_link = file_info['can_link']
            self.can_write = can_write or self.mode in ['r+', 'w']
            self.filepath = file_info['resource']
            self.external = file_info['external']
            self.path = file_info['path']

            if self.mode == 'r':
                try:
                    h5file = hdf5_state().open(self.filepath, 'r')
                    group = GroupWrapper(h5file)
                except ValueError:
                    raise IOError(
                        'Could not open assumed hdf5-file : "{}"'.format(
                            self.filepath))
                self._group = create_path(group, self.path)

            elif self.mode == 'w':
                # Create new hdf5 file with userblock set.
                self._header_data = _header_data(
                    file_info['type_expanded'],
                    file_info['dstype'] or file_info['type'])

                h5file = h5py.File(
                    self.filepath, self.mode,
                    userblock_size=_header_data_size(
                        self._header_data))
                hdf5_state().add(self.filepath, h5file)
                group = GroupWrapper(h5file)
                self._group = create_path(group, self.path)

    @property
    def group(self):
        return self._group

    def _group_get_or_create(self, key):
        group = self.group
        if key in group:
            chldgroup = group[key]
        else:
            chldgroup = group.create_group(key)
        return chldgroup

    def _create_item(self, type_cls, group):
        return self.factory.from_type_group(
                type_cls, group,
                external=self.external,
                can_write=self.can_write,
                can_link=self.can_link)

    def transferable(self, other):
        """
        Returns True if the content from datasource can be linked directly,
        and False otherwise.
        """
        return (self.can_link and other.can_link and
                isinstance(other, Hdf5Group))

    def transfer(self, name, other, other_name):
        """
        Performs linking if possible, this is only allowed if transferrable()
        returns True.
        """
        pass

    def link(self):
        group = self.group
        return h5py.ExternalLink(
            group.filename,
            group.name)

    def shares_origin(self, other):
        """
        Checks if two datasources originate from the same resource.
        """
        try:
            group = self.group
            other_group = other.group

            return (
                group.filename ==
                other_group.filename and
                group.name == other_group.name)
        except Exception:
            return False

    def write_link(self, name, other, other_name):
        name = replace_slash(name)
        other_name = replace_slash(other_name)
        lnk = other.group.getlink(other_name)
        if lnk is None:
            group = other.group
            lnk = h5py.ExternalLink(
                group.filename,
                group.name + '/' + other_name)

        self.group[name] = lnk
        return True

    def close(self):
        """Close the hdf5 file using the group member."""
        # If open fails, avoid causing argument exception on close.
        if self._group is not None:
            hdf5_state()._close_file(self.group)
            if self.mode == 'w':
                write_header(self.filepath, self._header_data)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
