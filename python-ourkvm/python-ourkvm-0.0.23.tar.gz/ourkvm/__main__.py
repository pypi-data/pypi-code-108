import importlib
import sys
import pathlib
import json
import time
import logging
import http.client
import tempfile
from typing import Optional, List, Dict, Union, Any

if pathlib.Path('./ourkvm/__init__.py').absolute().exists():
	spec = importlib.util.spec_from_file_location("ourkvm", "./ourkvm/__init__.py")
	ourkvm = importlib.util.module_from_spec(spec)
	sys.modules["ourkvm"] = ourkvm
	spec.loader.exec_module(sys.modules["ourkvm"])
else:
	import ourkvm

def generate_base_hardware() -> ourkvm.DupeDict:
	"""
	This function sets up the basic hardware for a qemu machine.
	Things such as CPU type, Memory ammount, BIOS/UEFI and --serial device.
	"""
	hardware = ourkvm.DupeDict()
	hardware["cpu"] = ourkvm.storage['arguments'].cpu
	hardware["enable-kvm"] = True
	hardware["machine"] = "q35,accel=kvm"
	hardware["device"] = "intel-iommu"
	hardware["m"] = ourkvm.storage['arguments'].memory

	# Add a hotplug enabled (https://www.linux-kvm.org/images/d/d7/02x07-Aspen-Michael_Roth-QEMU_Hotplug_infrastructure.pdf):
	# Intel X58 north bridge IOH
	# PCI Express root port device id 3420
	hardware["device"] = "pcie-root-port,multifunction=on,bus=pcie.0,id=port9-0,addr=9.0,chassis=0"

	if ourkvm.storage['arguments'].bios is False:
		hardware["drive"] = f"if=pflash,format=raw,readonly=on,file={ourkvm.storage['arguments'].uefi_code}"
		hardware["drive"] = f"if=pflash,format=raw,readonly=on,file={ourkvm.storage['arguments'].uefi_vars}"

	if ourkvm.storage['arguments'].serial:
		# https://patchwork.kernel.org/project/qemu-devel/patch/1455638581-5912-1-git-send-email-peter.maydell@linaro.org/
		# https://superuser.com/questions/1373226/how-to-redirect-qemu-serial-output-to-both-a-file-and-the-terminal-or-a-port
		"""
			-chardev stdio,id=mux,mux=on
			-serial chardev:mux
			-monitor chardev:mux"
		"""
		serial_path = pathlib.Path(ourkvm.storage['arguments'].serial).expanduser().absolute() / f"{ourkvm.storage['arguments'].machine_name}.serial"

		hardware["chardev"] = f"socket,path={serial_path},server=on,wait=off,id=char0,mux=on,logfile={serial_path}.log,signal=off"
		hardware["serial"] = "chardev:char0"
		hardware["mon"] = "chardev=char0"

	return hardware

def make_network_processable(struct :Dict[str, Any]) -> List[Dict[str, Union[str, bool, int, None]]]:
	"""
	Converts a --network string into a dictionary that is workable.
	Basically just a glorified `json.loads()` but with namespace parsing.
	"""
	if struct:
		struct = json.loads(struct)

		for interface_obj in struct:
			if type(interface_obj.get('namespace', {}).get('to')) == bool and interface_obj['namespace']['to']:
				if not ourkvm.storage['arguments'].namespace:
					raise SystemError(f"Could not automatically determine a namespace for target namespace on interface {interface_obj.get('name')}")

				interface_obj['namespace']['to'] = ourkvm.storage['arguments'].namespace

			if type(interface_obj.get('namespace', {}).get('from')) == bool and interface_obj['namespace']['from']:
				if not ourkvm.storage['arguments'].namespace:
					raise SystemError(f"Could not automatically determine a namespace for target namespace on interface {interface_obj.get('name')}")

				interface_obj['namespace']['from'] = ourkvm.storage['arguments'].namespace
	else:
		struct = []

	return struct

