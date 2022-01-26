from __future__ import annotations

from abc import abstractmethod
from typing import ClassVar, TypeVar, Union

import attr
from pyVmomi import vim
from typing_extensions import Protocol

from cloudshell.cp.vcenter.exceptions import BaseVCenterException
from cloudshell.cp.vcenter.models.custom_spec import (
    Empty,
    LinuxCustomizationSpecParams,
    NetworksList,
    SpecType,
    WindowsCustomizationSpecParams,
    is_not_empty,
)

CUSTOM_SPEC_PARAM_TYPES = Union[
    WindowsCustomizationSpecParams, LinuxCustomizationSpecParams
]


class CustomSpecTypeNotFound(BaseVCenterException):
    def __init__(self, type_: str):
        self.type = type_
        super().__init__(f"There isn't custom spec with type {type_}")


class WrongCustomSpecParams(BaseVCenterException):
    def __init__(
        self,
        custom_spec_params: CUSTOM_SPEC_PARAM_TYPES,
        custom_spec: CustomSpecHandler,
    ):
        self.custom_spec_params = custom_spec_params
        self.custom_spec = custom_spec
        super().__init__(
            f"Wrong type of the Custom Spec Params {type(custom_spec_params)}"
            f"for the Custom Spec {type(custom_spec)}"
        )


T = TypeVar("T")


@attr.s(auto_attribs=True)
class CustomSpecHandler(Protocol):
    SPEC_TYPE: ClassVar[SpecType]
    spec: vim.CustomizationSpecItem

    @classmethod
    @abstractmethod
    def create(cls: type[T], name: str) -> T:
        ...

    def _populate_nics(self, total_if_num: int):
        """Adding missing interfaces with DHCP."""
        for _ in range(total_if_num - len(self.spec.spec.nicSettingMap)):
            adapter = vim.vm.customization.IPSettings(
                ip=vim.vm.customization.DhcpIpGenerator()
            )
            adapter_mapping = vim.vm.customization.AdapterMapping(adapter=adapter)
            self.spec.spec.nicSettingMap.append(adapter_mapping)

    def _set_network_params(self, networks: NetworksList, num_vm_nics: int):
        if networks is Empty:
            return

        self._populate_nics(max(num_vm_nics, len(networks)))
        nic_setting_map = self.spec.spec.nicSettingMap

        for network, nic_setting in zip(networks, nic_setting_map):
            if network.use_dhcp is True:
                nic_setting.adapter = vim.vm.customization.IPSettings(
                    ip=vim.vm.customization.DhcpIpGenerator()
                )
            else:
                network_adapter = nic_setting.adapter

                if network.ipv4_address is not Empty:
                    network_adapter.ip = vim.vm.customization.FixedIp(
                        ipAddress=network.ipv4_address
                    )
                if network.subnet_mask is not Empty:
                    network_adapter.subnetMask = network.subnet_mask

                gateways = [network.default_gateway, network.alternate_gateway]
                gateways = list(filter(is_not_empty, gateways))
                if gateways:
                    network_adapter.gateway = gateways

    def set_custom_spec_params(
        self, custom_spec_params: CUSTOM_SPEC_PARAM_TYPES, num_vm_nics: int
    ):
        self._set_network_params(custom_spec_params.networks, num_vm_nics)


