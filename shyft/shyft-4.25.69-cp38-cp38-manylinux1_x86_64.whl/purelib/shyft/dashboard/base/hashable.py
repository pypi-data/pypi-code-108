"""
This module contains the Hashable base class
"""
import uuid


class Hashable:
    """
    This class is used as base class.
    From this class derived objects can be used as dictionary keys.
    The class has a unique __uid and implements the __hash__ and __eq__ functions
    """

    def __init__(self):
        """
        Init of the hashable base class
        """
        self.__uid = uuid.uuid4().int

    def __hash__(self):
        """
        This function returns the hash of the object
        """
        return hash(self.__uid)

    def __eq__(self, other: 'Hashable') -> bool:
        """
        Compares if 2 objects are the same
        """
        return isinstance(other, self.__class__) and self.uid == other.uid

    @property
    def uid(self) -> int:
        """
        Returns the uid of the hashable object
        """
        return self.__uid
