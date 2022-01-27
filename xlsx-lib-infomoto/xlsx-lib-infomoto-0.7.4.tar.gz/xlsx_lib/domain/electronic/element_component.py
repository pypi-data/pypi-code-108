from typing import List, Optional

from camel_model.camel_model import CamelModel

from xlsx_lib.domain.electronic.component_attribute import ComponentAttribute


class ElementComponent(CamelModel):
    name: Optional[str]
    value: Optional[str]
    observations: Optional[str]
    attributes: Optional[List[ComponentAttribute]]
