from typing import List, Optional, Union, Dict
from pathlib import Path

from sandboxcreator.input_parser.sandbox import Sandbox, Device, Protocol,\
    DevicePurpose, DeviceType
from sandboxcreator.io.writer import Writer


class String:
    """Ruby string attribute"""

    def __init__(self, variable: str, value: str):
        self.variable: str = variable
        self.value: str = value


class Integer:
    """Ruby integer attribute"""

    def __init__(self, variable: str, value: str):
        self.variable: str = variable
        self.value: str = value


class Variable:
    """Ruby variable attribute"""

    def __init__(self, name: str, value: str, equal: bool = True):
        self.name: str = name
        self.value: str = value
        self.equal: bool = equal


class Block:
    """Ruby block"""

    def __init__(self, variable: str, name: Optional[str],
                 internal_variable: str, content: List,
                 note: Optional[str] = None):
        self.variable: str = variable
        self.name: Optional[str] = name
        self.internal_variable: str = internal_variable
        self.content: List = content
        self.note: Optional[str] = note

    def __iter__(self):
        return iter(self.content)


class Method:
    """Ruby method"""

    def __init__(self, variable: str, arguments: List[Union[Integer, String]],
                 single_line: bool = False):
        self.variable: str = variable
        self.arguments: List[Union[Integer, String]] = arguments
        self.single_line: bool = single_line


class Hash:
    """Ruby hash attribute"""

    def __init__(self, name: str, content: Dict):
        self.name: str = name
        self.content: Dict = content


class Array:
    """Ruby array"""

    def __init__(self, name: str, content: List):
        self.name: str = name
        self.content: List = content


