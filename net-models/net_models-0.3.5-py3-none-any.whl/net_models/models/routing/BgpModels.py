# Standard Libraries
import ipaddress
# Third party packages
from pydantic import validator, root_validator, Field
from pydantic.typing import Optional, List, Union, Literal
# Local package
from net_models.validators import validate_unique_name_field
from net_models.fields import *
from net_models.models import VendorIndependentBaseModel, KeyBase
# Local module
from .RoutingProtocols import RoutingProtocolBase

class BgpTimers(VendorIndependentBaseModel):

    hello: int = Field(title="Hello time", description="Hello timer in seconds")
    hold: int = Field(title="Hold time", description="Hold timer in seconds")

    @root_validator
    def hold_higher_than_hello(cls, values: dict) -> dict:
        """Validates that hold time is higher than hello time"""
        if values.get("hello") >= values.get("hold"):
            msg = "'hold' must be higher than 'hello'"
            raise AssertionError(msg)
        return values

class BgpFallOver(VendorIndependentBaseModel):

    enabled: bool
    type: Optional[Literal["route-map", "bfd"]]
    route_map: Optional[ROUTE_MAP_NAME]
    """Name of the route-map"""

    @root_validator
    def routemap_required(cls, values: dict) -> dict:
        """Asserts that ``route-map`` is provided if ``type`` == ``"route-map"``"""
        if values.get("type") == "route-map" and not values.get("route-map"):
            msg = "Field 'route-map' is required when 'type' == 'route-map'"
            raise AssertionError()
        return values


class BgpNeighborBase(VendorIndependentBaseModel):
    """
    Base Class for BGP Nighbor, used for neighbors and peer-groups
    """
    # TODO: Unfinished
    name: Optional[GENERIC_OBJECT_NAME]
    """Optional name, might be used for looking up neighbors from inventory"""
    asn: Optional[ASN]
    """Autonomous System Number"""
    description: Optional[str]
    """Neighbor description"""
    version: Optional[conint(le=4, ge=4)]
    key: Optional[KeyBase]
    src_interface: Optional[INTERFACE_NAME]
    """Update source"""
    next_hop_self: Optional[bool]
    """Set NextHop to model"""
    rr_client: Optional[bool]
    """Route Reflector Client"""
    # TODO: Be more specific
    send_community: Optional[Literal['both', 'extended', 'standard']]
    """Send Community"""
    ha_mode: Optional[Literal["sso"]]
    fall_over: Optional[BgpFallOver]
    timers: Optional[BgpTimers]

class BgpPeerGroup(BgpNeighborBase):
    """
    BGP Peer Group
    """

    is_peergroup: bool = True

class BgpNeighbor(BgpNeighborBase):
    """
    BGP Neighbor
    """
    # TODO: Unfinished

    address: Optional[Union[ipaddress.IPv4Address, ipaddress.IPv6Address]]
    peer_group: Optional[GENERIC_OBJECT_NAME]
    """Name of the peer-group"""
    dest_interface: Optional[INTERFACE_NAME]
    """Might be used when referencing neighbor by name rather than address"""

    @root_validator
    def check_if_address_needed(cls, values: dict) -> dict:
        if not all([values.get(x) for x in ["name"]]):
            if not values.get("address"):
                msg = "Neighbor needs `address` specified, unless there is at least 'name'."
                raise AssertionError(msg)

        return values


class BgpNetwork(VendorIndependentBaseModel):

    network: ipaddress.IPv4Network


class BgpRedistributeEntry(VendorIndependentBaseModel):
    """
    BGP Redistribute Statement
    """
    type: str
    """What to redistribure"""
    route_map: Optional[GENERIC_OBJECT_NAME]
    """Name of the route-map"""
    metric: Optional[str]


class BgpImportPath(VendorIndependentBaseModel):

    limit: Optional[int]
    selection: Optional[str]


class BgpAddressFamily(VendorIndependentBaseModel):
    # TODO: Unfinished
    afi: AFI
    """Address family type"""
    safi: Optional[SAFI]
    """Address family sub-type"""
    vrf: Optional[VRF_NAME]
    """Name of the VRF"""
    neighbors: Optional[List[BgpNeighbor]]
    """List of :py:class:`BgpNeighbor` in this Address Family"""
    peer_groups: Optional[List[BgpPeerGroup]]
    """List of :py:class:`BgpPeerGroup` in this Address Family"""
    networks: Optional[List[BgpNetwork]]
    redistribute: Optional[List[BgpRedistributeEntry]]
    import_path: Optional[BgpImportPath]
    additional_paths: Optional[Literal["install"]]

    _validate_peergroups_unique_name = validator('peer_groups', allow_reuse=True)(validate_unique_name_field)


class RoutingBgpProcess(RoutingProtocolBase):
    # TODO: Unfinished
    asn: ASN
    """Autonomous System Number"""
    neighbors: Optional[List[BgpNeighbor]]
    """List of :py:class:`BgpNeighbor` objects"""
    peer_groups: Optional[List[BgpPeerGroup]]
    networks: Optional[List[BgpNetwork]]
    address_families: Optional[List[BgpAddressFamily]]
    # TODO: Be more specific
    router_id: Optional[str]
    # TODO: Be more specific
    cluster_id: Optional[str]
    use_default_af: Optional[bool]
    log_neighbor_changes: Optional[bool]
    """
    if ``False`` than no `bgp default ipv4-unicast`
    """
    use_name_for_description: Optional[bool]

    _validate_peergroups_unique_name = validator('peer_groups', allow_reuse=True)(validate_unique_name_field)

    @classmethod
    def _assert_peer_group_exists(cls, neighbor: BgpNeighbor, peer_groups: List[BgpPeerGroup]) -> None:
        if not neighbor.peer_group:
            pass
        else:
            if peer_groups is None:
                msg = f"'peer_groups' is undefined."
                raise AssertionError(msg)
            candidate_peer_groups = [x for x in peer_groups if x.name == neighbor.peer_group]
            if len(candidate_peer_groups) == 1:
                pass
            else:
                msg = f"Can not find 'peer_group' {neighbor.peer_group}."
                raise AssertionError(msg)


    # Validate Global Neighbors
    @root_validator
    def validate_global_neighbors(cls, values):
        neighbors = values.get("neighbors")
        peer_groups = values.get("peer_groups")
        if neighbors:
            for neighbor in neighbors:
                if not neighbor.address:
                    if not all([neighbor.name, neighbor.dest_interface]):
                        msg = f"Global BGP Neighbors must have either 'address', or both ['name', 'dest_interface']"
                        raise AssertionError(msg)
                if neighbor.peer_group:
                    cls._assert_peer_group_exists(neighbor=neighbor, peer_groups=peer_groups)


                if not neighbor.asn:
                    if not neighbor.peer_group:
                        msg = f"Global BGP Neighbor must have either 'asn' or 'peer_group' (with 'asn' set)."
                        raise AssertionError(msg)
                    else:
                        cls._assert_peer_group_exists(neighbor=neighbor, peer_groups=peer_groups)
                        peer_group = [x for x in peer_groups if x.name == neighbor.peer_group][0]
                        if not peer_group.asn:
                            msg = "Neither neighbor nor its 'peer_group' have 'asn' defined."
                            raise AssertionError(msg)


        return values


