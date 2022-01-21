from __future__ import annotations

from logging import Logger
from typing import TYPE_CHECKING

import attr
from pyVmomi import vim
from typing_extensions import Protocol

from cloudshell.shell.flows.connectivity.models.connectivity_model import (
    ConnectionModeEnum,
)

from cloudshell.cp.vcenter.exceptions import BaseVCenterException
from cloudshell.cp.vcenter.handlers.managed_entity_handler import ManagedEntityHandler
from cloudshell.cp.vcenter.handlers.network_handler import (
    AbstractPortGroupHandler,
    DVPortGroupHandler,
    DVPortGroupNotFound,
    HostPortGroupHandler,
    HostPortGroupNotFound,
)
from cloudshell.cp.vcenter.utils.task_waiter import VcenterTaskWaiter

if TYPE_CHECKING:
    from cloudshell.cp.vcenter.handlers.cluster_handler import HostHandler


class DvSwitchNotFound(BaseVCenterException):
    def __init__(self, entity: ManagedEntityHandler, name: str):
        self.entity = entity
        self.name = name
        msg = f"DistributedVirtualSwitch with name {name} not found in the {entity}"
        super().__init__(msg)


class VSwitchNotFound(BaseVCenterException):
    def __init__(self, entity: ManagedEntityHandler, name: str):
        self.entity = entity
        self.name = name
        super().__init__(f"VirtualSwitch with name {name} not found in the {entity}")


def get_vlan_spec(port_mode: ConnectionModeEnum, vlan_range: str):
    if port_mode is port_mode.ACCESS:
        spec = vim.dvs.VmwareDistributedVirtualSwitch.VlanIdSpec
        vlan_id = int(vlan_range)
    else:
        spec = vim.dvs.VmwareDistributedVirtualSwitch.TrunkVlanSpec
        parts = list(map(int, vlan_range.split("-")))
        if len(parts) == 1:
            start = end = next(parts)
        else:
            start, end = parts
        vlan_id = [vim.NumericRange(start=start, end=end)]
    return spec(vlanId=vlan_id, inherited=False)


class AbstractSwitchHandler(Protocol):
    def get_port_group(self, name: str) -> AbstractPortGroupHandler:
        raise NotImplementedError

    def create_port_group(
        self,
        port_name: str,
        vlan_range: str,
        port_mode: ConnectionModeEnum,
        promiscuous_mode: bool,
        logger: Logger,
        num_ports: int = 32,
        task_waiter: VcenterTaskWaiter | None = None,
    ) -> None:
        raise NotImplementedError


class DvSwitchHandler(ManagedEntityHandler, AbstractSwitchHandler):
    def __str__(self) -> str:
        return f"DistributedVirtualSwitch '{self.name}'"

    def create_port_group(
        self,
        dv_port_name: str,
        vlan_range: str,
        port_mode: ConnectionModeEnum,
        promiscuous_mode: bool,
        logger: Logger,
        num_ports: int = 32,
        task_waiter: VcenterTaskWaiter | None = None,
    ) -> None:
        port_conf_policy = (
            vim.dvs.VmwareDistributedVirtualSwitch.VmwarePortConfigPolicy(
                securityPolicy=vim.dvs.VmwareDistributedVirtualSwitch.SecurityPolicy(
                    allowPromiscuous=vim.BoolPolicy(value=promiscuous_mode),
                    forgedTransmits=vim.BoolPolicy(value=True),
                    macChanges=vim.BoolPolicy(value=False),
                    inherited=False,
                ),
                vlan=get_vlan_spec(port_mode, vlan_range),
            )
        )
        dv_pg_spec = vim.dvs.DistributedVirtualPortgroup.ConfigSpec(
            name=dv_port_name,
            numPorts=num_ports,
            type=vim.dvs.DistributedVirtualPortgroup.PortgroupType.earlyBinding,
            defaultPortConfig=port_conf_policy,
        )

        task = self._entity.AddDVPortgroup_Task([dv_pg_spec])
        logger.info(f"DV Port Group '{dv_port_name}' CREATE Task")
        task_waiter = task_waiter or VcenterTaskWaiter(logger)
        task_waiter.wait_for_task(task)

    def get_port_group(self, name: str) -> DVPortGroupHandler:
        for port_group in self._entity.portgroup:
            if port_group.name == name:
                return DVPortGroupHandler(port_group, self._si)
        raise DVPortGroupNotFound(self, name)


@attr.s(auto_attribs=True)
class VSwitchHandler(AbstractSwitchHandler):
    _entity: vim.host.VirtualSwitch
    _host: HostHandler

    def __str__(self) -> str:
        return f"VirtualSwitch '{self.name}'"

    @property
    def key(self) -> str:
        return self._entity.key

    @property
    def name(self) -> str:
        return self._entity.name

    def get_port_group(self, name: str) -> HostPortGroupHandler:
        for pg in self._host.port_groups:
            if pg.name == name and pg.v_switch_key == self.key:
                return pg
        raise HostPortGroupNotFound(self, name)

    def create_port_group(
        self,
        port_name: str,
        vlan_range: str,
        port_mode: ConnectionModeEnum,
        promiscuous_mode: bool,
        logger: Logger,
        num_ports: int = 32,
        task_waiter: VcenterTaskWaiter | None = None,
    ) -> None:
        pg_spec = vim.host.PortGroup.Specification()
        pg_spec.vswitchName = self.name
        pg_spec.name = port_name
        pg_spec.vlanId = int(vlan_range)
        network_policy = vim.host.NetworkPolicy()
        network_policy.security = vim.host.NetworkPolicy.SecurityPolicy()
        network_policy.security.allowPromiscuous = promiscuous_mode
        network_policy.security.macChanges = False
        network_policy.security.forgedTransmits = True
        pg_spec.policy = network_policy

        self._host.add_port_group(pg_spec)
