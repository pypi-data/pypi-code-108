from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from netaddr import IPNetwork, IPAddress
import kypo.topology_definition.models as kypo

from sandboxcreator.input_parser.topology_parser import Topology
from sandboxcreator.io.reader import Reader


class Protocol(Enum):
    """VM communication protocol"""
    SSH = 1
    WINRM = 2

    def __str__(self):
        return self.name


class DeviceType(Enum):
    """Type of device"""
    ROUTER = 1
    HOST = 2

    def __str__(self):
        return self.name.lower()


class NetworkType(Enum):
    """Type of network"""
    PRIVATE = 1
    PUBLIC = 2

    def __str__(self):
        return f"{self.name.lower()}_network"


class DevicePurpose(Enum):
    """Function of a device - also determines building order"""
    ROUTER = 1
    HOST = 2
    CONTROLLER = 3

    def __str__(self):
        return self.name.lower()


class Flavor:
    """Representation of a flavor"""

    def __init__(self, name: str, memory: int, cpus: int):
        self.name: str = name
        self.memory: int = memory
        self.cpus: int = cpus

    def __str__(self):
        return f"Flavor(name: {self.name}, memory: {self.memory} GB," \
               f"CPUs: {self.cpus})"


class Network:
    """Virtual network"""

    def __init__(self, name: str, network_type: NetworkType, cidr: str):
        self.name: str = name
        self.type: NetworkType = network_type
        self.cidr: IPNetwork = IPNetwork(cidr)

    def __str__(self):
        return f"Network(name: {self.name}, type: {self.type}," \
               f" cidr: {self.cidr})"


class Interface:
    """Network interface of a device"""

    def __init__(self, network: Network, ip: str):
        self.network: Network = network
        self.ip: IPAddress = IPAddress(ip)

    def __str__(self):
        return f"Interface(network: {self.network.name}, " \
               f"type: {self.network.type}, ip: {self.ip})"


class Device:
    """A device of the sandbox"""

    def __init__(self, name: str, device_purpose: DevicePurpose, box: str,
                 memory: int, cpus: int, protocol: Protocol = Protocol.SSH,
                 interfaces: List[Interface] = [],
                 usb_passthrough: bool = False):
        self.name: str = name
        self.device_purpose: DevicePurpose = device_purpose
        if device_purpose is DevicePurpose.ROUTER:
            self.device_type = DeviceType.ROUTER
        elif (device_purpose is DevicePurpose.HOST or
              device_purpose == DevicePurpose.CONTROLLER):
            self.device_type = DeviceType.HOST
        else:
            raise ValueError("Invalid device purpose")
        self.box: str = box
        self.protocol: Protocol = protocol
        self.memory: int = memory
        self.cpus: int = cpus
        self.interfaces: List[Interface] = interfaces
        self.usb_passthrough: bool = usb_passthrough

    def __lt__(self, other):
        return self.device_purpose.value < other.device_purpose.value

    def __str__(self):
        return f"Device(name: {self.name}, type: {self.device_type}, purpose: " \
               f"{self.device_purpose}, box: {self.box})"


