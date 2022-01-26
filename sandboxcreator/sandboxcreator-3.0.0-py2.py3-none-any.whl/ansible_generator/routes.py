from typing import List, Dict

from sandboxcreator.input_parser.sandbox import Network, Sandbox, \
    Interface, DevicePurpose, Device, DeviceType


class Routes:
    """Static methods for routing table changes"""

    @staticmethod
    def _find_router_interface(network: Network, sandbox: Sandbox) -> Interface:
        """Find the interface of a router inside a network"""
        for device in sandbox.devices:
            if device.device_purpose is DevicePurpose.ROUTER:
                for interface in device.interfaces:
                    if network == interface.network:
                        return interface
        raise AttributeError(f"There is no router in the network {network.name}")

    @staticmethod
    def _find_router_in_network(network: Network, sandbox: Sandbox) -> Device:
        """Find the a router inside a network"""
        for device in sandbox.devices:
            if device.device_purpose is DevicePurpose.ROUTER:
                for interface in device.interfaces:
                    if network == interface.network:
                        return device
        raise AttributeError(f"There is no router in the network {network.name}")

    @staticmethod
    def _create_host_routes(device: Device, sandbox: Sandbox) -> List[Dict]:
        """Create routes for hosts (and controller)"""
        routes: List = []
        if sandbox.router_present:
            configure_auto = {
                "interface_ip": "{{ ansible_default_ipv4.address  | "
                                "default(ansible_all_ipv4_addresses[0]) }}",
                "interface_netmask": "{{ ansible_default_ipv4.netmask"
                                     "  | default('24') }}",
                "interface_default_gateway": ""}
            routes.append(configure_auto)

            router_int: Interface = Routes. \
                _find_router_interface(device.interfaces[0].network, sandbox)
            to_router = {
                "interface_ip": str(device.interfaces[0].ip),
                "interface_netmask":
                    str(device.interfaces[0].network.cidr.netmask),
                "interface_default_gateway": str(router_int.ip),
                "interface_routes": []}
            routes.append(to_router)
        return routes

    @staticmethod
    def _create_router_routes(device: Device, sandbox: Sandbox) -> List[Dict]:
        """Create routes for routers"""
        routes: List = []
        unreachable_networks: List[Network] = sandbox.networks.copy()
        for interface in device.interfaces:
            unreachable_networks.remove(interface.network)
        to_other_networks: List[Dict] = []
        for network in unreachable_networks:
            gateway: Device = Routes._find_router_in_network(network, sandbox)
            gateway_ip: str = ""
            for interface in gateway.interfaces:
                if interface.network.name == sandbox.wan.name:
                    gateway_ip = str(interface.ip)
                    break
            if gateway_ip:
                to_other_networks.append({"gateway": gateway_ip,
                                          "network": str(network.cidr.ip),
                                          "netmask": str(network.cidr.netmask)})
            else:
                raise AttributeError(f"There is no router in the network {network.name}")
        wan_ip: str = ""
        for interface in device.interfaces:
            if interface.network.name == sandbox.wan.name:
                wan_ip = str(interface.ip)
                break
        if wan_ip:
            routes.append({
                "interface_default_gateway": "",
                "interface_ip": str(wan_ip),
                "interface_netmask": str(sandbox.wan.cidr.netmask),
                "interface_routes": to_other_networks})
        else:
            raise AttributeError(f'Router "{device.name}" is not part of the'
                                 f'network "{sandbox.wan.name}"')
        return routes

    @staticmethod
    def create_routes(device: Device, sandbox: Sandbox) -> List[Dict]:
        """Create specific routes for each type of device"""
        routes: List[Dict] = []
        auto_route: str = "{{ ansible_default_ipv4.gateway }}"
        configure_auto = {
            "interface_ip": "{{ ansible_default_ipv4.address  | "
                            "default(ansible_all_ipv4_addresses[0]) }}",
            "interface_netmask": "{{ ansible_default_ipv4.netmask"
                                 "  | default('24') }}",
            "interface_default_gateway": auto_route}
        routes.append(configure_auto)

        if device.device_type is DeviceType.HOST:
            routes.extend(Routes._create_host_routes(device, sandbox))
        elif device.device_purpose is DevicePurpose.ROUTER:
            routes.extend(Routes._create_router_routes(device, sandbox))

        return routes
