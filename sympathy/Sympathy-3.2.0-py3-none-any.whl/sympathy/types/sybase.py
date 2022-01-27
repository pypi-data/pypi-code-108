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
"""Base module for sy-type containers."""
import numpy as np
from .. utils import complete
from . import exception as exc
from .. platform.types import get_storage_type


def assert_type(group, type1, type2):
    """
    Asserts that the types are the same,
    raises TypeError otherwise.
    """
    try:
        assert(type1 == type2)
    except Exception:
        type1 == type2
        name = group.__class__.__name__
        raise TypeError(
            "'{0}', unmatched types for operation '{1}' != '{2}'".format(
                name, type1, type2))


class GroupVisitor(object):
    """Visitor interface for sygroups."""
    def visit_dict(self, sydict):
        """Visit dict group."""
        raise NotImplementedError

    def visit_list(self, sylist):
        """Visit list group."""
        raise NotImplementedError

    def visit_record(self, syrecord):
        """Visit record group."""
        raise NotImplementedError

    def visit_table(self, sytable):
        """Visit table group."""
        raise NotImplementedError

    def visit_text(self, sytext):
        """Visit text group."""
        raise NotImplementedError


class VJoinVisitor(GroupVisitor):
    """Visitor that joins groups vertically."""

    def __init__(self, current, input_index, output_index, fill,
                 minimum_increment):
        self.current = current
        self.input_index = input_index
        self.output_index = output_index
        self.fill = fill
        self.minimum_increment = minimum_increment

    def visit_list(self, sylist):
        """
        VJoin common table columns.

        A index column named by self.index_name will be created to clarify
        interpretation.
        """
        def index(sytable):
            try:
                return sytable.get_column(self.input_index)
            except Exception:
                return np.array([0] * sytable.number_of_rows(), dtype=int)

        def column_or_nan(sytable, column, length):
            try:
                return sytable.get_column(column)
            except Exception:
                return int(length)

        def str_filler(x):
            return np.zeros(x, dtype='S1')

        def nan_filler(x):
            return np.zeros(x, dtype='f4') * np.nan

        def natdt_filler(x):
            z = np.zeros(x, dtype='datetime64[us]')
            z[:] = np.datetime64('NaT')
            return z

        def nattd_filler(x):
            z = np.zeros(x, dtype='timedelta64[us]')
            z[:] = np.timedelta64('NaT')
            return z

        def mask_filler(dtype):
            def inner(x):
                arr = np.ma.zeros(x, dtype=dtype)
                arr.mask = True
                return arr
            return inner

        def nonempty_or_last(results):
            res = []
            for result in results:
                if not len(result) == 0:
                    res.append(result)
            if not res and results:
                res = [results[-1]]
            return res

        def nonscalar(results):
            return [result for result in results if
                    not isinstance(result, int)]

        def hstack_dataset(arg):
            try:
                return np.hstack(arg)
            except TypeError as e:
                raise exc.DatasetTypeError(*e.args)

        def ma_hstack_dataset(arg):
            try:
                return np.ma.hstack(arg)
            except TypeError as e:
                raise exc.DatasetTypeError(*e.args)

        def fill(columns, mask):
            test = []
            for column in nonempty_or_last(nonscalar(columns)):
                test.append(column[:0])
            test = [[]] if not test else test
            dtype = hstack_dataset(test).dtype
            kind = dtype.kind

            if mask:
                filler = mask_filler(dtype)
            else:
                if kind in ['S', 'U']:
                    filler = str_filler
                elif kind == 'M':
                    filler = natdt_filler
                elif kind == 'm':
                    filler = nattd_filler
                else:
                    filler = nan_filler

            result = []
            has_fill = False
            has_masked = False

            for column in columns:
                if isinstance(column, np.ma.MaskedArray):
                    has_masked = True

                if isinstance(column, int):
                    result.append(filler(column))
                    has_fill = True
                else:
                    result.append(column)

            if not result:
                return np.array([], dtype=dtype)

            if mask and has_fill or has_masked:
                return ma_hstack_dataset(nonempty_or_last(result))

            return hstack_dataset(nonempty_or_last(result))

        common_columns = set()
        all_columns = []
        order = {}
        offset = 0
        indices = [[]]
        lengths = []

        # Pre-compute columns etc.
        for item in sylist:
            item_columns = item.columns()
            all_columns.append(item_columns)
            order.update(dict.fromkeys(item_columns))
            current_index = index(item)
            length = item.number_of_rows()
            minimum = np.min(current_index) if length else 0
            indices.append(current_index + (offset - minimum))

            offset += (np.max(current_index) - minimum + 1
                       if length else
                       self.minimum_increment)

            lengths.append(length)

        # Keep only common columns except when in fill mode.
        if self.fill is False:
            try:
                common_columns.update(order.keys())
                for current_columns in all_columns:
                    if current_columns:
                        common_columns = common_columns.intersection(
                            current_columns)
            except Exception:
                pass
            order = dict.fromkeys(
                [key for key in order.keys() if key in common_columns])

        # VJoin columns and attributes.
        for column in order:
            data = []
            attrs = {}

            if self.fill is not False:
                for i, item in enumerate(sylist):
                    data.append(column_or_nan(item, column, lengths[i]))
                    if column in all_columns[i]:
                        attrs.update(item.get_column_attributes(column).get())
            else:
                for length, item in zip(lengths, sylist):
                    try:
                        data.append(item.get_column(column))
                    except KeyError:
                        pass
                    try:
                        attrs.update(item.get_column_attributes(column).get())
                    except KeyError:
                        pass

            self.current.set_column(column, fill(data, self.fill is None))
            self.current.get_column_attributes(column).set(attrs)

        # VJoin index column.
        if self.current.number_of_columns() and self.output_index:
            self.current.set_column(self.output_index, hstack_dataset(indices))