class Sandbox:
    """Structure that holds all information about the sandbox"""

    def __init__(self, topology_path: Path, configuration_path: Path,
                 flavors_path: Path, sandbox_dir: Path,
                 ansible_installed: bool, user_provisioning_dir: Optional[Path],
                 extra_vars_file: Optional[Path], generate_provisioning: bool,
                 verbose_ansible: bool):
        try:
            topology: Topology = Topology.from_file(topology_path)
        except Exception as e:
            raise ValueError(f"Invalid topology definition:\n{e}")
        self.generate_provisioning: bool = generate_provisioning
        self.sandbox_dir: Path = sandbox_dir
        self.ansible_installed: bool = ansible_installed
        self.verbose_ansible: bool = verbose_ansible
        self.user_provisioning_dir: Optional[Path] = user_provisioning_dir
        if self.user_provisioning_dir is not None:
            self.include_requirements: bool = (self.user_provisioning_dir /
                                               "requirements.yml").is_file()
        else:
            self.include_requirements: bool = False
        self.extra_vars: Optional[Path] = extra_vars_file
        self.config: Dict = Reader.open_yaml(configuration_path)
        self.flavors: List[Flavor] = self._load_flavors(flavors_path)
        self.networks: List[Network] = self._create_network_list(topology,
                                                                 self.config)
        self.wan: Network = Network(topology.wan.name, NetworkType.PRIVATE,
                                    topology.wan.cidr)
        self.devices: List[Device] = self._create_device_list(topology,
                                                              self.flavors,
                                                              self.config,
                                                              ansible_installed,
                                                              self.networks)
        self.router_present: bool = bool(topology.routers)
        self.controller_present: bool =\
            Sandbox._controller_needed(self.devices, ansible_installed)
        self.groups: Dict = Sandbox._load_groups(topology)

    @classmethod
    def _load_groups(cls, topology: Topology) -> Dict:
        """Load the list of user defined Ansible groups"""
        groups: Dict = {}

        for group in topology.groups:
            groups[group.name] = group.nodes

        return groups

    @classmethod
    def _create_network_list(cls, topology: Topology,
                             config: Dict) -> List[Network]:
        """Create list of networks"""
        networks: List[Network] = []
        for network in topology.networks:
            networks.append(Network(network.name, NetworkType.PRIVATE,
                                    network.cidr))
        if topology.routers:
            networks.append(Network(topology.wan.name, NetworkType.PRIVATE,
                                    topology.wan.cidr))

        return networks

    @classmethod
    def _load_flavors(cls, flavors_path: Path) -> List[Flavor]:
        """Load list of possible flavors from configuration file"""

        flavors: List[Flavor] = []
        flavors_file_content: Dict = Reader.open_yaml(flavors_path)

        for flavor_name, attributes in flavors_file_content.items():
            try:
                memory: int = int(attributes["memory"])
            except ValueError:
                raise ValueError(f'Memory value "{attributes["memory"]}"'
                                 ' is not an integer')
            try:
                cpus: int = int(attributes["cores"])
            except ValueError:
                raise ValueError(f'Cpus value "{attributes["cores"]}"'
                                 ' is not an integer')
            flavors.append(Flavor(flavor_name, memory, cpus))

        return flavors

    @staticmethod
    def _controller_needed(devices: List[Device], ansible_installed: bool) \
            -> bool:
        """Check if a controller device should be created"""
        if ansible_installed:
            return False
        for device in devices:
            if device.protocol == Protocol.WINRM:
                return True
        return False

    @staticmethod
    def _resolve_flavor(flavor_name: str, flavors: List[Flavor]) -> Tuple[int, int]:
        for flavor in flavors:
            if flavor.name == flavor_name:
                return flavor.memory, flavor.cpus
        raise AttributeError(f"Invalid flavor: {flavor_name}")

    @staticmethod
    def _parse_memory_and_cpus(host: kypo.Host, flavors: List[Flavor])\
            -> Tuple[int, int]:
        if host.flavor:
            memory, cpus = Sandbox._resolve_flavor(host.flavor, flavors)
        if host.extra is not None:
            if "memory" in host.extra:
                try:
                    memory = int(host.extra["memory"])
                except ValueError:
                    raise ValueError(f'Memory value "{host.extra["memory"]}"'
                                     ' is not an integer')
            if "cpus" in host.extra:
                try:
                    cpus = int(host.extra["cpus"])
                except ValueError:
                    raise (f'Cpus value "{host.extra["cpus"]}" is not an'
                           'integer')
        return memory, cpus

    @staticmethod
    def _create_host_device(host: kypo.Host, topology: Topology,
                            flavors: List[Flavor], config: Dict,
                            networks: List[Network]) -> Device:

        memory, cpus = Sandbox._parse_memory_and_cpus(host, flavors)

        device_networks: List[Interface] = []
        for net_mapping in topology.net_mappings:
            if net_mapping.host == host.name:
                network = Sandbox._find_network(net_mapping.network,
                                                networks)
                device_networks.append(Interface(network, net_mapping.ip))

        if host.base_box.mgmt_protocol == kypo.Protocol.SSH:
            protocol: Protocol = Protocol.SSH
        elif host.base_box.mgmt_protocol == kypo.Protocol.WINRM:
            protocol: Protocol = Protocol.WINRM

        usb_passthrough: bool = False
        if host.extra is not None and "usb_passthrough" in host.extra:
            usb_passthrough: bool = host.extra["usb_passthrough"]

        return Device(host.name, DevicePurpose.HOST, host.base_box.image,
                      memory, cpus, protocol, device_networks, usb_passthrough)

    @staticmethod
    def _create_router_device(router: kypo.Router, topology: Topology,
                              flavors: List[Flavor], config: Dict,
                              networks: List[Network], router_n: int) -> Device:

        if router.flavor:
            memory, cpus = Sandbox._resolve_flavor(router.flavor, flavors)
        else:
            memory, cpus = config["default_router_memory"], \
                           config["default_router_cpus"]

        device_networks: List[Interface] = []
        for router_mapping in topology.router_mappings:
            if router_mapping.router == router.name:
                network = Sandbox._find_network(router_mapping.network,
                                                networks)
                device_networks.append(Interface(network, router_mapping.ip))

        for net in networks:
            if net.name == topology.wan.name:
                wan_network: Network = net
        wan_ip: IPAddress = IPNetwork(topology.wan.cidr)[router_n]
        device_networks.append(Interface(wan_network, wan_ip))

        if router.base_box.mgmt_protocol == kypo.Protocol.SSH:
            protocol: Protocol = Protocol.SSH
        elif router.base_box.mgmt_protocol == kypo.Protocol.WINRM:
            protocol: Protocol = Protocol.WINRM

        return Device(router.name, DevicePurpose.ROUTER, router.base_box.image,
                      memory, cpus, protocol, device_networks)

    @staticmethod
    def _find_network(network_name: str, networks: List[Network])\
            -> Optional[Network]:
        """Return a Network by its name"""
        for network in networks:
            if network.name == network_name:
                return network

        return None


    @staticmethod
    def _find_available_ip(network: Network, devices: List[Device])\
            -> Interface:
        """Find an available IP address in a network and return the Interface"""

        all_addresses: List[IPAddress] = list(network.cidr)
        if len(all_addresses) > 5:  # avoid low addresses
            all_addresses = all_addresses[5:]
        new_ip: str = None
        for address in all_addresses:
            conflict = False
            for device in devices:
                for interface in device.interfaces:
                    if interface.network is network and interface.ip == address:
                        conflict = True
            if not conflict:
                new_ip = str(address)
                break
        return Interface(network, new_ip)

    @staticmethod
    def _find_network_for_controller(devices: List[Device]) -> Network:
        """Find appropriate network for controller"""

        for device in devices:
            if device.device_purpose is DevicePurpose.HOST and\
               device.protocol is Protocol.WINRM:
                if device.interfaces:
                    return device.interfaces[0].network
                raise RuntimeError(f"Host {device.name} has no network")
        raise RuntimeError("No appropriate network for controller")

    @staticmethod
    def _create_device_list(topology: Topology, flavors: List[Flavor],
                            config: Dict, ansible_installed: bool,
                            networks: List[Network]) -> List[Device]:
        """Creates priority sorted list of devices with all attributes"""

        devices: List[Device] = []

        for host in topology.hosts:
            devices.append(Sandbox._create_host_device(host, topology, flavors,
                                                       config, networks))
        router_n: int = 0
        for router in topology.routers:
            router_n += 1
            devices.append(Sandbox._create_router_device(router, topology,
                                                         flavors, config,
                                                         networks, router_n))
        if Sandbox._controller_needed(devices, ansible_installed):  # needs to be at the end
            controller_network: Network =\
                Sandbox._find_network_for_controller(devices)
            controller_ip: Interface =\
                Sandbox._find_available_ip(controller_network, devices)
            devices.append(Device(config["controller_name"],
                                  DevicePurpose.CONTROLLER,
                                  config["controller_box"],
                                  int(config["controller_memory"]),
                                  int(config["controller_cpus"]), Protocol.SSH,
                                  [controller_ip]))

        return sorted(devices)
