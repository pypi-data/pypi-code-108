"""
Nozomi
Index Equitable Module
author: hugh@blinkybeach.com
"""


class IndexEquitable:
    """
    Abstract class defining an interface which, when adopted, allows
    conformant classes to test for equality using their database indexids.

    This protocol is suitable for adoption by classes whose whole identity is
    uniquely, universally, and totally defined by their indexid.
    """

    indexid: int = NotImplemented

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return False
        if not isinstance(self.indexid, int):
            raise NotImplementedError('Public .indexid required')
        return other.indexid == self.indexid