class Vagrantfile:
    """Object with all data for Vagrantfile generation"""

    def __init__(self, sandbox: Sandbox):
        self.root: Block = Vagrantfile._create_root(sandbox)
        self.variables: List = Vagrantfile._create_variables(sandbox)

    @staticmethod
    def _create_variables(sandbox) -> List:
        """Create a list of Ruby variables for the Vagrantfile"""
        variables: List = [Vagrantfile._generate_groups(sandbox)]

        return variables

    @staticmethod
    def _generate_groups(sandbox) -> Hash:
        """Generate a variable with all groups for Vagrantfile"""

        hosts_group: List[str] = []
        routers_group: List[str] = []
        ssh_group: List[str] = []
        winrm_group: List[str] = []
        ansible_group: List[str] = []

        for device in sandbox.devices:
            ansible_group.append(device.name)
            if device.device_type == DeviceType.HOST:
                hosts_group.append(device.name)
            elif device.device_type == DeviceType.ROUTER:
                routers_group.append(device.name)
            if device.protocol == Protocol.SSH:
                ssh_group.append(device.name)
            elif device.protocol == Protocol.WINRM:
                winrm_group.append(device.name)

        groups: Dict = {"hosts": Array("hosts", hosts_group),
                        "routers": Array("routers", routers_group),
                        "ssh": Array("ssh", ssh_group),
                        "winrm": Array("winrm", winrm_group),
                        "ansible": Array("ansible", ansible_group)}

        for name, devices in sandbox.groups.items():
            if name not in ["hosts", "routers", "ssh", "winrm", "ansible"]:
                groups[name] = Array(name, devices)

        return Hash("ansible_groups", groups)

    @staticmethod
    def _create_root(sandbox: Sandbox) -> Block:
        """Create root of the vagrantfile with all its content"""
        content: List = Vagrantfile._add_devices(sandbox)
        return Block("configure(\"2\")", None, "config", content)

    @staticmethod
    def _add_preconfig(device: Device, sandbox: Sandbox,
                       group: Optional[str] = None) -> Block:
        """Add pre-configuration block to Vagrantfile definition"""
        provisioner = "ansible" if sandbox.ansible_installed else "ansible_local"
        content: List = Vagrantfile._add_preconfig_attributes(device, sandbox,
                                                              group)
        return Block("vm.provision", provisioner, "ansible", content)

    @staticmethod
    def _add_preconfig_attributes(device: Device, sandbox: Sandbox,
                                  group: Optional[str] = None) -> List:
        """Add attributes to pre-configuration"""
        attributes: List = [String("playbook",
                                   sandbox.config["preconfig_playbook"]),
                            Variable("groups", "ansible_groups")]
        if group is None:
            attributes.append(String("limit", device.name))
        else:
            attributes.append(String("limit", group))
        if sandbox.verbose_ansible:
            attributes.append(String("verbose", "vv"))
        return attributes

    @staticmethod
    def _add_provisioning(device: Device, sandbox: Sandbox,
                          group: Optional[str] = None) -> Block:
        """Add provisioning block to Vagrantfile definition"""
        provisioner = "ansible" if sandbox.ansible_installed else "ansible_local"
        content: List = Vagrantfile._add_provisioning_attributes(device,
                                                                 sandbox, group)
        return Block("vm.provision", provisioner, "ansible", content)

    @staticmethod
    def _add_provisioning_attributes(device: Device, sandbox: Sandbox,
                                     group: Optional[str] = None) -> List:
        """Add attributes to provisioning"""
        attributes: List = [String("playbook",
                                   sandbox.config["provisioning_playbook"]),
                            Variable("groups", "ansible_groups")]
        if sandbox.verbose_ansible:
            attributes.append(String("verbose", "vv"))
        if sandbox.extra_vars is not None:
            attributes.append(String("extra_vars",
                                     sandbox.config["user_extra_vars"]))
        if sandbox.include_requirements:
            attributes.append(String("galaxy_role_file",
                                     "provisioning/requirements.yml"))
            attributes.append(String("galaxy_roles_path", "provisioning/roles"))
            attributes.append(String("galaxy_command",
                                     "sudo ansible-galaxy install --role-file="
                                     "%{role_file} --roles-path=%{roles_path} "
                                     "--force"))
        if group is None:
            attributes.append(String("limit", device.name))
        else:
            attributes.append(String("limit", group))

        return attributes

    @staticmethod
    def _add_devices(sandbox: Sandbox) -> List[Block]:
        """Add device blocks and their content to vagrantfile definition"""

        devices: List = []
        for device in sandbox.devices:
            device_attributes: List = Vagrantfile._add_device_attributes(device,
                                                                         sandbox)
            devices.append(Block("vm.define", device.name, "device",
                                 device_attributes,
                                 f"Device({device.device_type}): {device.name}"))

        return devices

    @staticmethod
    def _list_winrm_hosts(sandbox: Sandbox) -> str:
        """Return a string with names of all winrm hosts"""
        winrm_hosts: List[str] = []
        for device in sandbox.devices:
            if device.device_purpose is DevicePurpose.HOST and \
                    device.protocol is Protocol.WINRM:
                winrm_hosts.append(device.name)

        joined_winrm_hosts: str = ",".join(winrm_hosts)
        return joined_winrm_hosts

    @staticmethod
    def _add_device_attributes(device: Device, sandbox: Sandbox):
        """Add attributes to devices"""

        attributes: List = [String("vm.hostname", device.name),
                            String("vm.box", device.box)]

        if device.protocol == Protocol.WINRM:
            attributes.append(String("vm.communicator", "winrm"))
            attributes.append(String("ssh.username", "windows"))
            attributes.append(String("winrm.username", "windows"))
            attributes.append(String("winrm.password", "vagrant"))

        vm_attributes: List = [Integer("memory", device.memory),
                               Integer("cpus", device.cpus)]
        if device.usb_passthrough:
            vm_attributes.append(Variable("customize",
                                          '["modifyvm", :id, "--usb", "on"]', False))
        attributes.append(Block("vm.provider", "virtualbox", "vb",
                                vm_attributes))

        if not sandbox.ansible_installed and device.protocol is Protocol.SSH:
            synced_folder_attributes: List = [String("", "."),
                                              String("", "/vagrant"),
                                              String("type", "rsync"),
                                              String("rsync__exclude", ".git/")]
            attributes.append(Method("vm.synced_folder",
                                     synced_folder_attributes, False))

        for interface in device.interfaces:
            net_attributes: List = [String("", interface.network.type),
                                    String("virtualbox__intnet",
                                           interface.network.name),
                                    String("ip", interface.ip),
                                    String("netmask",
                                           interface.network.cidr.netmask)]
            attributes.append(Method("vm.network", net_attributes, False))

        if sandbox.ansible_installed:
            attributes.append(Vagrantfile._add_preconfig(device, sandbox))
            attributes.append(Vagrantfile._add_provisioning(device, sandbox))
        else:
            if sandbox.controller_present:
                if device.protocol is Protocol.SSH:
                    if device.device_purpose is DevicePurpose.CONTROLLER:
                        attributes.append(Vagrantfile._add_preconfig(device,
                                                                     sandbox))
                        attributes.append(
                            Vagrantfile._add_preconfig(device, sandbox, "winrm"))
                        attributes.append(
                            Vagrantfile._add_provisioning(device, sandbox,
                                                          Vagrantfile._list_winrm_hosts(sandbox)))
                    else:
                        attributes.append(
                            Vagrantfile._add_preconfig(device, sandbox))
                        attributes.append(
                            Vagrantfile._add_provisioning(device, sandbox))
            else:
                attributes.append(Vagrantfile._add_preconfig(device, sandbox))
                attributes.append(Vagrantfile._add_provisioning(device, sandbox))

        return attributes

    def generate(self, output_file: Path, template_name: str):
        """Generate Vagrantfile"""

        Writer.generate_file_from_template(output_file, template_name,
                                           self.root, self.variables)
