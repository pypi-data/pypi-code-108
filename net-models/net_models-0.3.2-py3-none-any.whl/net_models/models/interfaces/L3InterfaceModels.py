# Standard Libraries
# Third party packages
from pydantic import validator, root_validator
from pydantic.typing import (
    List,
    Literal,
    Optional
)
# Local package
from net_models.validators import *
from net_models.fields import *
from net_models.models import (
    VendorIndependentBaseModel,
    AuthBase,
    KeyBase
)
# Local module


class InterfaceIPv4Address(VendorIndependentBaseModel):

    _modelname = "interface_ipv4_address_model"

    address: ipaddress.IPv4Interface
    secondary: Optional[bool]

    _validate_address = validator("address", allow_reuse=True)(ipv4_is_assignable)


class InterfaceIPv6Address(VendorIndependentBaseModel):

    _modelname = "interface_ipv6_address_model"

    address: ipaddress.IPv6Interface


class InterfaceDhcpClientConfig(VendorIndependentBaseModel):

    _model_name = "interface_dhcp_client"

    enabled: Optional[bool]


class InterfaceIPv4Container(VendorIndependentBaseModel):

    _modelname = "interface_ipv4_container"

    addresses: Optional[List[InterfaceIPv4Address]]
    unnumbered: Optional[INTERFACE_NAME]
    dhcp_client: Optional[InterfaceDhcpClientConfig]

    # @root_validator(allow_reuse=True)
    # def validate_non_overlapping(cls, values):
    #     addresses = values.get("addresses")
    #     if addresses is None:
    #         return values
    #     for address in addresses:
    #         other_addresses = list(addresses)
    #         other_addresses.remove(address)
    #         for other_address in other_addresses:
    #             if address.address in other_address.address.network:
    #                 raise AssertionError(f"Address {str(other_address.address)} overlaps with {str(address.address)}")
    #     return values

    @root_validator(allow_reuse=True)
    def validate_single_primary(cls, values):
        addresses = values.get("addresses")
        if addresses is None:
            return values
        if len(addresses) == 1:
            return values
        # Get addresses with secondary==False or secondary==None
        primary_addresses = [x for x in addresses if x.secondary in [False, None]]
        if len(primary_addresses) > 1:
            raise AssertionError(f"Multiple 'primary addresses' found, only one allowed. {[x.dict() for x in addresses]}")
        return values


class InterfaceIPv6Container(VendorIndependentBaseModel):

    _modelname = "interface_ipv6_container"

    addresses: Optional[List[InterfaceIPv6Address]]


class KeyOspf(KeyBase):

    value: constr(max_length=8)

    @validator('value', allow_reuse=True, pre=True)
    def truncate_value(cls, value):
        if len(value) > 8:
            value = value[:8]
        return value

class InterfaceOspfAuthentication(AuthBase):

    method: Optional[Literal['message-digest', 'key-chain', 'null']]
    keychain: Optional[GENERIC_OBJECT_NAME]
    key: Optional[KeyOspf]

    @root_validator(allow_reuse=True)
    def validate_keychain_present(cls, values):
        method = values.get('method')
        keychain = values.get('keychain')
        key = values.get('key')
        if method == 'key-chain' and keychain is None:
            raise AssertionError("When method is 'keychain', keychain cannot be None")
        if method != 'key-chain' and keychain is not None:
            raise AssertionError("Field keychain can only be set if method == 'key-chain'")
        if method not in [None, 'message-digest'] and key is not None:
            raise AssertionError("Field key can only be set if method in [None, 'message-digest']")
        return values


class InterfaceOspfTimers(VendorIndependentBaseModel):

    hello: Optional[conint(ge=1, le=65535)]
    dead: Optional[Union[conint(ge=1, le=65535), Literal['minimal']]]
    retransmit: Optional[conint(ge=1, le=65535)]


class InterfaceOspfConfig(VendorIndependentBaseModel):

    _modelname = "interface_ospf_config"

    process_id: Optional[int]
    area: Optional[int]
    network_type: Optional[Literal['broadcast', 'non-broadcast', 'point-to-multipoint', 'point-to-point']]
    cost: Optional[int]
    priority: Optional[int]
    authentication: Optional[InterfaceOspfAuthentication]
    timers: Optional[InterfaceOspfTimers]
    bfd: Optional[Union[bool, Literal['strict-mode']]]

    @root_validator(allow_reuse=True)
    def validate_process_and_area(cls, values):
        if values.get("process_id") is not None and  values.get("area") is None:
            raise AssertionError("When 'process_id' is set, 'area' is required.")
        elif values.get("process_id") is None and values.get("area") is not None:
            raise AssertionError("When 'area' is set, 'process_id' is required.")
        return values


class InterfaceBfdConfig(VendorIndependentBaseModel):

    template: GENERIC_OBJECT_NAME


class IsisMetricField(VendorIndependentBaseModel):

    _modelname = "isis_metric_field"

    level: Literal["level-1", "level-2"]
    metric: int


