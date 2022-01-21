# Standard Libraries
import ipaddress
# Third party packages
from pydantic import conint, constr, root_validator
from pydantic.typing import Optional, Union, List, Literal
# Local package
from net_models.validators import *
from net_models.fields import GENERIC_OBJECT_NAME, VRF_NAME, BASE_INTERFACE_NAME, InterfaceName
from net_models.models import VendorIndependentBaseModel, NamedModel, KeyBase, AuthBase
# Local module


class ServerBase(VendorIndependentBaseModel):

    pass


class ServerPropertiesBase(ServerBase):

    server: Union[ipaddress.IPv4Address, ipaddress.IPv6Address]
    src_interface: Optional[InterfaceName]
    vrf: Optional[VRF_NAME]


class NtpKey(KeyBase):

    key_id: int
    method: Literal["md5"]
    trusted: Optional[bool]


class NtpServer(ServerPropertiesBase):

    key_id: Optional[int]
    prefer: Optional[bool]


class NtpAccessGroups(VendorIndependentBaseModel):

    serve_only: Optional[GENERIC_OBJECT_NAME]
    query_only: Optional[GENERIC_OBJECT_NAME]
    serve: Optional[GENERIC_OBJECT_NAME]
    peer: Optional[GENERIC_OBJECT_NAME]


class NtpConfig(VendorIndependentBaseModel):

    authenticate: Optional[bool]
    servers: Optional[List[NtpServer]]
    peers: Optional[List[NtpServer]]
    ntp_keys: Optional[List[NtpKey]]
    src_interface: Optional[InterfaceName]
    access_groups: Optional[NtpAccessGroups]


class LoggingSource(VendorIndependentBaseModel):

    src_interface: Optional[InterfaceName]
    vrf: Optional[VRF_NAME]

class LoggingDiscriminatorAction(VendorIndependentBaseModel):

    match: Literal["facility", "mnemonics", "msg-body", "rate-limit", "severity"]
    value: str
    action: Literal["drops", "includes"]

class LoggingDiscriminator(VendorIndependentBaseModel):

    name: constr(max_length=8)
    actions: List[LoggingDiscriminatorAction]



class LoggingServer(ServerPropertiesBase):

    protocol: Optional[Literal["tcp", "udp"]]
    port: Optional[int]
    discriminator: Optional[GENERIC_OBJECT_NAME]

    @root_validator(allow_reuse=True)
    def validate_port_protocol(cls, values):
        return validators.required_together(values=values, required=["port", "protocol"])


class LoggingLevels(VendorIndependentBaseModel):

    history: Optional[Union[str, int]]
    trap: Optional[Union[str, int]]




class LoggingConfig(VendorIndependentBaseModel):

    servers: Optional[List[LoggingServer]]
    sources: Optional[List[LoggingSource]]
    discriminators: Optional[List[LoggingDiscriminator]]
    buffer_size: Optional[conint(ge=0)]
    traps: Optional[List[str]]

    @root_validator(allow_reuse=True)
    def _validate_servers_unique(cls, values):
        servers = values.get('servers')
        if servers is not None:
            validate_fields_unique(obj_list=servers, fields=['server'])
        return values


class AaaServer(ServerBase):

    name: GENERIC_OBJECT_NAME
    server: Union[ipaddress.IPv4Address, ipaddress.IPv6Address]
    address_version: Optional[Literal["ipv4", "ipv6"]]
    timeout: Optional[conint(ge=1)]
    key: KeyBase
    single_connection: Optional[bool]

    @root_validator(allow_reuse=True)
    def generate_address_version(cls, values):
        if not values.get("address_version"):
            if isinstance(values.get("server"), ipaddress.IPv4Address):
                values["address_version"] = "ipv4"
            elif isinstance(values.get("server"), ipaddress.IPv6Address):
                values["address_version"] = "ipv6"
        return values


class RadiusServer(AaaServer):

    retransmit: Optional[conint(ge=1)]


class TacacsServer(AaaServer):

    pass


class AaaServerGroup(ServerBase):

    name: GENERIC_OBJECT_NAME
    src_interface: Optional[InterfaceName]
    vrf: Optional[VRF_NAME]

    @root_validator(allow_reuse=True)
    def _validate_unique_fields(cls, values):
        servers = values.get('servers')
        if servers is not None:
            validate_fields_unique(obj_list=servers, fields=['name', 'server'])
        return values


class RadiusServerGroup(AaaServerGroup):

    servers: List[RadiusServer]


class TacacsServerGroup(AaaServerGroup):

    servers: List[TacacsServer]


class AAAServerConfig(VendorIndependentBaseModel):

    radius_groups: Optional[List[RadiusServerGroup]]
    tacacs_groups: Optional[List[TacacsServerGroup]]

    def _validate_tacacs_group_uniquenes(cls, values):
        tacacs_groups = values.get('tacacs_groups')
        if tacacs_groups is not None:
            validate_fields_unique(obj_list=tacacs_groups, fields=['name', 'server'])
        return values

    def _validate_tacacs_group_uniquenes(cls, values):
        radius_groups = values.get('radius_groups')
        if radius_groups is not None:
            validate_fields_unique(obj_list=radius_groups, fields=['name', 'server'])
        return values

class SnmpView(VendorIndependentBaseModel):

    name: GENERIC_OBJECT_NAME
    mib: str
    action: Literal["included", "excluded"]


class SnmpUserAuth(AuthBase):

    method: Literal["md5", "sha"]
    value: str


class SnmpUserPriv(AuthBase):

    method: Literal["des", "3des", "aes"]
    key_length: Optional[Literal[128, 192, 256]]
    value: str

    @root_validator(allow_reuse=True)
    def key_length_required(cls, values):
        method = values.get('method')
        if method == 'aes':
            key_length = values.get('key_length')
            if key_length is None:
                raise AssertionError("If method == 'aes', 'key_length' must be specified")
        return values

class SnmpGroup(VendorIndependentBaseModel):

    name: GENERIC_OBJECT_NAME
    version: Literal["v1", "v2c", "v3"]
    level: Optional[Literal["noauth", "auth", "priv"]]
    read: Optional[GENERIC_OBJECT_NAME]
    write: Optional[GENERIC_OBJECT_NAME]
    notify: Optional[GENERIC_OBJECT_NAME]
    access_list: Optional[GENERIC_OBJECT_NAME]


class SnmpUser(VendorIndependentBaseModel):

    name: GENERIC_OBJECT_NAME
    group: GENERIC_OBJECT_NAME
    version: Literal["v1", "v2c", "v3"]
    auth: Optional[SnmpUserAuth]
    priv: Optional[SnmpUserPriv]
    group: GENERIC_OBJECT_NAME
    access_list: Optional[GENERIC_OBJECT_NAME]

class SnmpServer(ServerPropertiesBase):

    version: Optional[Literal['1', '2c', '3']]
    auth: Optional[str]

class SnmpTrapsConfig(VendorIndependentBaseModel):

    src_traps: Optional[InterfaceName]
    src_informs: Optional[InterfaceName]
    dscp: Optional[str]
    chassis_id: Optional[Literal['hostname']]
    traps_enable: Optional[List[str]]

class SnmpConfig(VendorIndependentBaseModel):

    users: Optional[List[SnmpUser]]
    groups: Optional[List[SnmpGroup]]
    views: Optional[List[SnmpView]]
    traps_config: Optional[SnmpTrapsConfig]