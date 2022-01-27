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
API for working with the Text type.

Import this module like this::

    from sympathy.api import text

Class :class:`text.File`
------------------------
.. autoclass:: File
   :members:
   :special-members:

"""
import numpy as np
from .. utils import filebase
from .. utils.context import inherit_doc


def is_text(scheme, filename):
    return File.is_type(filename, scheme)


def is_texts(scheme, filename):
    return FileList.is_type(filename, scheme)


@filebase.typeutil('sytypealias text = sytext')
@inherit_doc
class File(filebase.TypeAlias):
    """
    A Text type containing arbitrary text, be it Hamlet or some json encoded
    data structure.

    Any node port with the *Text* type will produce an object of this kind.
    """

    def set(self, text_data):
        """Set text data."""
        self._data.set(text_data)

    def get(self):
        """Return text data."""
        return self._data.get()

    def update(self, other):
        """Copy the contents from ``other`` :class:`text.File`.
        Equivalent to :meth:`source`.
        """
        self._data.update(other._data)

    def source(self, other, shallow=False):
        """Copy the contents from ``other`` :class:`text.File`.
        Equivalent to :meth:`update`.
        """
        self.set(other.get())

    def names(self, kind=None, fields=None, **kwargs):
        """
        Return a formatted list with a name and type of the data.
        columns.
        """
        names = filebase.names(kind, fields)
        kind, fields = names.updated_args()
        fields_list = names.fields()

        if kind == 'cols':
            item = names.create_item()
            for f in fields_list:
                if f == 'type':
                    item[f] = np.dtype('U')
                elif f == 'expr':
                    item[f] = ".get()"

        return names.created_items_to_result_list()

    @classmethod
    def viewer(cls):
        from .. platform import text_viewer
        return text_viewer.TextViewer

    @classmethod
    def icon(cls):
        return 'ports/text.svg'


@inherit_doc
class FileList(filebase.FileListBase):
    """
    FileList has been changed and is now just a function which creates
    generators to sybase types.

    Old documentation follows:

    The :class:`FileList` class is used when working with lists of Texts.

    The main interfaces in :class:`FileList` are indexing or iterating for
    reading (see the :meth:`__getitem__()` method) and the :meth:`append()`
    method for writing.
    """

    sytype = '[text]'
    scheme = 'hdf5'
