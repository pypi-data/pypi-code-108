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
"""Text Data source module."""
from . import dsgroup


class TextText(dsgroup.TextGroup):
    """Abstraction of an HDF5-text."""
    def __init__(self, factory, **kwargs):
        super().__init__(factory, **kwargs)

    def read(self):
        """Return stored text, or '' if nothing is stored."""
        try:
            return self.group['text']
        except KeyError:
            return ''

    def write(self, text):
        """
        Stores text in the text file, at path,
        with data from the given text
        """
        self.group['text'] = text
