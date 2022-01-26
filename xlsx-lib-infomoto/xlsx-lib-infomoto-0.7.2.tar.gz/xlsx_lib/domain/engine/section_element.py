from typing import List, Optional

from camel_model.camel_model import CamelModel

from xlsx_lib.domain.engine.element_attribute import ElementAttribute


class SectionElement(CamelModel):
    name: Optional[str]
    value: Optional[str]
    observations: Optional[str]
    element_attributes: Optional[List[ElementAttribute]]
