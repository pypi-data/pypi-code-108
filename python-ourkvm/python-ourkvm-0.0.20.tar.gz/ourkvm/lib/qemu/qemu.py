import re
import pathlib
import socket
import json
import tempfile
import logging
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Callable, Type, List, Union
from ..networking import epoll, EPOLLIN, EPOLLHUP
from ..helpers.dupedict import DupeDict
from ..helpers.syscalls import SysCommand
from ..helpers.exceptions import ResourceNotFound, ResourceError, QMPError
from ..helpers.logger import log

def DupeDict_to_qemu_string(struct :Optional[DupeDict] = None) -> str:
	"""
	Converts a Duplicate Key'd Dictionary (DupeDict) into
	Qemu values, that is "-key val -key val".
	"""
	result = ''

	if struct:
		for key, val in struct:
			if type(val) == bool:
				result += f" -{key}"
			else:
				result += f" -{key} {val}"

	return result


def build_binary_start(name :str, namespace :Optional[str] = None) -> str:
	"""
	Builds the start of a qemu string.
	Appends namespace relevant data if supplied.
	"""
	qemu_binary = 'qemu-system-x86_64'
	if namespace:
		qemu_binary = f'ip netns exec {namespace} {qemu_binary}'

	return qemu_binary + f' -name "{name}" -pidfile {tempfile.gettempdir()}/ourkvm_{name}.pid'


def handle_graphics(enable :bool = False) -> str:
	"""
	Returns qemu parameters relevant to graphics.
	If graphics is turned off, this returns an empty string
	"""
	if not enable:
		return ' -display none -nographic'

	return ''


def handle_monitors(name :str) -> str:
	"""
	Returns qemu parameters surrounding monitoring sockets (qmp and monitor)
	"""
	return f' -qmp unix:{tempfile.gettempdir()}/{name}.qmp,server,nowait -monitor unix:{tempfile.gettempdir()}/{name}.monitor,server,nowait'


# https://hvornum.se/kvm_diagram.png
# https://news.ycombinator.com/item?id=19736722
# https://forums.freebsd.org/threads/qemu-kvm-and-shared-irq-for-dual-network-interfaces.78328/
def create_qemu_string(name :str,
		namespace :Optional[str] = None,
		base_hardware :Optional[DupeDict] = None,
		pcie_buses :Optional[DupeDict] = None,
		pcie_root_ports :Optional[DupeDict] = None,
		pcie_slave_buses :Optional[DupeDict] = None,
		pcie_slave_devices :Optional[DupeDict] = None,
		graphics :bool = False) -> str:
	"""
	Converts a set of parametrs into a qemu string with qemu parameters.
	Mainly a wrapper around DupeDict_to_qemu_string() but this is what
	builds the full qemu string given a set of hardware instructions.
	"""

	qemu_string = build_binary_start(name, namespace)
	qemu_string += handle_graphics(graphics)
	qemu_string += handle_monitors(name)
	qemu_string += DupeDict_to_qemu_string(base_hardware)
	qemu_string += DupeDict_to_qemu_string(pcie_buses)
	qemu_string += DupeDict_to_qemu_string(pcie_root_ports)
	qemu_string += DupeDict_to_qemu_string(pcie_slave_buses)
	qemu_string += DupeDict_to_qemu_string(pcie_slave_devices)

	return qemu_string


