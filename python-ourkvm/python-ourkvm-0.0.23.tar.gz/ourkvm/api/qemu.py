import json
import pathlib
import glob
import re
import psutil
from typing import Optional, Dict, Any, List, Union, Iterator, Tuple
from pydantic import BaseModel
from fastapi import Security, HTTPException
from .app import app
from .security import User, process_user_claim
from ..lib.qemu import (
	write_qemu_service_file,
	create_qemu_string,
	verify_qemu_resources,
	qemu_img,
	get_diskimage_information,
	take_snapshot,
	get_machine_status,
	# get_machine_resources
)
from ..lib.helpers.dupedict import DupeDict, JSON
from ..lib.helpers.syscalls import SysCommand
from ..lib.helpers.logger import log
# from ..lib.networking.interfaces import curate_interfaces

class NetworkInterfaces(BaseModel):
	type: str
	name: str
	bridge: Optional[str]
	namespace: Optional[Union[str, bool]]
	attach: Optional[bool]
	veth_pair: Optional[str]
	mac: Optional[str]

class NewVirtualMachine(BaseModel):
	namespace :Optional[str] = None
	cpu :str = "host"
	enable_kvm :bool = True
	machine :str = "q35,accel=kvm"
	devices :List[str] = ["intel-iommu"]
	chardev :List[str] = []
	serial :List[str] = []
	mon :List[str] = []
	cpu_cores :Optional[int] = min(4, int(SysCommand('nproc').decode().strip())) # Maximum 4 cores by default
	memory :int = (psutil.virtual_memory().total / 1024 / 1024) / 8 # Split memory into 8 available machines by default
	drives :List[str] = []
	# 	"if=pflash,format=raw,readonly=on,file=/usr/share/ovmf/x64/OVMF_CODE.fd",
	# 	"if=pflash,format=raw,readonly=on,file=/usr/share/ovmf/x64/OVMF_VARS.fd"
	# ]
	pcie_root_ports :Optional[List[str]] = None
	pcie_slave_buses :Optional[List[str]] = None
	pcie_slave_devices :Optional[List[str]] = None
	harddrives :Optional[List[Tuple[str, ...]]] = []
	cdroms :List[str] = []
	network :List[NetworkInterfaces] = []
	graphics :bool = False
	service_location :str = '/etc/systemd/system/'
	config_location :str = '/etc/qemu.d/'
	force: Optional[bool] = False

class ResourceLocations(BaseModel):
	service_location: str = '/etc/systemd/system/'
	config_location: str = '/etc/qemu.d/'
	run_as: str = 'root'

def convert_to_gigabyte(byte :int) -> float:
	return byte / 1024 / 1024 / 1024

