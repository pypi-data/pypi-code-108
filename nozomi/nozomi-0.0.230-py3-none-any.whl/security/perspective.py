"""
Nozomi
Perspective Module
author: hugh@blinkybeach.com
"""
from nozomi.ancillary.immutable import Immutable


class Perspective:
    """
    Abstract class defining a protocol for concrete classes that identify
    perspectives
    """
    def __init__(
        self,
        perspective_id: int
    ) -> None:

        self._perpective_id = perspective_id

        return

    perspective_id = Immutable(lambda s: s._perpective_id)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Perspective):
            return False
        if not self.perspective_id == other.perspective_id:
            return False
        return True