class IsisInterfaceAuthentication(AuthBase):

    mode: Optional[Literal['md5', 'text']]
    keychain: Optional[str]

class InterfaceIsisConfig(VendorIndependentBaseModel):

    _modelname = "interface_isis_config"

    process_id: Optional[Union[int, GENERIC_OBJECT_NAME]]
    network_type: Optional[str]
    circuit_type: Optional[str]
    authentication: Optional[IsisInterfaceAuthentication]
    metric: Optional[List[IsisMetricField]]


class RoutePortEncapsulation(VendorIndependentBaseModel):

    encapsulation: Literal['dot1q']
    tag: VLAN_ID
    native: Optional[bool]


class InterfaceFhrpBase(VendorIndependentBaseModel):

    protocol: Literal['vrrp', 'hsrp', 'glbp']


class InterfaceFhrpGroup(VendorIndependentBaseModel):

    group_id: conint(ge=0, le=4095)


class HsrpTimers(VendorIndependentBaseModel):

    hello: conint(ge=1)
    hold: conint(ge=1)
    milliseconds: Optional[bool]

    @root_validator(allow_reuse=True)
    def validate_timers(cls, values):
        hello = values.get('hello')
        hold = values.get('hold')
        if hold <= hello:
            raise AssertionError(f"Timer for 'hold' must be greater than 'hello'")
        return values



class HsrpAuthentication(VendorIndependentBaseModel):

    method: Literal['md5', 'text', 'key-chain']
    keychain: Optional[GENERIC_OBJECT_NAME]
    key: Optional[KeyBase]

    @root_validator(allow_reuse=True)
    def validate_keychain_present(cls, values):
        method = values.get('method')
        keychain = values.get('keychain')
        key = values.get('key')
        if method == 'key-chain' and keychain is None:
            raise AssertionError("When method is 'keychain', keychain cannot be None")
        if method != 'key-chain' and keychain is not None:
            raise AssertionError("Field keychain can only be set if method == 'key-chain'")
        if method not in ['text', 'md5'] and key is not None:
            raise AssertionError("Field key can only be set if 'method' in ['text', 'md5']")
        return values


class HsrpIpv4Address(VendorIndependentBaseModel):

    address: ipaddress.IPv4Address
    secondary: Optional[bool]


class HsrpTrack(VendorIndependentBaseModel):

    track_id: conint(ge=1)
    action: Literal['shutdown', 'decrement']
    decrement_value: Optional[conint(ge=1)]


class InterfaceHsrpGroup(InterfaceFhrpGroup):

    name: Optional[HSRP_GROUP_NAME]
    ipv4: Optional[List[HsrpIpv4Address]]
    priority: Optional[conint(ge=1, le=255)]
    preemption: Optional[bool]
    timers: Optional[HsrpTimers]
    authentication: Optional[HsrpAuthentication]
    tracks: Optional[List[HsrpTrack]]
    follow: Optional[HSRP_GROUP_NAME]
    """Name of HSRP group to follow"""



class InterfaceHsrp(InterfaceFhrpBase):

    protocol: Literal['hsrp'] = 'hsrp'
    version: Literal[1, 2]
    groups: Optional[List[InterfaceHsrpGroup]]
    extra_config: Optional[List[str]]

    @root_validator(allow_reuse=True)
    def validate_group_numbers(cls, values):
        version = values.get('version')
        groups = values.get('groups')
        if isinstance(groups, list):
            if version == 1:
                high_group_ids = [x['group_id'] for x in groups if x['group_id'] > 255]
                if len(high_group_ids):
                    raise AssertionError(f"With 'version' == 1, maximum of 255 is allowed for group['group_id']")
        return values

    @root_validator(allow_reuse=True)
    def sort_groups(cls, values):
        groups = values.get('groups')
        if groups is not None:
            groups = sorted(groups, key=lambda x: x.group_id)
            values['groups'] = groups
        return values


class InterfaceRouteportModel(VendorIndependentBaseModel):

    _modelname = "routeport_model"
    _identifiers = []

    ipv4: Optional[InterfaceIPv4Container]
    ipv6: Optional[InterfaceIPv6Container]
    encapsulation: Optional[RoutePortEncapsulation]
    vrf: Optional[str]
    ip_mtu: Optional[int]
    ospf: Optional[InterfaceOspfConfig]
    isis: Optional[InterfaceIsisConfig]
    bfd: Optional[InterfaceBfdConfig]
    hsrp: Optional[InterfaceHsrp]

    def add_ipv4_address(self, address: Union[InterfaceIPv4Address, ipaddress.IPv4Interface]):
        if self.ipv4 is None:
            self.ipv4 = InterfaceIPv4Container()
        if self.ipv4.addresses is None:
            self.ipv4.addresses = []
        if not isinstance(address, InterfaceIPv4Address):
            address = InterfaceIPv4Address(address=address)
        self.ipv4.addresses.append(address)
        self.ipv4 = self.ipv4.clone()


