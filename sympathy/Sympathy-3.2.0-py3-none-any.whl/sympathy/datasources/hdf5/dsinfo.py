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
from . dsgroup import read_header as sy_read_header
from . dsgroup import VERSION as sy_version
from . dsgroup import TYPE as sy_datatype
from . dsgroup import TYPEALIAS as sy_type


class FileInfo(object):
    """File header information."""
    def __init__(self, filepath):
        try:
            self.header = sy_read_header(filepath)
        except:
            self.header = None

    def is_file(self):
        return self.header is not None

    def version(self):
        return self.header[sy_version]

    def platform_version(self):
        return self.header.get('Platform')

    def datatype(self):
        dtype = self.header[sy_datatype]
        dtype = dtype.replace('sytable', 'table')
        dtype = dtype.replace('sytext', 'text')
        return dtype

    def type(self):
        return self.header[sy_type]
