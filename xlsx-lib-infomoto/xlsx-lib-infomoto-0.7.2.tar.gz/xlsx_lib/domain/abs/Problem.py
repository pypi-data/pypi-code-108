from typing import Optional

from camel_model.camel_model import CamelModel


class Problem(CamelModel):
    code: Optional[str]
    involved_element: Optional[str]
    description: Optional[str]
