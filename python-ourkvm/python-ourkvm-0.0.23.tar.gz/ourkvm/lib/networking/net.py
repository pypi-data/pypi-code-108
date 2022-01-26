import json
import sys
import getpass
import logging
from typing import Dict, List, Any, Optional, Union, Iterator, cast

from .structs import InterfaceStruct, NamespaceStruct
from ..helpers.logger import log
from ..helpers.syscalls import SysCommand
from ..helpers.exceptions import NamespaceNotFound, NamespaceError, UnsupportedHardware, InterfaceNotFound, InterfaceError

if sys.platform == 'linux':
	from select import epoll as epoll
	from select import EPOLLIN as EPOLLIN
	from select import EPOLLHUP as EPOLLHUP
else:
	import select
	EPOLLIN = 0
	EPOLLHUP = 0

	class epoll():
		""" #!if windows
		Create a epoll() implementation that simulates the epoll() behavior.
		This creates one interface for epoll() across all platforms by wrapping select() when epoll() is not available.
		"""
		def __init__(self) -> None:
			self.sockets: Dict[str, Any] = {}
			self.monitoring: Dict[int, Any] = {}

		def unregister(self, fileno :int, *args :List[Any], **kwargs :Dict[str, Any]) -> None:
			try:
				del(self.monitoring[fileno])
			except: # nosec
				pass

		def register(self, fileno :int, *args :int, **kwargs :Dict[str, Any]) -> None:
			self.monitoring[fileno] = True

		def poll(self, timeout: float = 0.05, *args :str, **kwargs :Dict[str, Any]) -> List[Any]:
			try:
				return [[fileno, 1] for fileno in select.select(list(self.monitoring.keys()), [], [], timeout)[0]]
			except OSError:
				return []


class ip:
	"""
	A wrapper for different iproute2 ip commands.
	"""
	@staticmethod
	def link(*args :str, options :List[str] = []) -> SysCommand:
		"""
		Wrapps ``ip link`` and returns a ``SysCommand()`` handle.
		"""
		return SysCommand(f"ip {''.join(options)} link {' '.join(args)}")

	@staticmethod
	def netns(*args :str, options :List[str] = []) -> SysCommand:
		"""
		Wrapps ``ip netns`` and returns a ``SysCommand()`` handle.
		"""
		return SysCommand(f"ip {''.join(options)} netns {' '.join(args)}")

	@staticmethod
	def tuntap(*args :str, options :List[str] = []) -> SysCommand:
		"""
		Wrapps ``ip tuntap`` and returns a ``SysCommand()`` handle.
		"""
		return SysCommand(f"ip {''.join(options)} tuntap {' '.join(args)}")


def cidr_to_netmask(cidr :int, bitlen :Optional[int] = 32) -> str:
	"""
	This function converts a CIDR notation (/24 or /62 for instace)
	to a humanly readable netmask (not officially endorsed for IPv6).
	cidr 24 would become '255.255.255.0' for instance.
	"""
	if not bitlen or bitlen not in [32, 64]:
		raise InterfaceError(f"Could not convert cidr notation {cidr} using a bitlen of None")

	netmask = ''
	while cidr > 8:
		netmask += '255.'
		cidr -= 8
	netmask += str(2 ** cidr - 1) # math.log(128, 2)

	return netmask + ('.0' * (3 - netmask.count('.') if bitlen == 32 else 7 - netmask.count('.')))

def add_namespace(namespace :str) -> bool:
	"""
	This function can be used to create namespaces.
	Currently only supports non-nested namespaces.
	"""
	if (output := ip.netns(f"add {namespace}")).exit_code != 0:
		raise NamespaceError(f"Could not create namespace {namespace}: {output}")

	return True


def del_namespace(namespace :str) -> bool:
	"""
	This function deletes a namespace.
	Currently only supports non-nested namespaces.
	"""
	if (output := ip.netns(f"del {namespace}")).exit_code != 0:
		raise NamespaceError(f"Could not delete namespace {namespace}: {output}")

	return True


def run_namespace(namespace :str, *args :str) -> SysCommand:
	"""
	Executes a command inside a namespace.
	Eqeuvilent of doing: ip netns exec <namespace> <command string>
	Returns a SysCommand() instance.
	"""
	if (worker := ip.netns(f"exec {namespace}", *args)).exit_code != 0:
		raise NamespaceError(f"Could not execute in namespace {namespace}: {worker}")

	return worker


