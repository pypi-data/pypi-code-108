from typing import List, Optional

from camel_model.camel_model import CamelModel

from xlsx_lib.domain.tightening_specifications.tightening_torque_step import TighteningSpecificationStep


class Screw(CamelModel):
    name: Optional[str]
    tightening_specification: Optional[str]
    steps: Optional[List[TighteningSpecificationStep]]
    detail: Optional[str]
