from typing import Optional

from camel_model.camel_model import CamelModel


class Fault(CamelModel):
    code: Optional[str]
    description: Optional[str]
    observations: Optional[str]
