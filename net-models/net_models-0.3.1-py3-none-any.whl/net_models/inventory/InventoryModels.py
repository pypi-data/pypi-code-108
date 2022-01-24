# Standard Libraries
import ipaddress
# Third party packages
import logging

from pydantic import Extra, root_validator, validator, conint
from pydantic.typing import Optional, List, Literal, Dict, Tuple
# Local package
from net_models.exceptions import *
from net_models.fields import InterfaceName, GENERIC_OBJECT_NAME, LAG_MODE, VRF_NAME
from net_models.validators import sort_interface_dict, required_together, ipv4s_in_same_subnet, ipv4_is_assignable, validate_unique, remove_duplicates_and_sort
from net_models.models import (
    BaseNetModel,
    InterfaceModel,
    VRFModel,
    VLANModel
)
from net_models.models.routing import *
# Local module
from .Config import HostConfig, GroupConfig



class InventoryModel(BaseNetModel):

    _logger: logging.Logger = get_logger(name="InventoryModel")


class Host(InventoryModel):

    class Config:
        extra = Extra.allow
        anystr_strip_whitespace = True
        validate_assignment = True

    name: GENERIC_OBJECT_NAME
    config: Optional[HostConfig]

    def _get_or_create_config(self) -> HostConfig:
        if self.config is None:
            self.config = HostConfig()
        return self.config

    def get_or_create_interface(self, interface_name: str = None, interface: Union[InterfaceModel, dict] = None, create_if_missing: bool = False):
        config = self._get_or_create_config()
        return config._get_or_create_interface(interface_name=interface_name, interface=interface)






class Group(InventoryModel):

    class Config:
        extra = Extra.allow
        anystr_strip_whitespace = True
        validate_assignment = True

    name: Optional[GENERIC_OBJECT_NAME]
    config: Optional[GroupConfig]
    children: Optional[Dict[GENERIC_OBJECT_NAME, 'Group']]

    hosts: Optional[Dict[GENERIC_OBJECT_NAME, Union[dict, None]]]

    def _get_or_create_config(self):
        if self.config is None:
            self.config = GroupConfig()
        return self.config

    def add_child(self, group_name: GENERIC_OBJECT_NAME, group: 'Group' = None):
        result = None
        if self.children is None:
            self.children = {}
        if group_name in self.children.keys():
            result = False
        else:
            self.children[group_name] = group if group is not None else Group()
            result = True
        return result

    def add_host(self, host_name: GENERIC_OBJECT_NAME):
        result = None
        if self.hosts is None:
            self.hosts = {}
        if host_name in self.hosts.keys():
            result = False
        else:
            self.hosts[host_name] = None
            result = True
        return result

    def get_flat_children(self) -> Dict[GENERIC_OBJECT_NAME, 'Group']:
        group_dict = {}
        if self.children is not None:
            for name, group in self.children.items():
                group_dict.update(group.get_flat_children())
                group_clone = group.clone()
                group_clone.children = None
                if name not in group_dict.keys():
                    group_dict[name] = group_clone
        return group_dict

    def structure(self):
        structure = {}
        if self.hosts is not None:
            structure['hosts'] = {k: None for k in self.hosts.keys()}
        if self.children is not None:
            structure['children'] = {}
            for name, group in self.children.items():
                structure['children'].update({name: group.structure()})
        return structure

Group.update_forward_refs()


class Link(InventoryModel):

    a_host: GENERIC_OBJECT_NAME
    z_host: GENERIC_OBJECT_NAME
    a_interface: InterfaceName
    z_interface: InterfaceName


class DescriptionLink(Link):

    a_description: Optional[str]
    z_description: Optional[str]


class PhysicalLink(Link):


    a_description: Optional[str]
    z_description: Optional[str]
    a_lag_group: Optional[conint(ge=1)]
    z_lag_group: Optional[conint(ge=1)]
    a_lag_mode: Optional[LAG_MODE]
    z_lag_mode: Optional[LAG_MODE]


