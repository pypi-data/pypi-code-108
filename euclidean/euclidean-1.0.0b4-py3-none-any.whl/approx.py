from sortedcontainers import SortedList
from collections.abc import Iterable, Set


def approx(a, b, atol=1e-6):
    try:
        return abs(a - b) <= atol
    except TypeError:
        return False


class ApproxSet(Set):
    """A Set of approximable instances.

    .. note::

        In order for an item to be retained by this collection, it must support
        a **total ordering**. Rather than hashing values for membership, items
        are maintained in a sorted ordering to support log(n) membership testing.

    :param iterable:
    :param approx_fcn:

    """

    def __init__(self, iterable, approx_fcn=approx):
        self.__impl = SortedList()
        self.__approx = approx_fcn
        for item in iterable:
            if item not in self:
                self.__impl.add(item)

    def __len__(self):
        return len(self.__impl)

    def __iter__(self):
        return iter(self.__impl)

    def __eq__(self, other):
        if isinstance(other, ApproxSet):
            return self.__equals(other)
        if isinstance(other, Set):
            return self.__equals(other)
        if isinstance(other, Iterable):
            return self.__equals(ApproxSet(other))
        return NotImplemented

    def __equals(self, sequence):
        if len(self) != len(sequence):
            return False
        sequence = sequence if isinstance(sequence, ApproxSet) else ApproxSet(sequence)
        return all(self.__approx(a, b) for a, b in zip(self.__impl, sequence))

    def __contains__(self, item):
        """Does the Set contain an item approximately equal to ``item``.

        :param item: The item to test for membership.
        :rtype: ``bool``
        """
        idx = self.__impl.bisect_right(item)
        return self.__test_index(idx, item) or self.__test_index(idx - 1, item)

    def __test_index(self, index, item):
        try:
            return self.__approx(self.__impl[index], item)
        except IndexError:
            return False
