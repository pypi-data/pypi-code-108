"""NanamiLang HashMap Data Type"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from typing import Generator
from nanamilang import shortcuts

from .base import Base
from .vector import Vector
from ._imdict import ImDict
from .boolean import Boolean
from .collection import Collection


class HashMap(Collection):
    """NanamiLang HashMap Data Type Class"""

    name: str = 'HashMap'
    _expected_type = dict
    _default = {}
    _python_reference: dict
    purpose = 'Implement HashMap of NanamiLang Base data types'

    def _init__assertions_on_non_empty_reference(self,
                                                 reference) -> None:
        """NanamiLang HashMap, needed assertions listed here"""

        self._init_assert_only_base(reference)
        self._init_assert_ref_length_must_be_even(reference)
        # make-hashmap already takes care, but we must ensure anyway

    def _init__chance_to_process_and_override(self, reference) -> dict:
        """NanamiLang HashMap, process and override reference"""

        # Here we can complete HashMap structure initialization procedure

        partitioned = shortcuts.plain2partitioned(reference)
        return ImDict({key.hashed(): (key, val) for key, val in partitioned})

    def get(self, by: Base) -> Base:
        """NanamiLang HashMap, get() implementation"""

        shortcuts.ASSERT_IS_CHILD_OF(
            by,
            Base,
            message='HashMap.get: by must be Base derived'
        )

        return shortcuts.get(self.reference().get(by.hashed(), ()), 1, self._nil)

    def items(self) -> Generator:
        """NanamiLang Hashmap, items() method implementation"""

        return (Vector(elem) for elem in self.reference().values())

    def contains(self, element) -> Boolean:
        """NanamiLang HashMap, contains? method implementation"""

        return Boolean(element.hashed() in self.reference().keys())

    def format(self, **_) -> str:
        """NanamiLang HashMap, the format() method implementation"""

        # There is no sense to iterate over elements when we just can return  a '{}'
        if not self._python_reference:
            return '{}'
        return '{' + f'{" ".join([f"{k.format()} {v.format()}" for k, v in self.reference().values()])}' + '}'
