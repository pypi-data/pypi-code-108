# This file is part of Sympathy for Data.
# Copyright (c) 2015, Combine Control Systems AB
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
"""Text Data source module."""
from . import dsgroup


class TextLambda(dsgroup.TextGroup):
    """Abstraction of an Text-lambda."""
    def __init__(self, factory, **kwargs):
        super().__init__(factory, **kwargs)

    def read(self):
        """
        Return stored pair of flow and list of port assignments or None if
        nothing is stored.
        """
        if 'lambda' in self.group:
            column = self.group['lambda']
            return (column[0], column[1])
        return None

    def write(self, value):
        """
        Stores lambda in the hdf5 file, at path,
        with data from the given text
        """
        self.group['lambda'] = (value[0],) + value[1]

    def transferable(self, other):
        return False

    def transfer(self, other):
        self.group['lambda'] = other.group['lambda']
