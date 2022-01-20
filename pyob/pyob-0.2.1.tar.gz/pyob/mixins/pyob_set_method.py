# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ GENERAL IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from functools import cmp_to_key
from operator import itemgetter

# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PROJECT IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from pyob.exceptions import MultipleObjectsError, NonExistentKeyError, ZeroObjectsError
from pyob.tools import (
    filter_and,
    filter_by_key,
    filter_by_keys,
    is_pyob_set,
)
from pyob.utils import Nothing


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PYOB SET METHOD MIXIN
# └─────────────────────────────────────────────────────────────────────────────────────


class PyObSetMethodMixin:
    """A mixin class for PyOb set methods"""

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ APPEND
    # └─────────────────────────────────────────────────────────────────────────────────

    def append(self, ob, distinct=False):
        """Appends a PyOb to a PyOb set"""

        # Return if distinct and PyOb already in PyOb set
        if distinct and ob in self:
            return

        # Update current instance
        self.__dict__ = (self + ob).__dict__

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ COPY
    # └─────────────────────────────────────────────────────────────────────────────────

    def copy(self):
        """Copies a PyOB set into a new PyOb set"""

        # Return a copied PyOb set
        return self.New() + self

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ COUNT
    # └─────────────────────────────────────────────────────────────────────────────────

    def count(self):
        """Returns a count of PyObs in a PyOb set"""

        # Return the length of the PyOb set
        return len(self)

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ DIFFERENCE
    # └─────────────────────────────────────────────────────────────────────────────────

    def difference(self, obs):
        """Returns the difference of two PyOb sets using the - operator"""

        # Return the difference of the PyOb sets
        return self - obs

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ DISTINCT
    # └─────────────────────────────────────────────────────────────────────────────────

    def distinct(self):
        """Returns a PyOb set of distinct items from the current PyOb set"""

        # Return the union of an empty and the current PyOb set
        return self.New() + set(self)

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ EXTEND
    # └─────────────────────────────────────────────────────────────────────────────────

    def extend(self, obs, distinct=False):
        """Extends the current PyOb set by another PyOb set"""

        # Check if distinct
        if distinct:

            # Filter out PyObs that already exist in current PyOb set
            obs = obs - self if is_pyob_set(obs) else [o for o in obs if o not in self]

        # Update current instance
        self.__dict__ = (self + obs).__dict__

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ FILTER
    # └─────────────────────────────────────────────────────────────────────────────────

    def filter(self, **kwargs):
        """Filters a PyOb set based on a series of keyword arguments"""

        # Return filtered PyOb set
        return self.New() + filter_and(self._pyob_dict, **kwargs)

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ FILTER BY KEY
    # └─────────────────────────────────────────────────────────────────────────────────

    def filter_by_key(self, value):
        """Filters a PyOb set based on key"""

        # Return filtered PyOb set
        return self.New() + filter_by_key(
            pyob_dict=self._pyob_dict,
            keys=self._PyObClass.PyObMeta.keys,
            value=value,
            ob_label_plural=self.ob_label_plural,
        )

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ FILTER BY KEYS
    # └─────────────────────────────────────────────────────────────────────────────────

    def filter_by_keys(self, *values):
        """Filters a PyOb set based on key"""

        # Return filtered PyOb set
        return self.New() + filter_by_keys(
            pyob_dict=self._pyob_dict,
            keys=self._PyObClass.PyObMeta.keys,
            values=values,
            ob_label_plural=self.ob_label_plural,
        )

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ FILTER FIRST
    # └─────────────────────────────────────────────────────────────────────────────────

    def filter_first(self, **kwargs):
        """Filters a PyOb set and returns the first result"""

        # Return first PyOb of filtered PyOb set
        return self.filter(**kwargs).first()

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ FILTER ONLY
    # └─────────────────────────────────────────────────────────────────────────────────

    def filter_only(self, **kwargs):
        """Filters a PyOb set and returns the only result or error"""

        # Return the only PyOb of the filtered PyOb set
        return self.filter(**kwargs).only()

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ FIRST
    # └─────────────────────────────────────────────────────────────────────────────────

    def first(self, n=None):
        """Returns the first PyOb of a PyOb set"""

        # Get PyObs as list
        pyobs = list(self)

        # Return the first (n) PyOb(s) of the PyOb set
        return self[: n + 1] if n is not None else (pyobs[0] if pyobs else None)

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ INTERSECTION
    # └─────────────────────────────────────────────────────────────────────────────────

    def intersection(self, pyobs):
        """Returns the intersection of two PyOb sets using the & operator"""

        # Return the intersection of both PyOb sets
        return self & pyobs

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ KEY
    # └─────────────────────────────────────────────────────────────────────────────────

    def key(self, key, default=Nothing):
        """Returns the PyOb associated with a key from the PyOb set"""

        # Get PyObs by key
        pyobs = self.filter_by_key(key)

        # Check if distinct PyOb count is 1
        if pyobs.distinct().count() == 1:

            # Return the first and only PyOb
            return pyobs.first()

        # Check if default is Nothing
        if default is Nothing:

            # Get PyOb label singular
            ob_label_singular = self.ob_label_singular

            # Raise NonExistentKeyError
            raise NonExistentKeyError(
                f"A {ob_label_singular} instance with a key of {key} does not exist"
            )

        # Return default
        return default

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ KEYS
    # └─────────────────────────────────────────────────────────────────────────────────

    def keys(self, *keys):
        """Returns a PyOb set of PyObs associated with a series of keys"""

        # Initialize an empty PyOb set
        obs = self.New()

        # Iterate over keys
        for key in keys:

            # Filter by key and add distinct PyObs to PyOb set
            obs |= self.filter_by_key(key)

        # Return filtered PyOb set
        return obs

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ LAST
    # └─────────────────────────────────────────────────────────────────────────────────

    def last(self, n=None):
        """Returns the last PyOb of a PyOb set"""

        # Get PyObs as list
        pyobs = list(self)

        # Return the last (n) PyOb(s) of the PyOb set
        return self[-n:] if n is not None else (pyobs[-1] if pyobs else None)

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ ONLY
    # └─────────────────────────────────────────────────────────────────────────────────

    def only(self):
        """Returns the one and only PyOb in a PyOb set or raises an error"""

        # Get distinct PyOb count
        ob_count = self.distinct().count()

        # Return first and only PyOb
        if ob_count == 1:
            return self.first()

        # Get PyOb set name
        name = self.name

        # Get PyOb plural label
        ob_label_plural = self.ob_label_plural.lower()

        # Check if there are multiple PyObs
        if ob_count > 1:

            # Raise MultipleObjectsError
            raise MultipleObjectsError(
                f"{name}.only() returned multiple {ob_label_plural}"
            )

        # Otherwise raise ZeroObjectsError
        raise ZeroObjectsError(f"{name}.only() returned zero {ob_label_plural}")

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ SORT
    # └─────────────────────────────────────────────────────────────────────────────────

    def sort(self, *fields):
        """
        Sorts a PyOb set based on a series of field arguments

        https://stackoverflow.com/questions/1143671/how-to-sort-objects-by-multiple-
            keys-in-python
        """

        # ┌─────────────────────────────────────────────────────────────────────────────
        # │ FIELDS
        # └─────────────────────────────────────────────────────────────────────────────

        # Strip fields
        fields = [field.strip() for field in fields]

        # Convert fields into signed itemgetters
        fields = [
            (
                (itemgetter(field[1:]), -1)
                if field.startswith("-")
                else (itemgetter(field), 1)
            )
            for field in fields
        ]

        # ┌─────────────────────────────────────────────────────────────────────────────
        # │ CMP
        # └─────────────────────────────────────────────────────────────────────────────

        # Define inner cmp helper function
        def cmp__(x, y):
            """Compares the x and y values"""

            # Return result
            return (x > y) - (x < y)

        # Define outer cmp helper function
        def cmp_(x, y, mult):
            """
            Replacement for built-in function cmp that was removed in Python 3

            Compare the two objects x and y and return an integer according to
            the outcome. The return value is negative if x < y, zero if x == y
            and strictly positive if x > y.

            https://portingguide.readthedocs.io/en/latest/comparisons.html
                #the-cmp-function
            """

            # Iterate over x and y
            for (value, result) in ((x, 1), (y, -1)):

                # Check if value is None
                if value is None:

                    # Return result based on sort direction
                    return mult * result

                    # NOTE: This ensures that None values are always at the end

            # Initialize try-except block
            try:

                # Return comparison of x and y
                return cmp__(x, y)

            # Handle TypeError, e.g. "foo" > 5
            except TypeError:

                # Return comparison of x and y type IDs
                return cmp__(*[id(type(val)) for val in (x, y)])

                # NOTE: We can't arbitrarily drop elements; so just sort them by type

        # Define main cmp function
        def cmp(left, right):

            # Define field iterator
            field_iter = (
                cmp_(fn(left.__dict__), fn(right.__dict__), mult) * mult
                for fn, mult in fields
            )

            # Return result
            return next((result for result in field_iter if result), 0)

        # ┌─────────────────────────────────────────────────────────────────────────────
        # │ RETURN SORTED OBJECT SET
        # └─────────────────────────────────────────────────────────────────────────────

        # Return sorted PyOb set
        return self.New() + sorted(self._pyob_dict, key=cmp_to_key(cmp))

        # TODO: HANDLE DICT IN __ADD__
        # TODO: FieldError for non-existent fields?
        # TODO: Make sortable objects traversable

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ UNION
    # └─────────────────────────────────────────────────────────────────────────────────

    def union(self, obs):
        """Returns the union of two PyOb sets using the | operator"""

        # Return the union of both PyOb sets
        return self | obs