def add_bridge(ifname :str, namespace :Optional[str] = None) -> bool:
	"""
	Create a bridge interface inside or outside of a namespace.
	Equvilent of calling: ip link add name <ifname> type bridge
	"""
	if namespace:
		if ip.netns(f"exec {namespace} ip link add name {ifname} type bridge").exit_code == 0:
			return bool(ip.netns(f"exec {namespace} ip link set dev {ifname} up").exit_code == 0)
	else:
		if ip.link(f"add name {ifname} type bridge").exit_code == 0:
			return bool(ip.link(f"set dev {ifname} up").exit_code == 0)
	return False


def add_if_to_bridge(bridge :str, ifname :str, namespace :Optional[str] = None) -> bool:
	"""
	Sets a bridge as master to a interface using iproute2
	Equvilent of calling: ip link set dev <ifname> master <bridge>
	"""
	if namespace:
		return bool(ip.netns(f"exec {namespace} ip link set dev {ifname} master {bridge}").exit_code == 0)
	else:
		return bool(ip.link(f"set dev {ifname} master {bridge}").exit_code == 0)


def ifup(ifname :str, namespace :Optional[str] = None) -> bool:
	"""
	Brings an interface UP, either inside or outside a namespace
	Equvilent of calling: ip link set dev <ifname> up
	"""
	if namespace:
		return bool(ip.netns(f"exec {namespace} ip link set dev {ifname} up").exit_code == 0)
	else:
		return bool(ip.link(f"set {ifname} up").exit_code == 0)


def ifdown(ifname :str, namespace :Optional[str] = None) -> bool:
	"""
	Brings an interface DOWN, either inside or outside a namespace
	Equvilent of calling: ip link set dev <ifname> down
	"""
	if namespace:
		return bool(ip.netns(f"exec {namespace} ip link set dev {ifname} down").exit_code == 0)
	else:
		return bool(ip.link(f"set {ifname} down").exit_code == 0)


def get_namespaces() -> List[Dict[str, Any]]:
	"""
	Returns a list of namespaces and their information (if exists).
	Returns an empty list of there were no namespaces.
	"""
	if (output := SysCommand("ip -oneline -color=never -j netns list")).exit_code == 0:
		if not len(output.decode().strip()):
			return []
		return [dict(x) for x in json.loads(output.decode().strip())]
	else:
		raise ValueError(f"Could not execute namespace info grabber: {output.exit_code} {output}")


def get_namespace_info(namespace :str) -> Dict[str, Any]:
	"""
	Returns information surrounding the specified namespace.
	Equivilent of executing: ip -j netns list
	"""
	if (output := SysCommand("ip -oneline -color=never -j netns list")).exit_code == 0:
		try:
			for info in json.loads(str(output.decode())):
				if info.get('name') == namespace:
					return dict(info)
			raise NamespaceNotFound(f"Could not locate namespace {namespace} in output: {output}")
		except json.decoder.JSONDecodeError:
			raise NamespaceError(f"Could not locate namespace {namespace} in output: {output}")
	elif output.exit_code == 256:
		raise NamespaceNotFound(f"Could not locate namespace {namespace} in output: {output}")
	else:
		raise ValueError(f"Could not execute namespace info grabber: {output.exit_code} {output}")


def get_interface_info(ifname :str, namespace :Optional[str] = None) -> Iterator[Dict[str, Union[int, None, str]]]:
	"""
	Returns information on a network interface.
	The structure is pre-defined to:

	.. code:: python

		{
			"family": AnyOf["mac", "inet", "inet6"],
			"address": AnyOf["ip", "mac"],
			"netmask": AnyOf["netmask", None],
			"broadcast": AnyOf["ip", "mac"],
			"point_to_point": bool
		}
	"""
	
	interface_info = {}
	
	if namespace:
		interfaces = json.loads(SysCommand(f"ip netns exec {namespace} ip --json addr").decode().strip())
	else:
		interfaces = json.loads(SysCommand(f"ip --json addr").decode().strip())

	for interface in interfaces:
		if interface.get('ifname') == ifname:
			interface_info = interface
			break

	if not len(interface_info):
		raise InterfaceNotFound(f"Could not locate interface {ifname}.")

	# Yield the MAC separately, as it's not part of the addr_info struct (?).
	yield {
		"family": "mac",
		"address": interface_info.get('address'),
		"netmask": None,
		"prefixlen": None,
		"broadcast": interface_info.get('broadcast'),
		"point_to_point": ('POINTOPOINT' in interface_info.get('flags', []))
	}

	for address in interface_info.get('addr_info', []):
		yield {
			"family": address.get('family'),
			"address": address.get('local'),
			"netmask": cidr_to_netmask(
				address.get('prefixlen'),
				bitlen={'inet6': 64, 'inet': 32}.get(address.get('family', None))
			),
			"prefixlen": address.get('prefixlen'),
			"broadcast": address.get('broadcast'),
			"point_to_point": ('POINTOPOINT' in address.get('flags', []))
		}

