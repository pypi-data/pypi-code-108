# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PROJECT IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from pyob.mixins import PyObSetDunderMixin, PyObSetLabelMixin, PyObSetMethodMixin
from pyob.tools import convert_string_to_pascal_case


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PYOB SET
# └─────────────────────────────────────────────────────────────────────────────────────


class PyObSet(PyObSetLabelMixin, PyObSetDunderMixin, PyObSetMethodMixin):
    """A base class for PyOb sets"""

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ CLASS ATTRIBUTES
    # └─────────────────────────────────────────────────────────────────────────────────

    # Initialize PyOb class to None
    _PyObClass = None

    # Initialize PyOb dict to None
    _pyob_dict = None

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ INIT METHOD
    # └─────────────────────────────────────────────────────────────────────────────────

    def __init__(self, PyObClass):
        """Init Method"""

        # Set PyOb class
        self._PyObClass = PyObClass

        # Initialize PyOb dict
        self._pyob_dict = {}

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ NEW
    # └─────────────────────────────────────────────────────────────────────────────────

    def New(self):
        """Returns a new empty PyOb set with the same PyOb class"""

        # Return new PyOb set
        return PyObSet(PyObClass=self._PyObClass)

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ NAME
    # └─────────────────────────────────────────────────────────────────────────────────

    @property
    def name(self):
        """Returns the name of the PyOb set"""

        # Get the name based on the computed singular label
        name = self.label_singular

        # Convert name to Pascal case
        name = convert_string_to_pascal_case(name)

        # Return the name
        return name
