# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PROJECT IMPORTS
# └─────────────────────────────────────────────────────────────────────────────────────

from pyob.tools import (
    convert_string_to_pascal_case,
    is_pyob,
    validate_and_index_pyob_attribute_value,
)


# ┌─────────────────────────────────────────────────────────────────────────────────────
# │ PYOB DUNDER MIXIN
# └─────────────────────────────────────────────────────────────────────────────────────


class PyObDunderMixin:
    """A mixin class for PyOb dunder methods"""

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __ADD__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __add__(self, other):
        """Add Method"""

        # Return an PyOb set containing the two PyObs
        return self.Set() + self + other

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __REPR__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __repr__(self, display=None):
        """Representation Method"""

        # Initialize representation
        representation = self.label_singular

        # Convert representation to Pascal case
        representation = convert_string_to_pascal_case(representation)

        # Add angle brackets to representation
        representation = f"<{representation}: {self.__str__(display=display)}>"

        # Return representation
        return representation

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __SETATTR__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __setattr__(self, name, value):
        """Set Attr Method"""

        # ┌─────────────────────────────────────────────────────────────────────────────
        # │ ATTRIBUTES
        # └─────────────────────────────────────────────────────────────────────────────

        # Get PyOb class
        cls = self.__class__

        # ┌─────────────────────────────────────────────────────────────────────────────
        # │ PRE-SETTER
        # └─────────────────────────────────────────────────────────────────────────────

        # Get pre-setter methods
        pre = cls.PyObMeta.pre or {}

        # Check if name in pre-setter methods
        if name in pre:

            # Apply pre-setter to value
            value = pre[name](self, value)

        # ┌─────────────────────────────────────────────────────────────────────────────
        # │ VALIDATE AND INDEX ATTRIBUTE VALUE
        # └─────────────────────────────────────────────────────────────────────────────

        # Validate and index attribute value
        validate_and_index_pyob_attribute_value(cls, self, name, value)

        # ┌─────────────────────────────────────────────────────────────────────────────
        # │ RETURN PARENT SET ATTR
        # └─────────────────────────────────────────────────────────────────────────────

        # Call parent set attr method
        super().__setattr__(name, value)

        # ┌─────────────────────────────────────────────────────────────────────────────
        # │ POST-SETTER
        # └─────────────────────────────────────────────────────────────────────────────

        # Get post-setter methods
        post = cls.PyObMeta.post or {}

        # Check if name in post-setter methods
        if name in post:

            # Apply post-setter to value
            value = post[name](self, value)

    # ┌─────────────────────────────────────────────────────────────────────────────────
    # │ __STR__
    # └─────────────────────────────────────────────────────────────────────────────────

    def __str__(self, root=None, display=None):
        """String Method"""

        # Initialize root
        root = root if root is not None else self

        # Get display field if defined otherwise the first key if any
        display_field = (
            display
            or self.PyObMeta.display
            or (self.PyObMeta.keys[0] if self.PyObMeta.keys else None)
        )

        # Set string to value of string field
        string = display_field and getattr(self, display_field, None)

        # Check if string is a PyOb
        if is_pyob(string):

            # Check if related PyOb is not root and has a string field
            if string != root and (string.PyObMeta.display or string.PyObMeta.keys):

                # Evaluate the string of the related PyOb
                # Root is passed for comparison to avoid cases of infinite recursion
                string = string.__str__(root=root)

            # Otherwise ignore the object
            else:

                # Set string to None
                # Otherwise would return the hex which would be confusing
                string = None

        # Set default to hex address if string is null
        string = string or hex(id(root))

        # Ensure string is actually a string
        string = str(string)

        # Return string
        return string