class VSplitVisitor(GroupVisitor):
    """Visitor that split groups vertically."""

    def __init__(self, output_list, input_index, remove_fill):
        self.output_list = output_list
        self.remove_fill = remove_fill
        self.input_index = input_index

    def visit_table(self, sytable):
        """
        VSplit table columns.

        Split table into a list of tables.
        If a column named input_index is available then it will be used to
        group the output. Otherwise the split will operate as if a split column
        with values: 0...sytable.number_of_row() existed.

        The in either case, the index column, will not be written to the
        output.
        """
        def index(sytable):
            if self.input_index is not None:
                if isinstance(self.input_index, np.ndarray):
                    assert self.input_index.dtype.kind in 'iu', (
                        'When index is passed as a numpy array it must only '
                        ' contain integers.')
                    return self.input_index

                try:
                    return sytable.get_column(self.input_index)
                except Exception:
                    pass
            return np.arange(sytable.number_of_rows())

        def slices_using_group_array(group_array):
            """Return the slices to split by.
            A group array is made of strictly increasing group identifiers.

            >>> slices_using_group_array(np.array([0, 0, 0, 1, 1, 2, 3, 3, 3]))
            [(0, 3), (3, 5), (5, 6), (6, 9)]
            """
            unique_elements = np.unique(group_array)
            slices = []
            for unique_element in unique_elements:
                indexes = np.flatnonzero(group_array == unique_element)
                low, high = (indexes[0], indexes[-1] + 1)
                slices.append((unique_element, slice(low, high)))
            return slices

        def indices_using_group_array(group_array):
            """
            Return list of index lists, ordered by first occurance of value.
            """
            unique_elements, idx = np.unique(group_array, return_index=True)
            unique_elements = unique_elements[np.argsort(
                idx, kind='mergesort')]

            # Handle Masked
            if isinstance(unique_elements, np.ma.MaskedArray):
                mask = np.array(unique_elements.mask)
                idx = np.flatnonzero(mask)
                if len(idx):
                    mask[idx[0]] = False
                    unique_elements = unique_elements[~mask]

            # Handle NaN
            if unique_elements.dtype.kind == 'f':
                mask = np.isnan(unique_elements)
                idx = np.flatnonzero(mask)
                if len(idx):
                    mask[idx[0]] = False
                    if isinstance(mask, np.ma.MaskedArray):
                        mask = mask.filled(False)
                    unique_elements = unique_elements[~mask]

            indices = []
            for unique_element in unique_elements:
                if unique_element is np.ma.masked:
                    indices.append(
                        (unique_element, np.flatnonzero(group_array.mask)))
                elif unique_element != unique_element:
                    indices.append(
                        (np.nan, np.flatnonzero(np.isnan(group_array))))
                else:
                    indices.append(
                        (unique_element,
                         np.flatnonzero(group_array == unique_element)))
            return indices

        tattrs = sytable.get_table_attributes()
        columns = sytable.columns()
        # Perform the split and append the new tables to output.
        slice_indices = indices_using_group_array(index(sytable))
        column_attrs = {}

        loop = []

        for unique_element, slice_index in slice_indices:
            result = type(sytable)(sytable.container_type)
            self.output_list.append((unique_element, result))
            loop.append((result, slice_index))

        for column in columns:
            array = sytable.get_column(column)
            kind = array.dtype.kind
            attrs = dict(
                sytable.get_column_attributes(column).get())
            column_attrs[column] = attrs

            for result, slice_index in loop:
                # Sets of all columns except for the INDEX columns.
                sarray = array[slice_index]

                if self.remove_fill and len(sarray):
                    if isinstance(sarray, np.ma.MaskedArray):
                        if isinstance(sarray.mask, np.bool_) and sarray.mask:
                            continue
                        elif np.all(sarray.mask):
                            continue
                    if kind == 'U':
                        if np.all(sarray == u''):
                            continue
                    elif kind == 'S':
                        if np.all(sarray == b''):
                            continue
                    elif kind == 'f':
                        if np.all(np.isnan(sarray)):
                            continue

                result.set_column(column, sarray)
                attrs = column_attrs.get(column)
                if attrs:
                    result.get_column_attributes(column).set(attrs)
                if tattrs:
                    result.set_table_attributes(tattrs)


