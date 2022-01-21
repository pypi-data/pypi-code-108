# Standard Libraries
# Third party packages
import ipaddress

from pydantic import root_validator, conint, constr
from pydantic.typing import Union, Optional, List, Literal, List
# Local package
from net_models.fields import (
    GENERIC_OBJECT_NAME, VRF_NAME, VLAN_ID, BRIDGE_DOMAIN_ID,
    ROUTE_TARGET, ROUTE_DISTINGUISHER, AFI, SAFI
)
# Local module
from .BaseNetModels import VendorIndependentBaseModel, BaseNetModel


__all__ = [
    'KeyBase',
    'KeyChain',
    'AuthBase',
    'VLANModel',
    'RouteTarget',
    'VRFAddressFamily',
    'VRFModel',
    'AclBase',
    'AclBaseEntry',
    'AclStandard',
    'AclExtended',
    'AclStandardIPv4',
    'AclStandardIPv4Entry',
    'AclStandardIPv6',
    'AclStandardIPv6Entry'
]


class KeyBase(VendorIndependentBaseModel):

    value: str
    encryption_type: Optional[int]


class KeyChain(VendorIndependentBaseModel):

    name: GENERIC_OBJECT_NAME
    description: Optional[str]
    keys_list: List[KeyBase]


class AuthBase(VendorIndependentBaseModel):

    pass


class VLANModel(VendorIndependentBaseModel):

    _modelname = "vlan_model"

    vlan_id: VLAN_ID
    name: Optional[GENERIC_OBJECT_NAME]
    enabled: Optional[bool]


class VtpConfig(VendorIndependentBaseModel):
    version: Optional[Literal[1, 2, 3]]
    mode: Optional[Literal['server', 'client', 'transparent', 'off']]
    domain: Optional[GENERIC_OBJECT_NAME]
    primary: Optional[bool]

    @root_validator(allow_reuse=True)
    def validate_primary(cls, values):
        primary = values.get('primary')
        version = values.get('version')
        if primary is not None:
            if version is None:
                raise AssertionError(f"If 'primary' is set, 'version' cannot be None.")
            elif isinstance(version, int):
                if version != 3:
                    raise AssertionError(f"If 'primary' is set, 'version' must be set to 3.")
        return values


class StpConfig(VendorIndependentBaseModel):
    protocol: Optional[str]
    # TODO: Finish up


class BridgeDomainModel(VendorIndependentBaseModel):
    bridge_domain_id: BRIDGE_DOMAIN_ID
    enabled: Optional[bool]


class RouteTarget(VendorIndependentBaseModel):

    rt: ROUTE_TARGET
    action: Literal['export', 'import', 'both']
    rt_type: Optional[Literal['stitching']]


class VRFAddressFamily(VendorIndependentBaseModel):

    afi: AFI
    """Address family type"""
    safi: Optional[SAFI]
    """Address family sub-type"""
    route_targets: Optional[List[RouteTarget]]


class VRFModel(VendorIndependentBaseModel):

    name: VRF_NAME
    rd: Optional[ROUTE_DISTINGUISHER]
    address_families: Optional[List[VRFAddressFamily]]
    description: Optional[str]



class AclBaseEntry(BaseNetModel):
    
    seq_no: Optional[conint(ge=1)]
    remark: Optional[str]
    action: Literal['permit', 'deny']


class AclBase(BaseNetModel):

    name: Union[int, GENERIC_OBJECT_NAME]
    entries: Optional[List[AclBaseEntry]]
    acl_type: Literal['standard', 'extended']
    acl_version: Literal['ipv4', 'ipv6']


class AclStandard(AclBase):

    acl_type: Literal['standard'] = 'standard'


class AclExtended(AclBase):

    acl_type: Literal['extended'] = 'extended'


class AclStandardIPv4Entry(AclBaseEntry):

    src_address: Union[ipaddress.IPv4Address, ipaddress.IPv4Network, Literal['any']]
    src_wildcard: Optional[Union[constr(regex=r"(?:\d{1,3}\.){3}(?:\d{1,3})")]]

    root_validator(allow_reuse=True)
    def wildcard_required(cls, values):
        src_wildcard = values.get('src_wildcard')
        if isinstance(values.get('src_address'), ipaddress.IPv4Network):
            if src_wildcard is not None:
                msg = f"If 'src_address' is specified with netmask, 'src_wildcard' must be None"
                raise AssertionError(msg)
        if isinstance(values.get('src_address'), ipaddress.IPv4Address):
            if src_wildcard is None:
                msg = f"If 'src_address' is specified as without netmask, 'src_wildcard' must be set"
                raise AssertionError(msg)
        if values.get('src_address') == 'any':
            if src_wildcard is not None:
                msg = f"If 'src_address' is any, 'src_wildcard' must be None"
                raise AssertionError(msg)
        return values


class AclStandardIPv6Entry(AclBaseEntry):

    pass


class AclStandardIPv4(AclStandard):

    acl_version: Literal['ipv4'] = 'ipv4'
    entries: List[AclStandardIPv4Entry]


class AclStandardIPv6(AclStandard):

    acl_version: Literal['ipv6'] = 'ipv6'
    entries: List[AclStandardIPv4Entry]