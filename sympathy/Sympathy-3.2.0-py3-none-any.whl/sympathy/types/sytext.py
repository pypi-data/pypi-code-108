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
"""Sympathy text."""

from . import sybase
from . sytable import sytable
from .. platform.types import TypeTable
from . import exception as exc


class sytext(sybase.sygroup):
    """A type representing a text."""
    def __init__(self, container_type, datasource=sybase.NULL_SOURCE):
        """
        Init. container_type parameter is not used, needed to
        conform factory interface.
        """
        self.__table = sytable(TypeTable())
        super(sytext, self).__init__(container_type,
                                     datasource or sybase.NULL_SOURCE)
        self._cache = (None, False, self._datasource)

    def get(self):
        """Get contained text."""
        value, _, datasource = self._cache
        if value is None:
            value = datasource.read() or ''
            self._cache = (value, False, datasource)
        return value

    def set(self, text):
        """Set contained text."""
        assert(isinstance(text, str) or
               isinstance(text, bytes))
        self._cache = (text or "", True, sybase.NULL_SOURCE)

    def update(self, other):
        """Updates the text with other text if it exists."""
        self._cache = tuple(other._cache)

    def __copy__(self):
        obj = super(sytext, self).__copy__()
        obj.__table = self.__table.__copy__()
        obj._cache = tuple(self._cache)
        return obj

    def __deepcopy__(self, memo=None):
        return self.__copy__()

    def source(self, other, shallow=False):
        self.update(other)

    def visit(self, group_visitor):
        """Accept group visitor."""
        group_visitor.visit_text(self)

    def writeback(self):
        super(sytext, self).writeback()

    def _writeback(self, datasource, link=None):
        # Transfer relies on direct compatiblity, for example, in the hdf5
        # datasource case both sources need to be hdf5 and the source needs to
        # be read only.
        origin = self._datasource
        target = datasource
        exc.assert_exc(target.can_write, exc=exc.WritebackReadOnlyError)

        if link:
            return self._link(datasource, link)

        shares_origin = target.shares_origin(origin)
        value, dirty, datasource = self._cache

        if shares_origin and not dirty:
            # At this point there is no support for writing texts more than
            # once.
            return

        if target.transferable(datasource) and not dirty:
            target.transfer(
                None, datasource, None)
        else:
            # No transfer possible, writing using numpy texts.
            if value is None:
                value = self.get()

            if value is not None:
                target.write(value)

    def __repr__(self):
        return "sytext()"
