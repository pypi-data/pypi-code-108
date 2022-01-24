# Standard Libraries
# Third party packages
from pydantic.typing import Union
# Local package
from net_models.fields import InterfaceName
from net_models.models import InterfaceModel
from net_models.inventory import (Inventory, Group, Host, HostConfig, GroupConfig)
from net_models.utils import get_logger
# Local module


class BaseLoader(object):

    def __init__(self, inventory: Inventory = None, verbosity: int = 4):
        self.logger = get_logger(name="BaseLoader", verbosity=verbosity)
        self.inventory = inventory
        if self.inventory is None:
            self.logger.debug(msg="No Inventory passed during initialization, creating empty inventory.")
            self.init_inventory()

    def init_inventory(self):
        if self.inventory is None:
            self.inventory = Inventory(hosts={}, groups={})

    def find_host(self, host_name) -> Union[Host, None]:

        host = None
        try:
            host = self.inventory.hosts.get(host_name)
        except KeyError:
            self.logger.debug(msg=f"Host {host_name} not found in inventory.")
        except Exception as e:
            msg = f"Unhandled Exception occured while searching host {host_name}. Exception: {repr(e)}"
            self.logger.error(msg=msg)
            raise

        return host

    def recursive_find_group(self, group_name: str, group_dict: dict) -> Union[Group, None]:
        group_candidate = None
        if group_name in group_dict.keys():
            self.logger.debug(f'Found group {group_name}')
            group_candidate = group_dict.get(group_name)
            return group_candidate
        if group_candidate is None:
            for name, group in group_dict.items():
                if group.children is not None:
                    self.logger.debug(f"Traversing children of group {name}")
                    group_candidate = self.recursive_find_group(group_name=group_name, group_dict=group.children)
                if group_candidate is not None:
                    return group_candidate
                    self.logger.debug(f'Found group {group_name}')
        return group_candidate


    def get_all_group_names(self):
        group_dict = {}
        for group_name, group in self.inventory.groups.items():
            group_dict.update({k:v.serial_dict(include=set(), exclude_none=True) for k, v in group.get_flat_children().items()})
            # Include self
            group_dict.update({group_name: group.serial_dict(include={'config'}, exclude_none=True)})
        return list(group_dict.keys())

    def get_group(self, group_name: str, parent_name: str = None, create_if_missing: bool = True) -> Union[Group, None]:
        group = None
        parent_group = None
        if parent_name is not None:
            # Try finding the parent_name
            parent_group = self.recursive_find_group(group_name=parent_name, group_dict=self.inventory.groups)
            if parent_group is None:
                # Check if the group exists regardless of parent_name
                group_candidate = self.recursive_find_group(group_name=group_name, group_dict=self.inventory.groups)
                if group_candidate is not None:
                    msg = f"Parent {parent_name} does not exist, however the group {group_name} was found."
                    self.logger.critical(msg=msg)
                    raise AssertionError(msg)
                else:
                    self.logger.error(f"Cannot get specified group {group_name} as its parent {parent_name} does not exist.")
            else:
                # Try getting the group as a direct child of parent_name
                if parent_group.children is not None:
                    group = parent_group.children.get(group_name)
        else:
            # Try finding the group itself
            group = self.recursive_find_group(group_name=group_name, group_dict=self.inventory.groups)


        # If group is still None at this point, it does not exist
        if group is None:
            if create_if_missing:
                group = Group(name=group_name)
                if parent_name is not None:
                    if parent_group is not None:
                        self.logger.debug(f"Creating group '{group_name}' under parent {parent_name}")
                        if parent_group.children is None:
                            parent_group.children = {}
                        parent_group.children[group_name] = group
                    else:
                        # At this point, the AssertionError above should have been raised
                        raise Exception("You should not get to this situation.")
                else:
                    self.logger.debug(f"Creating top-level group '{group_name}'")
                    self.inventory.groups[group_name] = group
            else:
                self.logger.debug(f"Group '{group_name}' not present in inventory")
        return group

    def get_host(self, host_name: str, create_if_missing: bool = True) -> Union[Host, None]:
        host = self.inventory.hosts.get(host_name, None)
        if host is None:
            if create_if_missing:
                self.logger.debug(f"Creating host '{host_name}'")
                host = Host(name=host_name)
                self.inventory.hosts[host.name] = host
            else:
                self.logger.debug(f"Host '{host_name}' not present in inventory")
        return host


    def get_interface(self, host_name: str, interface_name: InterfaceName, create_if_missing: bool = True) -> Union[InterfaceModel, None]:
        if not isinstance(interface_name, InterfaceName):
            interface_name = InterfaceName.validate(interface_name)
        # Host must already exist
        host = self.get_host(host_name=host_name, create_if_missing=False)
        interface = None
        if host is None:
            self.logger.error(f"Specified host {host_name} not present in inventory, cannot retreive interface {interface_name}")
            return None
        if host.config is None:
            if create_if_missing:
                self.logger.debug(f"Creating GlobalConfig for host {host.name}")
                host.config = HostConfig(interfaces={})
            else:
                self.logger.error(f"Host {host_name} does not have config, cannot retreive interface.")
                return None
        interface = host.config.interfaces.get(interface_name, None)
        if interface is None:
            if create_if_missing:
                self.logger.debug(f"Creating interface {interface_name} on host {host.name}")
                interface = InterfaceModel(name=interface_name)
                host.config.interfaces[interface.name] = interface
            else:
                self.logger.debug(f"Interface {interface_name} not present on host {host.name}")
        return interface





    def update_host(self, host_name: str, params: dict = None):
        host = self.find_host(host_name=host_name)
        if params is None:
            params = {}
        if host is None:
            self.logger.debug(msg=f"Creating host {host_name}")
            host = Host(name=host_name, **params)
            self.inventory.hosts.update({host_name: host})
        elif isinstance(host, Host):
            for k, v in params.items():
                if v is not None:
                    setattr(host, k, v)


    def update_host_interface(self, host_name: str, interface_name: InterfaceName, params: dict = None):
        host = None
        if params is None:
            params = {}
        if not isinstance(interface_name, InterfaceName):
            interface_name = InterfaceName.validate(interface_name)
        try:
            host = self.inventory.hosts.get(host_name)
            if host.config is None:
                self.logger.debug(f"Creating HostConfig for host '{host_name}'")
                host.config = HostConfig(interfaces={})
            if host.config.interfaces is None:
                self.logger.debug(f"Constructing Interfaces for host '{host_name}'")
                host.config.interfaces = {}
            if interface_name not in host.config.interfaces.keys():
                self.logger.debug(f"Creating interface {interface_name} on host {host_name}")
                interface = InterfaceModel(name=interface_name, **params)
                host.config.interfaces[interface_name] = interface
            else:
                self.logger.debug(f"Found existing interface {interface_name} on host {host_name}")
                for k, v in params.items():
                    if v is not None:
                        setattr(host.config.interfaces[interface_name], k, v)
        except Exception as e:
            msg = f"Unhandled Exception occured while getting host {host_name}. Exception: {repr(e)}"
            self.logger.error(msg=msg)
            raise




    def finish(self):
        self.inventory = self.inventory.clone()
        # model.inventory.check()
        # print(self.inventory.yaml(exclude_none=True, indent=2))