class L3Link(Link):

    a_description: Optional[str]
    z_description: Optional[str]
    a_vrf: Optional[VRF_NAME]
    z_vrf: Optional[VRF_NAME]
    a_ipv4_address: Optional[ipaddress.IPv4Interface]
    z_ipv4_address: Optional[ipaddress.IPv4Interface]
    ipv4_network: Optional[ipaddress.IPv4Network]

    @root_validator(allow_reuse=True)
    def validate_both_ipv4_present(cls, values):
        required_together(values=values, required=['a_ipv4_address', 'z_ipv4_address'])

        return values

    @root_validator(allow_reuse=True)
    def validate_ipv4_addresses(cls, values):

        a_addr: ipaddress.IPv4Interface = values.get('a_ipv4_address')
        z_addr: ipaddress.IPv4Interface = values.get('z_ipv4_address')
        addr_list = [a_addr, z_addr]
        if all(addr_list):
            ipv4s_in_same_subnet(ips=addr_list)
            for addr in addr_list:
                ipv4_is_assignable(address=addr)
            validate_unique(values=addr_list)

        return values


class Inventory(InventoryModel):

    hosts: Dict[GENERIC_OBJECT_NAME, Host]
    groups: Dict[GENERIC_OBJECT_NAME, Group]

    def structure(self):
        structure = {}
        if self.groups is not None:
            for group_name, group in self.groups.items():
                structure.update({group_name: group.structure()})
        return structure

    def get_flat_groups(self):
        group_dict = {}
        for group_name, group in self.groups.items():
            group_dict.update(group.get_flat_children())
            group_clone = group.clone()
            group_clone.children = None
            if group_name not in group_dict.keys():
                group_dict[group_name] = group_clone
        return group_dict

    @classmethod
    def recursive_find_group(cls, group_name: str, group_dict: dict) -> Union[Group, None]:
        group_candidate = None
        if group_name in group_dict.keys():
            group_candidate = group_dict.get(group_name)
            return group_candidate
        if group_candidate is None:
            for name, group in group_dict.items():
                if group.children is not None:
                    group_candidate = cls.recursive_find_group(group_name=group_name, group_dict=group.children)
                    if group_candidate is not None:
                        return group_candidate
        return group_candidate

    def get_group(self, group_name: str, parent_name: str = None, create_if_missing: bool = True) -> Union[Group, None]:
        group = None
        parent_group = None
        if parent_name is not None:
            # Try finding the parent_name
            parent_group = self.recursive_find_group(group_name=parent_name, group_dict=self.groups)
            if parent_group is None:
                # Check if the group exists regardless of parent_name
                group_candidate = self.recursive_find_group(group_name=group_name, group_dict=self.groups)
                if group_candidate is not None:
                    msg = f"Parent {parent_name} does not exist, however the group {group_name} was found."
                    raise AssertionError(msg)
                else:
                    pass
            else:
                # Try getting the group as a direct child of parent_name
                if parent_group.children is not None:
                    group = parent_group.children.get(group_name)
        else:
            # Try finding the group itself
            group = self.recursive_find_group(group_name=group_name, group_dict=self.groups)

        # If group is still None at this point, it does not exist
        if group is None:
            if create_if_missing:
                group = Group(name=group_name)
                if parent_name is not None:
                    if parent_group is not None:
                        if parent_group.children is None:
                            parent_group.children = {}
                        parent_group.children[group_name] = group
                    else:
                        # At this point, the AssertionError above should have been raised
                        raise Exception("You should not get to this situation.")
                else:
                    self.groups[group_name] = group
            else:
                pass
        return group

    def get_host(self, host_name: str, create_if_missing: bool = True) -> Union[Host, None]:
        host = self.hosts.get(host_name)
        if host is None:
            if create_if_missing:
                host = Host(name=host_name)
                self.hosts[host.name] = host
            else:
                pass
        return host

    def assign_host_to_group(self, host_name, group_name):
        group = self.get_group(group_name=group_name, create_if_missing=False)
        host = self.get_host(host_name=host_name, create_if_missing=False)
        if group is None:
            msg = f"Group '{group_name}' not found in inventory"
            self._logger.error(msg=msg)
            raise GroupNotFound(msg)
        if host is None:
            msg = f"Host '{host_name}' not found in inventory"
            self._logger.error(msg=msg)
            raise HostNotFound(msg)
        if group and host:
            if group.hosts is None:
                group.hosts = {}
            if host.name in group.hosts.keys():
                self._logger.info(msg=f"Host {host.name} is aleready in {group.name}")
                return True
            else:
                group.hosts.update({host.name: None})
                self._logger.info(msg=f"Added host {host.name} to group {group.name}")
                return True
        return False