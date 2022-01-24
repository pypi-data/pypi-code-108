from net_models.models import BaseNetModel
from net_models.fields import GENERIC_OBJECT_NAME, VRF_NAME
from net_models.models.services.cisco_ios.AaaMethods import IosLineAaaConfig
from pydantic.types import conlist, conint
from pydantic.typing import Optional, Literal, List, Union


__all__ = [
    "IosLineTransport",
    "IosLineAccessClass",
    "IosLineConfig"
]

class IosLineTransport(BaseNetModel):

    input: Optional[Literal['all', 'none', 'ssh', 'telnet']]
    output: Optional[Literal['all', 'none', 'ssh', 'telnet']]
    preferred: Optional[Literal['none', 'ssh', 'telnet']]


class IosLineLogging(BaseNetModel):

    synchronous: Optional[bool]
    level: Optional[Union[Literal['all'], conint(ge=0, le=7)]]
    limit: Optional[int]

class IosLineAccessClass(BaseNetModel):

    name: GENERIC_OBJECT_NAME
    vrf_also: Optional[bool]
    vrf: Optional[VRF_NAME]
    direction: Literal['in', 'out']


class IosLineConfig(BaseNetModel):

    line_type: Literal['aux', 'console', 'vty']
    line_range: conlist(item_type=conint(ge=0), min_items=1, max_items=2)
    aaa_config: Optional[IosLineAaaConfig]
    """AAA Configuration Object"""
    exec_timeout: Optional[conint(ge=0)]
    """EXEC Timeout in seconds"""
    transport: Optional[IosLineTransport]
    access_classes: Optional[List[IosLineAccessClass]]
