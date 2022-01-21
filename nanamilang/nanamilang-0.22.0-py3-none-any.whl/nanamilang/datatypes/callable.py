"""NanamiLang Callable Data Type"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)


from .base import Base
from .string import String
from .vector import Vector
from .hashmap import HashMap
from ._exports import export


class Callable(Base):
    """NanamiLang Callable Data Type Class"""

    name = 'Callable'
    _expected_type = dict
    _python_reference: dict

    @export()
    def meta(self) -> HashMap:
        """NanamiLang Callable, meta() method implementation"""

        _meta_ = self.reference().meta
        _forms_ = tuple(String(_) for _ in _meta_.get('forms'))

        return HashMap(
            (String('forms'), Vector(_forms_),
             String('kind'), String(_meta_.get('kind')),
             String('name'), String(_meta_.get('name')),
             String('docstring'), String(_meta_.get('docstring'))))

    def origin(self) -> str:
        """NanamiLang Callable, an origin() method implementation"""

        return self.format()

    @export()
    def nominal(self) -> String:
        """NanamiLang Callable, a nominal() method implementation"""

        return String(self.name)

    def truthy(self) -> bool:
        """NanamiLang Callable, our truthy() method implementation"""

        return True
        # Let the Callable data type always return True on truthy() call
