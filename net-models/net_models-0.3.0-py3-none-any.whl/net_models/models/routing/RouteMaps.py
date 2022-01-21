# Standard Libraries
# Third party packages
from pydantic import PositiveInt
from pydantic.typing import Optional, Literal, List, Any
# Local package
from net_models.fields import GENERIC_OBJECT_NAME
from net_models.models import VendorIndependentBaseModel
# Local module

#TODO: WORK IN PROGRESS

class RouteMapMatchBase(VendorIndependentBaseModel):

    match_type: Literal[
        "additional-paths", "as-path", "clns", "community", "extcommunity", "interface", "ip", "ipv6", "length",
        "local-preference", "mdt-group", "metric", "mpls-label", "policy-list", "route-type", "rpki", "security-group",
        "source-protocol", "tag", "track"
    ]
    match_value: Optional[Any]


class RouteMapSetBase(VendorIndependentBaseModel):

    set_type: Literal[
        "aigp-metric", "as-path", "automatic-tag", "clns", "comm-list", "community", "dampening", "default",
        "extcomm-list", "extcommunity", "global", "interface", "ip", "ipv6", "level", "lisp", "local-preference",
        "metric", "metric-type", "mpls-label", "origin", "tag", "traffic-index", "vrf", "weight"
    ]
    set_value: Optional[Any]

class RouteMapEntry(VendorIndependentBaseModel):

    seq_no: Optional[PositiveInt]
    action: Literal["permit", "deny"]
    description: Optional[str]
    match: Optional[RouteMapMatchBase]
    set: Optional[RouteMapSetBase]


class RouteMap(VendorIndependentBaseModel):

    name: GENERIC_OBJECT_NAME
    description: Optional[str]
    entries: Optional[List[RouteMapEntry]]

