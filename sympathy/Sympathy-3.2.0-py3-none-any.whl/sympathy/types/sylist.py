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
"""Sympathy list type."""
from .. utils import names as names_m
from .. utils import complete
from . import sybase
from . import exception as exc

# TODO(erik):
# Really needs refactoring here, when a list gets created it starts out as
# sylist. Then if it is top-level port it gets cast based on the type:
# * input port  - sylistReadThrough
# * output port - sylistWriteThrough
#
# This is very unusual and causes implementation subtleties to be handled for
# little benefit. Create the different list types in the first place and never
# change the implementation or possibly, use one single class with multiple modes.
def set_write_through(sylist_instance):
    assert(isinstance(sylist_instance, sylist))
    assert(sylist_instance._datasource is not sybase.NULL_SOURCE)

    length = len(sylist_instance)
    if length:
        raise Exception('Write-through requires empty list.')

    sylist_instance.__class__ = sylistWriteThrough
    sylist_instance._set_count(length)
    return sylist_instance


def set_read_through(sylist_instance):
    assert(isinstance(sylist_instance, sylist))
    assert(sylist_instance._datasource is not sybase.NULL_SOURCE)
    length = len(sylist_instance)
    sylist_instance.__class__ = sylistReadThrough
    sylist_instance._set_indices(range(length))
    return sylist_instance


def list_names(list_, kind=None, fields=None, **kwargs):
    names = names_m.names(kind, fields, store_created=False)
    kind, fields = names.updated_args()
    fields_list = names.fields()

    for i in range(len(list_)):
        for n in list_[i].names(kind=kind, fields=fields_list):
            item = names.create_item(n)
            for f in fields_list:
                if f == 'expr':
                    item[f] = '[{}]{}'.format(
                        i, n.get(f, ''))
                elif f == 'path':
                    v = [('[]', i)]
                    v.extend(n.get(f, []))
                    item[f] = v
            yield names.item_to_result(item)


def list_completions(list_):
    def items(ctx):
        return range(len(list_))

    builder = complete.builder()
    child_builder = None
    if len(list_):
        child = list_[0]
        child_builder = child.completions()
    builder.getitem(items, child_builder)
    return builder


class sylistReadThrough(sybase.syseq):

    def __init__(self, sylist_instance):
        assert False, 'Can not create new sylistReadThrough'
        self.__indices = range(len(self))

    def create(self):
        return self._factory.from_type(self.content_type)

    def append(self, item):
        raise ValueError('Method not available on read-through.')

    def extend(self, other_list):
        raise ValueError('Method not available on read-through.')

    def source(self, other, shallow=False):
        raise ValueError('Method not available on read-through.')

    def visit(self, group_visitor):
        raise ValueError('Method not available on read-through.')

    def __copy__(self):
        obj = super().__copy__()
        obj._content_type = self._content_type
        obj.content_type = self.content_type
        obj.__indices = list(self.__indices)
        obj._cache = list(self._cache)
        return obj

    def __deepcopy__(self, memo=None):
        obj = self.__copy__()
        obj._cache = [None if v is None else v.__deepcopy__()
                      for v in self._cache]
        return obj

    def names(self, kind=None, fields=None, **kwargs):
        return list_names(self, kind=kind, fields=fields, **kwargs)

    def completions(self):
        return list_completions(self)

    def __len__(self):
        return len(self._cache)

    def _get_uncached(self, key):
        index = self.__indices[key]
        return self._factory.from_datasource(
            self._datasource.read_with_type(index, type(self._content_type)),
            self.content_type)

    def __getitem__(self, index):
        """
        Returns a single sygroup by index if it exists in the datasource,
        otherwise None.
        """
        value = self._cache[index]
        if value is None:
            value = self._get_uncached(index)
            self._set_cached_own(index, value)

        return value

    def __setitem__(self, index, item):
        raise ValueError('Method not available on read-through.')

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __delitem__(self, index):
        raise ValueError('Method not available on read-through.')

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return str(self._cache)

    def writeback(self):
        pass

    def _index_type(self):
        return 'sylist'

    def _get_content_type(self, key):
        return self._content_type

    def _set_indices(self, indices):
        self.__indices = list(indices)


class sylistWriteThrough(sybase.syseq):

    def __init__(self, sylist_instance):
        assert False, 'Can not create new sylistWriteThrough'

    def create(self):
        return self._factory.from_type(self.content_type)

    def append(self, item):
        """Append item to list."""
        # Ensure correct type?
        sybase.assert_type(self, item.container_type,
                           self.content_type)
        target = self._datasource
        content_type = self._content_type

        if item is not None:
            item.sync()
            if not item._writeback(target, str(self.__count)):
                new_target = target.write_with_type(
                    str(self.__count), item, type(content_type))
                item._writeback(new_target)
            self.__count += 1
        self._dirty = True

    def extend(self, other_list):
        for item in other_list:
            self.append(item)

    def source(self, other, shallow=False):
        if self.__count:
            raise ValueError(
                'Method not available on write-through of modified table.')
        else:
            self.extend(other)

    def __copy__(self):
        raise ValueError('Method not available on write-through.')

    def __deepcopy__(self, memo=None):
        raise ValueError('Method not available on write-through.')

    def visit(self, group_visitor):
        raise ValueError('Method not available on write-through.')

    def __len__(self):
        return self.__count

    def __getitem__(self, index):
        return self._factory.from_datasource(
            self._datasource.read_with_type(index, type(self._content_type)),
            self.content_type)

    def __setitem__(self, index, item):
        raise ValueError('Method not available on write-through.')

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __delitem__(self, index):
        raise ValueError('Method not available on write-through.')

    def __str__(self):
        return 'sylistwritethrough()'

    def __repr__(self):
        raise ValueError('Method not available on write-through.')

    def writeback(self):
        pass

    def _writeback(self, datasource, link=None):
        pass

    def index(self, lmit=None):
        raise ValueError('Method not available on write-through.')

    def set_index(self, index):
        raise ValueError('Method not available on write-through.')

    def _index_type(self):
        return 'sylist'

    def _get_content_type(self, key):
        return self._content_type

    def _set_count(self, count):
        self.__count = count


