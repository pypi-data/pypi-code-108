# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PROJECT IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from pyob.pyob_meta import PyObMeta
from pyob.pyob_set import PyObSet

from pyob.mixins import PyObDunderMixin, PyObLabelMixin
from pyob.tools import localize


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PYOB
# └─────────────────────────────────────────────────────────────────────────────────────


class PyOb(PyObLabelMixin, PyObDunderMixin, metaclass=PyObMeta):
    """A base class for PyOb classes"""

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ LOCALIZED
    # └─────────────────────────────────────────────────────────────────────────────────

    @classmethod
    def Localized(cls, include=None):
        """Returns a localized version of the PyOb class with an empty object store"""

        # Return localized classes
        return localize(cls, *(include or []))

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ SET
    # └─────────────────────────────────────────────────────────────────────────────────

    @classmethod
    def Set(cls):
        """Initializes a new PyOb set for the current PyOb class"""

        # Return the initialized PyOb set
        return PyObSet(PyObClass=cls)

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ PYOB META
    # └─────────────────────────────────────────────────────────────────────────────────

    class PyObMeta:
        """PyOb Meta Class"""
