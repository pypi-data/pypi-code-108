from typing import Optional

from camel_model.camel_model import CamelModel


class Component(CamelModel):
    number: Optional[str]
    name: Optional[str]