def setup_pcie_paths() -> List[ourkvm.DupeDict]:
	"""
	This function converts --harddrives and --cdroms into something qemu understands.
	And that is PCIe bus lanes and devices.
	"""
	root_ports = ourkvm.DupeDict()
	slave_buses = ourkvm.DupeDict()
	slave_devices = ourkvm.DupeDict()

	scsi_index = 0
	boot_index = 0
	if ourkvm.storage['arguments'].harddrives:
		for drive_index, drive_spec in enumerate(ourkvm.storage['arguments'].harddrives.split(',')):
			if ':' not in drive_spec:
				drive_spec += ':20G'

			image_name, size = drive_spec.split(':',1)
			image_format = pathlib.Path(image_name).suffix[1:]
			image_path = pathlib.Path(image_name).expanduser().absolute()

			if not image_path.exists():
				image_path.parent.mkdir(parents=True, exist_ok=True)
				
				if (output := ourkvm.qemu_img(f"create -f {image_format} {image_path} {size}")).exit_code != 0:
					raise SystemError(f"Could not create test image {image_path}: {output}")

			root_ports["device"] = f"virtio-scsi-pci,bus=pcie.0,id=scsi{scsi_index}"
			slave_buses["device"] = f"scsi-hd,drive=hdd{drive_index},bus=scsi{scsi_index}.0,id=scsi{scsi_index}.0,bootindex={boot_index}"
			slave_devices["drive"] = f"file={image_path},if=none,format={image_format},discard=unmap,aio=native,cache=none,id=hdd{drive_index}"

			scsi_index += 1
			boot_index += 1

	if ourkvm.storage['arguments'].cdroms:
		for drive_index, image_name in enumerate(ourkvm.storage['arguments'].cdroms.split(',')):
			image_path = pathlib.Path(image_name).expanduser().absolute()

			if not image_path.exists():
				raise ourkvm.ResourceNotFound(f"Could not locate ISO image {image_path}")

			root_ports["device"] = f"virtio-scsi-pci,bus=pcie.0,id=scsi{scsi_index}"
			slave_buses["device"] = f"scsi-cd,drive=cdrom{drive_index},bus=scsi{scsi_index}.0,id=scsi{scsi_index}.0,bootindex={boot_index}"
			slave_devices["drive"] = f"file={image_path},media=cdrom,if=none,format=raw,cache=none,id=cdrom{drive_index}"

			scsi_index += 1
			boot_index += 1

	buses = ourkvm.DupeDict() # There's already a default pcie.0 bus builtin to qemu.

	return buses, root_ports, slave_buses, slave_devices

def create_qemu_cfg(
	name :str,
	namespace :str,
	base_hardware :Optional[ourkvm.DupeDict] = None,
	pcie_buses :Optional[ourkvm.DupeDict] = None,
	pcie_root_ports :Optional[ourkvm.DupeDict] = None,
	pcie_slave_buses :Optional[ourkvm.DupeDict] = None,
	pcie_slave_devices :Optional[ourkvm.DupeDict] = None,
	network_interfaces :List[Dict[str, Union[str, bool, int, None]]] = []
) -> pathlib.Path:
	"""
	TODO: This function can be removed in favor of ourkvm.create_qemu_cfg() in the future
	Takes a number of parameters and creates a /etc/qemu.d/{name}.cfg for a machines given parameters
	"""
	qemu_config_path = pathlib.Path(f"{ourkvm.storage['arguments'].config}/{name}.cfg").expanduser().absolute()

	if not qemu_config_path.parent.exists():
		qemu_config_path.parent.mkdir(parents=True)

	if qemu_config_path.exists() and not ourkvm.storage['arguments'].force:
		raise ourkvm.ResourceError(f"A environment configuration file for the machine {name} already exists: {qemu_config_path}")

	with qemu_config_path.open('w') as config:
		config.write(json.dumps({
			"namespace": namespace,
			"base_hardware": base_hardware,
			"pcie_buses": pcie_buses,
			"pcie_root_ports": pcie_root_ports,
			"pcie_slave_buses": pcie_slave_buses,
			"pcie_slave_devices": pcie_slave_devices,
			"interfaces": network_interfaces
		}, cls=ourkvm.JSON, indent=4))

	return qemu_config_path


