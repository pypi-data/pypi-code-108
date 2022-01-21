"""NanamiLang FloatNumber Data Type"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)


from .numeric import Numeric


class FloatNumber(Numeric):
    """NanamiLang FloatNumber Data Type Class"""

    name: str = 'FloatNumber'
    _expected_type = float
    _python_reference: float
    purpose = 'Encapsulate Python 3 float'

    def truthy(self) -> bool:
        """NanamiLang FloatNumber, truthy() method implementation"""

        return True
        # In Python 3 by default, all numbers == 0 are not truthy, but not in Clojure