class SpineCopyVisitor(GroupVisitor):
    """
    Visitor that copies the container spine structure.
    Non-container types: sytable and sytext are referenced instead
    of copied.
    """
    def __init__(self, current):
        self.current = current

    def visit_dict(self, sydict):
        """
        Copy elements of other dict and proceed with
        visiting each copy using the same visitor.
        """
        for key, value in sydict.items():
            child = type(value)(value.container_type)
            self.current[key] = child
            value.visit(SpineCopyVisitor(child))

    def visit_list(self, sylist):
        """
        Copy elements of other sylist and proceed with
        visiting each copy using the same visitor.
        """
        for value in sylist:
            child = type(value)(value.container_type)
            self.current.append(child)
            value.visit(SpineCopyVisitor(child))

    def visit_record(self, syrecord):
        """
        Copy elements of other record and proceed with
        visiting each copy using the same visitor.
        """
        for key, value in syrecord.items():
            child = type(value)(value.container_type)
            setattr(self.current, key, child)
            value.visit(SpineCopyVisitor(child))

    def visit_table(self, sytable):
        """Update table with content of other table."""
        self.current.update(sytable)

    def visit_text(self, sytext):
        """Update text with content of other text."""
        self.current.update(sytext)


class HJoinVisitor(GroupVisitor):
    """Visitor that joins groups horizontally."""

    def __init__(self, current, mask=False, rename=False):
        self.current = current
        self.mask = mask
        self.rename = rename

    def visit_dict(self, sydict):
        """HJoin dict with other dict."""
        self.current.update(sydict)

    def visit_list(self, sylist):
        """
        Iterate over list and hjoin the list type with the matching
        element from the other list.
        """
        if len(self.current) == 0:
            self.current.extend(sylist)

        for item, other_item in zip(self.current, sylist):
            hjoin(item, other_item)

    def visit_record(self, syrecord):
        """
        HJoin current record with items from 'other record'. If 'key'
        already exist hjoin the existing value with other_value.
        HJoin requires the item types to match.
        """
        for other_key, other_value in syrecord.items():
            try:
                getattr(self.current, other_key).update(other_value)
            except KeyError:
                setattr(self.current, other_key, other_value)

    def visit_table(self, other):
        """
        HJoin the columns in the table with columns from other table.
        Overwrite if already exist.
        """
        if (self.current.number_of_rows() != other.number_of_rows()
                and self.current.number_of_columns() > 0
                and other.number_of_columns() > 0
                and not self.mask):
            raise ValueError(
                'Attempting to hjoin tables with {} and {} rows, without mask'
                .format(self.current.number_of_rows(), other.number_of_rows()))
        else:
            new_rows = max(self.current.number_of_rows(),
                           other.number_of_rows())

            def extended_column(col):
                N = new_rows - len(col)
                if isinstance(col, np.ma.MaskedArray):
                    new_mask = np.r_[np.ma.getmaskarray(col), np.ones(
                        N, dtype=bool)]
                else:
                    new_mask = np.r_[np.zeros(len(col), dtype=bool),
                                     np.ones(N, dtype=bool)]
                new_data = np.r_[col, np.zeros(N, dtype=col.dtype)]
                return np.ma.array(new_data, mask=new_mask, dtype=col.dtype)

            new_tbl = type(self.current)(None)

            if self.current.number_of_rows() < new_rows:
                for name in self.current.columns():
                    col = self.current.get_column(name)
                    new_tbl.set_column(name, extended_column(col))
                attrs = self.current.get_table_attributes()
                self.current.source(new_tbl)
                self.current.set_table_attributes(attrs)

            attrs = dict(other.get_table_attributes())

            for name in other.columns():
                new_name = name
                if self.rename:
                    cnt = 1
                    while self.current.has_column(new_name):
                        new_name = '{} ({})'.format(name, cnt)
                        cnt += 1
                if new_name != name and name in attrs:
                    attrs[new_name] = attrs[name]
                    del attrs[name]
                if other.number_of_rows() < new_rows:
                    col = extended_column(other.get_column(name))
                    self.current.set_column(new_name, col)
                else:
                    self.current.update_column(new_name, other, name)

            orig_attrs = self.current.get_table_attributes()
            orig_attrs.update(attrs)
            self.current.set_table_attributes(orig_attrs)

    def visit_text(self, sytext):
        """
        HJoin the columns in the table with columns from other table.
        Overwrite if already exist.
        """
        self.current.update(sytext)


