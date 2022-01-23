"""
Nozomi
Immutable Module
Copyright Amatino Pty Ltd
"""


class Immutable(property):
    """
    An extension of the inbuit `property` class, which enforces immutability
    upon object properties.
    """
    _MESSAGE = """Immutable properties may not be mutated"""

    def __init__(self, fget) -> None:

        super().__init__(
            fget,
            self._set_error,
            self._del_error,
            None
        )

    def _set_error(self, _1, _2) -> None:
        raise RuntimeError(self._MESSAGE)

    def _del_error(self, _) -> None:
        raise RuntimeError(self._MESSAGE)