class sylist(sybase.syseq):
    """A type representing a list."""
    def __init__(self, container_type, datasource=sybase.NULL_SOURCE,
                 items=None):
        """Init."""
        super().__init__(container_type, datasource or sybase.NULL_SOURCE)
        self.content_type = container_type[0]
        # __indices is used to distinguish between data in the sylist's
        # own datasource and external data which is only in the cache.
        # None values mean that the data is only in the cache.
        # Integer values mean that the data is found in the datasource using
        # the values as indices.
        self._content_type = self.content_type
        self._content_type = self._datasource_type(self.content_type)

        if datasource is sybase.NULL_SOURCE:
            self._cache = [] if items is None else items
            self.__indices = [None] * len(self._cache)
        else:
            size = self._datasource.size()
            self._cache = [None] * size
            self.__indices = list(range(size))

    def create(self):
        return self._factory.from_type(self.content_type)

    def append(self, item):
        """Append item to list."""
        # Ensure correct type?
        sybase.assert_type(self, item.container_type,
                           self.content_type)
        self._cache.append(item)
        self.__indices.append(None)

    def extend(self, other_list):
        """Extend list with other list."""
        try:
            other_container_type = other_list.container_type
        except AttributeError:
            # Assume well typed iterator.
            other_list = list(other_list)
        else:
            sybase.assert_type(self, other_container_type,
                               self.container_type)
        self._cache.extend(other_list)
        self.__indices.extend([None] * len(other_list))

    def source(self, other, shallow=False):
        self._cache = []
        self.__indices = []
        if shallow:
            self.extend(other)
        else:
            self.extend(other.__deepcopy__())

    def __copy__(self):
        obj = super().__copy__()
        obj._content_type = self._content_type
        obj.content_type = self.content_type
        obj.__indices = list(self.__indices)
        obj._cache = list(self._cache)
        return obj

    def __deepcopy__(self, memo=None):
        obj = self.__copy__()
        obj._cache = [None if v is None else v.__deepcopy__()
                      for v in self._cache]
        return obj

    def names(self, kind=None, fields=None, **kwargs):
        return list_names(self, kind=kind, fields=fields, **kwargs)

    def completions(self):
        return list_completions(self)

    def visit(self, group_visitor):
        """Accept group visitor."""
        group_visitor.visit_list(self)

    def _get_uncached(self, key):
        index = self.__indices[key]
        return self._factory.from_datasource(
            self._datasource.read_with_type(index, type(self._content_type)),
            self.content_type)

    def __getitem__(self, index):
        """Get item."""
        def get_single_item(index):
            """
            Returns a single sygroup by index if it exists int the datasource,
            otherwise None.
            """
            value = self._get_uncached(index)
            self._set_cached_own(index, value)
            return value

        if isinstance(index, slice):
            # Read slice from datasource.
            # Use cache for cached items.
            if self._datasource:
                # Make concrete list from slice index
                # and read each index separately.
                items = []
                for i in self._slice_indices(index):
                    value = self._cache[i]
                    if value is not None:
                        items.append(value)
                    else:
                        value = get_single_item(i)
                    items.append(value)
                return sylist(self.container_type, items=items)
            else:
                # Read slice from cache.
                return sylist(
                    self.container_type, items=list(self._cache[index]))
        else:
            value = self._cache[index]
            if value is None:
                value = get_single_item(index)
            return value

    def __setitem__(self, index, item):
        """Set item."""
        if isinstance(index, slice):
            sybase.assert_type(self, item.container_type,
                               self.container_type)
            indices = self._slice_indices(index)
            self.__indices[index] = [None] * len(item)
        else:
            sybase.assert_type(self, item.container_type,
                               self.content_type)
            self.__indices[index] = None
            indices = [index]

        self._cache[index] = item
        self._unindex_keys(indices)

    def __iter__(self):
        self[:]
        return iter(self._cache)

    def __delitem__(self, index):
        indices = [index]
        if isinstance(index, slice):
            indices = self._slice_indices(index)

        del self._cache[index]
        del self.__indices[index]

        self._unindex_keys(indices)

    def __len__(self):
        return len(self._cache)

    def __repr__(self):
        return str(self._cache)

    def _index_type(self):
        return 'sylist'

    def _get_content_type(self, key):
        return self._content_type
