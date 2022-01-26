from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field, fields, is_dataclass
from enum import Enum
from ipaddress import IPv4Network
from typing import TYPE_CHECKING

from cloudshell.cp.vcenter.exceptions import BaseVCenterException

if TYPE_CHECKING:
    from cloudshell.cp.vcenter.handlers.vm_handler import VmHandler
    from cloudshell.cp.vcenter.models.deploy_app import BaseVCenterDeployApp


class CustomSpecNotSupportedForOs(BaseVCenterException):
    def __init__(self, os_name: str):
        self.os_name = os_name
        msg = f"Customization specification is not supported for the OS {os_name}"
        super().__init__(msg)


class LicenseTypes(Enum):
    per_server = "perServer"
    per_seat = "perSeat"


class SpecType(Enum):
    WINDOWS = "Windows"
    LINUX = "Linux"

    @classmethod
    def from_os_name(cls, os_name: str | None) -> SpecType:
        if os_name is None:
            return cls.LINUX

        if "other" in os_name.lower():
            raise CustomSpecNotSupportedForOs(os_name)
        elif "windows" in os_name.lower():
            return cls.WINDOWS
        return cls.LINUX


class Empty:
    pass


# todo: make it as an abstract class
class ObjectsList(list):
    OBJECT_CLASS: type


@dataclass
class CustomizationSpecParams:
    def _get_all_nested_fields(self, obj):
        if is_dataclass(obj):
            for f in (getattr(obj, f.name) for f in fields(obj)):
                yield from self._get_all_nested_fields(f)
        else:
            yield obj

    def is_empty(self) -> bool:
        return not any(filter(is_not_empty, self._get_all_nested_fields(self)))

    def __bool__(self) -> bool:
        return not self.is_empty()

    @classmethod
    @abstractmethod
    def from_deploy_app_model(
        cls, deploy_app: BaseVCenterDeployApp
    ) -> CustomizationSpecParams:
        raise NotImplementedError


@dataclass
class Network:
    use_dhcp: bool = Empty
    ipv4_address: str = Empty
    subnet_mask: str = Empty
    default_gateway: str = Empty
    alternate_gateway: str = Empty

    @classmethod
    def from_str(cls, ip: str) -> Network:
        """Create instance from str.

        Example, 192.168.1.0/24  - GW would be 192.168.1.1
                 192.168.1.0/24:192.168.1.2  - GW is specified 192.168.1.2
        """
        try:
            ip, gateway = ip.split(":")
        except ValueError:
            gateway = None
        ip = IPv4Network(ip)

        if not gateway:
            # presume Gateway is the .1 of the same subnet as the IP
            ip_octets = str(ip.network_address).split(".")
            ip_octets[-1] = "1"
            gateway = ".".join(ip_octets)

        return cls(
            ipv4_address=str(ip.network_address),
            subnet_mask=str(ip.netmask),
            default_gateway=gateway,
        )


class NetworksList(ObjectsList):
    OBJECT_CLASS = Network


@dataclass
class DNSSettings:
    primary_dns_server: str = Empty
    secondary_dns_server: str = Empty
    tertiary_dns_server: str = Empty
    dns_search_paths: list[str] = Empty


@dataclass
class LinuxCustomizationSpecParams(CustomizationSpecParams):
    networks: NetworksList = field(default_factory=NetworksList)
    computer_name: str = Empty
    domain_name: str = Empty
    dns_settings: DNSSettings = field(default_factory=DNSSettings)

    @classmethod
    def from_deploy_app_model(
        cls, deploy_app: BaseVCenterDeployApp
    ) -> LinuxCustomizationSpecParams:
        params = cls()

        if "." in deploy_app.hostname:
            params.computer_name, params.domain_name = deploy_app.hostname.split(".", 1)
        else:
            params.computer_name = deploy_app.hostname

        if deploy_app.private_ip:
            params.networks = [Network.from_str(deploy_app.private_ip)]

        return params


@dataclass
class RegistrationInfo:
    owner_name: str = Empty
    owner_organization: str = Empty


@dataclass
class License:
    product_key: str = field(default=Empty, repr=False)
    include_server_license_info: bool = Empty
    server_license_mode: LicenseTypes = Empty
    max_connections: int = Empty


@dataclass
class WindowsServerDomain:
    domain: str = Empty
    username: str = Empty
    password: str = field(default=Empty, repr=False)


@dataclass
class WindowsCustomizationSpecParams(CustomizationSpecParams):
    networks: NetworksList = field(default_factory=NetworksList)
    registration_info: RegistrationInfo = field(default_factory=RegistrationInfo)
    computer_name: str = Empty
    auto_logon: bool = Empty
    auto_logon_count: int = Empty
    license: License = field(default_factory=License)  # noqa: A003
    password: str = field(default=Empty, repr=False)
    commands_to_run_once: list[str] = Empty
    workgroup: str = Empty
    windows_server_domain: WindowsServerDomain = field(
        default_factory=WindowsServerDomain
    )

    @classmethod
    def from_deploy_app_model(
        cls, deploy_app: BaseVCenterDeployApp
    ) -> WindowsCustomizationSpecParams:
        params = cls()

        if deploy_app.hostname:
            params.computer_name = deploy_app.hostname

        if deploy_app.password:
            params.password = deploy_app.password

        if deploy_app.private_ip:
            params.networks = [Network.from_str(deploy_app.private_ip)]

        return params


def is_not_empty(val) -> bool:
    return val is not Empty


def get_custom_spec_params_class(
    vm: VmHandler,
) -> type[WindowsCustomizationSpecParams | LinuxCustomizationSpecParams]:
    spec_type = SpecType.from_os_name(vm.guest_id)
    if spec_type.WINDOWS:
        return WindowsCustomizationSpecParams
    else:
        return LinuxCustomizationSpecParams


def get_custom_spec_params(
    deploy_app: BaseVCenterDeployApp,
    vm: VmHandler,
) -> WindowsCustomizationSpecParams | LinuxCustomizationSpecParams | None:
    custom_spec = None
    if deploy_app.hostname or deploy_app.private_ip:
        class_ = get_custom_spec_params_class(vm)
        custom_spec = class_.from_deploy_app_model(deploy_app)
    return custom_spec