# Create a new machine if we have .machine_name and we're not trying to --stop it
# flake8: noqa: C901
if ourkvm.storage['arguments'].machine_name and \
	ourkvm.storage['arguments'].stop is False and \
	ourkvm.storage['arguments'].add_netdev is None and \
	ourkvm.storage['arguments'].snapshot is False:
	"""
	This block assumes:
		--machine_name X
		!--stop

	If the above is true, that means we want to create a new machine with the given name.
	Steps:
		1. Generate base hardware
		2. Setup PCIe devices
		3. Verify resources (and create those that are missing)
		4. Curate the --network definition
		5. Parse any --depends_on (service) dependencies
		6. Write a /etc/qemu.d/{name}.cfg
		7. Write a /etc/systemd/system/{name}.service
	"""
	base_hardware = generate_base_hardware()
	pcie_buses, pcie_root_ports, pcie_slave_buses, pcie_slave_devices = setup_pcie_paths()

	name = ourkvm.storage['arguments'].machine_name
	namespace = ourkvm.storage['arguments'].namespace
	# if not namespace and ourkvm.storage['arguments'].no_namespace is False:
	# 	namespace = name

	ourkvm.storage['arguments'].network = make_network_processable(ourkvm.storage['arguments'].network)

	ourkvm.verify_qemu_resources(name, base_hardware, pcie_buses, pcie_root_ports, pcie_slave_buses, pcie_slave_devices)
	network_interfaces = ourkvm.curate_interfaces([ourkvm.InterfaceStruct(**struct) for struct in ourkvm.storage['arguments'].network], ourkvm.storage['arguments'].namespace)

	service_path = pathlib.Path(f"{ourkvm.storage['arguments'].service}/{name}.service").expanduser().absolute()
	if service_path.exists() and not ourkvm.storage['arguments'].force:
		raise ourkvm.ResourceError(f"A service file for the machine {name} already exists: {service_path}")
	elif service_path.exists():
		# Because write_qemu_service_file() creates it
		service_path.unlink()

	dependencies = [dep.strip() for dep in ourkvm.storage['arguments'].depends_on.split(',') if len(dep.strip()) > 0]

	if ourkvm.storage['arguments'].service:
		qemu_config_path = create_qemu_cfg(name, namespace, base_hardware, pcie_buses, pcie_root_ports, pcie_slave_buses, pcie_slave_devices, network_interfaces)
		ourkvm.write_qemu_service_file(service_path, name, qemu_config_path, depends_on=dependencies, namespace=namespace, force=ourkvm.storage['arguments'].force)
	else:
		qemu_string = ourkvm.create_qemu_string(name, namespace, base_hardware, pcie_buses, pcie_root_ports, pcie_slave_buses, pcie_slave_devices, graphics=ourkvm.storage['arguments'].graphics)
		print(f"qemu-system-x86_64" + qemu_string)

elif (machine_name := ourkvm.storage['arguments'].machine_name) and (ifname := ourkvm.storage['arguments'].add_netdev):
	"""
	--add-netdev 'interface name'

	Will create and attach a new interface. Type has to be tap.
	The interface will also be saved to the machine's configuration.
	"""
	qmp_path = pathlib.Path(f"{tempfile.gettempdir()}/{ourkvm.secure_filename(machine_name)}.qmp")
	# monitor_path = pathlib.Path(f"{tempfile.gettempdir()}/{ourkvm.secure_filename(ourkvm.storage['arguments'].machine_name)}.monitor")
	
	if ourkvm.storage['arguments'].nocreate and not list(ourkvm.inteface_info(ifname)):
		raise ourkvm.InterfaceError(f"Could not locate {ifname} and --nocreate was given so cannot create it either.")

	if not ourkvm.storage['arguments'].nocreate and not list(ourkvm.inteface_info(ifname)):
		ourkvm.create_interface(ifname=ifname, iftype="tap", namespace=ourkvm.storage['arguments'].namespace)

	qemu_config_path = pathlib.Path(f"/etc/qemu.d/{ourkvm.secure_filename(machine_name)}.cfg").expanduser().absolute()

	if not qemu_config_path.exists():
		raise SystemError(f"Could not locate machine/environment configuration on /etc/qemu.d/{machine_name}.cfg")

	network_id = 0
	for interface_obj in ourkvm.get_network_card_info_from_env(qemu_config_path):
		if interface_obj.get('attach'):
			network_id += 1

	if (net_id := ourkvm.storage['arguments'].network_id) and net_id > network_id:
		network_id = net_id
	else:
		network_id += 1

	# -device virtio-net-pci,mac={mac},id=network{network_id},netdev=network{network_id}.0,status=on,bus=pcie.0
	# -netdev {interface['type']},ifname={interface['name']},id=network{network_id}.0,script=no,downscript=no
	execute_returns = 0

	filters :List[str] = [str(x) for x in ourkvm.get_all_mac_addresses_in_use().keys()]
	if not (mac_address := ourkvm.storage['arguments'].mac):
		mac_address = ourkvm.generate_mac(filters=filters)

	with qemu_config_path.open('r+') as conf_fh:
		config = json.load(conf_fh)

		for interface_obj in config.get("interfaces", []):
			if interface_obj.get('name') == ifname:
				raise ourkvm.InterfaceError(f"Interface already defined in configuration.")
		
		config["interfaces"] = config.get('interfaces', []) + [{
			"type": "tap",
			"name": ifname,
			"bridge": ourkvm.storage['arguments'].bridge,
			"namespace": {
				"from": None,
				"to": ourkvm.storage['arguments'].namespace
			},
			"attach": True,
			"mac": mac_address
		}]

		conf_fh.seek(0)
		conf_fh.flush()
		conf_fh.truncate()
		conf_fh.flush()

		conf_fh.write(json.dumps(config, indent=4))

	def return_handle(qmp, json_data :Dict[str, Any]) -> None:
		global execute_returns

		execute_returns += 1

	if qmp_path.exists():
		with ourkvm.QMP(pathlib.Path(f"{tempfile.gettempdir()}/{qemu_config_path.stem}.qmp")) as qmp:
			qmp.register('TRANSACTION_RETURN', return_handle)

			qmp.send(bytes(json.dumps({
				"execute": "netdev_add",
				"arguments": {
					"type": "tap",
					"ifname": ifname,
					"id": f"network{network_id}.0",
					"script": "no",
					"downscript": "no"
				}
			}), 'UTF-8'))

			qmp.send(bytes(json.dumps({
				"execute": "device_add",
				"arguments": {
					"driver": "virtio-net-pci",
					"id": f"network{network_id}",
					"netdev": f"network{network_id}.0",
					"bus": "port9-0",
					"mac": mac_address,
					"status": "on"
				}
			}), 'UTF-8'))

			while qmp.poll() and execute_returns < 3:
				qmp.recv()
	else:
		ourkvm.log(f"Could not attach the interface to any running machines with this name.", level=logging.INFO, fg="yellow")

	print(f"New interface has successfully been attached and configuration has been updated.")