def verify_qemu_resources(name :str,
		base_hardware :Optional[DupeDict] = None,
		pcie_buses :Optional[DupeDict] = None,
		pcie_root_ports :Optional[DupeDict] = None,
		pcie_slave_buses :Optional[DupeDict] = None,
		pcie_slave_devices :Optional[DupeDict] = None) -> bool:
	"""
	This function verifies PCIe slave devices file=x paths.
	If a path is missing, exceptions will be raised.
	If all resources exist, True is retuned.
	"""

	if pcie_slave_devices:
		for device_type, value_string in pcie_slave_devices:
			if len(device_info_str := re.findall('file=.*?,|format=.*?,', value_string)) == 2:
				device_info_list = [x.split('=', 1) for x in device_info_str]
				device_info :Dict[Any, Any] = {}
				for item in device_info_list:
					device_info[item[0]] = item[1]
				
				if device_info.get('file'):
					device_location = pathlib.Path(device_info['file'].strip(', '))
					if not device_location.exists():
						if (device_format := device_info.get('format')) and device_format.startswith('qcow2'):
							raise ResourceNotFound(f"Could not locate qemu harddrive {device_location}")
						elif device_format and device_format.startswith('raw'):
							if 'media=cdrom' in value_string:
								raise ResourceNotFound(f"Could not locate qemu cdrom image {device_location}")
							else:
								raise ResourceNotFound(f"Could not locate qemu raw image {device_location}")
						else:
							raise ResourceNotFound(f"Could not locate qemu device resource {device_location}")
				else:
					raise ResourceError(f"No file definition for qemu resource {device_info}")

	return True


def qemu_img(cmd :str) -> SysCommand:
	"""
	A wrapper around the qemu-img command.
	Returns a SysCommand() handle for processing.
	"""
	return SysCommand(f"qemu-img {cmd}")


def write_qemu_service_file(location :pathlib.Path, name :str, qemu_config_path :pathlib.Path, depends_on :Optional[List[str]] = [], namespace :Optional[str] = None, force :Optional[bool] = False) -> bool:
	"""
	Creates a /etc/systemd/system/{name}.service file (or whichever location was given at the time).
	This is what dictates what the .service file should contain.
	No hardware is defined here, only ourkvm calls are used in the service file.
	The only reference to hardware is via the .cfg file that is specified, which is where
	the hardware lives.
	"""
	if location.exists() and not force:
		raise SystemError(f"Service file already exists: {location}")

	with location.open('w') as service:
		service.write(f'[Unit]\n')
		service.write(f'Description=Qemu instance of {name}\n')
		if depends_on:
			for dependency in depends_on:
				if not dependency.endswith('.service'):
					dependency += '.service'

				service.write(f"After={dependency}\n")

		service.write(f"\n")
		service.write(f'[Service]\n')
		service.write(f"PIDFile={tempfile.gettempdir()}/ourkvm_{name}.pid\n")
		if namespace:
			service.write(f"Namespace={namespace}\n")

		service.write(f"\n")
		service.write(f"ExecStartPre=/usr/bin/python -c 'import ourkvm; ourkvm.load_environment(\"{qemu_config_path}\")'\n")
		service.write(f"ExecStart=/bin/bash -c '$$(/usr/bin/python -m ourkvm --qemu-string {qemu_config_path})'\n")
		service.write(f"ExecStartPost=/bin/bash -c '$$(/usr/bin/python -m ourkvm --bring-online {qemu_config_path})'\n")
		# service.write(f"ExecStartPost=/bin/sh -c 'umask 022; ps aux | grep -E \"qemu-system-x86_64.*?-name .*[^-]{name}\" | grep -v \"grep -E\" | awk '\"'\"'{{print $2}}'\"'\"' > /run/ourkvm_{name}.pid'\r\n")
		
		service.write(f"\n")
		service.write(f"ExecStop=/usr/bin/python -m ourkvm --machine-name {name} --stop\n")
		service.write(f"ExecStopPost=/usr/bin/python -c 'import ourkvm; ourkvm.dismantle_environment(\"{qemu_config_path}\")'\n")
		# service.write(f"ExecStopPost=/bin/sh -c 'rm /run/ourkvm_{name}.pid'\n")
		
		# TODO: Monitor for changes to the environment?

		service.write(f"\n")
		service.write(f'[Install]\n')
		service.write(f'WantedBy=multi-user.target\n')

	return True


