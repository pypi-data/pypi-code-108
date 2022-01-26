from typing import List, Optional

from camel_model.camel_model import CamelModel

from xlsx_lib.domain.shared.NewImageData import NewImageData
from xlsx_lib.domain.components.Component import Component


class ComponentsData(CamelModel):
    components: List[Component] = list()
    components_image: Optional[NewImageData]