elif (machine_name := ourkvm.storage['arguments'].machine_name) and ourkvm.storage['arguments'].snapshot:
	config_file = pathlib.Path(f"/etc/qemu.d/{ourkvm.storage['arguments'].machine_name}.cfg").expanduser().absolute()

	if (machine_status := ourkvm.get_machine_status(machine_name).strip()) != "active":
		raise ourkvm.RequirementError(f"Cannot snapshot {machine_status} machine yet")

	if namespace := ourkvm.load_conf(config_file).get('namespace') and ourkvm.storage['arguments'].norecurse is False:
		ourkvm.ip.netns(f"exec /usr/bin/python -m ourkvm --machine-name {machine_name} --snapshot --norecurse")

	ourkvm.take_snapshot(config_file)

elif ourkvm.storage['arguments'].machine_name and ourkvm.storage['arguments'].stop:
	"""
	If --stop was given in junction with --machine-name that means we want to stop a machine.
	We do that by connecting to the machines .qmp socket which we lazilly assume is located at:
	/tmp-dir/{name}.qmp
	In the future perhaps we should read the configuration, detect it and connect to it.

	If the machine hasn't responded to ACPI POWER_OFF within 30 seconds, the machine is forcefully
	shut down. This can be extended with --graceful-shutdown X where X is measured in seconds.
	"""

	qmp_path = pathlib.Path(f"{tempfile.gettempdir()}/{ourkvm.secure_filename(ourkvm.storage['arguments'].machine_name)}.qmp")
	# monitor_path = pathlib.Path(f"{tempfile.gettempdir()}/{ourkvm.secure_filename(ourkvm.storage['arguments'].machine_name)}.monitor")
	if not qmp_path.exists():
		raise SystemError(f"Could not locate QMP socket on {tempfile.gettempdir()}/{ourkvm.secure_filename(ourkvm.storage['arguments'].machine_name)}.qmp")

	import socket
	from .lib.networking import epoll, EPOLLIN, EPOLLHUP

	s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	s.connect(f"{qmp_path}")

	poller = epoll()
	poller.register(s.fileno(), EPOLLIN | EPOLLHUP)

	alive = True
	grace_hard_off = ourkvm.storage['arguments'].graceful_shutdown
	grace_quit = 5
	start = time.time()
	data = b''
	data_pos = 0
	qemu_quit_sent = False
	while alive and time.time() - start < grace_hard_off:
		for fileno, event in poller.poll(0.1):
			data += s.recv(8192)

		if time.time() - start > grace_quit and qemu_quit_sent is False:
			s.send(bytes('{ "execute": "quit" }', 'UTF-8'))
			qemu_quit_sent = True
			
		if b'\r\n' in data:
			output = data[data_pos:data_pos + data.rfind(b'\r\n')]
			new_pos = data.rfind(b'\r\n')
			data_pos = new_pos

			# TODO: Clear the old data and "reset" data_pos

			for line in output.split(b'\r\n'):
				if len(line) == 0:
					continue

				ourkvm.log(f"Raw line from QMP: {line}")

				try:
					qemu_output = json.loads(line.decode('UTF-8'))
					ourkvm.log(f"QMP json data: {qemu_output}")
				except:
					ourkvm.log(f"Could not load JSON data: {line}", level=logging.ERROR, fg="red")
					continue

				if qemu_output.get('QMP', {}).get('version'):
					s.send(bytes('{ "execute": "qmp_capabilities" }', 'UTF-8'))
					time.sleep(1)
					s.send(bytes('{ "execute": "system_powerdown" }', 'UTF-8'))
				elif qemu_output.get('event', {}) == 'SHUTDOWN':
					ourkvm.log(f"Machine has powered off completely.", fg="yellow")
					alive = False
					break
		else:
			ourkvm.log(f"No newline in output: {output}", level=logging.WARNING, fg="yellow")

	ourkvm.log(f"Shutdown complete.")
	s.close()

	exit(0)

