# Standard Libraries
# Third party packages
from pydantic import validator, root_validator
from pydantic.typing import Literal, List, Union, Optional
# Local package
from net_models.validators import *
from net_models.fields import *
from net_models.models import VendorIndependentBaseModel
# Local module



class InterfaceSpanningTreeConfig(VendorIndependentBaseModel):
    
    _modelname = "spanning_tree_port_config"
    _identifiers = []

    link_type: Optional[Literal["point-to-point", "shared"]]
    portfast: Optional[Literal["edge", "network", "disable", "trunk"]]
    bpduguard: Optional[bool]
    root_guard: Optional[bool]
    loop_guard: Optional[bool]


class InterfaceSwitchportModel(VendorIndependentBaseModel):
    """
    Model for switched interfaces
    """

    _modelname = "switchport_model"
    _identifiers = []
    _children = {InterfaceSpanningTreeConfig: "stp"}

    mode: Optional[Literal["access", "trunk", "dynamic auto", "dynamic desirable", "dot1q-tunnel", "private-vlan host", "private-vlan promiscuous"]]
    """Operational mode"""

    untagged_vlan: Optional[VLAN_ID]
    """ID of untagged VLAN. Used for Access or Native VLAN"""
    voice_vlan: Optional[VLAN_ID]
    """ID of voice VLAN """
    allowed_vlans: Optional[Union[List[VLAN_ID], Literal["all", "none"]]]
    """
    List of allowed VLANs on this interface.
    Preferably `List[int]`, however validators will take care of things like `"1-10,20"` or `[1, 2, 3, "5-10"]`
    """
    encapsulation: Optional[Literal["dot1q", "isl", "negotiate"]]

    negotiation: Optional[bool]
    """
    Wether or not negotiate trunking, for example via DTP. 
    Setting this value to `False` will result in :code:`switchport nonegotiate`
    """
    stp: Optional[InterfaceSpanningTreeConfig]

    @root_validator(allow_reuse=True)
    def validate_allowed_vlans_present(cls, values):
        if values.get("allowed_vlans", None) is not None:
            assert values.get('mode') in ['trunk', 'dynamic auto', 'dynamic desirable'], "Field 'allowed_vlans' is only allowed when 'mode' in ['trunk', 'dynamic auto', 'dynamic desirable']."
        return values

    @validator('allowed_vlans', pre=True, allow_reuse=True)
    def validate_vlan_range(cls, v):
        if v is not None:
            v = expand_vlan_range(vlan_range=v)
        return v
    # _vlan_range_validator = validator('allowed_vlans', allow_reuse=True)(expand_vlan_range)

