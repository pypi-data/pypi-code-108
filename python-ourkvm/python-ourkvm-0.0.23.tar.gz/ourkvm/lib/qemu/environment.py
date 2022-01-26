import json
import pathlib
import glob
from typing import Dict, Any, List

from .qemu import get_machine_disk_information
from ..networking import InterfaceStruct, load_network_info, unload_network_info, get_namespace_info, add_namespace, del_namespace, generate_mac, curate_interfaces
from ..helpers.exceptions import NamespaceNotFound, ConfigurationError, NamespaceError

def load_conf(config :pathlib.Path) -> Dict[str, Any]:
	"""
	This function loads a machine configuration (.cfg) and
	converts it to a dictionary.
	"""
	config_path = pathlib.Path(config).expanduser().absolute()

	if not config_path.exists():
		raise ConfigurationError(f"Could not locate configuration {config}")

	with config_path.open('r') as fh:
		try:
			configuration = json.load(fh)
		except:
			return {}

	return dict(configuration)


def load_environment(config :str) -> None:
	"""
	This function loads a machine configuration and
	sets up the environment for that machine (namespace & networking).

	It will not be able to bring up certain network devices.
	This is because qemu needs to attach to tap devices for instance
	before the interfaces can be brought up. See --bring-online flag
	in the CLI Tool for more information.
	"""
	configuration = load_conf(pathlib.Path(config).expanduser().absolute())

	if namespace := configuration.get('namespace'):
		try:
			get_namespace_info(namespace)
		except (NamespaceNotFound, NamespaceError):
			add_namespace(namespace)

	if interfaces := configuration.get('interfaces'):
		load_network_info(interfaces=curate_interfaces([InterfaceStruct(**interface) for interface in interfaces], namespace))


def dismantle_environment(config :str) -> None:
	"""
	Loads a machine configuration and dismantles the environment.
	This is essentially like load_environment() but in reverse.
	"""
	configuration = load_conf(pathlib.Path(config).expanduser().absolute())

	if configuration.get('interfaces'):
		unload_network_info(interfaces=configuration['interfaces'])

	if namespace := configuration.get('namespace'):
		try:
			get_namespace_info(namespace)
			del_namespace(namespace)
		except (NamespaceNotFound, NamespaceError):
			pass


def load_network_cards_from_env(config :str) -> str:
	"""
	Loads a machine configuration and returns a qemu-friendly
	string of the network definitions. This is what --qemu-string
	is calling to achieve the network part of the string.
	"""
	configuration = load_conf(pathlib.Path(config).expanduser().absolute())

	result = ''

	network_id = 0
	previous_macs :List[str] = []
	if interfaces := configuration.get('interfaces'):
		interface_on_network = 0
		for interface in interfaces:
			if interface.get('attach'):
				if not (mac := interface.get('mac')):
					mac = generate_mac(filters=previous_macs)

				previous_macs.append(mac)
				
				result += f" -device virtio-net-pci,mac={mac},id=network{network_id},netdev=network{network_id}.{interface_on_network},status=on,bus=port9-0" # ,bootindex=2
				result += f" -netdev {interface['type']},ifname={interface['name']},id=network{network_id}.{interface_on_network},script=no,downscript=no"
				interface_on_network += 1

				network_id += 1

	return result


def get_network_cards_from_env(config :str) -> Dict[str, Any]:
	"""
	Loads a machine configuration and returns a flag dictionary structure.
	The contents of the dict is ``{"ifname": "namespace name"}`` (or ``None`` in value if no namespace).
	"""
	configuration = load_conf(pathlib.Path(config).expanduser().absolute())

	result = {}
	if interfaces := configuration.get('interfaces'):
		interfaces = curate_interfaces([InterfaceStruct(**interface) for interface in interfaces], configuration.get('namespace', {}))

		for interface in interfaces:
			if interface.attach:
				result[interface.name] = interface.namespace

	return result


def get_network_card_info_from_env(config :pathlib.Path) -> List[InterfaceStruct]:
	configuration = load_conf(config)

	if interfaces := configuration.get('interfaces'):
		return curate_interfaces([InterfaceStruct(**interface) for interface in interfaces], configuration.get('namespace', {}))

	return []

def get_harddrives(
	include_outside_of_cfg :bool = True,
	include_inside_of_cfg :bool = True) -> List[Dict[str, Any]]:

	harddrives = []
	if include_inside_of_cfg:
		for configuration in glob.glob('/etc/qemu.d/*.cfg'):
			harddrives.append({
				"machine_id": pathlib.Path(configuration).stem,
				"harddrives": get_machine_disk_information(pathlib.Path(configuration).stem)
			})

	return harddrives