def create_interface(ifname :str, iftype :str, pair_name :Optional[str] = None, namespace :Optional[NamespaceStruct] = None) -> Dict[str, Union[str, None]]:
	"""
	This function will create one of three types of interfaces:
	* TAP
	* VETH
	* Physical interface (won't actually do anything)
	The way they get created depends on the type.
	But they call ip.tuntap for TAP interfaces, ip.link for veth
	and for physical interfaces we simply confirm that it exists.
	"""
	created_interfaces :Dict[str, Union[str, None]] = {}
	log(f'Creating interface {ifname}', level=logging.INFO)

	if iftype == 'tap':
		import pwd
		user_info = pwd.getpwnam(getpass.getuser())

		if namespace and namespace.to:
			log(f'Creating the interface inside namespace {namespace}', level=logging.INFO)
			if not (output := ip.netns(f"exec {namespace.to} ip tuntap add mode tap one_queue vnet_hdr user {user_info.pw_uid} group {user_info.pw_gid} name {ifname}")).exit_code == 0:
				raise InterfaceError(f"Could not add tap interface {ifname} in namespace {namespace.to}: [{output.exit_code}] {output}")
		else:
			log(f'Creating the interface in hostspace', level=logging.INFO)
			if not (output := ip.tuntap(f"add mode tap one_queue vnet_hdr user {user_info.pw_uid} group {user_info.pw_gid} name {ifname}")).exit_code == 0:
				raise InterfaceError(f"Could not add tap interface {ifname}: [{output.exit_code}] {output}")

		created_interfaces[ifname] = namespace.to if (namespace and type(namespace.to) is str) else None

	elif iftype == 'veth':
		if pair_name is None:
			pair_name = f"{ifname}_ns"

		found_interface = False
		# Look for the interface (and it's pair) in the target namespace
		try:
			list(get_interface_info(f"{ifname}", namespace=namespace.to if (namespace and type(namespace.to) is str) else None))
			found_interface = True
		except InterfaceNotFound:
			log(f'Veth interface {ifname} was not found in the target namespace {namespace.to if (namespace and type(namespace.to) is str) else None}', level=logging.INFO)
			pass

		# Look for the interface (and it's pair) in the host space (usually that's what 'from' is)
		try:
			list(get_interface_info(f"{ifname}", namespace=namespace.from_ if (namespace and type(namespace.from_) is str) else None))
			found_interface = True
		except InterfaceNotFound:
			log(f'Veth interface {ifname} was not found in the source namespace {namespace.from_ if (namespace and type(namespace.from_) is str) else None}', level=logging.INFO)
			pass

		if found_interface is False:
			if namespace and namespace.to and not namespace.from_:
				# We only create the interface if there's not a FROM -> TO
				# Since that should have been taken care of in the first veth definition for the pair
				# (because 'from' indicates that it was created in a namespace from another interface definition)
				if not (output := ip.netns(f"exec {namespace.to} ip link add {ifname} type veth peer name {pair_name}")).exit_code == 0:
					raise InterfaceError(f"Could not create veth pair {ifname}<-->{pair_name} in namespace {namespace.to}: {output}")

				log(f'Created veth interface {ifname} in namespace {namespace.to}', level=logging.INFO)

				created_interfaces[ifname] = namespace.to if (namespace and type(namespace.to) is str) else None
				created_interfaces[pair_name] = namespace.to if (namespace and type(namespace.to) is str) else None
			else:
				if (handle := ip.link(f"add {ifname} type veth peer name {pair_name}")).exit_code != 0:
					raise InterfaceError(f"Could not create veth pair {ifname}<-->{pair_name}: {handle}")

				log(f'Created veth interface {ifname} in hostspace', level=logging.INFO)

				created_interfaces[ifname] = None
				created_interfaces[pair_name] = None

		if namespace:
			if namespace.from_ and namespace.to:
				log(f'Moving veth interface {ifname} from namespace {namespace.from_} to namespace {namespace.to}', level=logging.INFO)
				if not (output := ip.netns(f"exec {namespace.from_} ip link set {ifname} netns {namespace.to}")).exit_code == 0:
					raise InterfaceError(f"Could not move veth interface {ifname} from namespace {namespace.from_} to namespace {namespace.to}: {output}")
			elif namespace.from_ is None and namespace.to and not list(get_interface_info(f"{ifname}", namespace=namespace.to)):
				log(f'Moving veth interface {ifname} from hostspace to namespace {namespace.to}', level=logging.INFO)
				if not (output := ip.link(f"set {ifname} netns {namespace.to}")).exit_code == 0:
					raise InterfaceError(f"Could not move veth interface {ifname} from hostspace to namespace {namespace.to}: {output}")

			created_interfaces[ifname] = namespace.to if (namespace and type(namespace.to) is str) else None

	elif iftype == 'phys':
		list(get_interface_info(ifname))
		created_interfaces[ifname] = namespace.to if (namespace and type(namespace.to) is str) else None

	else:
		raise UnsupportedHardware(f"Unknown interface type {iftype}")

	return created_interfaces


