"""NanamiLang Vector Data Type"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from nanamilang import shortcuts
from ._exports import export
from .base import Base
from .collection import Collection
from .integernumber import IntegerNumber


class Vector(Collection):
    """NanamiLang Vector Data Type Class"""

    name: str = 'Vector'
    _expected_type = tuple
    _default = tuple()
    _python_reference: tuple
    purpose = 'Implements Vector of NanamiLang Base data types'

    @export()
    def range(self,
              _from_: IntegerNumber,
              _to_:   IntegerNumber) -> Base:
        """
        NanamiLang Vector, range() implementation
        Takes _from_, _to_ and returns a new Vector
        """

        assert isinstance(_from_, IntegerNumber), (
            'Vector.range: needs to be an IntegerNumber'
        )
        assert isinstance(_to_, IntegerNumber), (
            'Vector.range: needs to be an IntegerNumber'
        )

        return self.__class__(tuple(map(IntegerNumber,
                                        range(_from_.reference(),
                                              _to_.reference()))))

    def get(self, by: IntegerNumber) -> Base:
        """NanamiLang Vector, get() implementation"""

        shortcuts.ASSERT_IS_INSTANCE_OF(
            by,
            IntegerNumber,
            message='Vector.get: an index must be an IntegerNumber'
        )

        return shortcuts.get(self.reference(), by.reference(), self._nil)

    def format(self, **_) -> str:
        """NanamiLang Vector, format() method implementation"""

        # There is no sense to iterate over elements when we can return '[]'
        if not self._python_reference:
            return '[]'
        return '[' + f'{" ".join((i.format() for i in self.reference()))}' + ']'
