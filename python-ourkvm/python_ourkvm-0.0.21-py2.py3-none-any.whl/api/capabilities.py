from typing import Dict, Union, List
from .app import app

@app.get("/capabilities/networking/interfaces/create", tags=["capabilities"])
def get_network_interface_arguments() -> Dict[
			str,
			Union[
				str, int, bool, None, List[str], Dict[
					str,
					Union[
						str, int, bool, None, List[str], Dict[
							str,
							Union[
								str, int, bool, None, List[str], Dict[
									str,
									Union[
										str, int, bool, None, List[str], Dict[
											str,
											Union[
												str, int, bool, None, List[str], Dict[
													str,
													Union[
														str, int, bool, None, List[str], Dict[
															str,
															Union[
																str, int, bool, None, List[str]
															]
														]
													]
												]
											]
										]
									]
								]
							]
						]
					]
				]
			]
		]:
	"""
	Returns the available interface types, and which arguments they take and
	at what URL it's found.
	"""
	return {
		"tap" : {
			"url": "/networking/interface/{ifname}",
			"arguments": {
				"iftype": {
					"type": "str",
					"description": "interface type",
					"default": "tap"
				},
				"mac": {
					"type": "str",
					"description": "mac address to assign to the interface",
					"default": None
				},
				"ip": {
					"type": "str",
					"description": "IP address to assign to the interface",
					"default": None
				},
				"netmask": {
					"type": "str",
					"description": "Which netmask to assign the the ip address on the interface",
					"default": None
				},
				"state": {
					"type": "str",
					"description": "Which state to put the interface in",
					"default": "up"
				},
				"attached": {
					"type": "bool",
					"description": "Defines if the interface should be attached to the virtual machine",
					"default": False
				},
				"bridge": {
					"type": "str",
					"description": "Which bridge (if any) this interface should be added to",
					"default": None
				},
				"namespace": {
					"type": "str",
					"description": "Which namespace (if any) this interface should be moved in to (also moves the bridge)",
					"default": None
				}
			}
		
		},
		"veth" : {
			"url": "/networking/interface/{ifname}",
			"arguments": {
				"iftype": {
					"type": "str",
					"description": "interface type",
					"default": "veth"
				},
				"mac": {
					"type": "str",
					"description": "mac address to assign to the interface",
					"default": None
				},
				"ip": {
					"type": "str",
					"description": "IP address to assign to the interface",
					"default": None
				},
				"netmask": {
					"type": "str",
					"description": "Which netmask to assign the the ip address on the interface",
					"default": None
				},
				"state": {
					"type": "str",
					"description": "Which state to put the interface in",
					"default": "up"
				},
				"attached": {
					"type": "bool",
					"description": "Defines if the interface should be attached to the virtual machine",
					"default": False
				},
				"bridge": {
					"type": "str",
					"description": "Which bridge (if any) this interface should be added to",
					"default": None
				},
				"namespace": {
					"type": "str",
					"description": "Which namespace (if any) this interface should be moved in to (also moves the bridge)",
					"default": None
				},
				"pair_name": {
					"type": "str",
					"description": "Which name to give the veth-pair's other interface (the target on the other end of this interface)",
					"default": None
				}
			}
		
		},
		"phys" : {
			"url": "/networking/interface/{ifname}",
			"arguments": {
				"iftype": {
					"type": "str",
					"description": "interface type",
					"default": "phys"
				},
				"mac": {
					"type": "str",
					"description": "mac address to assign to the interface",
					"default": None
				},
				"ip": {
					"type": "str",
					"description": "IP address to assign to the interface",
					"default": None
				},
				"netmask": {
					"type": "str",
					"description": "Which netmask to assign the the ip address on the interface",
					"default": None
				},
				"state": {
					"type": "str",
					"description": "Which state to put the interface in",
					"default": "up"
				},
				"attached": {
					"type": "bool",
					"description": "Defines if the interface should be attached to the virtual machine",
					"default": False
				},
				"bridge": {
					"type": "str",
					"description": "Which bridge (if any) this interface should be added to",
					"default": None
				},
				"namespace": {
					"type": "str",
					"description": "Which namespace (if any) this interface should be moved in to (also moves the bridge)",
					"default": None
				}
			}
		}
	}

@app.get("/capabilities/networking/namespace/create", tags=["capabilities"])
def get_network_namespace_arguments() -> Dict[
			str,
			Union[
				str, int, bool, None, List[str], Dict[
					str,
					Union[
						str, int, bool, None, List[str], Dict[
							str,
							Union[
								str, int, bool, None, List[str], Dict[
									str,
									Union[
										str, int, bool, None, List[str], Dict[
											str,
											Union[
												str, int, bool, None, List[str], Dict[
													str,
													Union[
														str, int, bool, None, List[str], Dict[
															str,
															Union[
																str, int, bool, None, List[str]
															]
														]
													]
												]
											]
										]
									]
								]
							]
						]
					]
				]
			]
		]:
	"""
	Returns information on how to create a namespace.
	"""
	return {
		"namespace" : {
			"url": "/networking/namespace/{name}",
			"arguments": {
				"name": {
					"type": "str",
					"description": "What name to give the new namespace that will be created",
					"default": None
				}
			}
		}
	}

