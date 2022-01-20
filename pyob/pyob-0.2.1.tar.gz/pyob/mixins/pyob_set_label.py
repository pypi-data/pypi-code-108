# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PYOB SET LABEL MIXIN
# └─────────────────────────────────────────────────────────────────────────────────────


class PyObSetLabelMixin:
    """A mixin class for PyOb set label methods"""

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ LABEL SINGULAR
    # └─────────────────────────────────────────────────────────────────────────────────

    @property
    def label_singular(self):
        """Returns a singular label for the PyOb set"""

        # Determine if PyOb set is mixed
        is_mixed = self.count() > 1 and self._PyObClass is None

        # Get PyOb label
        ob_label = "Mixed" if is_mixed else self.ob_label_singular

        # Return singular label
        return self.__class__.__name__.replace("PyOb", ob_label + " ")

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ LABEL PLURAL
    # └─────────────────────────────────────────────────────────────────────────────────

    @property
    def label_plural(self):
        """Returns a plural label for the PyOb set"""

        # Return plural label
        return self.label_singular + "s"

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ OB LABEL SINGULAR
    # └─────────────────────────────────────────────────────────────────────────────────

    @property
    def ob_label_singular(self):
        """Returns a singular label based on related PyOb if any"""

        # Return singular label
        return (self._PyObClass and self._PyObClass.label_singular) or "PyOb"

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ OB LABEL PLURAL
    # └─────────────────────────────────────────────────────────────────────────────────

    @property
    def ob_label_plural(self):
        """Returns a plural label based on related object if any"""

        # Return plural label
        return (self._PyObClass and self._PyObClass.label_plural) or "PyObs"
