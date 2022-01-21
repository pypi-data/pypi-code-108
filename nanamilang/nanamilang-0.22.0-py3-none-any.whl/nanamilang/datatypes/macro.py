"""NanamiLang Macro Data Type"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)


from .callable import Callable


class Macro(Callable):
    """NanamiLang Macro Data Type Class"""

    name: str = 'Macro'
    purpose = 'Encapsulate macro name and its Python 3 handle'

    def _set_hash(self, reference) -> None:
        """NanamiLang Macro, an overridden Base implementation"""

        self._hashed = hash(
            reference.get('macro_reference')
        )

    def _additional_assertions_on_init(self,
                                       reference) -> None:
        """NanamiLang Macro, an overridden Base implementation"""

        self.init_assert_reference_has_keys(
            reference, ('macro_name', 'macro_reference')
        )

    def format(self, **_) -> str:
        """NanamiLang Macro, the format() method implementation"""

        return self._python_reference.get('macro_name')

    def reference(self):
        """NanamiLang Macro, the reference() method implementation"""

        return self._python_reference.get('macro_reference')

    # format() and reference() return macro name and handle respectively
    # Since self._python_reference is a dict of macro name and reference