def hjoin(first_sygroup, second_sygroup, mask=False, rename=False):
    """HJoin first and second sygroup using the HJoinVisitor."""
    visitor = HJoinVisitor(first_sygroup, mask=mask, rename=rename)
    second_sygroup.visit(visitor)


def vjoin(output_table, sylist, input_index, output_index, fill,
          minimum_increment):
    """VJoin first and second sygroup using the VJoinVisitor."""
    visitor = VJoinVisitor(output_table, input_index, output_index, fill,
                           minimum_increment)
    sylist.visit(visitor)


def vsplit(sytable, output_list, input_index, remove_fill):
    """VSplit sytable"""
    visitor = VSplitVisitor(output_list, input_index, remove_fill)
    sytable.visit(visitor)


def spinecopy(sygroup_):
    """
    Copy sygroup container structure updated with non-container types.
    Container types: sydict, sylist and syrecord are copied.
    Non-container types: sytable and sytext are updated.
    """
    copy = type(sygroup_)(sygroup_.container_type)
    visitor = SpineCopyVisitor(copy)
    sygroup_.visit(visitor)
    return copy


class Mutator(object):
    def get(self, name=None):
        """
        Get elements from a collection.
        Returns:
            A copy of the entire collection when name is None.
            A single element collection with named element when the name is
            not None.
        """
        raise NotImplementedError

    def set(self, properties):
        """Set the elements of a collections to the content of properties."""
        raise NotImplementedError

    def delete(self, name=None):
        """
        Remove elements from a collections.
        Removes:
            Every item in the entire collection when the name is None.
            Named element when name is not None.
        """
        raise NotImplementedError


