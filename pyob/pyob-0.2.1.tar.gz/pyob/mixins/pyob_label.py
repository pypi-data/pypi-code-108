# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PYOB LABEL MIXIN
# └─────────────────────────────────────────────────────────────────────────────────────


class PyObLabelMixin:
    """A mixin class for PyOb label methods"""

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ LABEL SINGULAR
    # └─────────────────────────────────────────────────────────────────────────────────

    @property
    def label_singular(self):
        """Returns a singular label based on the class label definition or name"""

        # Return singular label
        return self.__class__.label_singular

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ LABEL PLURAL
    # └─────────────────────────────────────────────────────────────────────────────────

    @property
    def label_plural(self):
        """Returns a plural label based on the class definition or singular label"""

        # Return plural label
        return self.__class__.label_plural
