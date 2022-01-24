# Standard Libraries
# Third party packages
from pydantic import root_validator, Field
from pydantic.types import conint, conlist
from pydantic.typing import Optional, List, Literal
# Local package
from net_models.fields import GENERIC_OBJECT_NAME, InterfaceName, ISIS_LEVEL
from net_models.models.BaseModels import VendorIndependentBaseModel, AuthBase
from net_models.utils.get_logger import get_logger
# Local module

LOGGER = get_logger(name="NetCm-RoutingProtocols")

def validate_asn_is_defined(values):
    return values

class BfdAuthentication(AuthBase):

    method: Literal["md5","meticulous-md5","meticulous-sha-1","sha-1"]
    keychain: GENERIC_OBJECT_NAME

class BfdTemplate(VendorIndependentBaseModel):

    # TODO: Unfinished
    name: GENERIC_OBJECT_NAME
    type: Literal["single-hop", "multi-hop"]
    min_rx: Optional[int]
    min_tx: Optional[int]
    both: Optional[int]
    microseconds: Optional[bool]
    multiplier: int
    authentication: Optional[BfdAuthentication]

    @root_validator
    def validate_timers(cls, values):
        if values.get("min_tx") is not None and values.get("min_rx") is not None:
            if values.get("both") is not None:
                msg = "If 'min-tx and 'min-rx' are specified, 'both' must be None"
                LOGGER.error(msg=msg)
                raise AssertionError(msg)
        return values

class RoutingProtocolBase(VendorIndependentBaseModel):

    router_id: Optional[GENERIC_OBJECT_NAME]

class RoutingProtocolIgpBase(RoutingProtocolBase):

    passive_interface_default: Optional[bool]
    passive_interfaces: Optional[List[InterfaceName]]
    no_passive_interfaces: Optional[List[InterfaceName]]

class RoutingOspfProcess(RoutingProtocolIgpBase):

    process_id: GENERIC_OBJECT_NAME

class RoutingIsisNetwork(VendorIndependentBaseModel):

    area_id: str
    system_id: str
    nsel: str

class AuthenticationIsisMode(VendorIndependentBaseModel):

    level: ISIS_LEVEL
    auth_mode: Literal['md5', 'text']

class AuthenticationIsisKeychain(VendorIndependentBaseModel):

    level: ISIS_LEVEL
    keychain: GENERIC_OBJECT_NAME

class AuthenticationIsis(VendorIndependentBaseModel):

    mode: List[AuthenticationIsisMode]
    keychain: List[AuthenticationIsisKeychain]

class RoutingIsisLspGenInterval(VendorIndependentBaseModel):

    level: Optional[ISIS_LEVEL]
    interval: conint(ge=1, le=120)
    """Interval in seconds"""
    init_wait: Optional[conint(ge=1, le=120000)]
    """Initial wait in milliseconds"""
    wait: Optional[conint(ge=1, le=120000)]
    """Wait between first and second lsp generation in milliseconds"""

    @root_validator(allow_reuse=True)
    def validate_order(cls, values):
        level = values.get('level')
        interval = values.get('interval')
        init_wait = values.get('init_wait')
        wait = values.get('wait')

        if init_wait is not None:
            if not all([interval]):
                msg = "Field 'init_wait' can only be specified together with 'interval'."
                raise AssertionError(msg)
        if wait is not None:
            if not all([interval, init_wait]):
                msg = "Field 'wait' can only be specified together with 'interval' and 'init_wait'."
                raise AssertionError(msg)
        return values


class RoutingIsisLsp(VendorIndependentBaseModel):

    max_lifetime: Optional[conint(ge=1, le=65535)]
    refresh_interval: Optional[conint(ge=1, le=65535)]
    gen_intervals: Optional[conlist(RoutingIsisLspGenInterval, max_items=2)]

class RoutingIsisProcess(RoutingProtocolIgpBase):

    process_id: GENERIC_OBJECT_NAME
    is_type: Literal['level-1', 'level-1-2', 'level-2-only']
    metric_style: Optional[Literal['narrow', 'transition', 'wide']]
    fast_flood: Optional[conint(ge=1, le=15)]
    network: RoutingIsisNetwork
    authentication: Optional[AuthenticationIsis]
    lsp: Optional[RoutingIsisLsp]
    extra_config: Optional[List[str]]

