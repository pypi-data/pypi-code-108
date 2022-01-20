from __future__ import annotations

import ipaddress
import re
import time
from contextlib import nullcontext
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from pyVmomi import vim

from cloudshell.cp.vcenter.exceptions import VMIPNotFoundException

if TYPE_CHECKING:
    from logging import Logger

    from cloudshell.cp.core.cancellation_manager import CancellationContextManager

    from cloudshell.cp.vcenter.resource_config import VCenterResourceConfig


class VMNetworkActions:
    QUALI_NETWORK_PREFIX = "QS_"
    DEFAULT_IP_REGEX = ".*"
    DEFAULT_IP_WAIT_TIME = 5

    def __init__(
        self,
        resource_conf: VCenterResourceConfig,
        logger: Logger,
        cancellation_manager: CancellationContextManager | nullcontext = nullcontext(),
    ):
        self._resource_conf = resource_conf
        self._logger = logger
        self._cancellation_manager = cancellation_manager

    def is_quali_network(self, network_name: str) -> bool:
        return network_name.startswith(self.QUALI_NETWORK_PREFIX)

    def _is_ipv4_address(self, ip):
        self._logger.info(f"Checking if IP address {ip} is IPv4 ")
        is_ipv4 = True
        try:
            ipaddress.IPv4Address(ip)
        except ipaddress.AddressValueError:
            is_ipv4 = False

        self._logger.info(f"IP address is IPv4: {is_ipv4}")
        return is_ipv4

    def get_vm_ip_from_vnic(self, vm, vnic):
        """Get VM IP address from the vNIC."""
        self._logger.info(f"Getting IPv4 address from the vNIC {vnic}")
        for net in vm.guest.net:
            if str(net.deviceConfigId) == str(vnic.key):
                for ip_address in net.ipAddress:
                    if self._is_ipv4_address(ip_address):
                        return ip_address

    def _get_ip_regex_match_function(self, ip_regex=None):
        """Get Regex Match function for the VM IP address."""
        self._logger.info(f"Getting IP RegEx match function for the RegEx {ip_regex}")

        if ip_regex is None:
            ip_regex = self.DEFAULT_IP_REGEX
        try:
            return re.compile(ip_regex).match
        except Exception:
            raise AttributeError(f"Invalid IP regex : {ip_regex}")

    def _get_vm_ip_addresses(self, vm, default_network):
        """Get all VM IP address except the default network address."""
        self._logger.info(f"Getting all VM IP addresses for the vm {vm.name}")
        ips = []

        if vm.guest.ipAddress:
            ips.append(vm.guest.ipAddress)

        for nic in vm.guest.net:
            if not default_network or nic.network != default_network.name:
                for addr in nic.ipAddress:
                    if addr:
                        ips.append(addr)

        self._logger.info(f"Found VM IP addresses: {ips}")
        return ips

    def _find_vm_ip(self, vm, default_network, ip_match_function):
        """Find VM IP address."""
        self._logger.info(f"Finding VM IP address for the vm {vm.name}")
        for ip in self._get_vm_ip_addresses(vm, default_network):
            if self._is_ipv4_address(ip):
                if ip_match_function(ip):
                    return ip

    def get_vm_ip(
        self,
        vm: vim.VirtualMachine,  # todo VmHandler
        default_network: vim.Network | None = None,
        ip_regex: str | None = None,
        timeout: int | None = None,
    ) -> str:
        """Get VM IP address."""
        self._logger.info(f"Getting IP address for the VM {vm.name} from the vCenter")

        timeout = timeout or 0
        timeout_time = datetime.now() + timedelta(seconds=timeout)
        ip_regex_match = self._get_ip_regex_match_function(ip_regex)
        ip = None

        while not ip:
            with self._cancellation_manager:
                self._logger.info(f"Getting IP for VM {vm.name}")
                ip = self._find_vm_ip(
                    vm=vm,
                    default_network=default_network,
                    ip_match_function=ip_regex_match,
                )

            if ip:
                return ip

            with self._cancellation_manager:
                time.sleep(self.DEFAULT_IP_WAIT_TIME)

            if datetime.now() > timeout_time:
                raise VMIPNotFoundException("Unable to get VM IP")
