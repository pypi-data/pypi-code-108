from heaobject import root
from typing import List
import copy


class Mapping(root.AbstractMemberObject):
    """Example:
    """
    def __init__(self):
        super().__init__()
        self.source = []     # An iterable of 2-tuples, each containing a record type and an attribute of the record.
        self.target = tuple()    # A tuple containing a record type and attribute.
        self.transform = None  # A function that transforms the source attribute(s) into a target attribute.
        self.comment = None


class Source2Target(root.AbstractDesktopObject):
    def __init__(self):
        super().__init__()
        self.__mappings: List[Mapping] = []

    @property
    def mappings(self) -> List[Mapping]:
        return copy.deepcopy(self.__mappings)

    @mappings.setter
    def mappings(self, mappings: List[Mapping]) -> None:
        if mappings is None:
            raise ValueError('mappings cannot be None')
        if not all(isinstance(s, Mapping) for s in mappings):
            raise TypeError('mappings can only contain Mapping objects')
        self.__mappings = copy.deepcopy(mappings)
