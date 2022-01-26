from typing import List, Optional

from camel_model.camel_model import CamelModel

from xlsx_lib.domain.tightening_specifications.part_screw import Screw


class ElementPart(CamelModel):
    name: Optional[str]
    screws: Optional[List[Screw]]
