"""NanamiLang HashSet Data Type"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from typing import ValuesView
from nanamilang import shortcuts

from .base import Base
from ._imdict import ImDict
from .boolean import Boolean
from .collection import Collection


class HashSet(Collection):
    """NanamiLang HashSet Data Type Class"""

    name: str = 'HashSet'
    _expected_type = dict
    _default = {}
    _python_reference: dict
    purpose = 'Implements HashSet of NanamiLang Base data types'

    def _init__chance_to_process_and_override(self, reference) -> dict:
        """NanamiLang HashSet, process and override reference"""

        # Here we can complete HashSet structure initialization procedure

        return ImDict({element.hashed(): element for element in reference})

    def get(self, by: Base) -> Base:
        """NanamiLang HashSet, get() implementation"""

        shortcuts.ASSERT_IS_CHILD_OF(
            by,
            Base,
            message='HashSet.get: by must be Base derived'
        )

        return self.reference().get(by.hashed(), self._nil)

    def items(self) -> ValuesView:
        """NanamiLang HashSet, items() method implementation"""

        return self.reference().values()

    def contains(self, element) -> Boolean:
        """NanamiLang HashSet, contains? method implementation"""

        return Boolean(element.hashed() in self.reference().keys())

    def format(self, **_) -> str:
        """NanamiLang HashSet, the format() method implementation"""

        # There is no sense to iterate over elements when we just can return a '#{}'
        if not self._python_reference:
            return '#{}'
        return '#{' + f'{" ".join((v.format() for v in self.reference().values()))}' + '}'
