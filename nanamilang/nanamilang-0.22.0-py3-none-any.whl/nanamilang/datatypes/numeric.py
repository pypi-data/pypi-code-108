"""NanamiLang Numeric Data Type"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)


from .base import Base
from .string import String
from .boolean import Boolean
from ._exports import export


class Numeric(Base):
    """NanamiLang Numeric Data Type Class"""

    name = 'Numeric'

    @export()
    def abs(self) -> Base:
        """NanamiLang Numeric, abs"""

        return self.__class__(abs(self.reference()))

    @export()
    def even(self) -> Boolean:
        """NanamiLang Numeric, even?"""

        return Boolean(self.reference() % 2 == 0)

    @export()
    def odd(self) -> Boolean:
        """NanamiLang Numeric, odd?"""

        return Boolean(not self.reference() % 2 == 0)

    @export()
    def nominal(self) -> String:
        """NanamiLang Numeric, nominal() method implementation"""

        return String(self.name)

    # Maybe, we will implement other builtin numeric-specific methods later
