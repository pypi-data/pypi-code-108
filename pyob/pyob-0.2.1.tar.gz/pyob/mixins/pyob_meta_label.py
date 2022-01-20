# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PROJECT IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from pyob.tools import split_camel_case


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PYOB META LABEL MIXIN
# └─────────────────────────────────────────────────────────────────────────────────────


class PyObMetaLabelMixin:
    """A mixin class for PyOb meta object label methods"""

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ LABEL SINGULAR
    # └─────────────────────────────────────────────────────────────────────────────────

    @property
    def label_singular(cls):
        """Returns a singular label based on the class label definition or name"""

        # Get label singular
        label_singular = cls.PyObMeta.label_singular

        # Use the class name as a label if necessary
        label_singular = label_singular or " ".join(split_camel_case(cls.__name__))

        # Strip label singular
        label_singular = label_singular.strip()

        # Return singular label
        return label_singular

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ LABEL PLURAL
    # └─────────────────────────────────────────────────────────────────────────────────

    @property
    def label_plural(cls):
        """Returns a plural label based on the class definition or singular label"""

        # Initialize plural label
        label_plural = cls.PyObMeta.label_plural

        # Check if plural label is null
        if not label_plural:

            # Get singular label
            label_singular = cls.label_singular

            # Check if label ends with a "y"
            if label_singular.endswith("y"):

                # Pluralize label
                label_plural = label_singular[:-1] + "ies"

            # Otherwise check if label requires "-es"
            elif label_singular.endswith(("x", "ch")):

                # Pluralize label
                label_plural = label_singular + "es"

            # Otherwise handle general case
            else:

                # Pluralize label
                label_plural = label_singular + "s"

        # Return plural label
        return label_plural