def delete_interface(ifname :str, namespace :Optional[str] = None) -> bool:
	"""
	Deletes a interface using iproute2, both inside or outside a given namespace.
	Equivilent of executing: ip link del <ifname>
	"""
	if namespace:
		return bool(ip.netns(f"exec {namespace} ip link del {ifname}").exit_code == 0)
	else:
		return bool(ip.link(f"del {ifname}").exit_code == 0)


def delete_bridge(bridge :str, namespace :Optional[str] = None) -> bool:
	"""
	A wrapper for ``delete_interface()``
	"""
	return delete_interface(bridge, namespace)


def load_network_info(interfaces :List[InterfaceStruct] = []) -> None:
	"""
	This function can load a ourkvm dictionary structure of network interfaces,
	and creates the interfaces that are missing (also inside namespaces).
	"""
	log(f'Loading network information: {interfaces}', level=logging.INFO)
	for interface in interfaces:
		log(f'Parsing interface: {interface}', level=logging.INFO)
		if not (ifname := interface.name):
			raise InterfaceError(f"Loading interfaces require the interface information to have a name key with a str value.")

		namespace = None
		if interface.namespace and (namespace := interface.namespace.to):
			if not type(namespace) is str:
				raise InterfaceError(f"You need to curate_interfaces() first and convert namespace from '{type(namespace)}' to 'str'")

			try:
				get_namespace_info(namespace)
				log(f'Found namespace on interface: {namespace}', level=logging.INFO)
			except (NamespaceNotFound, NamespaceError):
				add_namespace(namespace)
				log(f'Created namespace for interface: {namespace}', level=logging.INFO)

		if (iftype := interface.type):
			for interface_created, if_namespace in create_interface(ifname, iftype, pair_name=interface.veth_pair, namespace=interface.namespace).items():
				ifup(interface_created, namespace=if_namespace)

		if br_name := interface.bridge:
			add_bridge(br_name, namespace=cast(str, namespace))
			add_if_to_bridge(br_name, interface.name, namespace=cast(str, namespace))
			ifup(br_name, namespace=cast(str, namespace))

def unload_network_info(interfaces :List[Dict[str, Any]] = []) -> None:
	"""
	Loads a ourkvm dictionary structure of network interfaces,
	proceeds to dismantle them but preserves bridges if there's interfaces left on them.
	"""
	from .interfaces import get_bridge_interfaces
	
	for interface in interfaces:
		if not interface.get('name'):
			raise InterfaceError(f"Loading interfaces require the interface information to have a name key with a str value.")

		delete_interface(str(interface.get('name')), namespace=str(interface.get('namespace', {}).get('to')))

		if (bridge := interface.get('bridge')):
			if len(get_bridge_interfaces(bridge, namespace=interface.get('namespace', {}).get('to'))) == 0:
				delete_interface(bridge, namespace=interface.get('namespace', {}).get('to'))
			else:
				log(f"Bridge {bridge} was not empty, leaving it alone.", level=logging.INFO)