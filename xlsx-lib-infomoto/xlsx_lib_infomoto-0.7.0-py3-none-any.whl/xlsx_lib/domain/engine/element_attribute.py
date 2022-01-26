from typing import Optional

from camel_model.camel_model import CamelModel


class ElementAttribute(CamelModel):
    name: Optional[str]
    value: Optional[str]
    observations: Optional[str]
