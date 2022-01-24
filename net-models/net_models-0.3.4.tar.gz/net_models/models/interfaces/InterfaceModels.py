# Standard Libraries
# Third party packages
from pydantic import root_validator, validator, conint, constr
from pydantic.typing import (Optional, Dict, Literal)
# Local package
from net_models.validators import *
from net_models.fields import InterfaceName, GENERIC_OBJECT_NAME, LAG_MODE, JINJA_OR_NAME
from net_models.models import VendorIndependentBaseModel
# Local module
from .InterfaceCommon import InterfaceServicePolicy
from .L2InterfaceModels import *
from .L3InterfaceModels import *
from .SpModels import ServiceInstance





__all__ = [
    'InterfaceLagMemberConfig',
    'InterfaceLldpConfig',
    'InterfaceCdpConfig',
    'InterfaceDiscoveryProtocols',
    'InterfaceNeighbor',
    'InterfaceModel',
    'InterfaceContainerModel'
]
class InterfaceLagMemberConfig(VendorIndependentBaseModel):

    _modelname = "interface_lag_member_config"

    group: conint(ge=1)
    protocol: Optional[Literal["lacp", "pagp"]]
    mode: LAG_MODE


class InterfaceLldpConfig(VendorIndependentBaseModel):

    transmit: Optional[bool]
    receive: Optional[bool]


class InterfaceCdpConfig(VendorIndependentBaseModel):

    enabled: bool


class InterfaceDiscoveryProtocols(VendorIndependentBaseModel):

    cdp: Optional[InterfaceCdpConfig]
    lldp: Optional[InterfaceLldpConfig]


class InterfaceNeighbor(VendorIndependentBaseModel):

    host: GENERIC_OBJECT_NAME
    interface: InterfaceName


class InterfaceModel(VendorIndependentBaseModel):

    _modelname = "interface_model"
    _identifiers = ["name"]
    _children = {InterfaceSwitchportModel: "l2_port", InterfaceRouteportModel: "l3_port"}

    tags: List[constr(strip_whitespace=True, to_lower=True)] = []

    name: InterfaceName
    description: Optional[str]
    enabled: Optional[bool]
    mtu: Optional[int]
    bandwidth: Optional[conint(ge=1)]
    delay: Optional[conint(ge=1)]
    load_interval: Optional[conint(ge=30)]
    l2_port: Optional[InterfaceSwitchportModel]
    l3_port: Optional[InterfaceRouteportModel]
    lag_member: Optional[InterfaceLagMemberConfig]
    discovery_protocols: Optional[InterfaceDiscoveryProtocols]
    service_policy: Optional[InterfaceServicePolicy]
    service_instances: Optional[List[ServiceInstance]]
    neighbor: Optional[InterfaceNeighbor]
    extra_config: Optional[List[str]]



    @root_validator(allow_reuse=True)
    def generate_tags(cls, values):
        tags = set(values.get("tags"))
        if values.get("l2_port"):
            tags.add("l2")
        if values.get("l3_port"):
            tags.add("l3")
        if values.get("lag_member"):
            tags.add("lag-member")

        # Interface types
        try:
            lower_name = values.get("name").lower()
            if "ethernet" in lower_name:
                tags.add("physical")
            elif any([x in lower_name for x in ["loopback", "vlan", "bdi", "tunnel", "pseudowire"]]):
                tags.add("virtual")
            elif "port-channel" in lower_name:
                tags.add('lag')
        except AttributeError as e:
            pass
        values["tags"] = sorted(list(tags))
        return values

    _normalize_tags = validator('tags', allow_reuse=True)(remove_duplicates_and_sort)
    # _normalize_interface_name = validator('name', allow_reuse=True, pre=True)(normalize_interface_name)

    def generate_description(self, format_str: str = "[{neighbor} | {neighbor_interface}]", tag: str = None, force: bool = False):

        if self.description is None:
            if self.neighbor is not None:
                description = format_str.format(
                    neighbor=self.neighbor.host,
                    neighbor_interface=normalize_interface_name(interface_name=self.neighbor.interface, short=True))
                self.description = description

    def add_ipv4_address(self, address: InterfaceIPv4Address):
        if isinstance(address, ipaddress.IPv4Interface):
            address = InterfaceIPv4Address(address=address)
        if self.l3_port is None:
            self.l3_port = InterfaceRouteportModel()
        if self.l3_port.ipv4 is None:
            self.l3_port.ipv4 = InterfaceIPv4Container()
        if self.l3_port.ipv4.addresses is None:
            self.l3_port.ipv4.addresses = []
        if address not in self.l3_port.ipv4.addresses:
            self.l3_port.ipv4.addresses.append(address)




class InterfaceContainerModel(VendorIndependentBaseModel):

    interfaces: Dict[InterfaceName, InterfaceModel] # Actually collections.OrderedDict, because Python 3.6

    _sort_interfaces = validator("interfaces", allow_reuse=True)(sort_interface_dict)

    @root_validator(allow_reuse=True, pre=True)
    def from_list(cls, values):
        interfaces = values.get('interfaces')
        if isinstance(interfaces, dict):
            pass
        elif isinstance(interfaces, list):
            interfaces = {x['name']: x for x in interfaces}
        else:
            pass
        values['interfaces'] = interfaces
        return values
