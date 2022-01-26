from typing import List, Optional

from camel_model.camel_model import CamelModel

from xlsx_lib.domain.engine.section_element import SectionElement


class EngineSection(CamelModel):
    name: Optional[str]
    section_elements: Optional[List[SectionElement]]