@app.put("/qemu/machine/{name}", tags=["qemu"])
def create_machine_configuration(name :str, info :NewVirtualMachine, current_user: User = Security(process_user_claim, scopes=["qemu*"])) -> Dict[str, Any]:
	"""
	This API can be used to create new virtual machine configuration.
	This API endpoint will create harddrive resources specified in `--harddrives`.
	This endpoint also creates the `.service` and `.cfg` files under `--service_location` and `--config_location` paths.
	"""

	service_path = (pathlib.Path(info.service_location) / f"{name}.service").expanduser().absolute()
	qemu_config_path = (pathlib.Path(info.config_location) / f"{name}.cfg").expanduser().absolute()

	if not qemu_config_path.parent.exists():
		qemu_config_path.parent.mkdir(parents=True)

	if service_path.exists() and info.force is False:
		raise HTTPException(status_code=409, detail=f"A service file for the machine {name} already exists: {service_path}")

	if qemu_config_path.exists() and info.force is False:
		raise HTTPException(status_code=409, detail=f"A environment configuration file for the machine {name} already exists: {qemu_config_path}")

	base_hardware = DupeDict()
	base_hardware["cpu"] = info.cpu
	base_hardware["enable-kvm"] = info.enable_kvm
	base_hardware["machine"] = info.machine
	base_hardware["m"] = info.memory
	
	for device in info.devices:
		base_hardware["device"] = device
	for drive in info.drives:
		base_hardware["drive"] = drive
	for chardev in info.chardev:
		base_hardware["chardev"] = chardev
	for serial in info.serial:
		base_hardware["serial"] = serial
	for mon in info.mon:
		base_hardware["mon"] = mon
	if info.cpu_cores:
		base_hardware["smp"] = info.cpu_cores

	pcie_buses = DupeDict() # There's already a default pcie.0 bus builtin to qemu.

	pcie_root_ports = DupeDict()
	if info.pcie_root_ports:
		for device in info.pcie_root_ports:
			pcie_root_ports["device"] = device

	pcie_slave_buses = DupeDict()
	if info.pcie_slave_buses:
		for device in info.pcie_slave_buses:
			pcie_slave_buses["device"] = device

	pcie_slave_devices = DupeDict()
	if info.pcie_slave_devices:
		for device in info.pcie_slave_devices:
			pcie_slave_devices["device"] = device

	scsi_index = 0
	boot_index = 0
	if info.harddrives:
		for drive_index, harddrive_info in enumerate(info.harddrives):
			if not len(harddrive_info):
				continue
			elif len(harddrive_info) == 1 and not len(harddrive_info[0]):
				continue
			elif len(harddrive_info) == 2 and not ((harddrive_info[0] and len(harddrive_info[0].strip())) or (harddrive_info[1] and not len(harddrive_info[1].strip()))):
				continue

			if len(harddrive_info) == 1:
				disk_info = get_diskimage_information(pathlib.Path(harddrive_info[0]))
				harddrive_info = tuple([harddrive_info[0], f"{convert_to_gigabyte(disk_info.virtual_size)}G"])

			image_name, size = harddrive_info
			image_format = pathlib.Path(image_name).suffix[1:]
			image_path = pathlib.Path(image_name).expanduser().absolute()

			if not image_path.exists():
				if (output := qemu_img(f"create -f {image_format} {image_path} {size}")).exit_code != 0:
					raise HTTPException(status_code=510, detail=f"Could not create test image {image_path}: {output}")

			pcie_root_ports["device"] = f"virtio-scsi-pci,bus=pcie.0,id=scsi{scsi_index}"
			pcie_slave_buses["device"] = f"scsi-hd,drive=hdd{drive_index},bus=scsi{scsi_index}.0,id=scsi{scsi_index}.0,bootindex={boot_index}"
			pcie_slave_devices["drive"] = f"file={image_path},if=none,format={image_format},discard=unmap,aio=native,cache=none,id=hdd{drive_index}"

			scsi_index += 1
			boot_index += 1

	if info.cdroms:
		for drive_index, image_name in enumerate(info.cdroms):
			if len(image_name) == 0:
				continue

			image_path = pathlib.Path(image_name).expanduser().absolute()

			if not image_path.exists():
				raise HTTPException(status_code=510, detail=f"Could not locate ISO image {image_path}")

			pcie_root_ports["device"] = f"virtio-scsi-pci,bus=pcie.0,id=scsi{scsi_index}"
			pcie_slave_buses["device"] = f"scsi-cd,drive=cdrom{drive_index},bus=scsi{scsi_index}.0,id=scsi{scsi_index}.0,bootindex={boot_index}"
			pcie_slave_devices["drive"] = f"file={image_path},media=cdrom,if=none,format=raw,cache=none,id=cdrom{drive_index}"

			scsi_index += 1
			boot_index += 1

	verify_qemu_resources(name, base_hardware, pcie_buses, pcie_root_ports, pcie_slave_buses, pcie_slave_devices)

	with qemu_config_path.open('w') as config:
		config.write(json.dumps({
			"name": name,
			"namespace": info.namespace,
			"base_hardware": base_hardware,
			"pcie_buses": pcie_buses,
			"pcie_root_ports": pcie_root_ports,
			"pcie_slave_buses": pcie_slave_buses,
			"pcie_slave_devices": pcie_slave_devices,
			"interfaces": [x.dict(exclude_none=True) for x in info.network] # curate_interfaces(info.network, info.namespace)
		}, cls=JSON, indent=4))

	write_qemu_service_file(service_path, name, qemu_config_path, namespace=info.namespace, force=info.force)

	struct = {
		"name": name,
		"namespace": info.namespace,
		"base_hardware": base_hardware,
		"pcie_buses": pcie_buses,
		"pcie_root_ports": pcie_root_ports,
		"pcie_slave_buses": pcie_slave_buses,
		"pcie_slave_devices": pcie_slave_devices
	}
	result = {}
	for key, val in json.loads(json.dumps(struct, cls=JSON)).items():
		result[str(key)] = val

	return result