def get_machine_disk_information(machine_name :str) -> Dict[Any, Dict[str, Union[Dict[str, None], Any, None]]]:
	"""
	Returns information surrounding the disk information.
	Which harddrive-id is located on which bus etc.
	"""
	qemu_config_path = (pathlib.Path('/etc/qemu.d') / f"{machine_name}.cfg").expanduser().absolute()

	with qemu_config_path.open('r') as config:
		try:
			conf = json.load(config)
		except:
			conf = {}

	scsi_information = {}
	for device_type, value_string in conf.get('pcie_slave_buses', []):
		if 'scsi-cd' in value_string:
			continue

		if len(device_info_str := re.findall('drive=.*?,|bus=.*?,|id=.*?,', value_string)) == 3:
			device_info_list = [x.split('=', 1) for x in device_info_str]
			device_info :Dict[Any, Any] = {}
			for item in device_info_list:
				device_info[item[0].strip(', \r\n')] = item[1].strip(', \r\n')
			
			if (dev_id := device_info.get('drive')):
				scsi_information[dev_id] = {
					'bus' : device_info.get('bus'),
					'scsi_id' : device_info.get('id'),
					'file' : {
						'path' : None,
						'info' : None
					}
				}

	for device_type, value_string in conf.get('pcie_slave_devices', []):
		if 'media=cdrom' in value_string:
			continue

		if len(disk_info_str := re.findall('file=.*?,|format=.*?,|id=.*', value_string)) == 3:
			disk_info_list = [x.split('=', 1) for x in disk_info_str]
			disk_info :Dict[Any, Any] = {}
			for item in disk_info_list:
				disk_info[item[0].strip(', \r\n')] = item[1].strip(', \r\n')
			
			if (dev_id := disk_info.get('id', '')).strip() in scsi_information and disk_info.get('file'):
				scsi_information[dev_id]['path'] = disk_info['file']
				scsi_information[dev_id]['info'] = get_diskimage_information(pathlib.Path(disk_info['file']))

	return scsi_information


class DiskInfoFormatData(BaseModel):
	"""
	The format of information found in ``(qemu-img info)['format_specific']['data']``
	"""
	compat: str
	compression_type: str = Field(alias='compression-type')
	lazy_refcounts: bool = Field(alias='lazy-refcounts')
	refcount_bits: int = Field(alias='refcount-bits')
	corrupt: bool
	extended_l2: bool = Field(alias='extended-l2')


class DiskInfoFormat(BaseModel):
	"""
	Disk Format information found in ``(qemu-img info)['format_specific']``
	"""
	type: str
	data: DiskInfoFormatData


class DiskInfoModel(BaseModel):
	"""
	This is the structured returned by ``qemu-img info``.
	It's a dictionary in the base, with a fixed set of fields.
	"""
	virtual_size: int = Field(alias='virtual-size')
	filename: str
	cluster_size: int = Field(alias='cluster-size')
	format: str
	actual_size: int = Field(alias='actual-size')
	format_specific: DiskInfoFormat = Field(alias='format-specific')
	dirty_flag: bool = Field(alias='dirty-flag')


# https://github.com/python/typing/issues/182
# https://stackoverflow.com/a/51294709/929999
# https://qemu.readthedocs.io/en/latest/tools/qemu-img.html
def get_diskimage_information(location :pathlib.Path) -> DiskInfoModel:
	"""
	This returns disk information given by ``qemu-img info`` for a specific file location.
	The return value is a pydantic BaseModel that defines the structure:
	
	.. code:: json

		{
			"virtual-size": 42949672960,
			"filename": "testlarge.qcow2",
			"cluster-size": 65536,
			"format": "qcow2",
			"actual-size": 200704,
			"format-specific": {
				"type": "qcow2",
				"data": {
					"compat": "1.1",
					"compression-type": "zlib",
					"lazy-refcounts": false,
					"refcount-bits": 16,
					"corrupt": false,
					"extended-l2": false
				}
			},
			"dirty-flag": false
		}
	"""
	if (result := SysCommand(f"qemu-img info --output=json {location.expanduser().absolute()}")).exit_code != 0:
		raise ResourceError(f"Could not get disk image information on {location}: {result}")

	return DiskInfoModel(**json.loads(result.decode()))

def get_machine_status(name :str) -> str:
	return str(SysCommand(f"systemctl -o json is-active {name}.service").decode())