@app.get("/capabilities/qemu/machine/create", tags=["capabilities"])
def get_qemu_machine_arguments() -> Dict[
			str,
			Union[
				str, int, bool, None, List[str], Dict[
					str,
					Union[
						str, int, bool, None, List[str], Dict[
							str,
							Union[
								str, int, bool, None, List[str], Dict[
									str,
									Union[
										str, int, bool, None, List[str], Dict[
											str,
											Union[
												str, int, bool, None, List[str], Dict[
													str,
													Union[
														str, int, bool, None, List[str], Dict[
															str,
															Union[
																str, int, bool, None, List[str]
															]
														]
													]
												]
											]
										]
									]
								]
							]
						]
					]
				]
			]
		]:
	"""
	Returns the information on how to create a virtual machine.
	"""
	return {
		"namespace" : {
			"url": "/qemu/machine/{name}",
			"arguments": {
				"name": {
					"type": "str",
					"description": "What name to give the new virtual machine",
					"default": None
				},
				"namespace": {
					"type": "str",
					"description": "What namespace to (create and) put this machine in (if any)",
					"default": None
				},
				"cpu": {
					"type": "str",
					"description": "What CPU parameters to give the machine",
					"default": "host"
				},
				"enable_kvm": {
					"type": "bool",
					"description": "This enables or disables hardware acceleration for the new vm",
					"default": True
				},
				"machine": {
					"type": "str",
					"description": "This tells qemu what kind of machine parameters to set",
					"default": "q35,accel=kvm"
				},
				"devices": {
					"type": "list",
					"description": "A list of devices to attach to the machine",
					"default": ["intel-iommu"]
				},
				"memory": {
					"type": "int",
					"description": "How much memory to attach to the machine",
					"default": 8192
				},
				"drives": {
					"type": "list",
					"description": "What drives to attach to the machine (default attaches UEFI)",
					"default": [
						"if=pflash,format=raw,readonly=on,file=/usr/share/ovmf/x64/OVMF_CODE.fd",
						"if=pflash,format=raw,readonly=on,file=/usr/share/ovmf/x64/OVMF_VARS.fd"
					]
				},
				"pcie_root_ports": {
					"type": "list",
					"description": "Which PCIe root ports to create (default creates pcie.0 without the need to define it)",
					"default": []
				},
				"pcie_slave_buses": {
					"type": "list",
					"description": "Which PCIe slave buses to create on the given root ports",
					"default": []
				},
				"pcie_slave_devices": {
					"type": "list",
					"description": "Which PCIe slave devices to create on the slave buses",
					"default": []
				},
				"harddrives": {
					"type": "list",
					"description": "Which haddrives to attach (this is an alias for setting up slave devices etc)",
					"default": [],
					"arguments": {
						"filename": {
							"type": "str",
							"description": "What filename to give or use for the haddrive",
							"default": None
						},
						"size": {
							"type": "int",
							"description": "What size (in GB) to allocate to the new drive",
							"default": None
						}
					}
				},
				"cdroms": {
					"type": "list",
					"description": "Which CD-ROM's/ISO's to attach (this is an alias for setting up slave devices etc)",
					"default": [],
					"arguments": {
						"filename": {
							"type": "str",
							"description": "What filename to locate when attaching the ISO",
							"default": None
						}
					}
				},
				"network": {
					"type": "list",
					"description": "Which network infrastructure to setup surrounding this virtual machine",
					"default": [],
					"arguments": {
						"iftype": {
							"type": "str",
							"description": "interface type",
							"default": "veth"
						},
						"mac": {
							"type": "str",
							"description": "mac address to assign to the interface",
							"default": None
						},
						"ip": {
							"type": "str",
							"description": "IP address to assign to the interface",
							"default": None
						},
						"netmask": {
							"type": "str",
							"description": "Which netmask to assign the the ip address on the interface",
							"default": None
						},
						"state": {
							"type": "str",
							"description": "Which state to put the interface in",
							"default": "up"
						},
						"attached": {
							"type": "bool",
							"if": "iftype=tap|veth",
							"description": "Defines if the interface should be attached to the virtual machine",
							"default": False
						},
						"bridge": {
							"type": "str",
							"description": "Which bridge (if any) this interface should be added to",
							"default": None
						},
						"namespace": {
							"type": "str",
							"description": "Which namespace (if any) this interface should be moved in to (also moves the bridge)",
							"default": None
						},
						"pair_name": {
							"type": "str",
							"if": "iftype=veth",
							"description": "Which name to give the veth-pair's other interface (the target on the other end of this interface)",
							"default": None
						}
					}
				},
				"graphics": {
					"type": "bool",
					"description": "Enable a graphical terminal (disables headless operation and requires X/Wayland)",
					"default": False
				},
				"service_location": {
					"type": "str",
					"description": "Where to store the service file (if any) for the new virtual machine",
					"default": "/etc/systemd/system/"
				},
				"config_location": {
					"type": "str",
					"description": "Where to store the machine configuration (environment file)",
					"default": "/etc/qemu.d/"
				}
			}
		}
	}