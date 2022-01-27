from typing import Optional

from camel_model.camel_model import CamelModel


class ReplacementPart(CamelModel):
    name: Optional[str]
    reference: Optional[str]
    observations: Optional[str]
