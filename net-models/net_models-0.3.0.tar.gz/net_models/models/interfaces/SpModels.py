# Standard Libraries
# Third party packages
from pydantic import root_validator, validator, conint, constr, conlist
from pydantic.typing import (
    Optional,
    Dict,
    Literal
)
# Local package
from net_models.validators import *
from net_models.fields import GENERIC_OBJECT_NAME, InterfaceName, VLAN_ID, BRIDGE_DOMAIN_ID, L2_PROTOCOL, CLASS_OF_SERVICE
from net_models.models import VendorIndependentBaseModel
# Local module
from .InterfaceCommon import InterfaceServicePolicy
from .L2InterfaceModels import InterfaceSwitchportModel
from .L3InterfaceModels import InterfaceRouteportModel


class PseudowireBase(VendorIndependentBaseModel):

    pass


class PseudowireFlowLabel(PseudowireBase):

    direction: Literal['transmit', 'receive', 'both']
    static: Optional[bool]


class PseudowireLoadBalancing(PseudowireBase):

    pseudowire_label: Optional[bool]
    flow_label: Optional[PseudowireFlowLabel]


class PseudowireEncapsulation(PseudowireBase):

    encapsulation_type: Literal['mpls', 'l2tpv3']
    control_word: Optional[bool]
    load_balancing: Optional[PseudowireLoadBalancing]


class PseudowireClass(PseudowireBase):
    """
    This model describes pseudowire class
    """

    name: GENERIC_OBJECT_NAME
    encapsulation: PseudowireEncapsulation


class PseudowireNeighborBase(PseudowireBase):
    """
    Base Class for both primary and backup pseudowire neighbors
    """
    pw_id: conint(ge=1, le=4294967295)
    pw_class: Optional[GENERIC_OBJECT_NAME]

class PseudowireNeighbor(PseudowireNeighborBase):
    """
    Primary Pseudowire Neighbor
    """
    address_version: Optional[Literal["ipv4", "ipv6"]]
    address: Union[ipaddress.IPv4Address, ipaddress.IPv6Address]

    @root_validator(allow_reuse=True)
    def generate_address_version(cls, values):
        if not values.get("address_version"):
            if isinstance(values.get("server"), ipaddress.IPv4Address):
                values["address_version"] = "ipv4"
            elif isinstance(values.get("server"), ipaddress.IPv6Address):
                values["address_version"] = "ipv6"
        return values


class PseudowireBackupNeighbor(PseudowireNeighborBase):
    """
    Backup Pseudowire Neighbor
    """
    address: ipaddress.IPv4Address


class Pseudowire(PseudowireBase):

    name: GENERIC_OBJECT_NAME
    pw_type: Optional[Literal['p2p', 'mp2mp']]
    interface: InterfaceName
    neighbor: PseudowireNeighbor
    backup_neighbor: Optional[PseudowireBackupNeighbor]


class XConnectGroup(VendorIndependentBaseModel):

    name: GENERIC_OBJECT_NAME
    members: List[Pseudowire]


class Dot1QEncapsulation(VendorIndependentBaseModel):
    """
    This class applies both to dot1q and dot1ad
    """
    vid_range: conlist(item_type=VLAN_ID, min_items=1)
    cos: Optional[CLASS_OF_SERVICE]
    etype: Optional[Literal['ipv4', 'ipv6', 'pppoe-all', 'pppoe-discovery', 'pppoe-session']]
    exact: Optional[bool]


class InterfaceEncapsulation(VendorIndependentBaseModel):

    encapsulation_type: Literal['default', 'dot1ad', 'dot1q', 'priority-tagged', 'untagged']
    outer_tag: Optional[Dot1QEncapsulation]
    inner_tag: Optional[Dot1QEncapsulation]


class ServiceInstanceL2Protocol(VendorIndependentBaseModel):

    forward: Optional[List[L2_PROTOCOL]]
    peer: Optional[List[L2_PROTOCOL]]


class RewriteOperation(VendorIndependentBaseModel):

    action: Literal['pop', 'push', 'translate']
    tag: Literal[1, 2]
    symmetric: Optional[bool]


class ServiceInstanceRewrite(VendorIndependentBaseModel):

    ingress: Optional[RewriteOperation]
    egress: Optional[RewriteOperation]


class ServiceInstance(VendorIndependentBaseModel):

    si_id: conint(ge=1)
    evc: Optional[GENERIC_OBJECT_NAME]
    description: Optional[str]
    encapsulation: Optional[InterfaceEncapsulation]
    evc_name: Optional[GENERIC_OBJECT_NAME]
    l2_protocol: Optional[ServiceInstanceL2Protocol]
    bridge_domain: Optional[BRIDGE_DOMAIN_ID]
    rewrite: Optional[ServiceInstanceRewrite]
    service_policy: Optional[InterfaceServicePolicy]
    enabled: Optional[bool]