elif (qemu_config_path := ourkvm.storage['arguments'].qemu_string):
	"""
	If --qemu-string is given, we will load the machine configuration
	and output a qemu-string that can be run manually.
	"""
	qemu_config_path = pathlib.Path(qemu_config_path).expanduser().absolute()

	if not qemu_config_path.exists():
		raise SystemError(f"Could not locate machine/environment configuration on {ourkvm.storage['arguments'].qemu_string}")

	valid_fields = {"name", "namespace", "base_hardware", "pcie_buses", "pcie_root_ports", "pcie_slave_buses", "pcie_slave_devices", "graphics"}
	qemu_string_base = ourkvm.create_qemu_string(**{
		'name' : qemu_config_path.stem,
		**{key: val for key, val in ourkvm.load_conf(qemu_config_path).items() if key in valid_fields}}
	)
	qemu_string_base += ourkvm.load_network_cards_from_env(qemu_config_path)

	ourkvm.log(f"Generated Qemu-string: {qemu_string_base}", level=logging.INFO, hide_term_output=True)
	print(qemu_string_base)

elif (qemu_config_path := ourkvm.storage['arguments'].bring_online):
	"""
	--bring-online is a flag that will go over a machine configuration
	and bring all of it's network interfaces to the state "UP".
	This is useful with ExecStartPost= in a .service file for instance.
	"""
	qemu_config_path = pathlib.Path(qemu_config_path).expanduser().absolute()

	if not qemu_config_path.exists():
		raise SystemError(f"Could not locate machine/environment configuration on {ourkvm.storage['arguments'].bring_online}")

	interfaces = ourkvm.get_network_cards_from_env(qemu_config_path)
	for interface, namespace in interfaces.items():
		ourkvm.ifup(interface, namespace)

elif ourkvm.storage['arguments'].report_health:
	if ourkvm.storage['arguments'].health_schema == 'http':
		connection = http.client.HTTPConnection(f"{ourkvm.storage['arguments'].health_server}:{ourkvm.storage['arguments'].health_port}")
	else:
		connection = http.client.HTTPSConnection(f"{ourkvm.storage['arguments'].health_server}:{ourkvm.storage['arguments'].health_port}") # nosec

	access_token = ourkvm.storage['arguments'].access_token
	payload = {
		'os' : {
			'version' : '250-1'
		}
	}

	headers = {
		"Content-type": "application/json",
	}

	connection.request("PUT", f"{ourkvm.storage['arguments'].health_base_url}/monitoring/machine/health?access_token={access_token}", json.dumps(payload))
	result = connection.getresponse()

elif (qemu_config_path := ourkvm.storage['arguments'].snapshot):
	qemu_config_path = pathlib.Path(qemu_config_path).expanduser().absolute()

	if not qemu_config_path.exists():
		raise SystemError(f"Could not locate machine/environment configuration to take a snapshot: {ourkvm.storage['arguments'].snapshot}")

	ourkvm.take_snapshot(qemu_config_path)

def main():
	pass