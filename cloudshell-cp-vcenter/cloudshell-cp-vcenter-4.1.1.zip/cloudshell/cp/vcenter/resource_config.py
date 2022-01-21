from __future__ import annotations

from enum import Enum
from typing import Union

from cloudshell.api.cloudshell_api import CloudShellAPISession, ResourceInfo
from cloudshell.shell.core.driver_context import (
    AutoLoadCommandContext,
    ResourceCommandContext,
    ResourceRemoteCommandContext,
    UnreservedResourceCommandContext,
)
from cloudshell.shell.standards.core.resource_config_entities import (
    GenericResourceConfig,
    PasswordAttrRO,
    ResourceAttrRO,
    ResourceBoolAttrRO,
    ResourceListAttrRO,
)

from cloudshell.cp.vcenter.constants import SHELL_NAME


class ResourceAttrROShellName(ResourceAttrRO):
    def __init__(self, name, namespace=ResourceAttrRO.NAMESPACE.SHELL_NAME):
        super().__init__(name, namespace)


class ShutdownMethodAttrRO(ResourceAttrRO):
    def __init__(self):
        super().__init__(
            VCenterAttributeNames.shutdown_method,
            ResourceAttrROShellName.NAMESPACE.SHELL_NAME,
        )

    def __get__(self, instance, owner) -> ShutdownMethod:
        val = super().__get__(instance, owner)
        if val is self:
            return val
        return ShutdownMethod(val)


CONTEXT_TYPES = Union[
    ResourceCommandContext,
    AutoLoadCommandContext,
    ResourceRemoteCommandContext,
    UnreservedResourceCommandContext,
]


class ShutdownMethod(Enum):
    SOFT = "soft"
    HARD = "hard"


class VCenterAttributeNames:
    user = "User"
    password = "Password"
    default_datacenter = "Default Datacenter"
    default_dv_switch = "Default dvSwitch"
    holding_network = "Holding Network"
    vm_cluster = "VM Cluster"
    vm_resource_pool = "VM Resource Pool"
    vm_storage = "VM Storage"
    saved_sandbox_storage = "Saved Sandbox Storage"
    behavior_during_save = "Behavior during save"
    vm_location = "VM Location"
    shutdown_method = "Shutdown Method"
    ovf_tool_path = "OVF Tool Path"
    reserved_networks = "Reserved Networks"
    execution_server_selector = "Execution Server Selector"
    promiscuous_mode = "Promiscuous Mode"


class VCenterResourceConfig(GenericResourceConfig):
    ATTR_NAMES = VCenterAttributeNames

    user = ResourceAttrROShellName(ATTR_NAMES.user)
    password = PasswordAttrRO(ATTR_NAMES.password, PasswordAttrRO.NAMESPACE.SHELL_NAME)
    default_datacenter = ResourceAttrROShellName(ATTR_NAMES.default_datacenter)
    default_dv_switch = ResourceAttrROShellName(ATTR_NAMES.default_dv_switch)
    holding_network = ResourceAttrROShellName(ATTR_NAMES.holding_network)
    vm_cluster = ResourceAttrROShellName(ATTR_NAMES.vm_cluster)
    vm_resource_pool = ResourceAttrROShellName(ATTR_NAMES.vm_resource_pool)
    vm_storage = ResourceAttrROShellName(ATTR_NAMES.vm_storage)
    saved_sandbox_storage = ResourceAttrROShellName(ATTR_NAMES.saved_sandbox_storage)
    behavior_during_save = ResourceAttrROShellName(ATTR_NAMES.behavior_during_save)
    vm_location = ResourceAttrROShellName(ATTR_NAMES.vm_location)
    shutdown_method = ShutdownMethodAttrRO()
    ovf_tool_path = ResourceAttrROShellName(ATTR_NAMES.ovf_tool_path)
    reserved_networks = ResourceListAttrRO(
        ATTR_NAMES.reserved_networks, ResourceListAttrRO.NAMESPACE.SHELL_NAME
    )
    execution_server_selector = ResourceAttrROShellName(
        ATTR_NAMES.execution_server_selector
    )
    promiscuous_mode = ResourceBoolAttrRO(
        ATTR_NAMES.promiscuous_mode, ResourceBoolAttrRO.NAMESPACE.SHELL_NAME
    )

    @classmethod
    def from_context(
        cls,
        context: CONTEXT_TYPES,
        shell_name: str = SHELL_NAME,
        api: CloudShellAPISession | None = None,
        supported_os: list[str] | None = None,
    ) -> VCenterResourceConfig:
        # noinspection PyTypeChecker
        # return type is VCenterResourceConfig not GenericResourceConfig
        return super().from_context(
            context=context, shell_name=shell_name, api=api, supported_os=supported_os
        )

    @classmethod
    def from_cs_resource_details(
        cls,
        details: ResourceInfo,
        shell_name: str = SHELL_NAME,
        api=None,
        supported_os=None,
    ) -> VCenterResourceConfig:
        attrs = {attr.Name: attr.Value for attr in details.ResourceAttributes}
        return cls(
            shell_name=shell_name,
            name=details.Name,
            fullname=details.Name,
            address=details.Address,
            family_name=details.ResourceFamilyName,
            attributes=attrs,
            supported_os=supported_os,
            api=api,
            cs_resource_id=details.UniqeIdentifier,
        )