class CustomWindowsSpecHandler(CustomSpecHandler):
    SPEC_TYPE = SpecType.WINDOWS
    VM_FULL_NAME = "Quali"
    VM_ORG_NAME = "Quali"
    VM_WORKGROUP_NAME = "WORKGROUP"

    @classmethod
    def create(cls, name: str) -> CustomWindowsSpecHandler:
        spec = vim.CustomizationSpecItem(
            info=vim.CustomizationSpecInfo(
                type=cls.SPEC_TYPE.value,
                name=name,
            ),
            spec=vim.vm.customization.Specification(
                identity=vim.vm.customization.Sysprep(
                    guiUnattended=vim.vm.customization.GuiUnattended(),
                    userData=vim.vm.customization.UserData(
                        computerName=vim.vm.customization.VirtualMachineNameGenerator(),
                        fullName=cls.VM_FULL_NAME,
                        orgName=cls.VM_ORG_NAME,
                    ),
                    identification=vim.vm.customization.Identification(
                        joinWorkgroup=cls.VM_WORKGROUP_NAME,
                    ),
                ),
                globalIPSettings=vim.vm.customization.GlobalIPSettings(),
                nicSettingMap=[],
                options=vim.vm.customization.WinOptions(
                    changeSID=True,
                ),
            ),
        )
        return cls(spec)

    def set_custom_spec_params(
        self, custom_spec_params: CUSTOM_SPEC_PARAM_TYPES, num_vm_nics: int
    ):
        if not isinstance(custom_spec_params, WindowsCustomizationSpecParams):
            raise WrongCustomSpecParams(custom_spec_params, self)

        super().set_custom_spec_params(custom_spec_params, num_vm_nics)

        if custom_spec_params.computer_name is not Empty:
            self.spec.spec.identity.userData.computerName = (
                vim.vm.customization.FixedName(name=custom_spec_params.computer_name)
            )

        if custom_spec_params.password is not Empty:
            self.spec.spec.identity.guiUnattended.password = (
                vim.vm.customization.Password(
                    value=custom_spec_params.password, plainText=True
                )
            )

        if custom_spec_params.auto_logon is not Empty:
            self.spec.spec.identity.guiUnattended.autoLogon = (
                custom_spec_params.auto_logon
            )

            if custom_spec_params.auto_logon_count is not Empty:
                self.spec.spec.identity.guiUnattended.autoLogonCount = (
                    custom_spec_params.auto_logon_count
                )

        if custom_spec_params.registration_info.owner_name is not Empty:
            self.spec.spec.identity.userData.fullName = (
                custom_spec_params.registration_info.owner_name
            )

        if custom_spec_params.registration_info.owner_organization is not Empty:
            self.spec.spec.identity.userData.orgName = (
                custom_spec_params.registration_info.owner_organization
            )

        if custom_spec_params.license.product_key is not Empty:
            self.spec.spec.identity.userData.productId = (
                custom_spec_params.license.product_key
            )

        if custom_spec_params.license.include_server_license_info is not Empty:
            self.spec.spec.identity.licenseFilePrintData = (
                vim.vm.customization.LicenseFilePrintData()
            )

            if custom_spec_params.license.server_license_mode is not Empty:
                self.spec.spec.identity.licenseFilePrintData.autoMode = (
                    custom_spec_params.license.server_license_mode
                )

            if custom_spec_params.license.max_connections is not Empty:
                self.spec.spec.identity.licenseFilePrintData.autoUsers = (
                    custom_spec_params.license.max_connections
                )

        if custom_spec_params.commands_to_run_once is not Empty:
            self.spec.spec.identity.guiRunOnce = vim.vm.customization.GuiRunOnce(
                commandList=custom_spec_params.commands_to_run_once
            )

        if custom_spec_params.workgroup is not Empty:
            self.spec.spec.identity.identification.joinWorkgroup = (
                custom_spec_params.workgroup
            )
            self.spec.spec.identity.identification.joinDomain = None

        if custom_spec_params.windows_server_domain.domain is not Empty:
            self.spec.spec.identity.identification.joinDomain = (
                custom_spec_params.windows_server_domain.domain
            )
            self.spec.spec.identity.identification.joinWorkgroup = None

        if custom_spec_params.windows_server_domain.password is not Empty:
            self.spec.spec.identity.identification.domainAdminPassword = (
                vim.vm.customization.Password(
                    value=custom_spec_params.windows_server_domain.password,
                    plainText=True,
                )
            )


class CustomLinuxSpecHandler(CustomSpecHandler):
    SPEC_TYPE = SpecType.LINUX
    VM_TIMEZONE = "US/Pacific"

    @classmethod
    def create(cls, name: str) -> CustomLinuxSpecHandler:
        spec = vim.CustomizationSpecItem(
            info=vim.CustomizationSpecInfo(
                type=cls.SPEC_TYPE.value,
                name=name,
            ),
            spec=vim.vm.customization.Specification(
                identity=vim.vm.customization.LinuxPrep(
                    hostName=vim.vm.customization.VirtualMachineNameGenerator(),
                    timeZone=cls.VM_TIMEZONE,
                    hwClockUTC=True,
                ),
                globalIPSettings=vim.vm.customization.GlobalIPSettings(),
                nicSettingMap=[],
                options=vim.vm.customization.LinuxOptions(),
            ),
        )
        return cls(spec)

    def set_custom_spec_params(
        self, custom_spec_params: CUSTOM_SPEC_PARAM_TYPES, num_vm_nics: int
    ):
        if not isinstance(custom_spec_params, LinuxCustomizationSpecParams):
            raise WrongCustomSpecParams(custom_spec_params, self)

        if custom_spec_params.computer_name is not Empty:
            self.spec.spec.identity.hostName = vim.vm.customization.FixedName(
                name=custom_spec_params.computer_name
            )

        if custom_spec_params.domain_name is not Empty:
            self.spec.spec.identity.domain = custom_spec_params.domain_name

        if custom_spec_params.dns_settings.dns_search_paths is not Empty:
            self.spec.spec.globalIPSettings.dnsSuffixList = (
                custom_spec_params.dns_settings.dns_search_paths
            )

        dns_servers = [
            custom_spec_params.dns_settings.primary_dns_server,
            custom_spec_params.dns_settings.secondary_dns_server,
            custom_spec_params.dns_settings.tertiary_dns_server,
        ]
        dns_servers = list(filter(is_not_empty, dns_servers))
        if dns_servers:
            self.spec.spec.globalIPSettings.dnsServerList = dns_servers


def get_custom_spec_from_vim_spec(spec: vim.CustomizationSpecItem) -> CustomSpecHandler:
    type_ = spec.info.type
    for spec_class in (CustomWindowsSpecHandler, CustomLinuxSpecHandler):
        if spec_class.SPEC_TYPE.value == type_:
            # noinspection PyArgumentList
            return spec_class(spec)
    raise CustomSpecTypeNotFound(type_)


def create_custom_spec_from_spec_params(
    spec_params: CUSTOM_SPEC_PARAM_TYPES, name: str
) -> CustomSpecHandler:
    if isinstance(spec_params, WindowsCustomizationSpecParams):
        spec_class = CustomWindowsSpecHandler
    else:
        spec_class = CustomLinuxSpecHandler
    spec = spec_class.create(name)
    return spec
