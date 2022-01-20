from contextlib import suppress

from django.core.exceptions import ImproperlyConfigured
from six import string_types


def cmp(a, b):
    """Comparison predicat."""
    return (a > b) - (a < b)


class Bit:
    """Represents a single Bit."""

    def __init__(self, number, is_set=True):
        """Initializing."""
        self.number = number
        self.is_set = bool(is_set)
        self.mask = 2 ** int(number)
        self.children = []
        if not self.is_set:
            self.mask = ~self.mask

    def evaluate(self, evaluator, qn, connection):
        """Evaluate."""
        return self.mask, []

    def prepare(self, evaluator, query, allow_joins):
        """Prepare."""
        return evaluator.prepare_node(self, query, allow_joins)

    def __repr__(self):
        return "<{0}: number={1}, is_set={2}>".format(
            self.__class__.__name__,
            self.number,
            self.is_set,
        )

    def __int__(self):
        return self.mask

    def __bool__(self):
        return self.is_set

    def __eq__(self, value):
        if isinstance(value, Bit):
            return value.number == self.number and value.is_set == self.is_set
        elif isinstance(value, bool):
            return value == self.is_set
        elif isinstance(value, int):
            return value == self.mask
        return value == self.is_set

    def __ne__(self, value):
        return not self == value  # noqa: WPS508

    def __coerce__(self, value):
        return (self.is_set, bool(value))

    def __invert__(self):
        return self.__class__(self.number, not self.is_set)

    def __and__(self, value):
        if isinstance(value, Bit):
            value = value.mask
        return value & self.mask

    def __rand__(self, value):
        if isinstance(value, Bit):
            value = value.mask
        return self.mask & value

    def __or__(self, value):
        if isinstance(value, Bit):
            value = value.mask
        return value | self.mask

    def __ror__(self, value):
        if isinstance(value, Bit):
            value = value.mask
        return self.mask | value

    def __lshift__(self, value):
        if isinstance(value, Bit):
            value = value.mask
        return value << self.mask

    def __rlshift__(self, value):
        if isinstance(value, Bit):
            value = value.mask
        return self.mask << value

    def __rshift__(self, value):
        if isinstance(value, Bit):
            value = value.mask
        return value >> self.mask

    def __rrshift__(self, value):
        if isinstance(value, Bit):
            value = value.mask
        return self.mask >> value

    def __xor__(self, value):
        if isinstance(value, Bit):
            value = value.mask
        return value ^ self.mask

    def __rxor__(self, value):
        if isinstance(value, Bit):
            value = value.mask
        return self.mask ^ value


class BitHandler:
    """Represents an array of bits, each as a ``Bit`` object."""

    def __init__(self, value, keys, labels=None):
        """Initializing."""
        # TODO: change to bitarray?
        if value:
            self._value = int(value)
        else:
            self._value = 0
        self._keys = keys
        self._labels = labels is not None and labels or keys

    def __str__(self):
        return str(self._value)

    @property
    def mask(self):
        """Mask."""
        return self._value

    def evaluate(self, evaluator, qn, connection):
        """Evaluate."""
        return self.mask, []

    def get_bit(self, bit_number):
        """Get bit by position."""
        mask = 2 ** int(bit_number)
        return Bit(bit_number, self._value & mask != 0)

    def set_bit(self, bit_number, true_or_false):
        """Set bit in position."""
        mask = 2 ** int(bit_number)
        if true_or_false:
            self._value |= mask
        else:
            self._value &= ~mask
        return Bit(bit_number, self._value & mask != 0)

    def keys(self):
        """Keys."""
        return self._keys

    def items(self):
        """Items."""
        return [(key, getattr(self, key).is_set) for key in self._keys]

    def get_label(self, flag):
        """Get flag label."""
        if isinstance(flag, string_types):
            flag = self._keys.index(flag)
        if isinstance(flag, Bit):
            flag = flag.number
        return self._labels[flag]

    def __eq__(self, other):
        if not isinstance(other, BitHandler):
            return False
        return self._value == other._value

    def __lt__(self, other):
        return int(self._value) < other

    def __le__(self, other):
        return int(self._value) <= other

    def __gt__(self, other):
        return int(self._value) > other

    def __ge__(self, other):
        return int(self._value) >= other

    def __cmp__(self, other):
        return cmp(self._value, other)

    def __repr__(self):
        return "<{0}: {1}>".format(
            self.__class__.__name__,
            ", ".join(
                "{0}={1}".format(k, self.get_bit(n).is_set)
                for n, k in enumerate(self._keys)
            ),
        )

    def __int__(self):
        return self._value

    def __bool__(self):
        return bool(self._value)

    def __and__(self, value):
        return BitHandler(self._value & int(value), self._keys)

    def __or__(self, value):
        return BitHandler(self._value | int(value), self._keys)

    def __add__(self, value):
        return BitHandler(self._value + int(value), self._keys)

    def __sub__(self, value):
        return BitHandler(self._value - int(value), self._keys)

    def __lshift__(self, value):
        return BitHandler(self._value << int(value), self._keys)

    def __rshift__(self, value):
        return BitHandler(self._value >> int(value), self._keys)

    def __xor__(self, value):
        return BitHandler(self._value ^ int(value), self._keys)

    def __contains__(self, key):
        bit_number = self._keys.index(key)
        return bool(self.get_bit(bit_number))

    def __getattr__(self, key):
        if key.startswith("_"):
            return object.__getattribute__(self, key)
        if key not in self._keys:
            raise AttributeError("{0} is not a valid flag".format(key))
        return self.get_bit(self._keys.index(key))

    def __setattr__(self, key, value):
        if key.startswith("_"):
            return object.__setattr__(self, key, value)
        if key not in self._keys:
            raise AttributeError("{0} is not a valid flag".format(key))
        self.set_bit(self._keys.index(key), value)

    def __iter__(self):
        yield from self.items()


def register_sqlite3_adapters():
    """Register adapters for sqlite."""
    with suppress(ImproperlyConfigured):
        from django.db.backends.sqlite3.base import Database

        Database.register_adapter(Bit, int)
        Database.register_adapter(BitHandler, int)


def register_postgres_adapters():
    """Register adapters for postgres."""
    with suppress(ImproperlyConfigured):
        from django.db.backends.postgresql.base import Database

        Database.extensions.register_adapter(
            Bit,
            lambda x: Database.extensions.AsIs(int(x)),
        )
        Database.extensions.register_adapter(
            BitHandler,
            lambda x: Database.extensions.AsIs(int(x)),
        )


register_sqlite3_adapters()
register_postgres_adapters()
