import json
import psutil
import socket
import glob
import logging
import pathlib
from typing import List, Any, Optional, Dict
from .net import ip, get_namespaces
from .structs import InterfaceStruct
from ..helpers.exceptions import InterfaceError, NamespaceError
from ..helpers.logger import log
from ..helpers.syscalls import SysCommand

def get_all_mac_addresses_in_use(*,
	include_namespaces :bool = True,
	include_clusters :bool = True,
	include_configurations :bool = True) -> Dict[str, str]:
	"""
	Returns all MAC addresses found on the local machine.
	If flags are set, includes:

	- dormant interface definitions in ``/etc/qemu.d/*.cfg`` files
	- interfaces inside namespaces
	- interfaces outside of namespaces
	- include interfaces other from cluster-nodes
	"""

	try:
		AF_MAC = socket.AddressFamily.AF_LINK
	except:
		AF_MAC = socket.AddressFamily.AF_PACKET

	mac_addresses = {}
	for name, interface in psutil.net_if_addrs().items():
		if name == 'lo':
			continue

		for information_obj in interface:
			if information_obj.family == AF_MAC:
				mac_addresses[information_obj.address.replace('-', ':').strip()] = name

	if include_namespaces:
		for namespace in get_namespaces():
			if (result := ip.netns(f"exec {namespace['name']} bash -c 'cat /sys/class/net/*/address'")).exit_code == 0:
				for line in result.decode().split('\n'):
					if len(line) > 0:
						mac_addresses[line.strip()] = namespace['name']
			else:
				raise NamespaceError(f"Could not execute in namespace {namespace['name']}: {result}")

	if include_configurations:
		from ..qemu.environment import load_conf

		for conf_file in glob.glob('/etc/qemu.d/*.cfg'):
			configuration = load_conf(pathlib.Path(conf_file).expanduser().absolute())

			for interface in configuration.get('interfaces', []):
				if (mac := interface.get('mac')) and type(mac) == str:
					mac_addresses[mac.strip()] = conf_file

	return mac_addresses

def get_all_interfaces(*,
	include_namespaces :bool = True,
	include_clusters :bool = True,
	include_configurations :bool = True) -> List[Dict[str, Any]]:
	"""
	Returns all MAC addresses found on the local machine.
	If flags are set, includes:

	- dormant interface definitions in ``/etc/qemu.d/*.cfg`` files
	- interfaces inside namespaces
	- interfaces outside of namespaces
	- include interfaces other from cluster-nodes
	"""

	interfaces = []
	if host_interfaces := SysCommand(f"ip --json addr").decode():
		try:
			interfaces += json.loads(host_interfaces)
		except json.decoder.JSONDecodeError:
			pass

	if include_namespaces:
		for namespace in get_namespaces():
			if (namespace_interfaces := ip.netns(f"exec {namespace['name']} ip --json addr")).exit_code == 0:
				try:
					interfaces += [{"namespace": namespace, **interface_struct} for interface_struct in json.loads(namespace_interfaces.decode())]
				except json.decoder.JSONDecodeError:
					pass
			else:
				raise NamespaceError(f"Could not execute in namespace {namespace['name']}: {namespace_interfaces}")

	if include_configurations:
		from ..qemu.environment import load_conf

		for conf_file in glob.glob('/etc/qemu.d/*.cfg'):
			configuration = load_conf(pathlib.Path(conf_file).expanduser().absolute())

			interfaces += [{"configuration": conf_file, "machine": configuration.get('name'), **interface_struct} for interface_struct in configuration.get('interfaces', [])]

	return interfaces

# https://serverfault.com/a/40720
def generate_mac(prefix :str = 'FE:00:00', filters :List[str] = []) -> str:
	"""
	Generates a MAC address, exlucdes any addresses found in filters=[]
	"""
	for number in range(16**6):
		hex_num = hex(number)[2:].zfill(6)

		if (address := "{}:{}{}:{}{}:{}{}".format(prefix, *hex_num)).lower() not in [f.lower() for f in filters]:
			return address

	raise InterfaceError(f"No available addresses with the prefix {prefix}")


def get_bridge_interfaces(bridge :str, namespace :Optional[str] = None) -> Any:
	"""
	Returns a dictionary of interfaces tied to a certain bridge interface.
	Equivilent of executing: ip link show master <bridge>
	"""
	if namespace:
		if (result := ip.netns(f"exec {namespace} ip link show master {bridge}", options=['--json'])).exit_code == 0:
			if (data := result.decode('UTF-8')):
				try:
					return json.loads(data)
				except json.decoder.JSONDecodeError:
					log(f"Could not read JSON data of bridge information: {data}", level=logging.WARNING, fg="yellow")
					return {}
	else:
		if (result := ip.link(f"show master {bridge}", options=['--json'])).exit_code == 0:
			if (data := result.decode('UTF-8')):
				try:
					return json.loads(data)
				except json.decoder.JSONDecodeError:
					log(f"Could not read JSON data of bridge information: {data}", level=logging.WARNING, fg="yellow")
					return {}

	return {}

def curate_interfaces(structure :List[InterfaceStruct], namespace :Optional[str] = None) -> List[InterfaceStruct]:
	"""
	This function curates a ourkvm dictionary structure of interfaces.
	It converts ``"namespace": True`` into ``"namespace": "machine namespace name"`` if applicable.
	It also adds MAC addresses to the configuration structure if no MAC was defined.
	"""
	filters :List[str] = [str(x) for x in get_all_mac_addresses_in_use().keys()]

	for interface in structure:
		if namespace and interface.namespace:
			if interface.namespace.to is True:
				# This can get automatically populated anyway
				# and will save the user from having to re-configure
				# the .cfg file later if they descide to change the namespace
				interface.namespace.to = namespace

			if interface.namespace.from_ is True:
				# This can get automatically populated anyway
				# and will save the user from having to re-configure
				# the .cfg file later if they descide to change the namespace
				interface.namespace.from_ = namespace

		# If "mac" is True, then we'll replace it with an actual MAC address.
		# That way it gets permanently frozen into place.
		if not interface.mac or type(interface.mac) != str:
			interface.mac = generate_mac(filters=filters)

	return structure