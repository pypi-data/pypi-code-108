# Some parts inspired by the AttrDict package written by Brendan Curran-Johnson (MIT Licence)

import re
import copy
import functools

from collections.abc import Mapping
import collections


def merge(left, right):
    """
    Merge two mappings objects together, combining overlapping Mappings,
    and favoring right-values
    left: The left Mapping object.
    right: The right (favored) Mapping object.
    NOTE: This is not commutative (merge(a,b) != merge(b,a)).
    """
    merged = collections.OrderedDict()

    left_keys = OrderedSet(left)
    right_keys = OrderedSet(right)

    # Items only in the left Mapping
    for key in left_keys - right_keys:
        merged[key] = left[key]

    # in both
    for key in left_keys & right_keys:
        left_value = left[key]
        right_value = right[key]

        if (isinstance(left_value, Mapping) and
                isinstance(right_value, Mapping)):  # recursive merge
            merged[key] = merge(left_value, right_value)
        else:  # overwrite with right value
            merged[key] = right_value

    # Items only in the right Mapping
    for key in right_keys - left_keys:
        merged[key] = right[key]

    return merged


def diff(left, right):
    d = collections.OrderedDict()

    left_keys = OrderedSet(left)
    right_keys = OrderedSet(right)

    # Items only in the left Mapping
    for key in left_keys - right_keys:
        d[key] = left[key]

    # in both
    for key in left_keys & right_keys:
        left_value = left[key]
        right_value = right[key]

        if (isinstance(left_value, Mapping) and
                isinstance(right_value, Mapping)):  # recursive merge
            diff_val = diff(left_value, right_value)
            if diff_val:
                d[key] = diff_val
        else:  # overwrite with right value
            if left_value == right_value:
                continue
            d[key] = left_value

    return d


def nested_dict_iter(nested):
    for key, value in nested.items():
        if isinstance(value, collections.abc.Mapping):
            for _, inner_key, inner_value in nested_dict_iter(value):
                yield value, f'{key}.{inner_key}', inner_value
        else:
            yield nested, key, value


class AttrMap(Mapping):
    """
    An implementation of MutableAttr.
    """

    def __init__(self, items=None):
        if items is None:
            items = collections.OrderedDict()
        elif not isinstance(items, Mapping):
            items = collections.OrderedDict(items)

        self._setattr('_mapping', items)

    def __getitem__(self, key):
        """
        Access a value associated with a key.
        """
        return self._mapping[key]

    def __setitem__(self, key, value):
        """
        Add a key-value pair to the instance.
        """
        self._mapping[key] = value

    def __delitem__(self, key):
        """
        Delete a key-value pair
        """
        del self._mapping[key]

    def __len__(self):
        """
        Check the length of the mapping.
        """
        return len(self._mapping)

    def __iter__(self):
        """
        Iterated through the keys.
        """
        return iter(self._mapping)

    def __repr__(self):
        """
        Return a string representation of the object.
        """
        # sequence type seems like more trouble than it is worth.
        # If people want full serialization, they can pickle, and in
        # 99% of cases, sequence_type won't change anyway
        return "AttrMap({mapping})".format(mapping=repr(self._mapping))

    @classmethod
    def _valid_name(cls, key):
        """
        Check whether a key is a valid attribute name.
        A key may be used as an attribute if:
         * It is a string
         * It matches /^[A-Za-z][A-Za-z0-9_]*$/ (i.e., a public attribute)
         * The key doesn't overlap with any class attributes (for Attr,
            those would be 'get', 'items', 'keys', 'values', 'mro', and
            'register').
        """
        return (
            isinstance(key, str) and
            re.match('^[A-Za-z][A-Za-z0-9_]*$', key) and
            not hasattr(cls, key)
        )

    def __getattr__(self, key):
        """
        Access an item as an attribute.
        """
        if key.startswith('_'):
            Mapping.__getattr__(self, key)

        if key not in self or not self._valid_name(key):
            raise AttributeError(
                "'{cls}' instance has no attribute '{name}'".format(
                    cls=self.__class__.__name__, name=key
                )
            )

        return self._build(self[key])

    def __add__(self, other):
        """
        Add a mapping to this Attr, creating a new, merged Attr.
        other: A mapping.
        NOTE: Addition is not commutative. a + b != b + a.
        """
        if not isinstance(other, Mapping):
            return NotImplemented

        s = self.copy()
        s.set_data(merge(self, other))

        return s

    def __radd__(self, other):
        """
        Add this Attr to a mapping, creating a new, merged Attr.
        other: A mapping.
        NOTE: Addition is not commutative. a + b != b + a.
        """
        if not isinstance(other, Mapping):
            return NotImplemented

        s = self.copy()
        s.set_data(merge(other, self))

        return s

    def __sub__(self, other):
        """
        Diff a mapping to this Attr, creating a new Attr.
        other: A mapping.
        NOTE: Addition is not commutative. a - b != b - a.
        """
        if not isinstance(other, Mapping):
            return NotImplemented

        s = self.copy()
        s.set_data(diff(self, other))

        return s

    def __rsub__(self, other):
        """
        Diff a mapping to this Attr, creating a new Attr.
        other: A mapping.
        NOTE: Addition is not commutative. a - b != b - a.
        """
        if not isinstance(other, Mapping):
            return NotImplemented

        s = self.copy()
        s.set_data(diff(other, self))

        return s

    def _build(self, obj):
        """
        Conditionally convert an object to allow for recursive mapping
        access.
        obj: An object that was a key-value pair in the mapping.
        """
        if isinstance(obj, Mapping):
            obj = AttrMap(obj)

        return obj

    def _setattr(self, key, value):
        """
        Add an attribute to the object, without attempting to add it as
        a key to the mapping.
        """
        Mapping.__setattr__(self, key, value)

    def __setattr__(self, key, value):
        """
        Add an attribute.
        key: The name of the attribute
        value: The attributes contents
        """
        if self._valid_name(key):
            self[key] = value
        elif key.startswith('_'):
            Mapping.__setattr__(self, key, value)
        else:
            raise TypeError(
                "'{cls}' does not allow attribute creation.".format(
                    cls=self.__class__.__name__
                )
            )

    def __delattr__(self, key, force=False):  # pragma: no cover
        """
        Delete an attribute.
        key: The name of the attribute
        """
        if self._valid_name(key):
            del self[key]
        elif key.startswith('_'):
            Mapping.__delattr__(self, key, force=force)
        else:
            raise TypeError(
                "'{cls}' does not allow attribute deletion.".format(
                    cls=self.__class__.__name__
                )
            )

    def set_data(self, mapping):
        self._mapping = mapping

    def copy(self):
        return copy.deepcopy(self)

    def update(self, other, allow_new=False):
        for key in other:
            if not allow_new:
                assert key in self, f'Key {key} does not exist'

            self[key] = other[key]

    def items(self):
        return self._mapping.items()

    def all_items(self):
        return nested_dict_iter(self)

    def all_keys(self):
        for _, k, _ in self.all_items():
            yield k

    def all_values(self):
        for _, _, v in self.all_items():
            yield v

    def get(self, key, default=None):
        try:
            return functools.reduce(lambda x, y: x[y], [self] + key.split('.'))
        except KeyError:
            return None


class OrderedSet(collections.abc.MutableSet):

    def __init__(self, iterable=None):
        self.end = end = []
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:
            key, prev, nex = self.map.pop(key)
            prev[2] = nex
            nex[1] = prev

    def __iter__(self):
        end = self.end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = self.end[1][0] if last else self.end[2][0]
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)
