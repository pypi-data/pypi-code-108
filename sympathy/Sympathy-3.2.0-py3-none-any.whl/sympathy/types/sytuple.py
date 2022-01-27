# This file is part of Sympathy for Data.
# Copyright (c) 2017, Combine Control Systems AB
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
from .. utils import complete
from . import sybase
from . import sylist
from . import exception as exc


def _int_index_guard(index):
    if not isinstance(index, int):
        raise TypeError(
            u'Only basic integer indexing is supported, not: "{}"'
            .format(index))


class sytuple(sybase.syseq):
    def __init__(self, container_type, datasource=sybase.NULL_SOURCE):
        super().__init__(container_type, datasource or sybase.NULL_SOURCE)
        self.content_types = []
        self._content_types = []

        for content_type in container_type:
            self.content_types.append(content_type)
            self._content_types.append(self._datasource_type(content_type))

        self._cache = [None] * len(container_type)

    def __repr__(self):
        return str(self._cache)

    def __len__(self):
        return len(self._cache)

    def __iter__(self):
        for i in range(len(self._cache)):
            yield self.__getitem__(i)

    def _get_uncached(self, key):
        content_type = self.content_types[key]
        try:
            # Read from datasource.
            source = self._datasource.read_with_type(
                str(key), type(self._content_types[key]))
        except KeyError:
            # Create content without datasource.
            value = self._factory.from_type(content_type)
        else:
            # Create content from datasource.
            source = source or sybase.NullSource
            value = self._factory.from_datasource(
                source,
                content_type)
        return value

    def __getitem__(self, index):
        _int_index_guard(index)
        value = self._cache[index]
        if value is None:
            value = self._get_uncached(index)
            self._set_cached_own(index, value)
        return value

    def __setitem__(self, index, value):
        _int_index_guard(index)
        content_type = self.content_types[index]
        sybase.assert_type(
            self, value.container_type, content_type)
        self._set_cached_ext(index, value)

    def __copy__(self):
        obj = super().__copy__()
        obj.content_types = self.content_types
        obj._content_types = self._content_types
        obj._datasource = self._datasource
        obj._cache = list(self._cache)
        return obj

    def __deepcopy__(self, memo=None):
        obj = self.__copy__()
        obj._cache = [None if v is None else v.__deepcopy__()
                      for v in self._cache]
        return obj

    def names(self, kind=None, fields=None, **kwargs):
        return sylist.list_names(self, kind=kind, fields=fields, **kwargs)

    def completions(self, **kwargs):
        def items(ctx):
            return list(range(len(self)))

        builder = complete.builder()
        child_builders = []

        for k in range(len(self)):
            child = self[k]
            child_builder = child.completions()
            child_builders.append(child_builder)

        builder.getitem(items, child_builders)
        return builder

    def update(self, other):
        sybase.assert_type(
            self, self.container_type, other.container_type)
        self._cache = list(other)
        self._unindex_all()

    def source(self, other, shallow=False):
        if shallow:
            self.update(other)
        else:
            self.update(other.__deepcopy__())

    def writeback(self):
        super().writeback()

    def _get_content_type(self, key):
        return self._content_types[key]
