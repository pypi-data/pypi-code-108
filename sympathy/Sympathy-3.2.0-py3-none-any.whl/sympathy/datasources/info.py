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
"""
Provides means to get FileInfo objects with the following interface.
These provide information usable to distinguish the file format.

>>> class FileInfo(object):
>>>     def __init__(self, filepath):
>>>         # ...
>>>         pass
>>>
>>>     def is_file(self):
>>>         # ...
>>>         pass
>>>
>>>     def header(self):
>>>         # ...
>>>         pass
>>>
>>>     def version(self):
>>>         # ...
>>>         pass
>>>
>>>     def datatype(self):
>>>         # ...
>>>         pass
"""
import re
from . hdf5.dsinfo import FileInfo as Hdf5FileInfo
from . text.dsinfo import FileInfo as TextFileInfo

retype = re.compile(b"^SFD ([A-Z0-9]*)")


INFO_FROM_SCHEME = {
    'hdf5': Hdf5FileInfo,
    'text': TextFileInfo,
}


def get_fileinfo_from_scheme(scheme):
    """Return the FileInfo class associated with scheme."""
    return INFO_FROM_SCHEME[scheme]


def get_fileinfo_from_file(filename):
    """Return the FileInfo class associated with filename."""
    return INFO_FROM_SCHEME[get_scheme_from_file(filename)]


def get_scheme_from_file(filename):
    """Return the scheme associated with filename."""
    res = None
    with open(filename, 'rb') as f:
        match = retype.match(
            f.readline().split(b'{')[0])
        if match:
            res = match.groups()[0].decode('ascii').lower()
    return res