class QMP:
	def __init__(self, qmp_socket :pathlib.Path):
		if not qmp_socket.exists():
			raise SystemError(f"Could not locate QMP socket on {qmp_socket}")

		self.poller = epoll()
		self.socket :Optional[socket.socket] = None
		self.data = b''
		self.data_pos = 0
		self.socket_path = qmp_socket
		self.hooks :Dict[str, List[Callable[['QMP', Dict[str, Any]], None]]] = {}

		self._waiting_for_capabilities = True

	def __enter__(self) -> 'QMP':
		if not self.socket:
			self.connect(self.socket_path)

		while self._waiting_for_capabilities and self.poll():
			self.recv()

		return self

	def __exit__(self,
		exc_type: Optional[Type[BaseException]] = None,
		exc_value: Optional[BaseException] = None,
		traceback: Optional[Any] = None) -> None:

		self.close()

		if exc_value:
			raise exc_value

	def connect(self, endpoint :pathlib.Path) -> None:
		if self.socket:
			self.close()

		self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		self.socket.connect(f"{endpoint}")
		self.poller.register(self.socket.fileno(), EPOLLIN | EPOLLHUP)
		self.send(b'{ "execute": "qmp_capabilities" }') # Turn on the QMP socket internally in Qemu

		# TODO: Add a safety loop that doesn't release until we get a response from qmp_capabilities

	def register(self, event :str, hook :Callable[['QMP', Dict[str, Any]], None]) -> None:
		if event not in self.hooks:
			self.hooks[event] = []
		self.hooks[event].append(hook)

	def poll(self, timeout :float = 0.25) -> bool:
		if not self.socket:
			return False

		socket_alive = True
		for fileno, event in self.poller.poll(0.1):
			tmp = self.socket.recv(8192)
			if len(tmp) == 0:
				socket_alive = False
				break
			self.data += tmp

		return socket_alive

	def recv(self, length :int = 0, break_on_newlines :bool = True, parse_json :bool = True) -> bytes:
		if len(self.data):
			if not length:
				if break_on_newlines is True:
					length = (self.data.rfind(b'\r\n') + 2) - self.data_pos
				else:
					length = len(self.data) - self.data_pos

			self.data_pos += length

			if parse_json:
				# print(f"Parsing {length}: {self.data[self.data_pos - length:self.data_pos]}")
				for obj in self.data[self.data_pos - length:self.data_pos].split(b'\r\n'):
					if len(obj) == 0:
						continue

					try:
						j_obj = json.loads(obj.decode('UTF-8'))
					except json.decoder.JSONDecodeError:
						raise ValueError(f"Could not decode JSON data from {self}: {obj!r}")

					if j_obj.get('error'):
						raise QMPError(j_obj["error"])
					
					elif (capabilities := j_obj.get('QMP', {}).get('capabilities')) and 'oob' in capabilities:
						self._waiting_for_capabilities = False

					elif (recieved_event := j_obj.get('event')) in self.hooks:
						for hook in self.hooks[recieved_event]:
							hook(self, j_obj)
					elif j_obj.get('return', None) is not None:
						for event in self.hooks:
							for hook in self.hooks[event]:
								hook(self, j_obj)

			return self.data[self.data_pos - length:self.data_pos]
		else:
			old_pos = self.data_pos
			self.data_pos = len(self.data)
			return self.data[old_pos:]

	def send(self, data :bytes) -> int:
		log(f"QMP Sent data to {self.socket_path}: {data!r}", level=logging.DEBUG)
		if self.socket:
			return self.socket.send(data)
		else:
			return 0

	def transaction(self, data :List[Dict[str, Any]]) -> int:
		# https://qemu-project.gitlab.io/qemu/interop/qemu-qmp-ref.html#qapidoc-2013
		
		log(f"QMP Sent transaction data to {self.socket_path}: {data!r}", level=logging.DEBUG)
		if self.socket:
			return self.socket.send(bytes(json.dumps({
				"execute": "transaction",
				"arguments": {
					"actions": data
				}
			}), 'UTF-8'))
		else:
			return 0

	def close(self) -> None:
		if self.socket:
			self.socket.close()