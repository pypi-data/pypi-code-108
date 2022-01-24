from pydantic.types import conint
from pydantic.typing import List, Optional, Literal

from net_models.fields import InterfaceName
from net_models.models.BaseModels import VendorIndependentBaseModel


class NetworkClockSource(VendorIndependentBaseModel):

    priority: conint(ge=1)
    interface: Optional[InterfaceName]
    external: Optional[str]
    src_type: Literal['interface']


class NetworkClockConfig(VendorIndependentBaseModel):

    sources: Optional[List[NetworkClockSource]]