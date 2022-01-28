from enum import Enum


class TopNDict2:
    class AppendType(Enum):
        APPEND_LAZY = 1
        APPEND_SORT_AND_SETTLE = 2
        APPEND_BISECT_INSERT = 3

    def __init__(
        self,
        n: int,
        name: str,
        dictionary: dict = None,
        append_type: AppendType = AppendType.APPEND_BISECT_INSERT,
        verbosity: int = 0,
    ):
        """Generate a two level dictionary of the top N appended items.

        Can take an active or lazy approach to appending items.

        Active means sorting and trimming the list on every append. This keeps
        the size down, at the expense of more sorts being performed, albeit on a
        list of fixed maximum size.

        Lazy adds items to the list, deferring sorting and trimming until
        completion is triggered. Less upfront work, more space may be used, final
        sort will be on all added items.

        Args:

            n (int): Maximum number of entries in the dictionary.

            name (str): Name of this instance.

            dictionary (dict, optional): Where the entries end up. If none is
                specified a new one is created to be returned at completion.

            lazy (bool, optional): Use the lazy append or not. Defaults to True.

            verbosity (int, optional): Display info on stdout. Defaults to 0.
        """
        self._n = n
        self.name = name
        self._dict = {} if dictionary is None else dictionary
        self._append_type = append_type
        self._verbosity = verbosity

        self._needs_settling = False
        self._list = [("", "", 0)]

    # --------------------------------------------------------------------------

    def settle(self):
        """Sort and trim the internal list as necessary"""

        if self._needs_settling:
            self._needs_settling = False
            self._list.sort(key=take_third, reverse=True)

            if len(self._list) > self._n:
                self._list = self._list[0 : self._n]

    # --------------------------------------------------------------------------

    def append_lazily(self, key1, key2, value):
        """Append the specified item, deferring sorting and trimming.

        Args:
            key1 : Key to first level of dict stack
            key2 : Key to second level of dict stack
            value : Value of item
        """

        self._needs_settling = True
        self._list.append((key1, key2, value))

    # --------------------------------------------------------------------------

    def append_and_settle(self, key1, key2, value):
        """Append the specified item if it meets the current criteria.

        Append if either the list isn't yet full, or if the new value
        supercedes that of (at least) the current tail.

        Args:
            key1 : Key to first level of dict stack
            key2 : Key to second level of dict stack
            value : Value of item
        """

        if self._needs_settling:
            self.settle()

        if (len(self._list) < self._n) or (value > self._list[-1][2]):
            self._list.append((key1, key2, value))
            self.settle()

    # --------------------------------------------------------------------------

    def bisect_insert(self, key1, key2, value):
        """Insert the specified item if it meets the current criteria.

        Insert if either the list isn't yet full, or if the new value
        supercedes that of (at least) the current tail.

        Args:
            key1 : Key to first level of dict stack
            key2 : Key to second level of dict stack
            value : Value of item
        """

        if self._needs_settling:
            self.settle()

        if (len(self._list) < self._n) or (value > self._list[-1][2]):

            # The list is known to be sorted, so bisect insertion should
            # be cheaper than append-then-sort.

            lo = 0
            hi = len(self._list)

            while lo < hi:
                mid = (lo + hi) // 2
                if value > self._list[mid][2]:
                    hi = mid
                else:
                    lo = mid + 1

            self._list.insert(lo, (key1, key2, value))

            if len(self._list) > self._n:
                self._list = self._list[0 : self._n]

    # --------------------------------------------------------------------------

    def append(self, key1, key2, value, append_type: AppendType = None):
        """Handle appending the specified item to the list.

        If 'lazy', either according to the instance's setting or, if set, this
        method's parameter, append the specified item, deferring sorting and
        trimming.

        Otherwise append the specified item if it meets the current criteria.
        I.e. append if either the list isn't yet full, or if the new value
        supercedes that of (at least) the current tail.

        Args:
            key1 : Key to first level of dict stack
            key2 : Key to second level of dict stack
            value : Value of item
            lazy (bool, optional) : Override this instance's lazyness
        """

        if append_type == self.AppendType.APPEND_LAZY:
            self.append_lazily(key1, key2, value)
        elif append_type == self.AppendType.APPEND_SORT_AND_SETTLE:
            self.append_and_settle(key1, key2, value)
        else:
            self.bisect_insert(key1, key2, value)

    # --------------------------------------------------------------------------

    def complete(self) -> dict:
        """Wrap things up and update dictionary

        Returns:
            dict: The values stored in a dictionary
        """
        if self._needs_settling:
            self.settle()

        if self._verbosity > 0:
            print(f"Top {self._n} by {self.name}:")

        for key1, key2, value in self._list:
            if key1 == "":
                print(f"WARN: Missing key1 in TopNDict2 '{self.name}'(?)")
            else:
                if key1 not in self._dict:
                    self._dict[key1] = {}

                self._dict[key1][key2] = True

                if self._verbosity > 0:
                    print(f"  {key1} [{key2}] {round(value,2)}")

        return self._dict


# ------------------------------------------------------------------------------
# Used to select third element of a tuple
def take_third(item):
    return item[2]
