from typing import List, Optional

from camel_model.camel_model import CamelModel

from xlsx_lib.domain.tightening_specifications.element_part import ElementPart


class SpecificationElement(CamelModel):
    name: Optional[str]
    parts: Optional[List[ElementPart]]