class sygroup(object):
    """Base class for sy-type containers."""
    def __init__(self, container_type, datasource):
        from . factory import typefactory
        self.container_type = container_type
        self._datasource = datasource
        self._datadestination = datasource
        self._factory = typefactory
        self._dirty = True
        self._closed = False

    def names(self, kind=None, fields=None, **kwargs):
        return []

    def types(self, kind=None, **kwargs):
        return self.names(kind='cols', fields='type')

    def completions(self, **kwargs):
        return complete.builder()

    def is_valid(self):
        return True

    def sync(self):
        pass

    def source(self, other, shallow=False):
        """
        Update self with a deepcopy of the data from other, without keeping the
        old state.

        self and other must be of the exact same type.
        """
        raise NotImplementedError

    def _writeback(self, datasource, link=None):
        """
        Write back contained information to datasource.
        When link is not None then the operation will attempt to create a link.

        Returns True if data was written/linked and False otherwise.
        """
        raise NotImplementedError

    def writeback(self):
        """Write back contained information to datasource."""
        exc.assert_exc(
            self._datadestination.can_write, exc=exc.WritebackReadOnlyError)
        self._writeback(self._datadestination)

    def _link(self, datasource, key):
        """
        Write link to the internal datasource datasource in the external
        datasource, if possible.

        Returns True if a link was written and False otherwise.
        """
        if not self._dirty and datasource.transferable(self._datasource):
            datasource.link_with(key, self._datasource)
            return True

        return False

    def __copy__(self):
        cls = type(self)
        obj = cls.__new__(cls)
        obj.container_type = self.container_type
        obj._datasource = self._datasource
        obj._factory = self._factory
        obj._dirty = self._dirty
        obj._closed = True
        obj._datadestination = None
        return obj

    def visit(self, group_visitor):
        """Accept group visitor."""
        raise NotImplementedError

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        if not self._closed and self._datadestination:
            if self.can_write():
                self.writeback()
            self._datadestination.close()

    def can_write(self):
        return self._datadestination.can_write

    def can_link(self):
        return self._datadestination.can_link

    def _datasource_type(self, data_type):
        return get_storage_type(data_type)

    def _index_type(self):
        return type(self).__name__

    def index(self, limit=None) -> dict:
        """
        INTERNAL use only!

        Return READ-ONLY index of internal storage including typealiases.
        Caller may view but not modify returned structure.

        The purpose is to provide an index which can be used to query the
        structure without forcing expensive traversals of data which has not
        yet been read. For this to work, the index first of all needs to be
        set using set_index() before calling index().

        The basic idea is this, when first writing a data file written
        data will have to be read anyway, so the index can be produced with
        little overhead. The index can now be stored somewhere.

        When loading the written file, make sure to also read the index and
        apply it using set_index(), then any queries of the index structure
        will give consistent responses without requiring unnecessary traversal.

        Limit can be used, for performance reasons, to exclude certain items
        from the output.
        """
        return {'type': self._index_type()}

    def set_index(self, index: dict) -> None:
        """
        INTERNAL use only!

        Set index to provided index (produced by matching index()).
        Does nothing unless implemented. Provided index need to match
        the internal storage data-structure exactly and can therefore not be
        set after modifications.

        Caller hands over ownership of index and may not modify the argument
        structure.

        The purpose is to be able to re-store index information about files
        written to disk and have the index API take care of keeping it in sync
        with the actual file structure after modifications, without forcing
        expensive traversals of data which have not yet been read.

        Index is set on a root level and is used to provide info about the
        structure of uncached child elements. When a child element is cached
        from the own data-source, any parent index about the child element is
        passed on to the child element itself. When a child element is cached
        from an external data-source, any parent index about the child element
        is discarded.

        At all levels, index information will only be stored for uncached
        elements. So, after traversing the whole structure, there will be no
        need to keep any index since the information is readily available in
        levels of caches.
        """
        assert index['type'] == self._index_type(), (
            'Index has incorrect type.')


