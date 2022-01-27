"""Data sorting helpers."""


class ReverseComparator:
    """Class to allow reverse comparison for initialized object."""

    def __init__(self, obj):
        """Init object to be compared in reverse order."""
        self.obj = obj

    def __eq__(self, other):
        """Check equality in reverse."""
        return other.obj == self.obj

    def __lt__(self, other):
        """Check less than in reverse."""
        return other.obj < self.obj
