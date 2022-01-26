from typing import Union, List, Optional

from camel_model.camel_model import CamelModel

from xlsx_lib.domain.frame.element_part import ElementPart


class FrameElement(CamelModel):
    name: Optional[str]
    value: Optional[str]
    observations: Optional[Union[str, List[str]]]
    element_parts: Optional[List[ElementPart]]