@app.get("/qemu/machine/{name}", tags=["qemu"])
def get_machine_configuration(name :str, current_user: User = Security(process_user_claim, scopes=["qemu*"])) -> Dict[str, Any]:
	"""
	This endpoint starts a qemu instance using a previously created service file with the given name.
	"""

	qemu_config_path = (pathlib.Path('/etc/qemu.d') / f"{name}.cfg").expanduser().absolute()

	if not qemu_config_path.parent.exists():
		raise HTTPException(status_code=404, detail="Machine not found")

	with qemu_config_path.open('r') as config:
		try:
			conf = json.load(config)
		except:
			conf = {}

	return {str(key): val for key,val in conf.items()}

@app.put("/qemu/machine/{name}/string", tags=["qemu"])
def create_qemu_string_from_struct(name :str, info :NewVirtualMachine, current_user: User = Security(process_user_claim, scopes=["qemu*"])) -> str:
	"""
	This API can be used to create new virtual machines.
	This API will not create machine resources, but simply returns a QEMU string that can be called.
	"""

	base_hardware = DupeDict()
	base_hardware["cpu"] = info.cpu
	base_hardware["enable-kvm"] = info.enable_kvm
	base_hardware["machine"] = info.machine
	base_hardware["device"] = "pcie-root-port,multifunction=on,bus=pcie.0,id=port9-0,addr=9.0,chassis=0"
	for device in info.devices:
		base_hardware["device"] = device
	base_hardware["m"] = info.memory
	for drive in info.drives:
		base_hardware["drive"] = drive

	pcie_buses = DupeDict() # There's already a default pcie.0 bus builtin to qemu.

	pcie_root_ports = DupeDict()
	if info.pcie_root_ports:
		for device in info.pcie_root_ports:
			pcie_root_ports["device"] = device

	pcie_slave_buses = DupeDict()
	if info.pcie_slave_buses:
		for device in info.pcie_slave_buses:
			pcie_slave_buses["device"] = device

	pcie_slave_devices = DupeDict()
	if info.pcie_slave_devices:
		for device in info.pcie_slave_devices:
			pcie_slave_devices["device"] = device

	return create_qemu_string(name, info.namespace, base_hardware, pcie_buses, pcie_root_ports, pcie_slave_buses, pcie_slave_devices)

@app.post("/qemu/machine/{name}/start", tags=["qemu"])
def start_qemu_machine(name :str, locations :ResourceLocations, current_user: User = Security(process_user_claim, scopes=["qemu*"])) -> None:
	"""
	This endpoint starts a qemu instance using a previously created service file with the given name.
	"""

	if locations.run_as == 'root':
		SysCommand(f"systemctl start {name}.service")
	else:
		SysCommand(f"systemctl --user start {name}.service")

@app.post("/qemu/machine/{name}/stop", tags=["qemu"])
def stop_qemu_machine(name :str, locations :ResourceLocations, current_user: User = Security(process_user_claim, scopes=["qemu*"])) -> None:
	"""
	This endpoint stops a qemu instance using a previously created service file with the given name.
	"""

	if locations.run_as == 'root':
		SysCommand(f"systemctl stop {name}.service")
	else:
		SysCommand(f"systemctl --user stop {name}.service")

@app.get("/qemu/machine/{name}/status", tags=["qemu"])
def status_qemu_machine(name :str, current_user: User = Security(process_user_claim, scopes=["qemu*"])) -> Dict[str, str]:
	"""
	This endpoint gets the service status of the machine.
	If the machine is missing or dead, it will return inactive.
	"""

	return {'status': get_machine_status(name)}

