from typing import Optional

from camel_model.camel_model import CamelModel


class TighteningSpecificationStep(CamelModel):
    name: Optional[str]
    tightening_specification: Optional[str]
