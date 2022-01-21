# Standard Libraries
import ipaddress
# Third party packages
from pydantic import conint
from pydantic.typing import Optional
# Local package
from net_models.fields import VRF_NAME, INTERFACE_NAME
from net_models.models import VendorIndependentBaseModel
# Local module



class StaticRoute(VendorIndependentBaseModel):

    vrf: Optional[VRF_NAME]
    interface: Optional[INTERFACE_NAME]
    metric: Optional[conint(ge=1, le=255)]

class StaticRouteV4(StaticRoute):

    network: ipaddress.IPv4Network
    next_hop: Optional[ipaddress.IPv4Address]


class StaticRouteV6(StaticRoute):

    network: ipaddress.IPv6Network
    next_hop: Optional[ipaddress.IPv6Address]