@app.patch("/qemu/machine/{name}/snapshot", tags=["qemu"])
def snapshot_qemu_machine(name :str, current_user: User = Security(process_user_claim, scopes=["qemu*"])) -> None:
	"""
	This endpoint enables you to take a snapshot of a machine's current state.
	If it's running the memory and all devices will be snapshotted using the builtin qemu snapshot tool.
	If the machine is at rest and the disk volumes are of format qcow2 (or stored on a btrfs/zfs storage) those
	will be snapshotted manually instead.
	"""

	# resources = get_machine_resources(name)
	if (machine_status := get_machine_status(name).strip()) != "active":
		raise HTTPException(status_code=501, detail=f"Cannot snapshot {machine_status} machines yet!")
		# resources = get_machine_resource_locations(name)
		# snapshot_resources(resources)
	else:
		take_snapshot(pathlib.Path(f"/etc/qemu.d/{name}.cfg").expanduser().absolute())

	raise HTTPException(status_code=501, detail="Not yet implemented")

@app.patch("/qemu/machine/{name}/migrate", tags=["qemu"])
def migrate_qemu_machine(name :str, current_user: User = Security(process_user_claim, scopes=["qemu*"])) -> None:
	"""
	This endpoint enables you to migrate the machine to a different cluster.
	"""

	raise HTTPException(status_code=501, detail="Not yet implemented")

@app.post("/qemu/machine/{name}/export", tags=["qemu"])
def export_qemu_machine(name :str, current_user: User = Security(process_user_claim, scopes=["qemu*"])) -> None:
	"""
	This endpoint enables you to export either the configuration or to do a full export including devices.
	"""

	raise HTTPException(status_code=501, detail="Not yet implemented")

@app.get("/qemu/machines", tags=["qemu"])
def get_all_qemu_machines(current_user: User = Security(process_user_claim, scopes=["qemu*"])) -> Iterator[Dict[str, Any]]:
	"""
	This endpoint starts a qemu instance using a previously created service file with the given name.
	"""
	for conf_file in glob.glob("/etc/qemu.d/*.cfg"):
		with open(conf_file) as fh:
			try:
				data = json.load(fh)
			except:
				log(f"Could not load JSON configuration found at: {conf_file}")
				continue

			yield {'name': data.get('name', pathlib.Path(conf_file).name[:-4]), **{str(key): val for key, val in data.items()}}
			# yield data.get('name', pathlib.Path(conf_file).name[:-4])

@app.delete("/qemu/machine/{name}", tags=["qemu"])
def delete_qemu_machine(name :str, locations :ResourceLocations, current_user: User = Security(process_user_claim, scopes=["qemu*"])) -> None:
	service_path = (pathlib.Path(locations.service_location) / f"{name}.service").expanduser().absolute()
	qemu_config_path = (pathlib.Path(locations.config_location) / f"{name}.cfg").expanduser().absolute()

	if not qemu_config_path.parent.exists():
		qemu_config_path.parent.mkdir(parents=True)

	# TODO: Parse all other *.cfg files and if any drive
	# is shared, do not unlink them.

	# Read the configuration and extract all drive=X
	# and unlink the virual drives.
	with qemu_config_path.open('r') as config:
		try:
			conf = json.load(config)
		except:
			conf = {}

	for device_type, value_string in conf.get('pcie_slave_devices', []):
		if 'media=cdrom' in value_string:
			continue

		if len(device_info_str := re.findall('file=.*?,|format=.*?,', value_string)) == 2:
			device_info_list = [x.split('=', 1) for x in device_info_str]
			device_info :Dict[Any, Any] = {}
			for item in device_info_list:
				device_info[item[0]] = item[1]
			
			if device_info.get('file'):
				device_location = pathlib.Path(device_info['file'].strip(', '))
				if device_location.exists():
					device_location.unlink()

	if service_path.exists():
		service_path.unlink()

	if qemu_config_path.exists():
		qemu_config_path.unlink()