from typing import List, Optional

from camel_model.camel_model import CamelModel

from xlsx_lib.domain.electronic.element_component import ElementComponent


class ElectronicElement(CamelModel):
    name: Optional[str]
    components: Optional[List[ElementComponent]]