class sycontainer(sygroup):
    """
    Base class for container sygroups: able to contain arbitrary
    sygroups.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._index = self._base_index()
        self._index_items = self._index['items']

    def _base_index(self):
        return {
            'type': self._index_type(),
            'items': {},
        }

    def __copy__(self):
        obj = super().__copy__()
        index = dict(self._index)
        index['items'] = dict(index['items'])
        obj._index = index
        obj._index_items = index['items']
        return obj

    def _get_uncached(self, field):
        raise NotImplementedError

    def _del_cached(self, key):
        del self._cache[key]
        self._index_items.pop(key, None)

    def _set_cached_own(self, key, value):
        self._cache[key] = value
        key_index = self._index_items.pop(key, None)
        if key_index is not None:
            value.set_index(key_index)

    def _set_cached_ext(self, key, value):
        self._cache[key] = value
        self._index_items.pop(key, None)

    def _unindex_keys(self, keys):
        items = self._index_items
        for key in set(keys):
            items.pop(key, None)

    def _unindex_all(self):
        self._index_items.clear()

    def _limited_items(self, items, limit):
        items = list(items)

        if limit:
            limit = limit['items']
            if len(limit) == 1 and list(limit.keys()) == [True]:
                res = ((k, v, limit[True]) for k, v in items)
            else:
                res = ((k, v, limit.get(k)) for k, v in items)
        else:
            res = ((k, v, None) for k, v in items)
        return res

    def _cached_items(self):
        raise NotImplementedError

    def _get_content_type(self, key):
        raise NotImplementedError

    def _writeback(self, datasource, link=None):
        origin = self._datasource
        target = datasource

        exc.assert_exc(target.can_write, exc=exc.WritebackReadOnlyError)
        shared_origin = target.shares_origin(origin)
        linkable = not shared_origin and target.transferable(origin)

        if link:
            return False

        for key, value in self._cached_items():
            strkey = str(key)
            if value is None:
                if linkable and target.write_link(strkey, origin, strkey):
                    pass
                else:
                    value = self._get_uncached(key)

            if value is not None:
                value.sync()
                if not value._writeback(target, strkey):
                    new_target = target.write_with_type(
                        strkey, value, type(self._get_content_type(key)))
                    value._writeback(new_target)
        return True


class symap(sycontainer):
    """
    Base class for mapping containers rather than sequence containers.
    """
    def set_index(self, index):
        super().set_index(index)

        res = self._base_index()
        res_items = res['items']
        ind_items = index['items']

        assert set(ind_items) == set(self._cache), (
            'Index must describe all items and nothing else.')

        for k, v in self._cache.items():
            if v is None:
                ind_item = ind_items[k]
                if ind_item is not None:
                    res_items[k] = ind_item
        self._index = res
        self._index_items = self._index['items']

    def index(self, limit=None):
        res = self._base_index()
        res_items = res['items']
        ind_items = self._index['items']

        for k, v, l in self._limited_items(self._cached_items(), limit):
            if l == False:
                res_items[k] = None
            elif v is None:
                if k in ind_items:
                    res_items[k] = ind_items[k]
                else:
                    v = self._get_uncached(k)
                    self._set_cached_own(k, v)
                    res_items[k] = v.index(l)
            else:
                res_items[k] = v.index(l)
        return res

    def _cached_items(self):
        return self._cache.items()


class syseq(sycontainer):
    """
    Base class for sequence containers rather than mapping containers.

    Item index for sequences such as sylist are also dict based internally, for
    consistency, and to allow a sparse representation.

    At the interface level they are lists.
    """

    def _slice_indices(self, slice_index):
        return list(range(len(self._cache))[slice_index])

    def set_index(self, index):
        super().set_index(index)

        res = self._base_index()
        res_items = res['items']
        ind_items = dict(enumerate(index['items']))

        assert len(ind_items) == len(self._cache), (
            'Assigned index should match length of sequence.')

        for k, v in enumerate(self._cache):
            if v is None:
                res_items[k] = ind_items[k]
        self._index = res
        self._index_items = self._index['items']

    def _res_index(self):
        return {
            'type': self._index_type(),
            'items': [],
        }

    def index(self, limit=None):
        res = self._res_index()
        res_items = res['items']
        ind_items = self._index['items']

        for k, v, l in self._limited_items(self._cached_items(), limit):
            if l == False:
                res_items.append(False)
            elif v is None:
                if k in ind_items:
                    res_items.append(ind_items[k])
                else:
                    v = self._get_uncached(k)
                    self._set_cached_own(k, v)
                    res_items.append(v.index(l))
            else:
                res_items.append(v.index(l))
        return res

    def _cached_items(self):
        return enumerate(self._cache)


class NullSource(object):
    """Null datasource."""
    can_link = False
    can_write = None

    def number_of_rows(self):
        return 0

    def number_of_columns(self):
        return 0

    @staticmethod
    def writeback(datasource):
        """Null writeback."""
        pass

    @staticmethod
    def transferable(datasource):
        """Null transferable."""
        return False

    @staticmethod
    def transfer(name, other, other_name):
        """Null transfer."""
        pass

    @staticmethod
    def shares_origin(other_datasource):
        """Null shares_origin."""
        return False

    @staticmethod
    def read_with_type(key, content_type):
        """Null read_with_type."""
        raise KeyError()

    @staticmethod
    def write_with_type(key, value, content_type):
        """Null write_with_type."""
        pass

    @staticmethod
    def size():
        """Null size."""
        return 0

    @staticmethod
    def columns():
        """Null columns."""
        return []

    @staticmethod
    def read_name():
        return None

    @staticmethod
    def write_name(name):
        pass

    @staticmethod
    def write_finished():
        pass

    @staticmethod
    def write_started(number_of_rows, number_of_columns):
        pass

    @staticmethod
    def read_column_attributes(self, column_name):
        """Null read_column_attributes."""
        return None

    @staticmethod
    def write_column_attributes(self, column_name, properties):
        """Null read_column_attributes."""
        pass

    def read_table_attributes(self):
        """Null read_table_attributes."""
        return None

    def write_table_attributes(self, properties):
        """Null write_table_attributes."""
        pass

    @staticmethod
    def read_column(column_name, index=None):
        """Null read_columns."""
        return None

    @staticmethod
    def write_column(column_name, column):
        """Null write_columns."""
        pass

    def write_link(self, name, other, other_name):
        """Write link to group in other."""
        return False

    @staticmethod
    def items(content_type):
        """Null items."""
        return []

    @staticmethod
    def keys():
        """Null keys."""
        return []

    @staticmethod
    def read():
        """Null read."""
        return ''

    @staticmethod
    def write(text):
        """Null write."""
        pass

    @staticmethod
    def close():
        """Null close."""
        pass


NULL_SOURCE = NullSource()
